from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.NyFolder import addNyFolder
from Products.NaayaContent.NyPublication.NyPublication import addNyPublication

class PageLoadTests(NaayaTestCase):
    def afterSetUp(self):
        portal = self.app.portal
        addNyFolder(portal, 'test_folder')
        addNyPublication(portal.test_folder, id='test_publication', title='test_publication')

    def beforeTearDown(self):
        self.app.portal.test_folder.manage_delObjects('test_publication')
        self.app.portal.manage_delObjects('test_folder')

    def test_page_load(self):
        """
        Try to render some basic pages; if they raise exceptions the test will fail.
        """
        test_folder = self.app.portal.test_folder
        test_publication = self.app.portal.test_folder.test_publication

        test_folder.publication_add_html()
        test_publication.index_html()
        test_publication.edit_html()

class CommonOperations(NaayaTestCase):
    def test_create(self):
        defitem = ('publication1', 'publication 1', 'addNyPublication')
        self.login('contributor')
        info = self.portal.info
        test_id = info.addNyPublication('test', 'test Publication')
        test = info[test_id]
        item_id = test[defitem[2]](defitem[0], defitem[1])
        item = test[item_id]
        item.approved

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(PageLoadTests))
    return suite
