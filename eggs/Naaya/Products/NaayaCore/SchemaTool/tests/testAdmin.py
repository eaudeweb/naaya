from unittest import TestSuite, makeSuite

from DateTime import DateTime
from Testing import ZopeTestCase
from Products.Naaya.tests import NaayaTestCase, NaayaFunctionalTestCase

from Products.NaayaCore.SchemaTool.Schema import Schema

class SchemaAdminTest(NaayaFunctionalTestCase.NaayaFunctionalTestCase):
    """ Functional TestCase for Naaya Schema Tool administration interface """

    def afterSetUp(self):
        self.browser_do_login('admin', '')

    def beforeTearDown(self):
        self.browser_do_logout()

    def test_schemas_list(self):
        self.browser.go('http://localhost/portal/portal_schemas/admin_html')

        html = self.browser.get_html()
        self.failUnless('<h1>Manage content types</h1>' in html)

        self.failUnless('HTML Document' in html)
        self.failUnless('portal_schemas/NyDocument/admin_html' in html)

    def test_schema(self):
        self.browser.go('http://localhost/portal/portal_schemas/NyDocument/admin_html')

        html = self.browser.get_html()
        self.failUnless('<h1>Manage content types - HTML Document</h1>' in html)

        self.failUnless('Title' in html)
        self.failUnless('portal_schemas/NyDocument/title-property/admin_html' in html)
        self.failUnless('Release date' in html)
        self.failUnless('portal_schemas/NyDocument/releasedate-property/admin_html' in html)

    def test_schema_widget(self):
        self.browser.go('http://localhost/portal/portal_schemas/NyDocument/title-property/admin_html')

        html = self.browser.get_html()
        self.failUnless('<h1>Manage content types - HTML Document - title</h1>' in html)


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(SchemaAdminTest))
    return suite
