from unittest import TestSuite, makeSuite

from Testing import ZopeTestCase

class TestOAIToken(ZopeTestCase.ZopeTestCase):
    def test_basic(self):
        """ """

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestOAIToken))
    return suite
