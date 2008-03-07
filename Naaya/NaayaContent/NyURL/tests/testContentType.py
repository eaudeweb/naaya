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
# David Batranu, Eau de Web
# Alin Voinea, Eau de Web

from unittest import TestSuite, makeSuite
from Products.NaayaContent.NyURL.NyURL import addNyURL
from Products.Naaya.tests import NaayaTestCase

class NaayaContentTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for NaayaContent object
    """
    def afterSetUp(self):
        self.login()
        
    def beforeTearDown(self):
        self.logout()

    def test_main(self):
        """ Add, Find, Edit and Delete Naaya URLs """
        #add NyURL
        addNyURL(self._portal().info, id='url1', title='url1', lang='en')
        addNyURL(self._portal().info, id='url1_fr', title='url1_fr', lang='fr')
        
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya URL'])
        
        #get added NyURL
        for x in meta:
            if x.getLocalProperty('title', 'en') == 'url1':
                meta = x
            if x.getLocalProperty('title', 'fr') == 'url1_fr':
                meta_fr = x
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'url1')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'url1_fr')
        
        #change NyURL title
        meta.saveProperties(title='url1_edited', lang='en')
        meta_fr.saveProperties(title='url1_fr_edited', lang='fr')
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'url1_edited')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'url1_fr_edited')
        
        #delete NyURL
        self._portal().info.manage_delObjects([meta.id])
        self._portal().info.manage_delObjects([meta_fr.id])
        
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya URL'])
        self.assertEqual(meta, [])

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NaayaContentTestCase))
    return suite
