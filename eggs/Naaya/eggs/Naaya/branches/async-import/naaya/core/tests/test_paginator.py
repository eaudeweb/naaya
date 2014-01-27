from BeautifulSoup import BeautifulSoup

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase

def make_url(page):
    return 'http://localhost/?page=%s' % page

class TestPaginator(NaayaTestCase):
    def test_odd_body_length(self):
        #>>> print DiggPaginator(range(1,1000), 10, body=5).page(1)
        #1 2 3 4 5 ... 99 100

        paginator = self.portal.make_paginator(range(1, 1000), 10, body=5)
        page = paginator.page(1)
        html = page.pagination(make_url=make_url)
        soup = BeautifulSoup(html)

        for i in [2, 3, 4, 5, 99, 100]:
            self.assertTrue(soup.find('a', href=make_url(i)))
        self.assertFalse(soup.find('a', href=make_url(1)))

        self.assertTrue(soup.find('span', text='Showing page'))
        self.assertTrue('999' in html)

    def test_with_main_range(self):
        #>>> print DiggPaginator(range(1,1000), 10, body=5, padding=1, margin=2).page(7)
        #1 2 ... 5 6 7 8 9 ... 99 100

        paginator = self.portal.make_paginator(range(1, 1000), 10, body=5,
                                               padding=1, margin=2)
        page = paginator.page(7)
        html = page.pagination(make_url=make_url)
        soup = BeautifulSoup(html)

        for i in [1, 2, 5, 6, 8, 9, 99, 100]:
            self.assertTrue(soup.find('a', href=make_url(i)))
        for i in [3, 4, 7, 10, 98]:
            self.assertFalse(soup.find('a', href=make_url(i)))
        self.assertTrue(soup.find('span', text='Showing page'))
        self.assertTrue('999' in html)

