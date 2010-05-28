from unittest import TestSuite, makeSuite

from Testing import ZopeTestCase

ZopeTestCase.installProduct('Five')
ZopeTestCase.installProduct('ZCatalog')
ZopeTestCase.installProduct('TextIndexNG3')

class TestZCatalogHarverster(ZopeTestCase.ZopeTestCase):
    def test_basic(self):
        """ """

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestZCatalogHarverster))
    return suite
