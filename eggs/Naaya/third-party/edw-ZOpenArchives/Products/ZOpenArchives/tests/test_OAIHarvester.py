from unittest import TestSuite, makeSuite

from Testing import ZopeTestCase

from Products.ZOpenArchives.OAIAggregator import manage_addOAIAggregator
from Products.ZOpenArchives.OAIHarvester import manage_addOAIHarvester

class TestOAIHarvester(ZopeTestCase.ZopeTestCase):
    def afterSetUp(self):
        """ """
        manage_addOAIAggregator(self.app, 'oai', title=u'OAI Aggregator')

    def test_basic(self):
        """ """
        manage_addOAIHarvester(self.app.oai, id='oai_harvester', title=u'OAI '
                               'Harvester', url='http://google.com/')
        self.assertTrue(hasattr(self.app.oai, 'oai_harvester'))

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestOAIHarvester))
    return suite
