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
from naaya.content.expert.expert_item import addNyExpert
from Products.Naaya.tests import NaayaTestCase

class NaayaContentTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for NaayaContent object
    """
    def afterSetUp(self):
        self.login()
        self.install_content_type('Naaya Expert')
        
    def beforeTearDown(self):
        self.remove_content_type('Naaya Expert')
        self.logout()

    def test_main(self):
        """ Add, Find, Edit and Delete Naaya Experts """
        #add NyExpert
        addNyExpert(self._portal().info, id='expert', name='Expert Name', surname='Expert Surname', lang='en')
        addNyExpert(self._portal().info, id='expert_fr', name='Expert Name FR', surname='Expert Surname FR', lang='fr')
        
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Expert'])
        
        #get added NyExpert
        for x in meta:
            if x.getLocalProperty('name', 'en') == 'Expert Name':
                meta = x
            if x.getLocalProperty('name', 'fr') == 'Expert Name FR':
                meta_fr = x
        
        self.assertEqual(meta.getLocalProperty('name', 'en'), 'Expert Name')
        self.assertEqual(meta_fr.getLocalProperty('name', 'fr'), 'Expert Name FR')
        
        #change NyExpert name
        meta.saveProperties(name='Expert Name edited', surname='Expert Surname edited', lang='en')
        meta_fr.saveProperties(name='Expert Name FR edited', surname='Expert Surname FR edited', lang='fr')
        
        self.assertEqual(meta.getLocalProperty('name', 'en'), 'Expert Name edited')
        self.assertEqual(meta_fr.getLocalProperty('name', 'fr'), 'Expert Name FR edited')
        
        self.assertEqual(meta.sortorder, 100)
        
        #delete NyExpert
        self._portal().info.manage_delObjects([meta.id])
        self._portal().info.manage_delObjects([meta_fr.id])
        
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Expert'])
        self.assertEqual(meta, [])

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NaayaContentTestCase))
    return suite
