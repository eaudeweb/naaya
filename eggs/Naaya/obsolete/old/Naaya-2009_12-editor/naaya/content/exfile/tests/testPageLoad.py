from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.NyFolder import addNyFolder
from naaya.content.exfile.exfile_item import addNyExFile

class PageLoadTests(NaayaTestCase):
    def afterSetUp(self):
        portal = self.app.portal
        portal.manage_install_pluggableitem('Naaya Extended File')
        addNyFolder(portal, 'test_folder')
        addNyExFile(portal.test_folder, id='test_file', title='Test file')

    def beforeTearDown(self):
        portal = self.app.portal
        self.app.portal.test_folder.manage_delObjects('test_file')
        self.app.portal.manage_delObjects('test_folder')
        portal.manage_uninstall_pluggableitem('Naaya Extended File')

    def test_page_load(self):
        """
        Try to render some basic pages; if they raise exceptions the test will fail.
        """
        test_folder = self.app.portal.test_folder
        test_file = self.app.portal.test_folder.test_file

        class test_response:
            def setHeader(self, name, value):
                pass

        test_folder.exfile_add_html()
        test_file.index_html()
        test_file.edit_html()
        test_file.download({}, test_response())
        test_file.view({}, test_response())

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(PageLoadTests))
    return suite
