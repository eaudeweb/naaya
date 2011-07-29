from unittest import TestSuite, makeSuite
from naaya.content.contact.contact_item import addNyContact as addNaayaContent
from naaya.content.contact.contact_item import NyContact as NaayaContent
from Products.Naaya.tests import NaayaTestCase

class NaayaContentTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for NaayaContent object
    """
    def afterSetUp(self):
        self.doc_name_en = 'mycontent_en'
        self.doc_name_fr = "mycontent_fr"
        self.doc_meta_type = NaayaContent.meta_type
        self.login()
        
    def beforeTearDown(self):
        del self.doc_name_en
        del self.doc_name_fr
        del self.doc_meta_type
        self.logout()

    def test_main(self):
        """ Add, Find, Edit and Delete Naaya Contact """
        #add Naaya Content
        addNaayaContent(self._portal().info, title=self.doc_name_en, lang='en')
        addNaayaContent(self._portal().info, title=self.doc_name_fr, lang='fr')
        
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=[self.doc_meta_type,])
        
        #Get added content
        for x in meta:
            if x.getLocalProperty('title', 'en') == self.doc_name_en:
                meta = x
            if x.getLocalProperty('title', 'fr') == self.doc_name_fr:
                meta_fr = x
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), self.doc_name_en)
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), self.doc_name_fr)
        
        #Change content title
        title_en = self.doc_name_en + '_edited'
        title_fr = self.doc_name_fr + 'edited'
        meta.saveProperties(title=title_en, lang='en')
        meta_fr.saveProperties(title=title_fr, lang='fr')
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), title_en)
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), title_fr)
        
        #delete NyNews
        self._portal().info.manage_delObjects([meta.id])
        self._portal().info.manage_delObjects([meta_fr.id])
        
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=[self.doc_meta_type,])
        
        self.assertEqual(meta, [])
