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

    def __init__(self, url):
        self.url = url
        self.paged_url = None
        self.session = requests.Session()
        self.next_page = 0
        self.total_pages = 1
        self.items_remaining = 0
        self.items = []
        self.next_item = 0

    def _limit_rate(self, headers):
        remaining = float(headers['X-RateLimit-Overall-Remaining'])
        limit = float(headers['X-RateLimit-Overall-Limit'])
        wait = 5 * (1 - remaining / limit) ** 2
        #print('limit %f, remaining %f, wait %f' % (limit, remaining, wait))
        if wait > 0.0:
            time.sleep(wait)

    def _query(self, url):
        time.sleep(0.1)
        resp = self.session.get(url)
        self._limit_rate(resp.headers)
        if resp.status_code >= 400:
            raise KivaQueryException(resp.status_code, url)
        return json.loads(resp.text)

    def _url_for_next_page(self):
        if self.next_page == 0:
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
        if self.total_pages == 1:
            if 'paging' in res:
                self.total_pages = res['paging']['pages']
        if list_name not in res:
            print("%s not found in response", list_name)
            raise KivaQueryException(400, url)
        return res[list_name]

    def get(self):
        return self._query(self.url)

    def get_next_batch(self, size, list_name):
        if len(self.items) < size:
            items = self._query_next_page(list_name)
            self.items.extend(items)
        if len(self.items) >= size:
            items = self.items[:size]
            self.items = self.items[size:]
            return items
        else:
            items = self.items
            self.items = []
        return items

