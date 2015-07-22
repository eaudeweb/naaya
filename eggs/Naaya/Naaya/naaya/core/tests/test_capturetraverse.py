from unittest import TestSuite, makeSuite

from zExceptions import NotFound
import transaction

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.Naaya.NyFolder import NyFolder
from naaya.content.document import NyDocument
from naaya.core.zope2util import CaptureTraverse


class CaptureFunctionalTest(NaayaFunctionalTestCase):
    def afterSetUp(self):
        self.calls = []
        def callback(context, path, REQUEST):
            if path[-1] == 'notfound':
                raise NotFound
            self.calls.append(repr(path))
            return '%r, x = %r' % (path, REQUEST.get('x', None))
        NyDocument.capturetestthingie = CaptureTraverse(callback)

    def beforeTearDown(self):
        del NyDocument.capturetestthingie

    def test_simple_get(self):
        self.browser.go('http://localhost/portal/info/contact/'
                        'capturetestthingie/aaa/bb/c13')
        expected_html = "('aaa', 'bb', 'c13'), x = None"
        self.assertEqual(self.browser.get_html(), expected_html)
        self.assertEqual(self.calls, ["('aaa', 'bb', 'c13')"])

        self.calls[:] = []
        self.browser.go('http://localhost/portal/info/contact/'
                        'capturetestthingie/other/zz?x=asdf')
        expected_html = "('other', 'zz'), x = 'asdf'"
        self.assertEqual(self.browser.get_html(), expected_html)
        self.assertEqual(self.calls, ["('other', 'zz')"])

    def test_not_found(self):
        self.browser.go('http://localhost/portal/info/contact/'
                        'capturetestthingie/a/b/somethingelse')
        self.assertEqual(self.browser.result.http_code, 200)
        self.browser.go('http://localhost/portal/info/contact/'
                        'capturetestthingie/a/b/notfound')
        self.assertEqual(self.browser.result.http_code, 404)

    def test_security(self):
        NyDocument.capturetestthingie__roles__ = ('Administrator', 'Manager')

        self.browser.go('http://localhost/portal/info/contact/'
                        'capturetestthingie/a/b/c')
        self.assertAccessDenied()
        self.assertEqual(len(self.calls), 0)

        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/info/contact/'
                        'capturetestthingie/a/b/c')
        self.assertAccessDenied()
        self.assertEqual(len(self.calls), 0)
        self.browser_do_logout()

        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/contact/'
                        'capturetestthingie/a/b/c')
        self.assertAccessDenied(False)
        self.assertEqual(len(self.calls), 1)
        self.browser_do_logout()

        del NyDocument.capturetestthingie__roles__
