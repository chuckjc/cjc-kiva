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


import json
import requests

import kivaquery as kq

# due to rate limiting, this takes a minute or 2 to complete
# this can fail due to real-time changes in server data, so
# only repeatable failures are important

url = kq.loan_scan_status_url_fmt % 'fundraising'
url2_fmt = url + '&page=%d'
query = kq.KivaQuery()

test_response = requests.get(url)
test_results = json.loads(test_response.text)
test_loans = test_results['loans']
item = query.get_next(url, 'loans')
assert(item == test_loans[0])
pages = test_results['paging']['pages']
total_items = test_results['paging']['total']
page_size = test_results['paging']['page_size']
batch_size = page_size
print('found %d pages of %d items each, %d items total' %
      (pages, page_size, total_items))
test_response = requests.get(url2_fmt % 2)
test_results = json.loads(test_response.text)
test_loans.extend(test_results['loans'])

query._reset_if_new(None)
collection = []
items = 0
batches = 0
while True:
    batch = query.get_next_batch(url, batch_size, 'loans')
    if not batch:
        break
    batches += 1
    print('batch %d, batch_size %d, last_page %d: retrieved items %d to %d' %
          (batches, batch_size, query.last_page, items, items+len(batch)-1))
    items += len(batch)
    collection.extend(batch)
    if query.last_page > query.limit + 2:
        print('exit loop: %d queries, %d limit' % (
            query.last_page, query.limit))
        break
    if items > page_size * 12:
        batch_size = page_size * 2
    elif items > page_size * 9:
        batch_size = page_size // 2
    elif items > page_size * 6:
        batch_size = page_size + 11
    elif items > page_size * 3:
        batch_size = page_size - 7

assert(len(collection) == items)
assert(collection[:page_size*2] == test_loans)
ids = [c['id'] for c in collection]
id_set = set(ids)
idset2 = set()
indices = []
dups = set()
for i in range(len(collection)):
    id = collection[i]['id']
    if id not in idset2:
        idset2.add(id)
    else:
        dups.add(id)
        indices.append(i)
print(len(ids), len(id_set))
print(indices, dups)
# this assertion frequently fails due to changes in the remote data,
# but I'll turn it on occasionally.  A successful run implies that paging
# and batching aren't duplicating entries in the result.
# TBD: test against static data
#assert(len(ids) == len(id_set))
