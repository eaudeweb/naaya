import os, sys, time
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
ZopeTestCase.installProduct('RDFSummary')

class RDFSummaryInZopeTestCase(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        rssurl = 'http://svn.eionet.europa.eu/repositories/Zope/trunk/RDFSummary/tests/exampleidabc.rss'
        self.app.manage_addProduct['RDFSummary'].manage_addRDFSummary('mysummary', 'Title', rssurl, '', 'no', self.app.REQUEST)
        assert hasattr(self.app, 'mysummary')
        self.assertNotEqual(self.app.mysummary, None)

    def test_update(self):
        self.app.mysummary.update()
        items = self.app.mysummary.items()
        self.assertEquals(5, len(items))
        self.assertEquals("CH: Federal Court's Office suite switch is first step to Open Source desktop",items[0]['title'])
        self.assertEquals("http://ec.europa.eu/idabc/en/document/7542", items[0]['link'])

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(RDFSummaryInZopeTestCase))
    return suite

if __name__ == '__main__':
    framework()
