import time

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.NaayaLinkChecker.LinkChecker import LinkChecker
from Products.NaayaLinkChecker.LinkChecker import manage_addLinkChecker


class PageLoadTests(NaayaTestCase):
    def afterSetUp(self):
        self.login()
        portal = self.app.portal
        manage_addLinkChecker(portal, 'linkchecker', 'Link Checker')
        # ZMI templates need URL0 and URL1, set by traversal in a real request
        request = portal.linkchecker.REQUEST
        request['URL'] = request['URL0'] = 'http://nohost/portal/linkchecker'
        request['URL1'] = 'http://nohost/portal'

    def beforeTearDown(self):
        self.app.portal.manage_delObjects('linkchecker')

    def test_properties_page(self):
        linkchecker = self.app.portal.linkchecker
        linkchecker.manage_edit('http://proxy.example.com:3128', 7,
                                title='Checker')
        html = linkchecker.manage_properties()
        self.assertIn('value="http://proxy.example.com:3128"', html)
        self.assertIn('name="batch_size"', html)
        self.assertIn('value="7"', html)

    def test_log_pages(self):
        linkchecker = self.app.portal.linkchecker
        self.assertNotIn('Log registered at', linkchecker.view_log())
        url_list = [('doc1', 'Naaya Document', 'portal/info/doc1',
                     'misc_/NaayaContent/NyDocument.gif',
                     [('http://broken.example.com', '404: Not Found',
                       'body', 'en')])]
        linkchecker.manage_addLogEntry('admin', time.localtime(), url_list)
        html = linkchecker.view_log()
        self.assertEqual(html.count('Log registered at'), 1)
        self.assertIn('Log registered at', linkchecker.log_html())
        [entry] = linkchecker.objectValues('LogEntry')
        entry_html = entry.index_html()
        self.assertIn('http://broken.example.com', entry_html)
        self.assertIn('404: Not Found', entry_html)

    def test_meta_types_not_shared(self):
        first = LinkChecker('first')
        second = LinkChecker('second')
        first.objectMetaType['Naaya Document'] = []
        self.assertEqual(list(second.objectMetaType), [])
