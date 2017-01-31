import sqlalchemy as sa
from sqlalchemy.ext import declarative


Base = declarative.declarative_base()


class LoanRepaymentSchedule(Base):

    __tablename__ = 'LoanRepaymentSchedules'

    id = sa.Column(sa.Integer, primary_key=True)
    loan_id = sa.Column(sa.Integer)
    num_payments = sa.Column(sa.Integer)
    payment_amount = sa.Column(sa.Numeric)
    last_payment_amount = sa.Column(sa.Numeric)
    first_payment_date = sa.Column(sa.String(21))


class LenderRepaymentSchedule(Base):

    __tablename__ = 'LenderRepaymentSchedules'

    id = sa.Column(sa.Integer, primary_key=True)
    loan_repay_sched_id = sa.Column(sa.Integer, sa.ForeignKey(
        'LoanRepaymentSchedules.id', ondelete="CASCADE"))
    lender_id = sa.Column(sa.String(40))
    payment_amount = sa.Column(sa.Numeric)
    last_payment_amount = sa.Column(sa.Numeric)


class LoanRepayment(Base):

    __tablename__ = 'LoanRepayments'

    id = sa.Column(sa.Integer, primary_key=True)
    loan_repay_sched_id = sa.Column(
        sa.Integer, sa.ForeignKey('LoanRepaymentSchedules.id'))
    payment_date = sa.Column(sa.String(21))
    amount = sa.Column(sa.Numeric)


class LenderRepayment(Base):

    __tablename__ = 'LenderRepayments'

    id = sa.Column(sa.Integer, primary_key=True)
    lender_repay_sched_id = sa.Column(
        sa.Integer, sa.ForeignKey('LenderRepaymentSchedules.id'))
    payment_date = sa.Column(sa.String(21))
    amount = sa.Column(sa.Numeric)
