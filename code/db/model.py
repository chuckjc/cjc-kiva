# Copyright (c) 2017 Charles Carlino

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


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
    loan_amount = sa.Column(sa.Numeric(precision=12, scale=2))


class LoanRepaymentSchedule(Base):

    __tablename__ = 'LoanRepaymentSchedules'

    id = sa.Column(sa.Integer, primary_key=True)
    loan_id = sa.Column(sa.Integer, unique=True)
    loan_amount = sa.Column(sa.Numeric(precision=12, scale=2))
    num_payments = sa.Column(sa.Integer)
    payment_amount = sa.Column(sa.Numeric(precision=12, scale=2))
    last_payment_amount = sa.Column(sa.Numeric(precision=12, scale=2))
    first_payment_date = sa.Column(sa.String(21))
    lender_schedules = orm.relationship(
        LenderRepaymentSchedule, backref='loan_schedule', lazy='joined',
        cascade='all, delete-orphan')


'''
TBD: play with repayment simulations
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
