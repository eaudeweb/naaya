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
from naaya.content.organisation.organisation_item import addNyOrganisation
from Products.Naaya.tests import NaayaTestCase

class NaayaContentTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for NaayaContent object
    """
    def afterSetUp(self):
        self.login()
        self.install_content_type('Naaya Organisation')
        
    def beforeTearDown(self):
        self.remove_content_type('Naaya Organisation')
        self.logout()

    def test_main(self):
        """ Add, Find, Edit and Delete Naaya Organisations """
        #add NyOrganisation
        addNyOrganisation(self._portal().info, id='myorganisation', title='My organisation', lang='en')
        addNyOrganisation(self._portal().info, id='myfrenchorganisation', title='My french organisation', lang='fr')
        
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Organisation'])
        
        #get added NyOrganisation
        for x in meta:
            if x.getLocalProperty('title', 'en') == 'My organisation':
                meta = x
            if x.getLocalProperty('title', 'fr') == 'My french organisation':
                meta_fr = x
        
        #change NyOrganisation title
        meta.saveProperties(title='My edited organisation', lang='en')
        meta_fr.saveProperties(title='My edited french organisation', lang='fr')
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'My edited organisation')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'My edited french organisation')
        
        self.assertEqual(meta.sortorder, 100)
        
        #delete NyOrganisation
        self._portal().info.manage_delObjects([meta.id])
        self._portal().info.manage_delObjects([meta_fr.id])
        
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Organisation'])
        self.assertEqual(meta, [])

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NaayaContentTestCase))
    return suite
