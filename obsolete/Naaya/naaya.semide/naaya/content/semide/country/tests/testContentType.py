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
# Alexandru Plugaru, Eau de Web

from unittest import TestSuite, makeSuite
from naaya.content.semide.country.country_item import addNyCountry, METATYPE_OBJECT as METATYPE_NYCOUNTRY 
from Products.Naaya.tests import NaayaTestCase

class NaayaContentTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for NaayaContent object
    """
    def afterSetUp(self):
        self.login()
        
    def beforeTearDown(self):
        self.logout()

    def test_main(self):
        """ Add, Find, Edit and Delete Naaya Country Folders """
        addNyCountry(self._portal().info, id='country1', title="Country1", lang="en")
        addNyCountry(self._portal().info, id='country2', title="Country2", lang="fr")
        
        for x in self._portal().getCatalogedObjectsCheckView(meta_type=[METATYPE_NYCOUNTRY, ]):
            if x.getLocalProperty('title', 'en') == 'Country1':
                country = x
            if x.getLocalProperty('title', 'fr') == 'Country2':
                country_fr = x
        
        self.assertEqual(country.getLocalProperty('title', 'en'), 'Country1')
        self.assertEqual(country_fr.getLocalProperty('title', 'fr'), 'Country2')
        
        country.saveProperties(title='Country1_edited', lang='en')
        country_fr.saveProperties(title='Country2_edited', lang='fr')
        
        self.assertEqual(country.getLocalProperty('title', 'en'), 'Country1_edited')
        self.assertEqual(country_fr.getLocalProperty('title', 'fr'), 'Country2_edited')
        
        #delete NyCountry
        self._portal().info.manage_delObjects([country.id, country_fr.id])
        
        self.assertEqual(len(self._portal().getCatalogedObjectsCheckView(meta_type=[METATYPE_NYCOUNTRY, ])), 0)
        
def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NaayaContentTestCase))
    return suite