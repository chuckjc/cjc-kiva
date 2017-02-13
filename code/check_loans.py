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


import decimal as dec
import sqlalchemy as sa
import sys

from db import model


def print_loan_schedule(sched):
    print('loan %d, amount %s, %d payments of %s, last_payment %s' % (
        sched.loan_id, sched.loan_amount, sched.num_payments-1,
        sched.payment_amount, sched.last_payment_amount))
    for lender_sched in sched.lender_schedules:
        print('  lender_id %s : loan %s, payments %s, last_payment %s' %(
            lender_sched.lender_id, lender_sched.loan_amount,
            lender_sched.payment_amount, lender_sched.last_payment_amount))


def loan_consistency_ok(sched):
    consistent = True
    num_payments = sched.num_payments
    num_payers = len(sched.lender_schedules)
    if sched.loan_amount != (sched.payment_amount * (num_payments-1)
                             + sched.last_payment_amount):
        print("loan %d amount %s payment %s last_payment %s num_payments %d incorrect" %
              (sched.loan_id, sched.loan_amount, sched.payment_amount,
               sched.last_payment_amount, num_payments))
        consistent = False
    payers_sum = dec.Decimal(0)
    payment_sum = dec.Decimal(0)
    last_payment_sum = dec.Decimal(0)
    for lender_sched in sched.lender_schedules:
        loan_amount= lender_sched.loan_amount
        payment = lender_sched.payment_amount
        last_payment = lender_sched.last_payment_amount
        payers_sum += loan_amount
        payment_sum += payment
        last_payment_sum += last_payment
        total_payments = payment * (num_payments-1) + last_payment
        if total_payments != loan_amount:
            print("(lender %s payment %s times (num_payments-1) %d plus last_payment %s == %s) != lender_loan_amount %s!!" % (
                lender_sched.lender_id, lender_sched.payment_amount,
                num_payments-1, lender_sched.last_payment_amount,
                total_payments, lender_sched.loan_amount))
            consistent = False
    if payers_sum != sched.loan_amount:
        print('sum of lender loan amounts %s != borrower loan amount %s' % (
            payers_sum, sched.loan_amount))
        consistent = False
    total_payment_sum = payment_sum * (num_payments-1)
    if total_payment_sum + last_payment_sum != sched.loan_amount:
        print('sum lender payments %s+%s == %s != borrower loan amount %s' % (
            total_payment_sum, last_payment_sum,
            total_payment_sum + last_payment_sum, sched.loan_amount))
        consistent = False
    if payment_sum > sched.payment_amount:
        print('not enough money %s to pay lenders %s' % (
            sched.payment_amount, payment_sum))
        consistent = False
    balance_b4_last_payment = sched.loan_amount - total_payment_sum
    if balance_b4_last_payment != last_payment_sum:
        print('balance before last %s-%s = %s != last lender payments %s' % (
            sched.loan_amount, total_payment_sum, balance_b4_last_payment,
            last_payment_sum))
        consistent = False
    return consistent


engine = sa.create_engine(model.DB_URL)
model.Base.metadata.create_all(engine)
Session = sa.orm.sessionmaker(bind=engine)
session = Session()

loan_schedules = session.query(model.LoanRepaymentSchedule).all()

bad_schedules = 0
for loan_schedule in loan_schedules:
    print_loan_schedule(loan_schedule)
    if loan_consistency_ok(loan_schedule):
        print('  loan checks out!')
    else:
        bad_schedules += 1

if bad_schedules == 0:
    print("It's all good")
else:
    print("%d bad schedules" % bad_schedules)

sys.exit(0 if bad_schedules == 0 else 1)

