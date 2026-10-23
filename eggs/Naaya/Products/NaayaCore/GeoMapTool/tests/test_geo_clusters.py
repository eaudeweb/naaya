from unittest import TestSuite, TestLoader
import random

from Products.Naaya.tests import NaayaTestCase
from Products.Naaya.tests import NaayaFunctionalTestCase

from Products.Naaya.NyFolder import addNyFolder
from Products.NaayaCore.GeoMapTool.clusters import get_discretized_limits
from .test_kml_parser import load_file

class RequestStub(object):
    # simulates HTTP Request with filled form-data
    form = {'lon_min': '24.62327117919922', 'lat_max': '44.43549691351629',
    'address': u'', 'geo_types': [],
    'lon_max': '26.16495895403205', 'geo_query': [u'', ''],
    'path': '', 'lat_min': '43.07123237879009'}

class GeoClustersTestCase(NaayaFunctionalTestCase.NaayaFunctionalTestCase):
    symbol_ids = ['symbol1', 'symbol2']
    howmany = 100
    ob_dicts = []
    cluster_count=20
    cluster_pos = (44.43549691351628, 26.16495895403204)

    def afterSetUp(self):
        self.portal.manage_install_pluggableitem('Naaya GeoPoint')
        self.portal.setDefaultSearchableContent()

        picture_data = load_file('data/symbol.png')

        for id in self.symbol_ids:
            self.portal.portal_map.addSymbol(id, id, '', '', None, picture_data, '')

        addNyFolder(self.portal, 'geo_clusters_test', contributor='contributor',
                submited=1)

    def beforeTearDown(self):
        ids = [ob_dict['id'] for ob_dict in self.ob_dicts]
        if ids:
            self.portal.geo_clusters_test.manage_delObjects(ids)

        self.portal.manage_delObjects(['geo_clusters_test'])

        for id in self.symbol_ids:
            self.portal.portal_map.deleteSymbol(id)

        self.portal.manage_uninstall_pluggableitem('Naaya GeoPoint')
        self.portal.setDefaultSearchableContent()

    def add_points(self, prefix, count, lat, lon, geo_type, approve=True,
                   step=0.00001):
        folder = self.portal.geo_clusters_test
        for i in range(count):
            ob_dict = {'id': '%s_%s' % (prefix, i), 'title': prefix,
                       'geo_location.lat': str(lat + i * step),
                       'geo_location.lon': str(lon + i * step),
                       'geo_type': geo_type}
            ob_dict['id'] = folder.addNyGeoPoint(**ob_dict)
            self.ob_dicts.append(ob_dict)
            ob = folder._getOb(ob_dict['id'])
            if approve:
                ob.approveThis()
            else:
                ob.approveThis(0)
            self.portal.portal_map.catalogNyObject(ob)
        schemas = self.portal.portal_schemas.objectValues()
        self.portal.portal_map.admin_set_contenttypes(
            [schema.id for schema in schemas])

    def found_ids(self, **criteria):
        cluster_obs, single_obs = self.portal.portal_map.search_geo_clusters(
            **criteria)
        ids = [path.split('/')[-1] for c, paths, b in cluster_obs
               for path in paths]
        return sorted(ids + [ob.getId() for ob in single_obs])

    def test_clusters_exclude_filtered_points(self):
        self.ob_dicts = []
        self.add_points('in', 12, 44.0, 25.0, 'symbol1')
        self.add_points('few', 3, 43.5, 24.5, 'symbol1')
        self.add_points('type', 12, 44.0, 25.0, 'symbol2')
        self.add_points('out', 12, 10.0, 10.0, 'symbol1')
        self.add_points('draft', 12, 44.0, 25.0, 'symbol1', approve=False)
        frame = dict(lat_min=43.0, lat_max=45.0, lon_min=24.0, lon_max=26.0)

        expected = sorted(['in_%d' % i for i in range(12)] +
                          ['few_%d' % i for i in range(3)])
        self.assertEqual(self.found_ids(geo_types=['symbol1'], **frame),
                         expected)
        self.assertEqual(
            self.found_ids(geo_types=['symbol1', 'symbol2'], **frame),
            sorted(expected + ['type_%d' % i for i in range(12)]))

    def test_xrjs_clusters_point_ids(self):
        import json
        self.ob_dicts = []
        self.add_points('same', 12, 44.0, 25.0, 'symbol1', step=0)
        self.add_points('spread', 12, 44.6, 25.6, 'symbol1', step=0.001)
        request = self.portal.REQUEST
        request.form.update({'lat_min': '43', 'lat_max': '45',
                             'lon_min': '24', 'lon_max': '26',
                             'geo_types': 'symbol1'})
        data = json.loads(self.portal.portal_map.xrjs_getGeoClusters(request))
        clusters = dict((len(p['point_ids']), p) for p in data['points'])
        self.assertEqual(sorted(clusters), [0, 12])
        same = clusters[12]
        self.assertEqual(sorted(path.split('/')[-1] for path in
                                same['point_ids']),
                         sorted('same_%d' % i for i in range(12)))
        spread = clusters[0]
        self.assertEqual(spread['num_records'], 12)
        lat_min, lat_max, lon_min, lon_max = spread['bounds']
        self.assertAlmostEqual(lat_max - lat_min, 0.011)

    def test_clusters_restricted_folder(self):
        import json
        self.ob_dicts = []
        self.add_points('open', 12, 44.0, 25.0, 'symbol1', step=0)
        self.add_points('few', 2, 43.5, 24.5, 'symbol1')
        folder = self.portal.geo_clusters_test
        addNyFolder(folder, 'secret', contributor='contributor', submitted=1)
        secret = folder.secret
        for i in range(12):
            ob_id = secret.addNyGeoPoint(**{
                'id': 'hidden_%d' % i, 'title': 'hidden',
                'geo_location.lat': '44.0', 'geo_location.lon': '25.0',
                'geo_type': 'symbol1'})
            secret._getOb(ob_id).approveThis()
            self.portal.portal_map.catalogNyObject(secret._getOb(ob_id))
        ob_id = secret.addNyGeoPoint(**{
            'id': 'lonely', 'title': 'lonely', 'geo_type': 'symbol1',
            'geo_location.lat': '43.6', 'geo_location.lon': '24.6'})
        secret._getOb(ob_id).approveThis()
        self.portal.portal_map.catalogNyObject(secret._getOb(ob_id))
        secret.setRestrictions(access='other', roles=['Reviewer'])
        secret.manage_setLocalRoles('user1', ['Reviewer'])
        request = self.portal.REQUEST
        request.form.update({'lat_min': '43', 'lat_max': '45',
                             'lon_min': '24', 'lon_max': '26',
                             'geo_types': 'symbol1'})

        def clusters():
            data = json.loads(
                self.portal.portal_map.xrjs_getGeoClusters(request))
            counts = sorted(p.get('num_records', 1) for p in data['points'])
            ids = sorted(path.split('/')[-1] for p in data['points']
                         for path in p.get('point_ids') or [p['id']])
            return counts, ids

        open_ids = ['few_0', 'few_1'] + ['open_%d' % i for i in range(12)]
        self.logout()
        self.assertEqual(clusters(), ([1, 1, 12], sorted(open_ids)))
        self.assertEqual(self.found_ids(lat_min=43.0, lat_max=45.0,
                                        lon_min=24.0, lon_max=26.0),
                         sorted(open_ids))
        self.login('user1')
        hidden = ['hidden_%d' % i for i in range(12)] + ['lonely']
        self.assertEqual(clusters(),
                         ([1, 1, 1, 24], sorted(open_ids + hidden)))
        self.logout()
        folder.manage_delObjects(['secret'])

    def test_clusters_close_to_map_bounds(self):
        # scene setup
        folder = self.portal.geo_clusters_test
        self.ob_dicts=[]
        for i in range(self.cluster_count):
            ob_dict=dict()
            ob_dict['id'] = 'id2_%s' % i
            ob_dict['title'] = 'Title for point in cluster %s' % i
            ob_dict['description'] = 'Description for point in cluster %s' % i
            # add radial points to the chosen cluster center in self.cluster_pos
            ob_dict['geo_location.lat'] = str(self.cluster_pos[0] + ((-1)**(i%2)) * (i*0.00001))
            ob_dict['geo_location.lon'] = str(self.cluster_pos[1] + ((-1)**(i%2)) * (i*0.00001))
            ob_dict['geo_location.address'] = 'Address for point in cluster %s' % i
            ob_dict['latitude'] = ob_dict['geo_location.lat']
            ob_dict['longitude'] = ob_dict['geo_location.lon']
            ob_dict['geo_type'] = self.symbol_ids[0]
            ob_dict['URL'] = 'URL for point in cluster %s' % i
            ob_dict['id'] = folder.addNyGeoPoint(**ob_dict)
            self.ob_dicts.append(ob_dict)
            ob = folder._getOb(ob_dict['id'])
            ob.approveThis()
            self.portal.portal_map.catalogNyObject(ob)
        schemas = self.portal.portal_schemas.objectValues()
        self.portal.portal_map.admin_set_contenttypes([schema.id for schema in schemas])

        r = RequestStub()
        r.form['geo_types'].extend(self.symbol_ids)
        # perform search with frame border slicing cluster in half
        # expecting to get one cluster containing all 20 points
        cluster_obs, single_obs = self.portal.portal_map.search_geo_clusters(REQUEST=r)
        # some random points may fall into our cluster
        # greaterequal is best to evaluate for assertion
        self.assertTrue(len(cluster_obs[0][1])>=self.cluster_count)
        # bounds: lat_min, lat_max, lon_min, lon_max of the cluster points
        lat_min, lat_max, lon_min, lon_max = cluster_obs[0][2]
        self.assertTrue(lat_min <= self.cluster_pos[0] <= lat_max)
        self.assertTrue(lon_min <= self.cluster_pos[1] <= lon_max)
        self.assertTrue(lat_max - lat_min < 0.01)


    def test_margin(self):
        assert (get_discretized_limits(-90., 90., -180., 180., 10)
                == get_discretized_limits(-89., 89., -179., 179., 10))
