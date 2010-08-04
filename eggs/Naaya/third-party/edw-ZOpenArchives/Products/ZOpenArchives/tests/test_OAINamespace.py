from unittest import TestSuite, makeSuite

from Testing import ZopeTestCase

class TestOAINamespace(ZopeTestCase.ZopeTestCase):
    def test_basic(self):
        """ """

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestOAINamespace))
    return suite
