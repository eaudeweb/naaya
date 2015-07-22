from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.NyFolder import addNyFolder
from naaya.content.document.document_item import addNyDocument

class PageLoadTests(NaayaTestCase):
    def afterSetUp(self):
        portal = self.app.portal
        addNyFolder(portal, 'test_folder')
        addNyDocument(portal.test_folder, 'test_document')

    def beforeTearDown(self):
        self.app.portal.test_folder.manage_delObjects('test_document')
        self.app.portal.manage_delObjects('test_folder')

    def test_page_load(self):
        """
        Try to render some basic pages; if they raise exceptions the test will fail.
        """
        test_document = self.app.portal.test_folder.test_document

        test_document.index_html()
        test_document.edit_html()
        test_document.add_html()

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(PageLoadTests))
    return suite
