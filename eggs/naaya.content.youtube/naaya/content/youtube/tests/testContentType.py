import unittest
import urllib.error
from naaya.content.youtube.youtube_item import addNyYoutube as addNaayaContent
from naaya.content.youtube.youtube_item import NyYoutube as NaayaContent
from naaya.content.youtube.youtube_item import checkExistingVideo
from naaya.content.youtube.tests.mock_youtube import YoutubeMockMixin
from naaya.content.youtube.tests.mock_youtube import patch_youtube
from Products.Naaya.tests import NaayaTestCase


class CheckExistingVideoTest(unittest.TestCase):

    def test_existing(self):
        with patch_youtube() as urlopen:
            self.assertTrue(checkExistingVideo('uelHwf8o7_U'))
        self.assertIn('watch?v=uelHwf8o7_U', urlopen.call_args[0][0])

    def test_missing(self):
        with patch_youtube():
            self.assertFalse(checkExistingVideo('aaaaaaaaaaa'))

    def test_youtube_unreachable(self):
        with patch_youtube() as urlopen:
            urlopen.side_effect = urllib.error.URLError('offline')
            self.assertTrue(checkExistingVideo('aaaaaaaaaaa'))


class NaayaContentTestCase(YoutubeMockMixin, NaayaTestCase.NaayaTestCase):
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
        """ Add, Find, Edit and Delete Naaya Youtube """
        #add Naaya Content
        addNaayaContent(self._portal().info, title=self.doc_name_en, lang='en',
            youtube_id='uelHwf8o7_U', iframe_width='640', iframe_height='360')
        addNaayaContent(self._portal().info, title=self.doc_name_fr, lang='fr',
            youtube_id='uelHwf8o7_U', iframe_width='640', iframe_height='360')
        
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
        meta.saveProperties(title=title_en, lang='en',
            youtube_id='uelHwf8o7_U', iframe_width='640', iframe_height='360')
        meta_fr.saveProperties(title=title_fr, lang='fr',
            youtube_id='uelHwf8o7_U', iframe_width='640', iframe_height='360')
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), title_en)
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), title_fr)
        
        #delete NyNews
        self._portal().info.manage_delObjects([meta.id])
        self._portal().info.manage_delObjects([meta_fr.id])
        
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=[self.doc_meta_type,])
        
        self.assertEqual(meta, [])
