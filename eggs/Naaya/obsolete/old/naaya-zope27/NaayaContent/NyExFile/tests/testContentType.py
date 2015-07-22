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
from Products.NaayaContent.NyExFile.NyExFile import addNyExFile
from Products.Naaya.tests import NaayaTestCase

class NaayaContentTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for NaayaContent object
    """
    def afterSetUp(self):
        self.login()
        
    def beforeTearDown(self):
        self.logout()

    def test_main(self):
        """ Add, Find, Edit and Delete Naaya Extended Files """
        #add NyExFile
        addNyExFile(self._portal().info, id='exfile1', title='exfile1', lang='en')
        addNyExFile(self._portal().info, id='exfile1_fr', title='exfile1_fr', lang='fr')
        
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Extended File'])
        #get added NyExFile
        for x in meta:
            if x.getLocalProperty('title', 'en') == 'exfile1':
                meta = x
            if x.getLocalProperty('title', 'fr') == 'exfile1_fr':
                meta_fr = x
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'exfile1')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'exfile1_fr')
        
        #change NyExFile title
        meta.saveProperties(title='exfile1_edited', lang='en')
        meta_fr.saveProperties(title='exfile1_fr_edited', lang='fr')
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'exfile1_edited')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'exfile1_fr_edited')
        
        #delete NyExFile
        self._portal().info.manage_delObjects([meta.id])
        self._portal().info.manage_delObjects([meta_fr.id])
        
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Extended File'])
        self.assertEqual(meta, [])

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NaayaContentTestCase))
    return suite
