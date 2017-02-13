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
import time


base_url = 'http://api.kivaws.org/v1/'
loan_scan_status_url_fmt = base_url + 'loans/search.json?status=%s'
loan_lenders_url_fmt = base_url + 'loans/%s/lenders.json'
loan_get_url_fmt = base_url + 'loans/%s.json'


class KivaQueryException(Exception):

    def __init__(self, status, url):
        self.msg = "url %s failed with status %d" % (url, status)
        super(KivaQueryException, self).__init__(self.msg)

    def __str__(self):
        return self.msg


class KivaQuery(object):

    def __init__(self):
        self.session = requests.Session()
        self._reset_if_new(None)
        self.limit = 0
        self.remaining = 0

    def _reset_if_new(self, url):
        if not url or url != self.url:
            self.paged_url = None
            self.next_page = 1
            self.total_pages = 1
            self.items_remaining = 0
            self.items = []
            self.total_items_delivered = 0
            self.last_page = 0
        self.url = url

    def _limit_rate(self, headers):
        remaining = float(headers['X-RateLimit-Overall-Remaining'])
        limit = float(headers['X-RateLimit-Overall-Limit'])  # per minute
        wait = 5 * (1 - remaining / limit) ** 2
        self.limit = limit
        self.remaining = remaining
        #print('limit %f, remaining %f, wait %f' % (limit, remaining, wait))
        if wait > 0.0:
            time.sleep(wait)

    def _query(self, url):
        print(self.last_page, url)
        resp = self.session.get(url)
        self._limit_rate(resp.headers)
        if resp.status_code >= 400:
            raise KivaQueryException(resp.status_code, url)
        return json.loads(resp.text)

    def _url_for_next_page(self):
        if self.next_page == 1:
            url = self.url
        else:
            if not self.paged_url:
                if '?' in self.url:
                    self.paged_url = self.url + '&page=%d'
                else:
                    self.paged_url = self.url + '?page=%d'
            url = self.paged_url % self.next_page
        self.next_page += 1
        return url

    def _query_next_page(self, list_name):
        if self.next_page > self.total_pages:
            return []
        else:
            url = self._url_for_next_page()
        res = self._query(url)
        if 'paging' in res:
            if self.total_pages == 1:
                self.total_pages = res['paging']['pages']
            self.last_page =  res['paging']['page']
        if list_name not in res:
            print("%s not found in response", list_name)
            raise KivaQueryException(400, url)
        return res[list_name]

    def get_next_batch(self, url, size, list_name):
        self._reset_if_new(url)
        while len(self.items) < size:
            items = self._query_next_page(list_name)
            if not items:
                break
            self.items.extend(items)
        if len(self.items) >= size:
            items = self.items[:size]
            self.items = self.items[size:]
        else:
            items = self.items
            self.items = []
        self.total_items_delivered += len(items)
        return items

    def get_next(self, url, list_name):
        self._reset_if_new(url)
        items = self.get_next_batch(url, 1, list_name)
        return items[0]
