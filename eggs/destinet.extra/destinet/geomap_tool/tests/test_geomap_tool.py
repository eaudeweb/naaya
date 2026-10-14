from unittest import mock

import transaction
from AccessControl.unauthorized import Unauthorized
from lxml import etree
from Products.NaayaCore.GeoMapTool.GeoMapTool import GeoMapTool
from Products.NaayaCore.GeoMapTool.tests.test_kml_parser import load_file
from Products.NaayaCore.SchemaTool.widgets.geo import Geo
from naaya.content.contact.contact_item import addNyContact

from destinet.geomap_tool.geomap_tool import get_map_results
from destinet.testing.DestinetTestCase import DestinetFunctionalTestCase

NS = {'atom': 'http://www.w3.org/2005/Atom',
      'georss': 'http://www.georss.org/georss',
      'ext': 'http://destinet.eu/extData'}


class GeoMapToolTest(DestinetFunctionalTestCase):

    def setUp(self):
        super(GeoMapToolTest, self).setUp()
        self.map_tool = self.portal.portal_map
        picture = load_file('data/symbol.png')
        self.map_tool.addSymbol('hotel', 'Hotel', '', '', None, picture, '')
        self.map_tool.admin_set_contenttypes(['NyContact'])
        self.add_manager()
        folder = self.portal['market-place']
        addNyContact(folder, id='c1', title='Green Hotel',
                     description='A nice place',
                     geo_location=Geo('45.5', '25.5', 'Brasov, Romania'),
                     geo_type='hotel', webpage='http://hotel.example.com',
                     coverage='Romania', keywords='eco, green',
                     **{'category-organization': 'hotel',
                        'category-marketplace': 'hotel'})
        addNyContact(folder, id='c2', title='Second',
                     geo_location=Geo('10', '10', 'Elsewhere'),
                     geo_type='hotel',
                     **{'category-organization': 'hotel'})
        transaction.commit()

    def go(self, path):
        self.browser.go('http://localhost/demo-design/' + path)
        return self.browser.result.text

    def assert_login_redirect(self):
        self.assertIn('/login_html', self.browser.get_url())

    def parse_feed(self, text):
        feed = etree.fromstring(text.encode('utf-8'))
        return {e.findtext('atom:title', namespaces=NS): e
                for e in feed.findall('atom:entry', NS)}

    def check_feed(self, text):
        entries = self.parse_feed(text)
        self.assertEqual(sorted(entries), ['Green Hotel', 'Second'])
        entry = entries['Green Hotel']

        def field(name):
            return entry.findtext(name, namespaces=NS)
        self.assertEqual(field('atom:id'), 'demo-design/market-place/c1')
        self.assertEqual(entry.find('atom:link', NS).get('href'),
                         'http://localhost/demo-design/market-place/c1')
        self.assertEqual(field('georss:point'), '45.5 25.5')
        self.assertEqual(field('georss:featuretypetag'), 'Hotel')
        self.assertEqual(field('ext:url'), 'http://hotel.example.com')
        self.assertEqual(field('ext:certificate'), 'eco, green')
        self.assertEqual(field('ext:type'), 'Hotel')
        self.assertEqual(field('ext:lat'), '45.5')
        self.assertEqual(field('ext:lng'), '25.5')
        summary = field('atom:summary')
        self.assertIn('A nice place', summary)
        self.assertIn('<b>Address</b>: Brasov, Romania', summary)
        self.assertIn('http://hotel.example.com', summary)
        self.assertEqual(entries['Second'].findtext('ext:type',
                                                    namespaces=NS), '')

    def test_patched_on_geomap_tool(self):
        self.assertTrue(hasattr(GeoMapTool, 'export_geo_rss_dzt'))
        self.assertEqual(GeoMapTool.list_locations.__module__,
                         'destinet.geomap_tool.geomap_tool')

    def test_export_feed_direct_call(self):
        out = self.map_tool.export_geo_rss_dzt(geo_types=['hotel'])
        self.assertIsInstance(out, str)
        self.check_feed(out)

    def test_export_feed_anonymous_on_portal_map(self):
        text = self.go('portal_map/export_geo_rss_dzt?geo_types=hotel')
        self.assertEqual(self.browser.get_code(), 200)
        self.assertEqual(self.browser_get_header('content-type'),
                         'application/atom+xml')
        self.assertEqual(self.browser_get_header('content-disposition'),
                         'attachment;filename=locations.xml')
        self.check_feed(text)

    def test_export_feed_view_requires_login(self):
        self.go('export_geo_rss?geo_types=hotel')
        self.assert_login_redirect()

    def test_export_feed_view_as_manager(self):
        self.browser_basic_auth()
        self.check_feed(self.go('export_geo_rss?geo_types=hotel'))

    def test_export_feed_filters_by_bounding_box(self):
        out = self.map_tool.export_geo_rss_dzt(
            geo_types='hotel', lat_min='40', lat_max='50', lon_min='20',
            lon_max='30')
        self.assertEqual(list(self.parse_feed(out)), ['Green Hotel'])

    def test_export_feed_rejects_bots(self):
        self.assertRaises(Unauthorized, self.map_tool.export_geo_rss_dzt)
        self.assertRaises(Unauthorized, self.map_tool.export_geo_rss_dzt,
                          geo_types='hotel', first_letter='ab')
        self.browser_basic_auth()
        self.go('portal_map/export_geo_rss_dzt')
        self.assertEqual(self.browser.get_code(), 401)

    def test_list_locations_anonymous_on_portal_map(self):
        text = self.go('portal_map/list_locations?geo_types=hotel')
        self.assertEqual(self.browser.get_code(), 200)
        self.assertIn('<strong>2</strong>', text)
        self.assertIn('>Green Hotel</a>', text)
        self.assertIn('>Second</a>', text)
        self.assertIn('<td>Romania</td>', text)

    def test_list_locations_view_requires_login(self):
        self.go('list_locations?geo_types=hotel')
        self.assert_login_redirect()
        self.browser_basic_auth()
        text = self.go('list_locations?geo_types=hotel')
        self.assertIn('>Green Hotel</a>', text)

    def test_list_locations_paging_and_sorting(self):
        text = self.go('portal_map/list_locations?geo_types=hotel'
                       '&sortable=1&sort_on=title&sort_order=reverse'
                       '&step=1&start=0&end=1')
        self.assertIn('>Second</a>', text)
        self.assertNotIn('>Green Hotel</a>', text)
        text = self.go('portal_map/list_locations?geo_types=hotel'
                       '&sortable=1&sort_on=title&step=1&start=1&end=2')
        self.assertIn('>Second</a>', text)
        self.assertNotIn('>Green Hotel</a>', text)

    def test_list_locations_rejects_bots(self):
        self.go('portal_map/list_locations')
        self.assert_login_redirect()

    def test_list_locations_keyword_arguments(self):
        with mock.patch.object(GeoMapTool, '_list_locations',
                               new=lambda self, **kw: kw, create=True):
            options = self.map_tool.list_locations(geo_types=['hotel'],
                                                   all_records='1')
        self.assertEqual(options['results'], 2)
        self.assertEqual(options['end'], 2)
        self.assertEqual(len(options['records']), 2)

    def test_get_map_results_options(self):
        options = {}
        results = get_map_results(
            self.map_tool, None, options, geo_types='hotel,other',
            lat_min='bad', lat_max='50', lon_min='20', lon_max='30',
            administrative_level='', landscape_type='', topics='',
            certificate_services='a,b', step='bad', start='x', end='y')
        self.assertEqual([ob.getId() for ob in results], ['c1'])
        self.assertEqual(options['geo_types'], ['hotel', 'other'])
        self.assertEqual(options['lat_min'], '')
        self.assertEqual(options['lat_max'], '50')
        self.assertEqual(options['certificate_services'], ['a', 'b'])
        self.assertEqual(options['administrative_level'], [])
        self.assertEqual(options['landscape_type'], [])
        self.assertEqual(options['topics'], [])
        self.assertEqual(options['step'], 50)
        self.assertEqual(options['start'], 0)
        self.assertEqual(options['end'], 50)
        self.assertEqual(options['results'], 1)
        self.assertEqual(options['prev_start'], -50)
        self.assertEqual(options['next_end'], 100)
        self.assertEqual([ob.getId() for ob in options['records']], ['c1'])
        self.assertEqual(options['sort_on'], '')

    def test_get_map_results_without_geo_types(self):
        options = {}
        self.assertIsNone(get_map_results(self.map_tool, None, options))
        self.assertEqual(options, {})
