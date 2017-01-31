import sqlalchemy as sa
from sqlalchemy.ext import declarative
import sqlalchemy.orm as orm


Base = declarative.declarative_base()
DB_URL = 'mysql+pymysql://localhost/kivatest'


class LenderRepaymentSchedule(Base):

    __tablename__ = 'LenderRepaymentSchedules'

    id = sa.Column(sa.Integer, primary_key=True)
    loan_repay_sched_id = sa.Column(sa.Integer, sa.ForeignKey(
        'LoanRepaymentSchedules.id', ondelete="CASCADE"))
    lender_id = sa.Column(sa.String(40))
    payment_amount = sa.Column(sa.Numeric(precision=12, scale=2))
    last_payment_amount = sa.Column(sa.Numeric(precision=12, scale=2))


class LoanRepaymentSchedule(Base):

    __tablename__ = 'LoanRepaymentSchedules'

    id = sa.Column(sa.Integer, primary_key=True)
    loan_id = sa.Column(sa.Integer, unique=True)
    num_payments = sa.Column(sa.Integer)
    payment_amount = sa.Column(sa.Numeric(precision=12, scale=2))
    last_payment_amount = sa.Column(sa.Numeric(precision=12, scale=2))
    first_payment_date = sa.Column(sa.String(21))
    lender_schedules = orm.relationship(
        LenderRepaymentSchedule, backref='loan_schedule', lazy='joined',
        cascade='all, delete-orphan')


'''
class LoanRepayment(Base):

    __tablename__ = 'LoanRepayments'

    id = sa.Column(sa.Integer, primary_key=True)
    loan_repay_sched_id = sa.Column(
        sa.Integer, sa.ForeignKey('LoanRepaymentSchedules.id'))
    payment_date = sa.Column(sa.String(21))
    amount = sa.Column(sa.Numeric(precision=12, scale=2))


class LenderRepayment(Base):

    __tablename__ = 'LenderRepayments'

    id = sa.Column(sa.Integer, primary_key=True)
    lender_repay_sched_id = sa.Column(
        sa.Integer, sa.ForeignKey('LenderRepaymentSchedules.id'))
    payment_date = sa.Column(sa.String(21))
    amount = sa.Column(sa.Numeric(precision=12, scale=2))
'''
