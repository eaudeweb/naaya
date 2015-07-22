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
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Andrei Laza, Eau de Web

#Python imports
from unittest import TestSuite, makeSuite
from HTMLParser import HTMLParser

#Zope imports
import transaction

#Product imports
from Products.Naaya.NyFolder import addNyFolder
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

class Parser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)

        self.found_letter_listing = False
        self.num_rows = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for at in attrs:
                if at[0] == 'href' and at[1].endswith('first_letter=A'):
                    self.found_letter_listing = True
        if tag == 'tr':
            self.num_rows += 1

class ListingByLetterTest(NaayaFunctionalTestCase):
    """ functional test for listing locations by letter """
    symbol_ids = ['symbol1', 'symbol2']
    titles = ['A point', 'a second point', 'the third point']
    ob_dicts = []

    def afterSetUp(self):
        self.portal.manage_install_pluggableitem('Naaya GeoPoint')
        self.portal.setDefaultSearchableContent()

        for id in self.symbol_ids:
            self.portal.portal_map.addSymbol(id, id, '', '', '', '')

        addNyFolder(self.portal, 'listing_by_letter_test', contributor='contributor',
                submited=1)
        folder = self.portal.listing_by_letter_test

        for i in range(len(self.titles)):
            ob_dict = {'id': 'id_%d' % i,
                'title': self.titles[i],
                'description': '',
                'geo_location.lat': '1.0', 'geo_location.lon': '1.0',
                'geo_location.address': '',
                'latitude': '1.0', 'longitude': '1.0',
                'geo_type': 'symbol1', 'URL': ''}
            ob_dict['id'] = folder.addNyGeoPoint(**ob_dict)
            self.ob_dicts.append(ob_dict)

            ob = self.portal.listing_by_letter_test._getOb(ob_dict['id'])
            ob.approveThis()
            self.portal.portal_map.catalogNyObject(ob)

        self.old_geotagged = self.portal.portal_map.list_geotaggable_types()
        schemas = self.portal.portal_schemas.objectValues()
        self.portal.portal_map.admin_set_contenttypes([schema.id for schema in schemas])

        transaction.commit()


    def beforeTearDown(self):
        self.portal.portal_map.admin_set_contenttypes([gt['id'] for gt in self.old_geotagged if gt['enabled']])

        ids = [ob_dict['id'] for ob_dict in self.ob_dicts]
        self.portal.listing_by_letter_test.manage_delObjects(ids)

        self.portal.manage_delObjects(['listing_by_letter_test'])

        for id in self.symbol_ids:
            self.portal.portal_map.deleteSymbol(id)

        self.portal.manage_uninstall_pluggableitem('Naaya GeoPoint')
        self.portal.setDefaultSearchableContent()

        transaction.commit()

    def test_listing(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/portal_map/admin_maplocations_html')
        parser = Parser()
        parser.feed(self.browser.get_html())
        self.assert_(not parser.found_letter_listing)

        catalog_tool = self.portal.getCatalogTool()
        catalog_tool.addIndex('full_title', 'FieldIndex', {'indexed_attrs': ['title']})
        catalog_tool.reindexIndex('full_title', {})
        transaction.commit()

        self.browser.go('http://localhost/portal/portal_map/admin_maplocations_html')
        parser = Parser()
        parser.feed(self.browser.get_html())
        self.assert_(parser.found_letter_listing)
        all_num_rows = parser.num_rows

        self.browser.go('http://localhost/portal/portal_map/admin_maplocations_html?first_letter=A')
        parser = Parser()
        parser.feed(self.browser.get_html())
        self.assert_(parser.found_letter_listing)
        a_num_rows = parser.num_rows

        self.browser.go('http://localhost/portal/portal_map/admin_maplocations_html?first_letter=B')
        parser = Parser()
        parser.feed(self.browser.get_html())
        self.assert_(parser.found_letter_listing)
        b_num_rows = parser.num_rows

        self.browser.go('http://localhost/portal/portal_map/admin_maplocations_html?first_letter=T')
        parser = Parser()
        parser.feed(self.browser.get_html())
        self.assert_(parser.found_letter_listing)
        t_num_rows = parser.num_rows

        self.assertEqual(all_num_rows - 1, a_num_rows)
        self.assertEqual(all_num_rows - 3, b_num_rows)
        self.assertEqual(all_num_rows - 2, t_num_rows)

        self.browser_do_logout()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(ListingByLetterTest))
    return suite

