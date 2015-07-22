from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.NyFolder import addNyFolder
from Products.NaayaContent.NyURL.NyURL import addNyURL

class PageLoadTests(NaayaTestCase):
    def afterSetUp(self):
        portal = self.app.portal
        addNyFolder(portal, 'test_folder')
        addNyURL(portal.test_folder, id='test_url', title='test_url')

    def beforeTearDown(self):
        self.app.portal.test_folder.manage_delObjects('test_url')
        self.app.portal.manage_delObjects('test_folder')

    def test_page_load(self):
        """
        Try to render some basic pages; if they raise exceptions the test will fail.
        """
        test_folder = self.app.portal.test_folder
        test_url = self.app.portal.test_folder.test_url

        test_folder.url_add_html()
        test_url.index_html()
        test_url.edit_html()

class CommonOperations(NaayaTestCase):
    def test_create(self):
        defitem = ('url1', 'url 1', 'addNyURL')
        self.login('contributor')
        info = self.portal.info
        test_id = info.addNyURL('test', 'test URL')
        test = info[test_id]
        item_id = test[defitem[2]](defitem[0], defitem[1])
        item = test[item_id]
        item.approved

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(PageLoadTests))
    return suite
