import lxml.etree
from urllib2 import HTTPError
from unittest import TestSuite, makeSuite

from Testing import ZopeTestCase
from Products.ZCatalog.ZCatalog import ZCatalog, manage_addZCatalog


from edw.ZOpenArchives.zOAIAggregator import manage_addOAIAggregator
from edw.ZOpenArchives.zOAIHarvester import manage_addOAIHarvester

ZopeTestCase.installProduct('Five')
ZopeTestCase.installProduct('ZCatalog')
ZopeTestCase.installProduct('TextIndexNG3')

class TestZCatalogHarverster(ZopeTestCase.FunctionalTestCase):

    def afterSetUp(self):
        manage_addOAIAggregator(self.app, 'aggregator')

    def test_basic(self):
        """
        This test requires an external fully functional OAI server.
        The ZopeOAIServer is not fully implemented. At least verb=ListSets
        is not implmemented.
        """
        return #
        manage_addOAIHarvester(self.app.aggregator, id='harvester', title="Harvester",
                        host='www.documentation.ird.fr', url='/fdi/oai.php')
        harvester = getattr(self.app.aggregator, 'harvester', None)
        self.assertNotEqual(harvester, None)
        self.assertNotEqual(harvester.list_sets, [])

        #Selecting only a few sets from the server
        harvester.list_sets_selected = [harvester.list_sets[0]['spec'], ]
        harvester.list_sets_all = '0'

        #make an update
        harvester.do_updateSite()
        self.assertNotEqual(harvester.objectValues(['zOAIRecord', ]), [])
        last_update = harvester.site_status['lastUpdate']

        # Now let's fail
        harvester.site_host = 'localhost'
        self.assertRaises(HTTPError, harvester.do_updateSite)

        #Should be equal because the last request for update should fail
        self.assertEqual(last_update, harvester.site_status['lastUpdate'])

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestZCatalogHarverster))
    return suite
