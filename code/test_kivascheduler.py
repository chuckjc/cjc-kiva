import decimal as dec

import kivascheduler as ks


calc_tests = [
    [(100,10), (10,10)],
    [(100,9), ('11.11','11.12')],
    [(100,11), ('9.09','9.1')],
    [(100,1), (100,100)],
    [(100,10,True), (10,10)],
    [(100,9,True), ('11.12','11.04')],
    [(100,11,True), ('9.1','9.0')],
    [(100,1, True), (100,100)],
]

date_tests = [
    ['2011-01-17T07:00:00Z', '2011-02-17T07:00:00Z'],
    ['2011-02-17T07:00:00Z', '2011-03-17T07:00:00Z'],
    ['2011-03-17T07:00:00Z', '2011-04-17T07:00:00Z'],
    ['2011-04-17T07:00:00Z', '2011-05-17T07:00:00Z'],
    ['2011-05-17T07:00:00Z', '2011-06-17T07:00:00Z'],
    ['2011-06-17T07:00:00Z', '2011-07-17T07:00:00Z'],
    ['2011-07-22T22:37:52Z', '2011-08-22T22:37:52Z'],
    ['2011-08-22T22:37:52Z', '2011-09-22T22:37:52Z'],
    ['2011-09-22T22:37:52Z', '2011-10-22T22:37:52Z'],
    ['2011-10-22T22:37:52Z', '2011-11-22T22:37:52Z'],
    ['2011-11-22T22:37:52Z', '2011-12-22T22:37:52Z'],
    ['2011-12-22T22:37:52Z', '2012-01-22T22:37:52Z'],
]

test_loans = [
    {'id': 7778888, 'terms': {
        'loan_amount': 1234,
        'repayment_term': 11,
        'disbursal_date': '2011-05-17T07:00:00Z',
    }},
    {'id': 7779999, 'terms': {
        'loan_amount': 4321,
        'repayment_term': 24,
        'disbursal_date': '2017-01-22T07:00:00Z',
    }},
    {'id': 9876543, 'terms': {
        'loan_amount': 500,
        'repayment_term': 10,
        'disbursal_date': '2016-12-19T07:11:22Z',
    }},
]

test_lenders = [
    {'lender_id': 'jackel8755'},
    {'lender_id': 'johnny809'},
    {'lender_id': 'harry223'},
    {'lender_id': 'joey755'},
    {'lender_id': 'mary4891'},
    {'lender_id': 'sally83857'},
    {'lender_id': 'fido347'},
    {'lender_id': 'candie103'},
    {'lender_id': 'perky20'},
    {'lender_id': 'smokey387'},
]


sched_tests = [
    (test_loans[0], test_lenders[:8]),
    (test_loans[1], test_lenders[2:]),
    (test_loans[2], [test_lenders[5]]),
    (test_loans[2], test_lenders[3:]),
]


for test in calc_tests:
    amt = test[0][0]
    num = test[0][1]
    d1, dlast = ks.calculate_distribution(*test[0])
    #print(amt, num, d1, dlast)
    assert(dec.Decimal(test[1][0]) == d1)
    assert(dec.Decimal(test[1][1]) == dlast)
    assert(d1 * (num-1) + dlast == amt)

for test in date_tests:
    res = ks.add_a_month_utc(test[0])
    #print(test[0], test[1], res)
    assert(test[1] == res)

scheduler = ks.KivaScheduler()
for loan, lenders in sched_tests:
    res = scheduler.schedule_loan(loan, lenders)
    amount = dec.Decimal('0.0')
    print(res)
    num_payments = loan['terms']['repayment_term']
    for lnd in res['lender_schedules']:
        lnd_pays = (lnd['payment_amount'] * (num_payments - 1) +
                   lnd['last_payment_amount'])
        amount += lnd_pays
        print(lnd['payment_amount'], num_payments,
              lnd['last_payment_amount'], lnd_pays, amount)
        assert(lnd_pays == lnd['loan_amount'])
    print(amount, loan['terms']['loan_amount'])
    assert(amount == loan['terms']['loan_amount'])

print('passed!')
