from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.NyFolder import addNyFolder
from naaya.content.mediafile.mediafile_item import addNyMediaFile

class PageLoadTests(NaayaTestCase):
    def afterSetUp(self):
        portal = self.app.portal
        portal.manage_install_pluggableitem('Naaya Media File')
        addNyFolder(portal, 'test_folder')
        addNyMediaFile(portal.test_folder, id='test_media_file', title='Test media file', _skip_videofile_check=True)

    def beforeTearDown(self):
        portal = self.app.portal
        portal.test_folder.manage_delObjects('test_media_file')
        portal.manage_delObjects('test_folder')
        portal.manage_uninstall_pluggableitem('Naaya Media File')

    def test_page_load(self):
        """
        Try to render some basic pages; if they raise exceptions the test will fail.
        """
        test_folder = self.app.portal.test_folder
        test_media_file = self.app.portal.test_folder.test_media_file

        test_folder.mediafile_add_html()
        test_media_file.index_html()
        test_media_file.edit_html()

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(PageLoadTests))
    return suite
