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
from naaya.content.institution.institution_item import addNyInstitution
from Products.Naaya.tests import NaayaTestCase

class NaayaContentTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for NaayaContent object
    """
    def afterSetUp(self):
        self.login()
        self.install_content_type('Naaya Institution')
        
    def beforeTearDown(self):
        self.remove_content_type('Naaya Institution')
        self.logout()

    def test_main(self):
        """ Add, Find, Edit and Delete Naaya Institutions """
        #add NyInstitution
        addNyInstitution(self._portal().info, id='institution', name='Institution Name', lang='en')
        addNyInstitution(self._portal().info, id='institution_fr', name='Institution Name FR', lang='fr')
        
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Institution'])
        
        #get added NyInstitution
        for x in meta:
            if x.getLocalProperty('name', 'en') == 'Institution Name':
                meta = x
            if x.getLocalProperty('name', 'fr') == 'Institution Name FR':
                meta_fr = x
        
        self.assertEqual(meta.getLocalProperty('name', 'en'), 'Institution Name')
        self.assertEqual(meta_fr.getLocalProperty('name', 'fr'), 'Institution Name FR')
        
        #change NyInstitution name
        meta.saveProperties(name='Institution Name edited', surname='Institution Surname edited', lang='en')
        meta_fr.saveProperties(name='Institution Name FR edited', surname='Institution Surname FR edited', lang='fr')
        
        self.assertEqual(meta.getLocalProperty('name', 'en'), 'Institution Name edited')
        self.assertEqual(meta_fr.getLocalProperty('name', 'fr'), 'Institution Name FR edited')
        
        self.assertEqual(meta.sortorder, 100)
        
        #delete NyInstitution
        self._portal().info.manage_delObjects([meta.id])
        self._portal().info.manage_delObjects([meta_fr.id])
        
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Institution'])
        self.assertEqual(meta, [])

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NaayaContentTestCase))
    return suite
