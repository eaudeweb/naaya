from unittest import TestSuite, makeSuite

import webob
import transaction

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.Naaya.NyFolder import addNyFolder
from naaya.content.document.document_item import addNyDocument

class RdfFunctionalTest(NaayaFunctionalTestCase):
    def afterSetUp(self):
        addNyFolder(self.portal, 'myfolder',
                    contributor='contributor', submitted=1)
        addNyDocument(self.portal.myfolder, id='mydoc', title='My document',
                      submitted=1, contributor='contributor')
        transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder'])
        transaction.commit()

    def assert_is_rdf(self, res):
        self.assertEqual(res.content_type, 'application/rdf+xml')
        self.assertTrue('<rdf:RDF' in res.body)

    def test_get_rdf(self):
        def get(accept=None, fmt=None, url='/portal/myfolder/mydoc'):
            req = webob.Request.blank('/portal/myfolder/mydoc')
            if accept is not None:
                req.accept = accept
            if fmt is not None:
                req.GET['format'] = 'rdf'
            return req.get_response(self.wsgi_request)

        res = get()
        self.assertEqual(res.content_type, 'text/html')

        res = get(accept='application/rdf+xml')
        self.assert_is_rdf(res)
        self.assertTrue('<rdf:Description '
                        'rdf:about="http://localhost/portal/'
                        'myfolder/mydoc">' in res.body)
        self.assertTrue('<dc:title>My document</dc:title>' in res.body)
        self.assertTrue('<dc:language>en</dc:language>' in res.body)

        res = get(fmt='rdf')
        self.assert_is_rdf(res)

    def test_security(self):
        url = 'http://localhost/portal/myfolder/mydoc?format=rdf'
        rdf_fragment = ('<rdf:Description '
                        'rdf:about="http://localhost/portal/myfolder/mydoc">')

        # first, do a public GET
        self.browser.go(url)
        self.assertAccessDenied(False)
        self.assertTrue(rdf_fragment in self.browser.get_html())

        # change the permissions
        self.portal.myfolder._View_Permission = ('Manager',)
        transaction.commit()

        # try another GET; it should fail
        self.browser.go(url)
        self.assertAccessDenied()
        self.assertFalse(rdf_fragment in self.browser.get_html())

        # try as contributor; it should fail
        self.browser_do_login('contributor', 'contributor')
        self.browser.go(url)
        self.assertAccessDenied()
        self.assertFalse(rdf_fragment in self.browser.get_html())
        self.browser_do_logout()

        # try as admin; it should work
        self.browser_do_login('admin', '')
        self.browser.go(url)
        self.assertAccessDenied(False)
        self.assertTrue(rdf_fragment in self.browser.get_html())
        self.browser_do_logout()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(RdfFunctionalTest))
    return suite
