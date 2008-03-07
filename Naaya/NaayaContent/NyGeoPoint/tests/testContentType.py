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
from Products.NaayaContent.NyGeoPoint.NyGeoPoint import addNyGeoPoint
from Products.Naaya.tests import NaayaTestCase

class NaayaContentTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for NaayaContent object
    """
    def afterSetUp(self):
        self.login()
        
    def beforeTearDown(self):
        self.logout()

    def test_main(self):
        """ Add, Find, Edit and Delete Naaya Geo Point """
        addNyGeoPoint(self._portal().info, id='doc1', title='doc1', lang='en', longitude="123.01", latitude="234.30")
        addNyGeoPoint(self._portal().info, id='doc1_fr', title='doc1_fr', lang='fr', longitude="123.11", latitude="234.20")
        
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya GeoPoint'])
        
        #Get added NyGeoPoint
        for x in meta:
            if x.getLocalProperty('title', 'en') == 'doc1':
                meta = x
            if x.getLocalProperty('title', 'fr') == 'doc1_fr':
                meta_fr = x
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'doc1')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'doc1_fr')
        
        #Change NyGeoPoint title
        meta.saveProperties(title='doc1_edited', lang='en', longitude="123.01", latitude="234.30")
        meta_fr.saveProperties(title='doc1_fr_edited', lang='fr', longitude="123.01", latitude="234.30")
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'doc1_edited')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'doc1_fr_edited')
        
        #delete NyGeoPoint
        self._portal().info.manage_delObjects([meta.getId(),])
        self._portal().info.manage_delObjects([meta_fr.getId(),])
        
        brains = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya GeoPoint'])
        self.assertEqual(len(brains), 0)

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NaayaContentTestCase))
    return suite
