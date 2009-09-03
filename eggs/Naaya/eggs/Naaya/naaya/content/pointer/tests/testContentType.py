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
from Products.NaayaContent.NyPointer.NyPointer import addNyPointer
from Products.Naaya.tests import NaayaTestCase

class NaayaContentTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for NaayaContent object
    """
    def afterSetUp(self):
        self.login()
        
    def beforeTearDown(self):
        self.logout()

    def test_main(self):
        """ Add, Find, Edit and Delete Naaya Pointers """
        #add NyPointer
        addNyPointer(self._portal().info, id='pointer1', title='pointer1', lang='en')
        addNyPointer(self._portal().info, id='pointer1_fr', title='pointer1_fr', lang='fr')
        
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Pointer'])
        
        #get added NyPointer
        for x in meta:
            if x.getLocalProperty('title', 'en') == 'pointer1':
                meta = x
            if x.getLocalProperty('title', 'fr') == 'pointer1_fr':
                meta_fr = x
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'pointer1')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'pointer1_fr')
        
        #change NyPointer title
        meta.saveProperties(title='pointer1_edited', lang='en', pointer='http://www.google.com')
        meta_fr.saveProperties(title='pointer1_fr_edited', lang='fr', pointer='http://fr.wikipedia.org')
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'pointer1_edited')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'pointer1_fr_edited')
        
        #delete NyPointer
        self._portal().info.manage_delObjects([meta.id])
        self._portal().info.manage_delObjects([meta_fr.id])
        
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Pointer'])
        self.assertEqual(meta, [])

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NaayaContentTestCase))
    return suite
