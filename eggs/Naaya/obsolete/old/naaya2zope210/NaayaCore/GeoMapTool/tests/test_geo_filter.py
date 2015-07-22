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

from unittest import TestSuite, makeSuite
from decimal import Decimal

from Products.Naaya.tests import NaayaTestCase
from Products.Naaya.tests import NaayaFunctionalTestCase
from Products.NaayaContent.NyGeoPoint.tests.testFunctional import GeoPointMixin

from Products.NaayaCore.GeoMapTool import GeoMapTool
from Products.Naaya.NyFolder import addNyFolder

class GeoFilterTestCase(NaayaFunctionalTestCase.NaayaFunctionalTestCase, GeoPointMixin):
    symbols = ['Capital', 'City', 'News_type', 'Document_type', 'Story_type',
            'Pointer_type', 'URL_type', 'Event_type', 'File_type']
    objects = [
            {
                'constructor': 'addNyGeoPoint',
                'data': {
                    'id': 'sofia',
                    'title': 'Sofia',
                    'description': 'Bulgaria',
                    'geo_location.lat': '42.7',
                    'geo_location.lon': '23.333333',
                    'geo_location.address': 'Sofia Bulgaria',
                    'latitude': '2.7',
                    'longitude': '3.333333',
                    'geo_type': '',
                    'url': 'http://en.wikipedia.org/wiki/Sofia'
                }
            },
            {
                'constructor': 'addNyGeoPoint',
                'data': {
                    'id': 'bucharest',
                    'title': 'Bucharest',
                    'description': 'Romania',
                    'geo_location.lat': '44.4325',
                    'geo_location.lon': '26.103889',
                    'geo_location.address': 'Bucharest Romania',
                    'latitude': '2.7',
                    'longitude': '3.333333',
                    'geo_type': 'Capital',
                    'url': 'http://en.wikipedia.org/wiki/Bucharest'
                }
            },
            {
                'constructor': 'addNyGeoPoint',
                'data': {
                    'id': 'contanta',
                    'title': 'Constanta',
                    'description': 'Romania',
                    'geo_location.lat': '44.173333',
                    'geo_location.lon': '28.638333',
                    'geo_location.address': 'Constanta Romania',
                    'latitude': '2.7',
                    'longitude': '3.333333',
                    'geo_type': 'City',
                    'url': 'http://en.wikipedia.org/wiki/Constanta'
                }
            },
            {
                'constructor': 'addNyNews',
                'data': {
                    'id': 'news123',
                    'title': 'Test news',
                    'description': '',
                    'geo_location.lat': '45.0',
                    'geo_location.lon': '22.5',
                    'geo_location.address': 'Testing news',
                    'geo_type': 'News_type'
                }
            },
            {
                'constructor': 'addNyDocument',
                'data': {
                    'id': 'doc123',
                    'title': 'Test Document',
                    'description': '',
                    'geo_location.lat': '30.2',
                    'geo_location.lon': '15.3',
                    'geo_location.address': 'Testing document',
                    'geo_type': 'Document_type'
                }
            },
            {
                'constructor': 'addNyStory',
                'data': {
                    'id': 'story123',
                    'title': 'Story',
                    'geo_location.lat': '23.0',
                    'geo_location.lon': '15.9',
                    'geo_location.address': 'Testing story',
                    'geo_type': 'Story_type'
                }
            },
            {
                'constructor': 'addNyPointer',
                'data': {
                    'id': 'pointer123',
                    'title': 'Pointer',
                    'geo_location.lat': '33.3',
                    'geo_location.lon': '19.0',
                    'geo_location.address': 'Testing pointer',
                    'geo_type': 'Pointer_type'
                }
            },
            {
                'constructor': 'addNyURL',
                'data': {
                    'id': 'url123',
                    'title': 'URL',
                    'geo_location.lat': '31.3',
                    'geo_location.lon': '22.0',
                    'geo_location.address': 'Testing URL',
                    'geo_type': 'URL_type'
                }
            },
            {
                'constructor': 'addNyEvent',
                'data': {
                    'id': 'event123',
                    'title': 'Event',
                    'geo_location.lat': '35.3',
                    'geo_location.lon': '15.0',
                    'geo_location.address': 'Testing event',
                    'geo_type': 'Event_type'
                }
            },
            {
                'constructor': 'addNyFile',
                'data': {
                    'id': 'file123',
                    'title': 'File',
                    'geo_location.lat': '23.3',
                    'geo_location.lon': '29.0',
                    'geo_location.address': 'Testing file',
                    'geo_type': 'File_type'
                }
            }]

    def afterSetUp(self):
        self.geopoint_install()
        self.portal.setDefaultSearchableContent()

        for id in self.symbols:
            self.portal.portal_map.addSymbol(id, id, '', '', '', '')

        addNyFolder(self.portal, 'geo_location_test', contributor='contributor', submitted=1)
        folder = self.portal.geo_location_test

        for ob_dict in self.objects:
            ob_dict['data']['id'] = getattr(folder, ob_dict['constructor'])(**(ob_dict['data']))
            ob = self.portal.geo_location_test._getOb(ob_dict['data']['id'])
            ob.approveThis()
            self.portal.portal_map.recatalogNyObject(ob)

        self.old_geotagged = self.portal.portal_map.list_geotaggable_types()
        schemas = self.portal.portal_schemas.objectValues()
        self.portal.portal_map.admin_set_contenttypes([schema.id for schema in schemas])


    def beforeTearDown(self):
        self.portal.portal_map.admin_set_contenttypes([gt['id'] for gt in self.old_geotagged if gt['enabled']])

        ids = [ob['data']['id'] for ob in self.objects]
        self.portal.geo_location_test.manage_delObjects(ids)

        self.portal.manage_delObjects(['geo_location_test'])

        for ob_dict in self.objects:
            self.portal.portal_map.deleteSymbol(ob_dict['data']['id'])

        self.geopoint_uninstall()
        self.portal.setDefaultSearchableContent()

    def test_indexes_in_catalog(self):
        indexes = filter(lambda x: x.id == 'geo_latitude',
                self.portal.portal_catalog.getIndexObjects())
        self.failUnless(len(indexes) == 1)

        indexes = filter(lambda x: x.id == 'geo_longitude',
                self.portal.portal_catalog.getIndexObjects())
        self.failUnless(len(indexes) == 1)

        indexes = filter(lambda x: x.id == 'geo_address',
                self.portal.portal_catalog.getIndexObjects())
        self.failUnless(len(indexes) == 1)

    def test_objects_in_folder(self):
        for ob_dict in self.objects:
            ob = self.portal.geo_location_test._getOb(ob_dict['data']['id'])
            self.failIf(ob == None)

    def test_geo_index(self):
        catalog_tool = self.portal.getCatalogTool()
        query = {}
        for ob_dict in self.objects:
            query['geo_latitude'] = Decimal(ob_dict['data']['geo_location.lat'])
            query['geo_longitude'] = Decimal(ob_dict['data']['geo_location.lon'])
            query['geo_address'] = ob_dict['data']['geo_location.address']
            matching_items = catalog_tool(query)
            self.failUnless(len(matching_items) == 1)

    def test_geo_search(self):
        objects = self.portal.portal_map.search_geo_objects(geo_types=[''],
                lat_min=40., lat_max=43., lon_min=20., lon_max=30.,
                lat_center=41.5, lon_center=25.)

        self.failUnless(len(objects) == 1)
        self.failUnless(objects[0].geo_location.lat == Decimal('42.7'))
        self.failUnless(objects[0].geo_location.lon == Decimal('23.333333'))
        self.failUnless(objects[0].geo_location.address == 'Sofia Bulgaria')

    def test_geo_search_with_query(self):
        objects = self.portal.portal_map.search_geo_objects(geo_types=[''], query='Sofia',
                lat_min=40., lat_max=43., lon_min=20., lon_max=30.,
                lat_center=41.5, lon_center=25.)

        self.failUnless(len(objects) == 1)
        self.failUnless(objects[0].geo_location.lat == Decimal('42.7'))
        self.failUnless(objects[0].geo_location.lon == Decimal('23.333333'))
        self.failUnless(objects[0].geo_location.address == 'Sofia Bulgaria')

    def test_geo_search_geo_types(self):
        objects = self.portal.portal_map.search_geo_objects(geo_types=[''])
        self.failUnless(len(objects) == 1)
        self.failUnless(objects[0].geo_location.lat == Decimal('42.7'))
        self.failUnless(objects[0].geo_location.lon == Decimal('23.333333'))
        self.failUnless(objects[0].geo_location.address == 'Sofia Bulgaria')

        objects = self.portal.portal_map.search_geo_objects(geo_types=['Capital'])
        self.failUnless(len(objects) == 1)
        self.failUnless(objects[0].geo_location.lat == Decimal('44.4325'))
        self.failUnless(objects[0].geo_location.lon == Decimal('26.103889'))
        self.failUnless(objects[0].geo_location.address == 'Bucharest Romania')

        objects = self.portal.portal_map.search_geo_objects(geo_types=['City'])
        self.failUnless(len(objects) == 1)
        self.failUnless(objects[0].geo_location.lat == Decimal('44.173333'))
        self.failUnless(objects[0].geo_location.lon == Decimal('28.638333'))
        self.failUnless(objects[0].geo_location.address == 'Constanta Romania')

        objects = self.portal.portal_map.search_geo_objects(geo_types=['News_type'])
        self.failUnless(len(objects) == 1)
        self.failUnless(objects[0].geo_location.lat == Decimal('45.0'))
        self.failUnless(objects[0].geo_location.lon == Decimal('22.5'))
        self.failUnless(objects[0].geo_location.address == 'Testing news')

        objects = self.portal.portal_map.search_geo_objects(geo_types=['Document_type'])
        self.failUnless(len(objects) == 1)
        self.failUnless(objects[0].geo_location.lat == Decimal('30.2'))
        self.failUnless(objects[0].geo_location.lon == Decimal('15.3'))
        self.failUnless(objects[0].geo_location.address == 'Testing document')

        objects = self.portal.portal_map.search_geo_objects(geo_types=['Story_type'])
        self.failUnless(len(objects) == 1)
        self.failUnless(objects[0].geo_location.lat == Decimal('23.0'))
        self.failUnless(objects[0].geo_location.lon == Decimal('15.9'))
        self.failUnless(objects[0].geo_location.address == 'Testing story')

        objects = self.portal.portal_map.search_geo_objects(geo_types=['Pointer_type'])
        self.failUnless(len(objects) == 1)
        self.failUnless(objects[0].geo_location.lat == Decimal('33.3'))
        self.failUnless(objects[0].geo_location.lon == Decimal('19.0'))
        self.failUnless(objects[0].geo_location.address == 'Testing pointer')

        objects = self.portal.portal_map.search_geo_objects(geo_types=['URL_type'])
        self.failUnless(len(objects) == 1)
        self.failUnless(objects[0].geo_location.lat == Decimal('31.3'))
        self.failUnless(objects[0].geo_location.lon == Decimal('22.0'))
        self.failUnless(objects[0].geo_location.address == 'Testing URL')

        objects = self.portal.portal_map.search_geo_objects(geo_types=['Event_type'])
        self.failUnless(len(objects) == 1)
        self.failUnless(objects[0].geo_location.lat == Decimal('35.3'))
        self.failUnless(objects[0].geo_location.lon == Decimal('15.0'))
        self.failUnless(objects[0].geo_location.address == 'Testing event')

        objects = self.portal.portal_map.search_geo_objects(geo_types=['File_type'])
        self.failUnless(len(objects) == 1)
        self.failUnless(objects[0].geo_location.lat == Decimal('23.3'))
        self.failUnless(objects[0].geo_location.lon == Decimal('29.0'))
        self.failUnless(objects[0].geo_location.address == 'Testing file')

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(GeoFilterTestCase))
    return suite
