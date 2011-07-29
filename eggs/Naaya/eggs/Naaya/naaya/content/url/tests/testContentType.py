from unittest import TestSuite, makeSuite
from naaya.content.url.url_item import addNyURL
from Products.Naaya.tests import NaayaTestCase

class NaayaContentTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for NaayaContent object
    """
    def afterSetUp(self):
        self.login()
        
    def beforeTearDown(self):
        self.logout()

    def test_main(self):
        """ Add, Find, Edit and Delete Naaya URLs """
        #add NyURL
        addNyURL(self._portal().info, id='url1', title='url1', lang='en')
        addNyURL(self._portal().info, id='url1_fr', title='url1_fr', lang='fr')
        
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya URL'])
        
        #get added NyURL
        for x in meta:
            if x.getLocalProperty('title', 'en') == 'url1':
                meta = x
            if x.getLocalProperty('title', 'fr') == 'url1_fr':
                meta_fr = x
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'url1')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'url1_fr')
        
        #change NyURL title
        meta.saveProperties(title='url1_edited', lang='en', locator='www.google.com')
        meta_fr.saveProperties(title='url1_fr_edited', lang='fr', locator='www.wikipedia.org')
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'url1_edited')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'url1_fr_edited')
        
        self.assertEqual(meta.sortorder, 100)
        
        #delete NyURL
        self._portal().info.manage_delObjects([meta.id])
        self._portal().info.manage_delObjects([meta_fr.id])
        
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya URL'])
        self.assertEqual(meta, [])
