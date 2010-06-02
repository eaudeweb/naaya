import lxml.etree
from unittest import TestSuite, makeSuite

from Testing import ZopeTestCase
from OFS.Folder import Folder, manage_addFolder
from Products.ZCatalog.ZCatalog import ZCatalog, manage_addZCatalog

from ZOpenArchives.ZopeOAIServer import manage_addZopeOAIServer, ZopeOAIServer
from ZOpenArchives.ZCatalogHarvester import manage_addZCatalogHarvester

ZopeTestCase.installProduct('Five')
ZopeTestCase.installProduct('ZCatalog')
ZopeTestCase.installProduct('TextIndexNG3')

class TestZCatalogHarverster(ZopeTestCase.FunctionalTestCase):
    def afterSetUp(self):
        manage_addZopeOAIServer(self.app, 'oai')
        manage_addFolder(self.app, 'folder', 'Folder')
        manage_addFolder(self.app, 'folder1', 'Folder1')
        manage_addZCatalog(self.app, 'catalog', 'Application ZCatalog')
        self.app.catalog.catalog_object(self.app.folder)
        self.app.catalog.catalog_object(self.app.folder1)

    def test_basic(self):
        """ """
        manage_addZCatalogHarvester(self.app.oai, id='harvester',
            title='Harvester', update_period='1000', autopublishRoles='Anonymous',
            pref_meta_types=Folder.meta_type)
        items = ZCatalog.searchResults(self.app.catalog, {'meta_type': Folder.meta_type})
        self.assertEqual(items[0].getObject().id, 'folder') #Is in catalog

        #Testing protocol
        response = self.publish('/oai?verb=ListRecords&metadataPrefix=oai_dc')
        dom = lxml.etree.fromstring(response.getBody())
        namespace = dom.nsmap[None]

        list_records = dom.find('./{%s}ListRecords/' % namespace)
        self.assertNotEqual(list_records, None)

        records = list_records.findall('./{%s}record' % namespace)
        self.assertEqual(len(records), 2)

        # Should raise a bad argument
        response = self.publish('/oai?verb=ListRecords')
        dom = lxml.etree.fromstring(response.getBody())
        self.assertNotEqual(dom.find("./{%s}error[@code='badArgument']" % namespace), None)

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestZCatalogHarverster))
    return suite
