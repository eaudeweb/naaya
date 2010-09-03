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
# Andrei Laza, Eau de Web

from unittest import TestSuite, makeSuite

import Products.Naaya
from Products.NaayaContent.NyPublication.NyPublication import addNyPublication
from Products.Naaya.tests import NaayaTestCase

class NaayaContentTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for NaayaContent object
    """
    def afterSetUp(self):
        self.login()
        
    def beforeTearDown(self):
        self.logout()

    def test_main(self):
        """ Add, Find, Edit and Delete Naaya Publications """
        #add NyPublication
        addNyPublication(self._portal().info, id='pub1', title='pub1', lang='en')
        addNyPublication(self._portal().info, id='pub1_fr', title='pub1_fr', lang='fr')
        
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Publication'])
        
        #get added NyPublication
        for x in meta:
            if x.getLocalProperty('title', 'en') == 'pub1':
                meta = x
            if x.getLocalProperty('title', 'fr') == 'pub1_fr':
                meta_fr = x
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'pub1')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'pub1_fr')
        
        #change NyPublication title
        meta.saveProperties(title='pub1_edited', lang='en', locator='www.google.com')
        meta_fr.saveProperties(title='pub1_fr_edited', lang='fr', locator='www.wikipedia.org')
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'pub1_edited')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'pub1_fr_edited')
        
        self.assertEqual(meta.sortorder, 100)
        
        #delete NyPublication
        self._portal().info.manage_delObjects([meta.id()])
        self._portal().info.manage_delObjects([meta_fr.id()])
        
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Publication'])
        self.assertEqual(meta, [])

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NaayaContentTestCase))
    return suite
