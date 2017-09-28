import time
import os
from StringIO import StringIO
from unittest import TestSuite, makeSuite
from naaya.content.mediafile.mediafile_item import addNyMediaFile
from Products.Naaya.tests.NaayaTestCase import FunctionalTestCase
from Globals import package_home
from mock import patch
from naaya.content.mediafile.converters.MediaConverter import can_convert


class NaayaContentTestCase(FunctionalTestCase):
    def loadFile(self, filename):
        filename = os.path.sep.join([package_home(globals()), filename])
        data = StringIO(open(filename, 'rb').read())
        data.filename = os.path.basename(filename)
        return data

    """ TestCase for NaayaContent object
    """
    def afterSetUp(self):
        self.login()

    def beforeTearDown(self):
        self.logout()

    def _test_with_coverter(self, doc):
        while not doc.mediaReady():
            time.sleep(1)
        broken = doc.mediaBroken()
        self.failIf(broken, broken)
        self.assertNotEqual(self.loadFile('data/square.mp4').read(), doc.get_data())
        self.failUnless(doc.get_size()>=4000)

    @patch('naaya.content.mediafile.converters.MediaConverter.can_convert')
    def test_upload(self, mock_can_convert):
        mock_can_convert.return_value = False
        addNyMediaFile(self._portal().info, id='media1', title='media1', lang='en', _skip_videofile_check=True)
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Media File'])[0]
        f = self.loadFile('data/square.mp4')
        f.headers = {'content-type': 'video/mp4'}
        meta.handleMediaUpload(f)
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'media1')

        self.assertEqual(self.loadFile('data/square.mp4').read(), meta.get_data())

        self._portal().info.manage_delObjects([meta.id])
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Media File'])
        self.assertEqual(meta, [])

    def test_main(self):
        """ Add, Find, Edit and Delete Naaya Media Files """
        #add NyMediaFile
        addNyMediaFile(self._portal().info, id='media1', title='media1', lang='en', _skip_videofile_check=True)
        addNyMediaFile(self._portal().info, id='media1_fr', title='media1_fr', lang='fr', _skip_videofile_check=True)

        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Media File'])

        ffmpeg = can_convert()

        #get added NyMediaFile
        for x in meta:
            if x.getLocalProperty('title', 'en') == 'media1':
                meta = x
            if x.getLocalProperty('title', 'fr') == 'media1_fr':
                meta_fr = x

        self.assertEqual(meta.getLocalProperty('title', 'en'), 'media1')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'media1_fr')

        #change NyMediaFile title
        meta.saveProperties(title='media1_edited', lang='en')
        meta_fr.saveProperties(title='media1_fr_edited', lang='fr')

        self.assertEqual(meta.getLocalProperty('title', 'en'), 'media1_edited')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'media1_fr_edited')

        #delete NyMediafile
        self._portal().info.manage_delObjects([meta.id])
        self._portal().info.manage_delObjects([meta_fr.id])

        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Media File'])
        self.assertEqual(meta, [])
