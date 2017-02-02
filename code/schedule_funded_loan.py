
import kivaquery as kq
import kivascheduler as ks

query = kq.KivaQuery()
url = kq.loan_scan_status_url_fmt % 'funded'

while True:
    loans = query.get_next_batch(url, 15, 'loans')
    i = 1
    for loan in loans:
        print(i, ' : ',
              'loan of %(loan_amount)d to %(name)s, %(lender_count)d lenders'
              % loan)
        i += 1
    index = -1
    while index < 0 or index > 14:
        resp = input('select one by number or press return for more: ')
        if not resp:
            break
        try:
            index = int(resp) - 1
        except ValueError:
            pass
    if index > -1:
           break

loan = loans[index]
url = kq.loan_get_url_fmt % loan['id']
loandata = query.get_next(url, 'loans')
url = kq.loan_lenders_url_fmt % loan['id']
lenders = query.get_next_batch(url, loan['lender_count'], 'lenders')

print(lenders)
scheduler = ks.KivaScheduler()
loan_schedule = scheduler.schedule_loan(loandata, lenders)

loan_schedules = scheduler.get_loan_schedules()

anonymous = 0
for sched in loan_schedules:
    if sched['loan_id'] == loan['id']:
        print('loan of %d to %s, %d payments of ' % (
            loan['loan_amount'], loan['name'], sched['num_payments']-1),
              str(sched['payment_amount']), 'last_payment',
              str(sched['last_payment_amount']), ', %d lenders' %
              loan['lender_count'])
        for lender in lenders:
            for lnd_sched in sched['lender_schedules']:
                if lnd_sched['lender_id'] == lender['lender_id']:
                    break
                lnd_sched = None
            if lnd_sched:
                name = lender['name'] if 'name' in lender else lender[
                    'lender_id']
                print('  lender %s : loan %s, payments %s, last_payment %s' %(
                    name, str(lnd_sched['loan_amount']),
                    str(lnd_sched['payment_amount']),
                    str(lnd_sched['last_payment_amount'])))
