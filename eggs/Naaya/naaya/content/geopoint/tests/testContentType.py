from unittest import TestSuite, makeSuite
from naaya.content.geopoint.geopoint_item import addNyGeoPoint
from Products.Naaya.tests import NaayaTestCase
from Products.NaayaCore.SchemaTool.widgets.geo import Geo

class NaayaContentTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for NaayaContent object
    """
    def afterSetUp(self):
        self.login()
        
    def beforeTearDown(self):
        self.logout()

    def test_main(self):
        """ Add, Find, Edit and Delete Naaya Geo Point """
        addNyGeoPoint(self._portal().info, id='doc1', title='doc1', lang='en',
            geo_location=Geo('13', '14', 'here!'))
        addNyGeoPoint(self._portal().info, id='doc1_fr', title='doc1_fr', lang='fr',
            geo_location=Geo('15', '16', 'there'))
        
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya GeoPoint'])
        
        #Get added NyGeoPoint
        for x in meta:
            if x.getLocalProperty('title', 'en') == 'doc1':
                meta = x
            if x.getLocalProperty('title', 'fr') == 'doc1_fr':
                meta_fr = x
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'doc1')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'doc1_fr')
        self.assertEqual(meta.geo_location, Geo('13', '14', 'here!'))
        
        #Change NyGeoPoint title
        meta.saveProperties(title='doc1_edited', lang='en', geo_location=Geo("123.01", "234.30"))
        meta_fr.saveProperties(title='doc1_fr_edited', lang='fr', geo_location=Geo("123.01", "234.30"))
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'doc1_edited')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'doc1_fr_edited')
        
        #delete NyGeoPoint
        self._portal().info.manage_delObjects([meta.getId(),])
        self._portal().info.manage_delObjects([meta_fr.getId(),])
        
        brains = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya GeoPoint'])
        self.assertEqual(len(brains), 0)
