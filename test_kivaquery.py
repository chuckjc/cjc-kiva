import json
import requests

import kivaquery as kq


url = kq.loan_scan_status_url_fmt % 'fundraising'
query = kq.KivaQuery(url)

test_response = requests.get(url)
test_results = json.loads(test_response.text)
get_results = query.get()
assert(test_results == get_results)

test_loans = test_results['loans']
num_items = test_results['paging']['pages']
page_size = test_results['paging']['page_size']
collection = []
count = 0
while True:
    batch = query.get_next_batch(17, 'loans')
    print('batch size: %d' % len(batch))
    if not batch:
        break
    count += len(batch)
    if len(collection) < page_size:
        to_append = page_size - len(collection)
        collection.extend(batch[:to_append])
        for i in range(len(collection)):
            print(i, collection[i]['id'], test_loans[i]['id'])
            #print(collection[i]['id'])
            #print(test_loans[i]['id'])
            assert(collection[i] == test_loans[i])

assert(len(collection) == page_size)
assert(collection == test_loans)
