from unittest import TestSuite, makeSuite

from Testing import ZopeTestCase

from Products.ZOpenArchives.OAIAggregator import \
                                    manage_addOAIAggregator, OAIAggregator

class TestOAIAggregator(ZopeTestCase.ZopeTestCase):
    def test_basic(self):
        """ """
        manage_addOAIAggregator(self.app, 'oai', title=u'OAI Aggregator')
        self.assertTrue(hasattr(self.app, 'oai'))

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestOAIAggregator))
    return suite
