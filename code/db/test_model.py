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
import model
import sqlalchemy.orm as orm


engine = sa.create_engine(model.DB_URL)
model.Base.metadata.create_all(engine)
Session = orm.sessionmaker(bind=engine)
session = Session()

loan_id = 123456
lender_data = [(654321, '3.47', '3.57'), (765432, '2.34', '2.35')]
loan_sch = session.query(
    model.LoanRepaymentSchedule).filter_by(loan_id=loan_id).one_or_none()

if loan_sch:
    session.delete(loan_sch)
    session.commit()

loan_sch = model.LoanRepaymentSchedule(
    loan_id=loan_id, num_payments=13, payment_amount=dec.Decimal('25.23'),
    last_payment_amount=dec.Decimal('25.32'),
    first_payment_date='2017-02-25T21:20:05Z')

for lid, pay, last in lender_data:
    loan_sch.lender_schedules.append(model.LenderRepaymentSchedule(
        lender_id=lid, payment_amount=dec.Decimal(pay),
        last_payment_amount=dec.Decimal(last)))

print('add')
session.add(loan_sch)
session.commit()

print('check')
loan_sch = session.query(
    model.LoanRepaymentSchedule).filter_by(loan_id=loan_id).one_or_none()
assert(loan_sch != None)
assert(loan_sch.first_payment_date == '2017-02-25T21:20:05Z')
assert(isinstance(loan_sch.payment_amount, dec.Decimal))
assert(isinstance(loan_sch.last_payment_amount, dec.Decimal))
assert(int(loan_sch.payment_amount*100) == 2523)
assert(int(loan_sch.last_payment_amount*100) == 2532)
assert(int(loan_sch.lender_schedules[0].payment_amount*100) == 347)
assert(int(loan_sch.lender_schedules[1].payment_amount*100) == 234)
assert(int(loan_sch.lender_schedules[0].last_payment_amount*100) == 357)
assert(int(loan_sch.lender_schedules[1].last_payment_amount*100) == 235)
for lnd_sch in loan_sch.lender_schedules:
    assert(isinstance(lnd_sch.payment_amount, dec.Decimal))
    assert(isinstance(lnd_sch.last_payment_amount, dec.Decimal))
loan_sch.first_payment_date = '2017-03-25T21:20:05Z'

print('update', session.dirty)
session.merge(loan_sch)
session.commit()

print('check')
loan_sch = session.query(
    model.LoanRepaymentSchedule).filter_by(loan_id=loan_id).one_or_none()
assert(loan_sch != None)
assert(loan_sch.first_payment_date == '2017-03-25T21:20:05Z')

print('delete')
session.delete(loan_sch)
session.commit()

print('check')
loan_sch = session.query(
    model.LoanRepaymentSchedule).filter_by(loan_id=loan_id).one_or_none()
assert(loan_sch == None)

print('passed!')
session.close()
