# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alin Voinea, Eau de Web
import time
from unittest import TestSuite, makeSuite
from naaya.content.mediafile.mediafile_item import addNyMediaFile
from Products.Naaya.tests.NaayaTestCase import FunctionalTestCase
from Globals import package_home
from naaya.content.mediafile.converters.MediaConverter import can_convert


class NaayaContentTestCase(FunctionalTestCase):
    home = package_home(globals())
    
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
        self.assertNotEqual(self.loadFile('data/square.flv').read(), doc.get_data())
        self.failUnless(doc.get_size()>=4000)
    
    def test_upload(self):
        addNyMediaFile(self._portal().info, id='media1', title='media1', lang='en', _skip_videofile_check=True)
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Media File'])[0]
        f = self.loadFile('data/square.flv')
        f.headers = {'content-type': 'application/x-flash-video'}
        meta.handleMediaUpload(f)
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'media1')
        
        if can_convert():
            self._test_with_coverter(meta)
        else:
            self.assertEqual(self.loadFile('data/square.flv').read(), meta.get_data())

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

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NaayaContentTestCase))
    return suite
