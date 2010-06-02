from unittest import TestSuite, makeSuite

from Testing import ZopeTestCase

from ZOpenArchives.ZopeOAIServer import manage_addZopeOAIServer, ZopeOAIServer

ZopeTestCase.installProduct('Five')
ZopeTestCase.installProduct('ZCatalog')
ZopeTestCase.installProduct('TextIndexNG3')

class TestZopeOAIServer(ZopeTestCase.ZopeTestCase):
    def test_basic(self):
        """ """
        manage_addZopeOAIServer(self.app, 'zoai')
        self.assertTrue(hasattr(self.app, 'zoai'))

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestZopeOAIServer))
    return suite
