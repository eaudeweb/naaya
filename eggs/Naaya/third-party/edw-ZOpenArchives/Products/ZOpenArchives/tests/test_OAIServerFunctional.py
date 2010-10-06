import lxml.etree
from oaipmh.client import Client
from unittest import TestSuite, makeSuite

from Testing import ZopeTestCase
from OFS.Folder import Folder, manage_addFolder
from Products.ZCatalog.ZCatalog import manage_addZCatalog
from Products.ZOpenArchives.OAIServer import manage_addOAIServer, OAIServer
from Products.ZOpenArchives.ZCatalogHarvester import \
                                            manage_addZCatalogHarvester

class TestOAIServerFunctional(ZopeTestCase.FunctionalTestCase):
    def afterSetUp(self):
        manage_addZCatalog(self.app, 'catalog', 'Catalog')
        manage_addOAIServer(self.app, 'oai', title=u'OAI Server')

        manage_addFolder(self.app, 'folder', 'Folder')
        self.app.folder.description = u'Some descr'

        manage_addFolder(self.app, 'folder1', 'Folder1')
        self.app.folder1.description = u'Some descr111'

        self.app.catalog.catalog_object(self.app.folder,
                                        self.app.folder.absolute_url(1))
        self.app.catalog.catalog_object(self.app.folder1,
                                        self.app.folder1.absolute_url(1))

    def test_basic(self):
        """ """
        manage_addZCatalogHarvester(self.app.oai, 'harvester',
                                    title=u'Harvester',
                                    search_meta_types=Folder.meta_type)

        items = self.app.catalog.searchResults({'meta_type': Folder.meta_type})

        #Is in catalog
        self.assertTrue(str(items[0].getObject().id).startswith('folder'))

        #Testing protocol
        response = self.publish('/oai?verb=ListRecords&metadataPrefix=oai_dc')
        dom = lxml.etree.fromstring(response.getBody())
        namespace = dom.nsmap[None]

        list_records = dom.find('./{%s}ListRecords' % namespace)
        self.assertNotEqual(list_records, None)

        records = list_records.findall('./{%s}record' % namespace)
        self.assertEqual(len(records), 2)

        # Should raise a bad argument
        response = self.publish('/oai?verb=ListRecords')
        dom = lxml.etree.fromstring(response.getBody())
        self.assertNotEqual(
            dom.find("./{%s}error[@code='badArgument']" % namespace), None)

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestOAIServerFunctional))
    return suite
