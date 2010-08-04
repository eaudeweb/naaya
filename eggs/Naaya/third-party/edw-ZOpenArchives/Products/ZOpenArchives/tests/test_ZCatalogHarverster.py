from unittest import TestSuite, makeSuite

from Testing import ZopeTestCase

from Products.ZOpenArchives.OAIServer import manage_addOAIServer
from Products.ZOpenArchives.ZCatalogHarvester import \
                                                manage_addZCatalogHarvester
from Products.ZCatalog.ZCatalog import manage_addZCatalog

class TestZCatalogHarvester(ZopeTestCase.ZopeTestCase):
    def afterSetUp(self):
        manage_addZCatalog(self.app, 'catalog', 'Catalog')
    def test_basic(self):
        """ """
        manage_addOAIServer(self.app, 'oai_server', title=u'OAI Server')
        self.assertTrue(hasattr(self.app, 'oai_server'))

        manage_addZCatalogHarvester(self.app.oai_server, 'harv',
                            title=u'Harvester', search_meta_types='Folder')
        self.assertTrue(hasattr(self.app.oai_server, 'harv'))

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestZCatalogHarvester))
    return suite
