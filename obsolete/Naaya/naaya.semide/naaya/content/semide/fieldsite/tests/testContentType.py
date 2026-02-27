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
# Alexandru Plugaru, Eau de Web

from unittest import TestSuite, makeSuite
from naaya.content.semide.fieldsite.semfieldsite_item import addNySemFieldSite, METATYPE_OBJECT
from Products.Naaya.tests import NaayaTestCase

class NaayaContentTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for NaayaContent object
    """
    def afterSetUp(self):
        self.login()
        
    def beforeTearDown(self):
        self.logout()

    def test_main(self):
        """ Add, Find, Edit and Delete Naaya Semide Events """
        #add NyEvent
        addNySemFieldSite(self._portal().info, id='fieldsite1', title='fieldsite1', lang='en', coverage="all")
        addNySemFieldSite(self._portal().info, id='fieldsite1_fr', title='fieldsite1_fr', lang='fr', coverage="all")
        
        docs = self._portal().getCatalogedObjectsCheckView(meta_type=[METATYPE_OBJECT, ])
        self.assertEqual(len(docs), 2)
        
        #get added NyFieldSite
        for x in docs:
            if x.getLocalProperty('title', 'en') == 'fieldsite1':
                meta = x
            if x.getLocalProperty('title', 'fr') == 'fieldsite1_fr':
                meta_fr = x
            
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'fieldsite1')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'fieldsite1_fr')
        
        #change NyFieldSite title
        meta.saveProperties(title='fieldsite1_edited', lang='en', coverage="all")
        meta_fr.saveProperties(title='fieldsite1_fr_edited', lang='fr', coverage="all")
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'fieldsite1_edited')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'fieldsite1_fr_edited')
        
        #delete NyFieldSite
        self._portal().info.manage_delObjects([meta.id])
        self._portal().info.manage_delObjects([meta_fr.id])
        
        brains = self._portal().getCatalogedObjectsCheckView(meta_type=[METATYPE_OBJECT, ])
        self.assertEqual(len(brains), 0)

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NaayaContentTestCase))
    return suite