import lxml.etree
from urllib2 import HTTPError
from unittest import TestSuite, makeSuite

from Testing import ZopeTestCase
from Testing.ZopeTestCase.utils import startZServer

from OFS.Folder import Folder, manage_addFolder
from Products.ZCatalog.ZCatalog import manage_addZCatalog
from Products.ZOpenArchives.OAIServer import manage_addOAIServer, OAIServer
from Products.ZOpenArchives.ZCatalogHarvester import \
                                            manage_addZCatalogHarvester
from Products.ZOpenArchives.OAIAggregator import manage_addOAIAggregator
from Products.ZOpenArchives.OAIHarvester import manage_addOAIHarvester
from Products.ZOpenArchives.OAIRecord import OAIRecord

class TestOAIAggregatorFunctional(ZopeTestCase.FunctionalTestCase):
    """ The OAI Aggregator has ZCatalog and SQLAlchemy storages.
    The test needs an updated OAIServer.

    """
    def afterSetUp(self):
        """ Adding an OAIServer, a ZCatalog and a ZCatalogHarvester

        """
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

        manage_addZCatalogHarvester(self.app.oai, 'harvester',
                                    title=u'Harvester',
                                    search_meta_types=Folder.meta_type)

        self.server = startZServer()
        self.server_url = 'http://%s:%s/' % (self.server[0],
                                             str(self.server[1]))

    def test_zcatalog(self):
        """ Using the ZCatalog storage
        Test flow:

        Add an OAIHarvester with the local URL of the OAIServer ->
        update it against and check the presence of the OAIRecords.

        Add one folder -> update the OAIServer -> update OAIAggregator ->
        update the specific OAIHarvester and recheck it there is a new OAIRecord
        in the OAIHarvester

        Same ideea after deleting the folder that was added.

        """
        manage_addOAIAggregator(self.app, 'oai_agg', title=u"OAI Aggregator",
                                storage='ZCatalog')
        manage_addOAIHarvester(self.app.oai_agg, 'oai_harv',
                               title=u"Local OAI Server",
                               url=self.server_url + 'oai')
        self.app.oai_agg.update()
        # Has 2 records in it's contents
        self.assertEqual(len(self.app.oai_agg.oai_harv.\
                             objectValues([OAIRecord.meta_type])), 2)

        #Search catalog
        catalog = self.app.oai_agg.getCatalog()
        results = catalog.searchResults(meta_type=OAIRecord.meta_type)
        self.assertEqual(len(results), 2)

        #Adding one folder and repeat the procedure
        manage_addFolder(self.app, 'other_folder', 'Some other folder')
        self.app.other_folder.description = u'This is some kind of description'
        self.app.catalog.catalog_object(self.app.other_folder,
                                        self.app.other_folder.absolute_url(1))
        self.app.oai.harvester.update(True) #Update forced

        #Update the aggregator once again
        self.app.oai_agg.update()

        # Has 2 records in it's contents because the harvester can be updated
        # only after a day
        self.assertEqual(len(self.app.oai_agg.oai_harv.\
                             objectValues([OAIRecord.meta_type])), 2)

        #We need to do an manual update of the harvester
        self.app.oai_agg.oai_harv.update()
        self.assertEqual(len(self.app.oai_agg.oai_harv.\
                             objectValues([OAIRecord.meta_type])), 3)

        self.app.catalog.uncatalog_object(
            self.app.other_folder.absolute_url(1))
        self.app.manage_delObjects(['other_folder'])

        #Updating ZCatalogHarvester
        self.app.oai.harvester.update(True) #Update forced

        #updating OAIHarvester
        self.app.oai_agg.oai_harv.update()
        self.assertEqual(len(self.app.oai_agg.oai_harv.\
                             objectValues([OAIRecord.meta_type])), 2)

    def test_sqlalchemy(self):
        """ Same ideea as above, but using sqlalchemy """
        pass

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestOAIAggregatorFunctional))
    return suite
