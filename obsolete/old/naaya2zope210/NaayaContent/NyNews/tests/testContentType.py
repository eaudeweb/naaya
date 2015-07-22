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
from Products.NaayaContent.NyNews.NyNews import addNyNews
from Products.Naaya.tests import NaayaTestCase

class NaayaContentTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for NaayaContent object
    """
    def afterSetUp(self):
        self.login()
        
    def beforeTearDown(self):
        self.logout()

    def test_main(self):
        """ Add, Find, Edit and Delete Naaya News """
        #add Naaya News
        addNyNews(self._portal().info, title='news1', lang='en')
        addNyNews(self._portal().info, title='news1_fr', lang='fr')
        
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya News'])
        
        #Get added NyNews
        for x in meta:
            if x.getLocalProperty('title', 'en') == 'news1':
                meta = x
            if x.getLocalProperty('title', 'fr') == 'news1_fr':
                meta_fr = x
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'news1')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'news1_fr')
        
        #Change NyNews title
        meta.saveProperties(title='news1_edited', lang='en')
        meta_fr.saveProperties(title='news1_fr_edited', lang='fr')
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'news1_edited')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'news1_fr_edited')
        
        #delete NyNews
        self._portal().info.manage_delObjects([meta.id])
        self._portal().info.manage_delObjects([meta_fr.id])
        
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya News'])
        
        self.assertEqual(meta, [])

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NaayaContentTestCase))
    return suite
