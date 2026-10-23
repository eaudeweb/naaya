import unittest
from unittest import TestSuite, TestLoader
from decimal import Decimal

from Products.Naaya.tests import NaayaTestCase
from Products.Naaya.tests import NaayaFunctionalTestCase

from Products.NaayaCore.GeoMapTool import GeoMapTool
from Products.NaayaCore.SchemaTool.widgets.geo import Geo
from Products.Naaya.NyFolder import addNyFolder
from .test_kml_parser import load_file

class GeoFilterTestCase(NaayaFunctionalTestCase.NaayaFunctionalTestCase):
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
                    'start_date': '10/10/2000',
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
        self.portal.manage_install_pluggableitem('Naaya GeoPoint')
        self.portal.setDefaultSearchableContent()

        picture_data = load_file('data/symbol.png')

        for id in self.symbols:
            self.portal.portal_map.addSymbol(id, id, '', '', None, picture_data, '')

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
        self.portal.portal_map.admin_set_contenttypes([gt['id'] for gt in self.old_geotagged if gt['geo_enabled']])

        ids = [ob['data']['id'] for ob in self.objects]
        self.portal.geo_location_test.manage_delObjects(ids)

        self.portal.manage_delObjects(['geo_location_test'])

        for ob_dict in self.objects:
            self.portal.portal_map.deleteSymbol(ob_dict['data']['id'])

        self.portal.manage_uninstall_pluggableitem('Naaya GeoPoint')
        self.portal.setDefaultSearchableContent()

    def test_indexes_in_catalog(self):
        indexes = list(filter(lambda x: x.id == 'geo_latitude',
                self.portal.portal_catalog.getIndexObjects()))
        self.assertTrue(len(indexes) == 1)

        indexes = list(filter(lambda x: x.id == 'geo_longitude',
                self.portal.portal_catalog.getIndexObjects()))
        self.assertTrue(len(indexes) == 1)

        indexes = list(filter(lambda x: x.id == 'geo_address',
                self.portal.portal_catalog.getIndexObjects()))
        self.assertTrue(len(indexes) == 1)

    def test_objects_geo_data(self):
        for ob_dict in self.objects:
            data = ob_dict['data']
            ob = self.portal.geo_location_test._getOb(data['id'])
            self.assertEqual(ob.geo_location.lat,
                             Decimal(data['geo_location.lat']))
            self.assertEqual(ob.geo_location.lon,
                             Decimal(data['geo_location.lon']))
            self.assertEqual(ob.geo_type, data['geo_type'])

    def test_geo_index(self):
        catalog_tool = self.portal.getCatalogTool()
        query = {}
        for ob_dict in self.objects:
            query['geo_latitude'] = Decimal(ob_dict['data']['geo_location.lat'])
            query['geo_longitude'] = Decimal(ob_dict['data']['geo_location.lon'])
            query['geo_address'] = ob_dict['data']['geo_location.address']
            matching_items = catalog_tool(query)
            self.assertTrue(len(matching_items) == 1)

    def test_geo_search(self):
        objects = self.portal.portal_map.search_geo_objects(geo_types=[''],
                lat_min=40., lat_max=43., lon_min=20., lon_max=30.,
                lat_center=41.5, lon_center=25.)

        self.assertTrue(len(objects) == 1)
        self.assertTrue(objects[0].geo_location.lat == Decimal('42.7'))
        self.assertTrue(objects[0].geo_location.lon == Decimal('23.333333'))
        self.assertTrue(objects[0].geo_location.address == 'Sofia Bulgaria')

    def test_geo_search_with_query(self):
        objects = self.portal.portal_map.search_geo_objects(geo_types=[''], query='Sofia',
                lat_min=40., lat_max=43., lon_min=20., lon_max=30.,
                lat_center=41.5, lon_center=25.)

        self.assertTrue(len(objects) == 1)
        self.assertTrue(objects[0].geo_location.lat == Decimal('42.7'))
        self.assertTrue(objects[0].geo_location.lon == Decimal('23.333333'))
        self.assertTrue(objects[0].geo_location.address == 'Sofia Bulgaria')

    def test_geo_search_geo_types(self):
        objects = self.portal.portal_map.search_geo_objects(geo_types=[''])
        self.assertTrue(len(objects) == 1)
        self.assertTrue(objects[0].geo_location.lat == Decimal('42.7'))
        self.assertTrue(objects[0].geo_location.lon == Decimal('23.333333'))
        self.assertTrue(objects[0].geo_location.address == 'Sofia Bulgaria')

        objects = self.portal.portal_map.search_geo_objects(geo_types=['Capital'])
        self.assertTrue(len(objects) == 1)
        self.assertTrue(objects[0].geo_location.lat == Decimal('44.4325'))
        self.assertTrue(objects[0].geo_location.lon == Decimal('26.103889'))
        self.assertTrue(objects[0].geo_location.address == 'Bucharest Romania')

        objects = self.portal.portal_map.search_geo_objects(geo_types=['City'])
        self.assertTrue(len(objects) == 1)
        self.assertTrue(objects[0].geo_location.lat == Decimal('44.173333'))
        self.assertTrue(objects[0].geo_location.lon == Decimal('28.638333'))
        self.assertTrue(objects[0].geo_location.address == 'Constanta Romania')

        objects = self.portal.portal_map.search_geo_objects(geo_types=['News_type'])
        self.assertTrue(len(objects) == 1)
        self.assertTrue(objects[0].geo_location.lat == Decimal('45.0'))
        self.assertTrue(objects[0].geo_location.lon == Decimal('22.5'))
        self.assertTrue(objects[0].geo_location.address == 'Testing news')

        objects = self.portal.portal_map.search_geo_objects(geo_types=['Document_type'])
        self.assertTrue(len(objects) == 1)
        self.assertTrue(objects[0].geo_location.lat == Decimal('30.2'))
        self.assertTrue(objects[0].geo_location.lon == Decimal('15.3'))
        self.assertTrue(objects[0].geo_location.address == 'Testing document')

        objects = self.portal.portal_map.search_geo_objects(geo_types=['Story_type'])
        self.assertTrue(len(objects) == 1)
        self.assertTrue(objects[0].geo_location.lat == Decimal('23.0'))
        self.assertTrue(objects[0].geo_location.lon == Decimal('15.9'))
        self.assertTrue(objects[0].geo_location.address == 'Testing story')

        objects = self.portal.portal_map.search_geo_objects(geo_types=['Pointer_type'])
        self.assertTrue(len(objects) == 1)
        self.assertTrue(objects[0].geo_location.lat == Decimal('33.3'))
        self.assertTrue(objects[0].geo_location.lon == Decimal('19.0'))
        self.assertTrue(objects[0].geo_location.address == 'Testing pointer')

        objects = self.portal.portal_map.search_geo_objects(geo_types=['URL_type'])
        self.assertTrue(len(objects) == 1)
        self.assertTrue(objects[0].geo_location.lat == Decimal('31.3'))
        self.assertTrue(objects[0].geo_location.lon == Decimal('22.0'))
        self.assertTrue(objects[0].geo_location.address == 'Testing URL')

        objects = self.portal.portal_map.search_geo_objects(geo_types=['Event_type'])
        self.assertTrue(len(objects) == 1)
        self.assertTrue(objects[0].geo_location.lat == Decimal('35.3'))
        self.assertTrue(objects[0].geo_location.lon == Decimal('15.0'))
        self.assertTrue(objects[0].geo_location.address == 'Testing event')

        objects = self.portal.portal_map.search_geo_objects(geo_types=['File_type'])
        self.assertTrue(len(objects) == 1)
        self.assertTrue(objects[0].geo_location.lat == Decimal('23.3'))
        self.assertTrue(objects[0].geo_location.lon == Decimal('29.0'))
        self.assertTrue(objects[0].geo_location.address == 'Testing file')

    def test_download_kml(self):
        request = self.portal.REQUEST
        request.form['geo_types'] = 'Event_type'
        kml = self.portal.portal_map.downloadLocationsKml(request)
        from xml.etree import ElementTree
        tree = ElementTree.fromstring(kml.encode('utf-8'))
        placemarks = tree.findall('.//{*}Placemark')
        self.assertEqual(len(placemarks), 1)
        self.assertIn('Testing event', kml)
        self.assertNotIn('Testing news', kml)

    def test_search_sorted_from_catalog(self):
        portal_map = self.portal.portal_map
        by_title = [ob.title for ob in portal_map.search_geo_objects(sort_on='title')]
        self.assertEqual(by_title, sorted(by_title))
        self.assertTrue(len(by_title) >= 2)
        reverse = [ob.title for ob in portal_map.search_geo_objects(
            sort_on='title', sort_order='reverse')]
        self.assertEqual(reverse, sorted(by_title, reverse=True))
        lats = [ob.geo_location.lat for ob in portal_map.search_geo_objects(
            sort_on='geo_latitude')]
        self.assertEqual(lats, sorted(lats))

    def test_duplicate_locations(self):
        folder = self.portal.geo_location_test
        ob_id = folder.addNyGeoPoint(**{
            'id': 'sofia2', 'title': 'Sofia', 'geo_location.lat': '42.7',
            'geo_location.lon': '23.333333', 'geo_location.address': 'Other address',
            'geo_type': ''})
        ob = folder._getOb(ob_id)
        ob.approveThis()
        self.portal.portal_map.recatalogNyObject(ob)
        try:
            portal_map = self.portal.portal_map
            ids = lambda criteria: sorted(ob.getId() for ob in
                                          portal_map.getDuplicateLocations(criteria))
            self.assertEqual(ids(['latlon']), ['sofia', 'sofia2'])
            self.assertEqual(ids(['title', 'latlon']), ['sofia', 'sofia2'])
            self.assertEqual(ids(['address']), [])
            self.assertEqual(ids(['type', 'latlon']), ['sofia', 'sofia2'])
            ob.geo_type = 'Capital'
            self.portal.portal_map.recatalogNyObject(ob)
            self.assertEqual(ids(['type', 'latlon']), [])
            sofia = folder.sofia
            sofia.geo_location = Geo(sofia.geo_location.lat,
                                     sofia.geo_location.lon, 'Other address')
            self.assertEqual(ids(['address']), ['sofia', 'sofia2'])
            self.assertEqual(ids(['address', 'title']), ['sofia', 'sofia2'])
            self.assertEqual(ids(['address', 'type']), [])
        finally:
            folder.manage_delObjects([ob_id])

    def test_xrjs_geo_points(self):
        import json
        request = self.portal.REQUEST
        request.form.update({'geo_types': 'Capital,City', 'lat_min': '40',
                             'lat_max': '50', 'lon_min': '20',
                             'lon_max': '30'})
        data = json.loads(self.portal.portal_map.xrjs_getGeoPoints(request))
        self.assertEqual(sorted(p['id'] for p in data['points']),
                         ['geo_location_test/bucharest',
                          'geo_location_test/contanta'])
        self.assertEqual(set(p['icon_name'] for p in data['points']),
                         {'mk_Capital', 'mk_City'})

    def test_xrjs_geo_points_restricted(self):
        import json
        request = self.portal.REQUEST
        request.form.update({'geo_types': 'Capital,City'})
        self.portal.geo_location_test.bucharest._View_Permission = (
            'Administrator',)
        self.logout()
        data = json.loads(self.portal.portal_map.xrjs_getGeoPoints(request))
        self.assertEqual([p['id'] for p in data['points']],
                         ['geo_location_test/contanta'])

    def add_restricted_folder(self):
        folder = self.portal.geo_location_test
        addNyFolder(folder, 'secret', contributor='contributor', submitted=1)
        secret = folder.secret
        ob_id = secret.addNyGeoPoint(**{
            'id': 'hidden', 'title': 'Hidden', 'geo_type': 'Capital',
            'geo_location.lat': '44.5', 'geo_location.lon': '26.5',
            'geo_location.address': 'Hidden place'})
        secret._getOb(ob_id).approveThis()
        self.portal.portal_map.recatalogNyObject(secret._getOb(ob_id))
        secret.setRestrictions(access='other', roles=['Reviewer'])
        secret.manage_setLocalRoles('user1', ['Reviewer'])

    def visible(self):
        import json
        portal_map = self.portal.portal_map
        request = self.portal.REQUEST
        request.form.clear()
        request.form['geo_types'] = 'Capital'
        listing = [ob.getId() for ob in portal_map.search_geo_objects(
            geo_types=['Capital'])]
        points = [p['id'].split('/')[-1] for p in json.loads(
            portal_map.xrjs_getGeoPoints(request))['points']]
        kml = portal_map.downloadLocationsKml(request)
        rss = portal_map.export_geo_rss(geo_types=['Capital'])
        near = [ob.getId() for ob in portal_map.get_geo_objects(
            '44.5', '26.5', geo_types=['Capital'])]
        return (sorted(listing), sorted(points), 'Hidden place' in kml,
                'Hidden' in rss, near)

    def test_restricted_folder(self):
        self.add_restricted_folder()
        self.logout()
        self.assertEqual(self.visible(),
                         (['bucharest'], ['bucharest'], False, False, []))
        self.login('user2')
        self.assertEqual(self.visible()[0], ['bucharest'])
        self.login('user1')
        self.assertEqual(self.visible(),
                         (['bucharest', 'hidden'], ['bucharest', 'hidden'],
                          True, True, ['hidden']))
        self.logout()
        self.portal.geo_location_test.secret.setRestrictions(access='all')
        self.assertEqual(self.visible()[0], ['bucharest', 'hidden'])

    def test_point_balloon(self):
        portal_map = self.portal.portal_map
        self.assertIn('Bucharest', portal_map.xrjs_getPointBalloon(
            'geo_location_test/bucharest'))
        self.portal.geo_location_test.bucharest._View_Permission = (
            'Administrator',)
        self.logout()
        self.assertIn('RESTRICTED ACCESS', portal_map.xrjs_getPointBalloon(
            'geo_location_test/bucharest'))
        both = portal_map.xrjs_getPointBalloon(
            ['geo_location_test/bucharest', 'geo_location_test/contanta',
             'geo_location_test/missing'])
        self.assertIn('(RESTRICTED ACCESS)', both)
        self.assertIn('Constanta', both)

    def test_geocode(self):
        import json
        from unittest.mock import patch
        from naaya.core import ggeocoding
        request = self.portal.REQUEST
        request.form['address'] = 'Sofia'
        result = {'location': {'lat': 42.7, 'lon': 23.3}}
        with patch('naaya.core.ggeocoding.geocode2', return_value=result):
            self.assertEqual(
                json.loads(self.portal.portal_map.geocode(request)), [result])
        error = ggeocoding.GeocoderServiceError('ZERO_RESULTS')
        with patch('naaya.core.ggeocoding.geocode2', side_effect=error):
            self.assertEqual(json.loads(self.portal.portal_map.geocode(request)),
                             {'error': 'ZERO_RESULTS'})

    def test_export_geo_rss(self):
        from xml.etree import ElementTree
        self.portal.geo_location_test.sofia.title = 'Sofia <&> "center"'
        feed = ElementTree.fromstring(self.portal.portal_map.export_geo_rss())
        atom = '{http://www.w3.org/2005/Atom}'
        titles = [e.find(atom + 'title').text for e in feed.findall(atom + 'entry')]
        self.assertIn('Sofia <&> "center"', titles)
        point = feed.find(atom + 'entry/{http://www.georss.org/georss}point')
        self.assertEqual(len(point.text.split()), 2)
