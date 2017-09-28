from unittest import TestSuite, makeSuite
from naaya.content.news.news_item import addNyNews
from Products.Naaya.tests import NaayaTestCase

class NaayaContentTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for NaayaContent object
    """
    def afterSetUp(self):
        self.login()
        
    def beforeTearDown(self):
        self.logout()

    def test_main(self):
        """ Add, Find, Edit and Delete Naaya News """
        #add Naaya News
        addNyNews(self._portal().info, title='news1', lang='en')
        addNyNews(self._portal().info, title='news1_fr', lang='fr')
        
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya News'])
        
        #Get added NyNews
        for x in meta:
            if x.getLocalProperty('title', 'en') == 'news1':
                meta = x
            if x.getLocalProperty('title', 'fr') == 'news1_fr':
                meta_fr = x
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'news1')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'news1_fr')
        
        #Change NyNews title
        meta.saveProperties(title='news1_edited', lang='en')
        meta_fr.saveProperties(title='news1_fr_edited', lang='fr')
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'news1_edited')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'news1_fr_edited')
        
        #delete NyNews
        self._portal().info.manage_delObjects([meta.id])
        self._portal().info.manage_delObjects([meta_fr.id])
        
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya News'])
        
        self.assertEqual(meta, [])
