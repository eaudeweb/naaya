import os, sys, time
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
import urllib.request
from unittest import mock

from Testing import ZopeTestCase
from Products.RDFSummary.rdfparser import RDFParser
ZopeTestCase.installProduct('RDFSummary')

class RDFSummaryInZopeTestCase(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        # Local copy of the feed, so the test does not need the network
        rssurl = 'file://' + os.path.join(os.path.dirname(__file__), 'exampleidabc.rss')
        self.app.manage_addProduct['RDFSummary'].manage_addRDFSummary('mysummary', 'Title', rssurl, '', 'no', self.app.REQUEST)
        assert hasattr(self.app, 'mysummary')
        self.assertNotEqual(self.app.mysummary, None)

    def test_update(self):
        self.app.mysummary.update()
        items = self.app.mysummary.items()
        self.assertEqual(5, len(items))
        self.assertEqual("CH: Federal Court's Office suite switch is first step to Open Source desktop",items[0]['title'])
        self.assertEqual("http://ec.europa.eu/idabc/en/document/7542", items[0]['link'])

class OpenUrlTestCase(unittest.TestCase):

    def open(self, url):
        proxy = urllib.request.ProxyHandler({})
        with mock.patch('urllib.request.build_opener') as build_opener:
            RDFParser(None, 0).open_url(url, proxy)
        return build_opener.return_value.open.call_args.args[0]

    def test_credentials_in_url(self):
        request = self.open('http://user:secret@example.com:8080/feed?x=1')
        self.assertEqual(request.full_url, 'http://example.com:8080/feed?x=1')
        self.assertEqual(request.get_header('Authorization'),
                         'Basic dXNlcjpzZWNyZXQ=')

    def test_no_credentials(self):
        request = self.open('http://example.com/feed')
        self.assertEqual(request.full_url, 'http://example.com/feed')
        self.assertIsNone(request.get_header('Authorization'))

def test_suite():
    from unittest import TestSuite, TestLoader
    suite = TestSuite()
    suite.addTest(TestLoader().loadTestsFromTestCase(RDFSummaryInZopeTestCase))
    suite.addTest(TestLoader().loadTestsFromTestCase(OpenUrlTestCase))
    return suite

if __name__ == '__main__':
    framework()
