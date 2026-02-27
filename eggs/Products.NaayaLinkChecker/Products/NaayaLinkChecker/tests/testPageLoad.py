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

        # ZMI page templates (manage_page_header.dtml) need URL0 and URL1
        # which are normally set by Zope's traversal mechanism.
        request = linkchecker.REQUEST
        base_url = 'http://nohost/portal/linkchecker'
        parent_url = 'http://nohost/portal'
        request['URL'] = base_url
        request['URL0'] = base_url
        request['URL1'] = parent_url

        linkchecker.index_html()
        linkchecker.manage_properties()
        linkchecker.log_html()
        linkchecker.view_log()

def test_suite():
    from unittest import TestSuite, TestLoader
    suite = TestSuite()
    suite.addTest(TestLoader().loadTestsFromTestCase(PageLoadTests))
    return suite
