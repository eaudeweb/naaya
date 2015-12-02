from unittest import TestSuite, makeSuite
from naaya.content.story.story_item import addNyStory
from Products.Naaya.tests import NaayaTestCase

class NaayaContentTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for NaayaContent object
    """
    def afterSetUp(self):
        self.login()
        
    def beforeTearDown(self):
        self.logout()

    def test_main(self):
        """ Add, Find, Edit and Delete Naaya Stories """
        #add NyStory
        addNyStory(self._portal().info, id='story1', title='story1', lang='en', submitted=1)
        addNyStory(self._portal().info, id='story1_fr', title='story1_fr', lang='fr', submitted=1)
        
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Story'])
        
        #get added NyStory
        for x in meta:
            if x.getLocalProperty('title', 'en') == 'story1':
                meta = x
            if x.getLocalProperty('title', 'fr') == 'story1_fr':
                meta_fr = x
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'story1')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'story1_fr')
        
        #change NyStory title
        meta.saveProperties(title='story1_edited', lang='en')
        meta_fr.saveProperties(title='story1_fr_edited', lang='fr')
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'story1_edited')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'story1_fr_edited')
        
        #delete NyStory
        self._portal().info.manage_delObjects([meta.id])
        self._portal().info.manage_delObjects([meta_fr.id])
        
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Story'])
        self.assertEqual(meta, [])
