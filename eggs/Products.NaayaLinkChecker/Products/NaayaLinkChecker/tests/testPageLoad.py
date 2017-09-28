from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.NaayaLinkChecker.LinkChecker import manage_addLinkChecker

class PageLoadTests(NaayaTestCase):
    def afterSetUp(self):
        self.login()
        portal = self.app.portal
        manage_addLinkChecker(portal, 'linkchecker', 'Link Checker')

    def beforeTearDown(self):
        self.app.portal.manage_delObjects('linkchecker')

    def test_page_load(self):
        """
        Try to render some basic pages; if they raise exceptions the test will fail.
        """
        linkchecker = self.app.portal.linkchecker

        linkchecker.index_html()
        linkchecker.manage_properties()
        linkchecker.log_html()
        linkchecker.view_log()

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(PageLoadTests))
    return suite
