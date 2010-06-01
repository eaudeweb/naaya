from unittest import TestSuite, makeSuite

from Testing import ZopeTestCase

from edw.ZOpenArchives.zOAIAggregator import manage_addOAIAggregator, zOAIAggregator

ZopeTestCase.installProduct('Five')
ZopeTestCase.installProduct('ZCatalog')
ZopeTestCase.installProduct('TextIndexNG3')

class TestzOAIAggregator(ZopeTestCase.ZopeTestCase):
    def test_basic(self):
        """ """
        manage_addOAIAggregator(self.app, 'oai')
        self.assertTrue(hasattr(self.app, 'oai'))
        

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestzOAIAggregator))
    return suite
