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
from unittest import TestSuite, makeSuite
from Products.NaayaPhotoArchive.NyPhotoGallery import NyPhotoGallery, addNyPhotoGallery
from Products.NaayaPhotoArchive.NyPhotoFolder import NyPhotoFolder
from Products.Naaya.tests import NaayaTestCase
from Products.NaayaBase.NyRoleManager import NyRoleManager

class NaayaContentTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for NaayaContent object
    """
    def afterSetUp(self):
        self.login()
        
    def beforeTearDown(self):
        self.logout()

    def _add_gallery(self):
        """ Add and search gallery """
        addNyPhotoGallery(self._portal().info, id='mygallery', title='Photo Gallery', lang='en')
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Photo Gallery'])
        for x in meta:
            if x.getLocalProperty('title', 'en') == 'Photo Gallery':
                return x
        return None
    
    def _add_album(self):
        """ Add and search album """
        gallery = self._add_gallery()
        if not gallery:
            raise AttributeError, gallery
        gallery.addNyPhotoFolder(id='myalbum', title='My Album', lang='en')
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Photo Folder'])
        for x in meta:
            if x.getLocalProperty('title', 'en') == 'My Album':
                return x
        return None
    
    def test_gallery(self):
        """ Add, Find, Edit and Delete Naaya Photo Gallery """
        #Add gallery
        meta = self._add_gallery()
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'Photo Gallery')
        
        #Change Gallery properties
        meta.saveProperties(title='Gallery Changed', lang='en', sortorder=meta.sortorder)
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'Gallery Changed')
        
        #Delete Gallery
        self._portal().info.manage_delObjects([meta.id])
        
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Photo Gallery'])
        for x in meta:
            if x.id == 'mygallery':
                meta = x
            else:
                meta = []
            
        self.assertEqual(meta, [])
    
    def test_album(self):
        """ Add, Find, Edit and Delete Naaya Photo Folder """
        # Add album
        meta = self._add_album()
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'My Album')
        
        # Change properties
        meta.saveProperties(title='Album changed', lang='en')
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'Album changed')
        
        #Delete Album
        gallery = meta.getParentNode()
        gallery.manage_delObjects([meta.id])
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Photo Folder'])
        for x in meta:
            if x.id == 'myalbum':
                meta = x
            else:
                meta = []
            
        self.assertEqual(meta, [])

    def test_NyRoleManager_wrappers(self):
        self.assertTrue(NyPhotoFolder.manage_addLocalRoles == NyRoleManager.manage_addLocalRoles)
        self.assertTrue(NyPhotoFolder.manage_setLocalRoles == NyRoleManager.manage_setLocalRoles)
        self.assertTrue(NyPhotoFolder.manage_delLocalRoles == NyRoleManager.manage_delLocalRoles)

        self.assertTrue(NyPhotoGallery.manage_addLocalRoles == NyRoleManager.manage_addLocalRoles)
        self.assertTrue(NyPhotoGallery.manage_setLocalRoles == NyRoleManager.manage_setLocalRoles)
        self.assertTrue(NyPhotoGallery.manage_delLocalRoles == NyRoleManager.manage_delLocalRoles)

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NaayaContentTestCase))
    return suite
