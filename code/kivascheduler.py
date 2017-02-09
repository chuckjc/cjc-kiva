import datetime
import dateutil.parser as dateparser
import decimal as dec
import json
import sqlalchemy as sa

from db import model


PRECISION = dec.Decimal('.01')


def calculate_distribution(amount, num_distributions, roundup=False):
    # round up for borrower payments, round down for everything else
    rounding = dec.ROUND_UP if roundup else dec.ROUND_DOWN
    dec_amount = amount
    if not isinstance(amount, dec.Decimal):
        dec_amount = dec.Decimal(amount).quantize(PRECISION)
    distrib = (dec_amount / num_distributions).quantize(
        PRECISION, rounding=rounding)
    last_distrib = dec_amount - (num_distributions-1) * distrib
    assert(amount == distrib * (num_distributions-1) + last_distrib)
    return distrib, last_distrib


def add_a_month_utc(date_str):
    date = dateparser.parse(date_str)
    month = date.month + 1 if date.month < 12 else 1
    year = date.year
    if month == 1:
        year += 1
    new_date = datetime.datetime(year, month, date.day, date.hour,
                                 date.minute, date.second, tzinfo=date.tzinfo)
    # format below works with UTC times, replaces '+00:00' suffix with 'Z'
    return new_date.isoformat('T').split('+')[0] + 'Z'


class KivaScheduler(object):

    def __init__(self):
        self._init_db()

    def schedule_loan(self, loan, lenders):
        session = self.session_maker()
        self.loan = loan
        self.loan_id = self.loan['id']
        self.loan_amount = dec.Decimal(
            self.loan['terms']['loan_amount']).quantize(PRECISION)
        self.num_payments = self.loan['terms']['repayment_term']
        self.disbursal_date = self.loan['terms']['disbursal_date']
        # give anonymous lenders fake ids
        anum = 1
        for lender in lenders:
            if 'lender_id' not in lender:
                lender['lender_id'] = 'anonymous' + str(anum)
                anum += 1
        # only use lender_id from api, but need dict for hack loan_amount
        self.lenders = {l['lender_id']: {'lender_id':l['lender_id']}
                        for l in lenders}
        self._read_loan_schedule_db(session)
        self._create_loan_schedule(session)
        session.commit()
        sched_dict = self._get_schedule_dict(self.loan_schedule)
        session.close()
        self.loan_schedule = None
        return sched_dict

    def get_loan_schedules(self):
        session = self.session_maker()
        loan_schedules = session.query(model.LoanRepaymentSchedule).all()
        session.close()
        schedules = []
        for loan_sched in loan_schedules:
            schedules.append(self._get_schedule_dict(loan_sched))
        return schedules

    def _init_db(self):
        self.engine = sa.create_engine(model.DB_URL)
        model.Base.metadata.create_all(self.engine)
        self.session_maker = sa.orm.sessionmaker(bind=self.engine)

    def _get_lender_schedule_dict(self, lender_sched):
        lender_dict = {
            'lender_id': lender_sched.lender_id,
            'payment_amount': lender_sched.payment_amount,
            'last_payment_amount': lender_sched.last_payment_amount,
            'loan_amount': lender_sched.loan_amount,
        }
        return lender_dict

    def _get_schedule_dict(self, loan_sched):
        loan_dict = {
            'loan_id': loan_sched.loan_id,
            'num_payments': loan_sched.num_payments,
            'payment_amount': loan_sched.payment_amount,
            'last_payment_amount': loan_sched.last_payment_amount,
            'first_payment_date': loan_sched.first_payment_date,
        }
        loan_dict['lender_schedules'] = []
        for lender_sched in loan_sched.lender_schedules:
            lender_dict = self._get_lender_schedule_dict(lender_sched)
            loan_dict['lender_schedules'].append(lender_dict)
        return loan_dict

    def _read_loan_schedule_db(self, session):
        self.loan_schedule = session.query(
            model.LoanRepaymentSchedule).filter_by(
            loan_id=self.loan_id).one_or_none()
        if self.loan_schedule:
            to_del = []
            # delete lenders not in api data
            for lender_sched in self.loan_schedule.lender_schedules:
                if lender_sched.lender_id not in self.lenders:
                    to_del.append(lender_sched)
            for ls in to_del:
                self.loan_schedule.lender_schedules.remove(ls)
            # add lenders not in db
            for lender_id in self.lenders.keys():
                found = False
                for lender_sched in self.loan_schedule.lender_schedules:
                    if lender_id == lender_sched.lender_id:
                        found = True
                if not found:
                    self.loan_schedule.lender_schedules.append(
                        model.LenderRepaymentSchedule(lender_id=lender_id))
        else:
            self._setup_new_loan_db()

    def _setup_new_loan_db(self):
        self.loan_schedule = model.LoanRepaymentSchedule(
            loan_id=self.loan_id, num_payments=self.num_payments)
        for lender_id in self.lenders.keys():
            self.loan_schedule.lender_schedules.append(
                model.LenderRepaymentSchedule(lender_id=lender_id))

    def _create_loan_schedule(self, session):
        self._calculate_lender_loans()
        self._calculate_borrower_schedule()
        for lender_sched in self.loan_schedule.lender_schedules:
            sched = self._calculate_lender_schedule(lender_sched)
        session.merge(self.loan_schedule)

    def _calculate_lender_loans(self):
        # hack since we're not privileged to get real lender loan amounts
        num_lenders = len(self.lenders)
        amount, last_amount = calculate_distribution(
            self.loan_amount, num_lenders, roundup=True)
        for id in self.lenders.keys():
            lender = self.lenders[id]
            lender['loan_amount'] = amount
        self.lenders[id]['loan_amount'] = last_amount

    def _calculate_borrower_schedule(self):
        payment, last_payment = calculate_distribution(
            self.loan_amount, self.num_payments, roundup=True)
        self.loan_schedule.loan_amount = self.loan_amount
        self.loan_schedule.payment_amount = payment
        self.loan_schedule.last_payment_amount = last_payment
        self.loan_schedule.first_payment_date = add_a_month_utc(
            self.disbursal_date)

    def _calculate_lender_schedule(self, lender_sched):
        lender=self.lenders[lender_sched.lender_id]
        payment, last_payment = calculate_distribution(
            lender['loan_amount'], self.num_payments)
        lender_sched.payment_amount = payment
        lender_sched.last_payment_amount = last_payment
        lender_sched.loan_amount = lender['loan_amount']
