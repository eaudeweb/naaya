from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.NyFolder import addNyFolder
from Products.NaayaContent.NyFile.NyFile import addNyFile

class PageLoadTests(NaayaTestCase):
    def afterSetUp(self):
        portal = self.app.portal
        addNyFolder(portal, 'test_folder')
        addNyFile(portal.test_folder, 'test_file', title='test_file')

    def beforeTearDown(self):
        self.app.portal.test_folder.manage_delObjects('test_file')
        self.app.portal.manage_delObjects('test_folder')

    def test_page_load(self):
        """
        Try to render some basic pages; if they raise exceptions the test will fail.
        """
        test_folder = self.app.portal.test_folder
        test_file = self.app.portal.test_folder.test_file

        class test_response:
            def setHeader(self, name, value):
                pass

        test_folder.file_add_html()
        test_file.index_html()
        test_file.edit_html()
        test_file.download({}, test_response())
        test_file.view({}, test_response())

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(PageLoadTests))
    return suite
