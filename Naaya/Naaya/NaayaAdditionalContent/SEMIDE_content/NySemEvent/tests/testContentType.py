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
from Products.NaayaContent.NySemEvent.NySemEvent import addNySemEvent
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
        addNySemEvent(self._portal().info, id='event1', title='event1', lang='en', coverage="all", start_date="12/12/2000")
        addNySemEvent(self._portal().info, id='event1_fr', title='event1_fr', lang='fr', coverage="all", start_date="12/12/2000")
        
        docs = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Semide Event'])
        self.assertEqual(len(docs), 2)
        
        #get added NyEvent
        for x in docs:
            if x.getLocalProperty('title', 'en') == 'event1':
                meta = x
            if x.getLocalProperty('title', 'fr') == 'event1_fr':
                meta_fr = x
            
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'event1')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'event1_fr')
        
        #change NyEvent title
        meta.saveProperties(title='event1_edited', lang='en', coverage="all", start_date="12/12/2000")
        meta_fr.saveProperties(title='event1_fr_edited', lang='fr', coverage="all", start_date="12/12/2000")
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'event1_edited')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'event1_fr_edited')
        
        #delete NyEvent
        self._portal().info.manage_delObjects([meta.id])
        self._portal().info.manage_delObjects([meta_fr.id])
        
        brains = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Semide Event'])
        self.assertEqual(len(brains), 0)

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NaayaContentTestCase))
    return suite
