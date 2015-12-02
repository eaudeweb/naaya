from unittest import TestSuite, makeSuite
import webob
import transaction
import lxml.etree
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.Naaya.NyFolder import addNyFolder
from naaya.content.document.document_item import addNyDocument


ns = {
    'dcterms': 'http://purl.org/dc/terms/',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
}


class RdfFunctionalTest(NaayaFunctionalTestCase):
    def afterSetUp(self):
        addNyFolder(self.portal, 'myfolder',
                    contributor='contributor', submitted=1)
        addNyDocument(self.portal.myfolder, id='mydoc', title='My document',
                      submitted=1, contributor='contributor')
        transaction.commit()

    def assert_is_rdf(self, res):
        self.assertEqual(res.content_type, 'application/rdf+xml')
        self.assertTrue('<rdf:RDF' in res.body)

    def _get(self, accept='application/rdf+xml',
                   url='/portal/myfolder/mydoc',
                   query={}):
        req = webob.Request.blank(url)
        if accept is not None:
            req.accept = accept
        req.GET.update(query)
        return req.get_response(self.wsgi_request)

    def test_get_rdf(self):
        res = self._get(accept=None)
        self.assertEqual(res.content_type, 'text/html')

        res = self._get()
        self.assert_is_rdf(res)

        res2 = self._get(accept='text/html', query={'format': 'rdf'})
        self.assert_is_rdf(res2)

        self.assertEqual(res.body, res2.body)


    def test_rdf_content(self):
        res = self._get()
        rdf = lxml.etree.fromstring(res.body)

        rdf_obj = rdf.xpath('./rdf:Description', namespaces=ns)[0]
        self.assertEqual(rdf_obj.attrib['{%s}about' % ns['rdf']],
                         'http://localhost/portal/myfolder/mydoc')

        rdf_title = rdf_obj.xpath('./dcterms:title', namespaces=ns)[0]
        self.assertEqual(rdf_title.text, "My document")

        rdf_language = rdf_obj.xpath('./dcterms:language',
                                             namespaces=ns)[0]
        self.assertEqual(rdf_language.text, "en")


    def test_rdf_description(self):
        res = self._get()
        rdf = lxml.etree.fromstring(res.body)
        rdf_obj = rdf.xpath('./rdf:Description', namespaces=ns)[0]
        self.assertEqual(rdf_obj.xpath('./dcterms:description', namespaces=ns),
                         [])

        self.portal['myfolder']['mydoc'].description = "document under test"
        transaction.commit()

        res = self._get()
        rdf = lxml.etree.fromstring(res.body)

        rdf_obj = rdf.xpath('./rdf:Description', namespaces=ns)[0]
        rdf_desc = rdf_obj.xpath('./dcterms:description', namespaces=ns)[0]
        self.assertEqual(rdf_desc.text, "document under test")


    def test_contributor(self):
        res = self._get()
        rdf = lxml.etree.fromstring(res.body)

        rdf_obj = rdf.xpath('./rdf:Description', namespaces=ns)[0]
        rdf_creator = rdf_obj.xpath('./dcterms:creator', namespaces=ns)[0]
        self.assertEqual(rdf_creator.text, "contributor")


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
