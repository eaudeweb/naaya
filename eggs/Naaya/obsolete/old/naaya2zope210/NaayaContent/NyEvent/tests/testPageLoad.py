from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.NyFolder import addNyFolder
from Products.NaayaContent.NyEvent.NyEvent import addNyEvent

class PageLoadTests(NaayaTestCase):
    def afterSetUp(self):
        portal = self.app.portal
        addNyFolder(portal, 'test_folder')
        addNyEvent(portal.test_folder, id='test_event', title='Test event')

    def beforeTearDown(self):
        self.app.portal.test_folder.manage_delObjects('test_event')
        self.app.portal.manage_delObjects('test_folder')

    def test_page_load(self):
        """
        Try to render some basic pages; if they raise exceptions the test will fail.
        """
        test_folder = self.app.portal.test_folder
        test_event = self.app.portal.test_folder.test_event

        test_folder.event_add_html()
        test_event.index_html()
        test_event.edit_html()

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(PageLoadTests))
    return suite
