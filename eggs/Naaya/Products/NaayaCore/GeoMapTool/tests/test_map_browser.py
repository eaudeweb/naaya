"""The portal map in Chromium: points and clusters, cluster zoom, address search."""
from unittest import mock

from Products.Naaya.NyFolder import addNyFolder
from Products.Naaya.tests.BrowserTestCase import BrowserTestCase
from naaya.content.geopoint.geopoint_item import addNyGeoPoint

BRASOV = {'location': {'lat': 45.65, 'lon': 25.6},
          'boundingbox': {'top': 45.7, 'bottom': 45.6, 'left': 25.5, 'right': 25.7}}


class MapBrowserTest(BrowserTestCase):

    def afterSetUp(self):
        portal_map = self.portal.portal_map
        portal_map.set_map_engine('openlayers')
        portal_map.addSymbol('hotel', 'Hotel', '', '', '#ff0000', None, '')
        self.portal.manage_install_pluggableitem('Naaya GeoPoint')
        addNyFolder(self.portal, 'mapfolder', contributor='admin', submitted=1)
        # 12 points around Bucharest make a cluster on the world map
        for i in range(12):
            ob_id = addNyGeoPoint(self.portal.mapfolder, title='Point %d' % i,
                                  geo_type='hotel', contributor='admin',
                                  **{'geo_location.lat': str(44.4 + i * 0.001),
                                     'geo_location.lon': str(26.1 + i * 0.001)})
            ob = self.portal.mapfolder[ob_id]
            ob.approveThis()
            self.portal.recatalogNyObject(ob)
        self.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['mapfolder'])
        self.portal.portal_map.deleteSymbol(['hotel'])
        self.portal.portal_map.set_map_engine('google')
        self.commit()

    def open_map(self, query='', points=True):
        self.page.goto(self.url('portal_map/') + query)
        if points:
            self.page.wait_for_function('window.map_engine && map_engine.get_current_places().length')
        else:
            self.page.wait_for_function('window.map_engine')

    def test_cluster_click_zooms_in(self):
        self.open_map()
        zoom = self.page.evaluate('map_engine.view.getZoom()')
        # page position of the first cluster, once the map has drawn it
        handle = self.page.wait_for_function("""() => {
            var c = map_engine.get_current_places().filter(p => p.id === '')[0];
            if (!c) return null;
            var px = map_engine.olmap.getPixelFromCoordinate(map_engine.from_wgs84(c));
            var hit = map_engine.olmap.forEachFeatureAtPixel(px, f => f.get('naaya_marker'));
            if (!hit) return null;
            var r = map_engine.olmap.getTargetElement().getBoundingClientRect();
            return [px[0] + r.left, px[1] + r.top]; }""")
        self.page.mouse.click(*handle.json_value())
        self.page.wait_for_function('map_engine.view.getZoom() > %s' % zoom)
        self.assertEqual(self.js_errors, [])

    def test_address_search(self):
        with mock.patch('naaya.core.ggeocoding.geocode2', return_value=BRASOV):
            self.open_map()
            self.page.wait_for_function("!document.getElementById('address_button').disabled")
            self.page.fill('#address', 'Brasov')
            self.page.click('#address_button')
            self.page.wait_for_function(
                'Math.abs(map_engine.get_center_and_zoom().lat_center - 45.65) < 0.1')
        self.assertEqual(self.js_errors, [])

    def test_address_parameter(self):
        # embed_map_html centers the map on ?address= (portal_map index does not)
        with mock.patch('naaya.core.ggeocoding.geocode2', return_value=BRASOV):
            # no points near Brasov
            self.open_map('embed_map_html?address=Brasov', points=False)
            self.page.wait_for_function(
                'Math.abs(map_engine.get_center_and_zoom().lat_center - 45.65) < 0.1')
        self.assertEqual(self.js_errors, [])
