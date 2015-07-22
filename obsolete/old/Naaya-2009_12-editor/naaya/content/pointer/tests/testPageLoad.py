from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.NyFolder import addNyFolder
from naaya.content.pointer.pointer_item import addNyPointer

class PageLoadTests(NaayaTestCase):
    def afterSetUp(self):
        portal = self.app.portal
        addNyFolder(portal, 'test_folder')
        addNyPointer(portal.test_folder, id='test_pointer', title='Test pointer')

    def beforeTearDown(self):
        self.app.portal.test_folder.manage_delObjects('test_pointer')
        self.app.portal.manage_delObjects('test_folder')

    def test_page_load(self):
        """
        Try to render some basic pages; if they raise exceptions the test will fail.
        """
        test_folder = self.app.portal.test_folder
        test_pointer = self.app.portal.test_folder.test_pointer

        test_folder.pointer_add_html()
        test_pointer.index_html()
        test_pointer.edit_html()

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(PageLoadTests))
    return suite
