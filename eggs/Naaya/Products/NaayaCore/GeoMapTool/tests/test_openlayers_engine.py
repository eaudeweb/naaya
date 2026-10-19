import json
from unittest.mock import patch

from naaya.core import ggeocoding

from Products.Naaya.tests.NaayaFunctionalTestCase import (
    NaayaFunctionalTestCase)
from Products.NaayaCore.GeoMapTool.engine_openlayers import (
    OL_FOLDER, OL_VERSION)

ENV = 'Products.NaayaCore.GeoMapTool.engine_openlayers.get_zope_env'


class OpenLayersEngineTest(NaayaFunctionalTestCase):

    def afterSetUp(self):
        self.portal_map = self.portal.portal_map
        self.portal_map.set_map_engine('openlayers')
        self.engine = self.portal_map.get_map_engine()

    def beforeTearDown(self):
        self.portal_map.set_map_engine('google')

    def test_setup_html(self):
        html = self.portal_map.setup_map_engine_html(self.portal.REQUEST)
        engine_url = self.engine.absolute_url()
        self.assertIn('%s/%s/ol.js' % (engine_url, OL_FOLDER), html)
        self.assertIn('%s/%s/ol.css' % (engine_url, OL_FOLDER), html)
        self.assertIn('%s/naaya_openlayers_js' % engine_url, html)
        self.assertIn('naaya_openlayers_map_api_config', html)
        self.assertNotIn('OpenLayers-2.12', html)
        self.assertNotIn('maps.google.com', html)

    def setup_html_for(self, base_layer, key=''):
        self.engine.base_layer = base_layer
        with patch(ENV, return_value=key):
            return self.portal_map.setup_map_engine_html(self.portal.REQUEST)

    def test_setup_html_replaced_base_layer(self):
        # Bing ids and Google ids without a key fall back to OSM or Esri
        self.assertIn('"factory": "osm_layer"', self.setup_html_for('bing_road'))
        self.assertIn('"id": "esri_imagery"', self.setup_html_for('bing_aerial'))
        self.assertIn('"id": "osm"', self.setup_html_for('google_streets'))
        html = self.setup_html_for('google_hybrid')
        self.assertIn('"id": "esri_imagery"', html)
        self.assertNotIn('google_key', html)

    def test_setup_html_address(self):
        html = self.portal_map.setup_map_engine_html(self.portal.REQUEST,
                                                     initial_address='Brasov')
        self.assertIn('"initial_address": "Brasov"', html)
        self.assertIn('"saved_address": "Europe"', html)

    def test_setup_html_google_layer(self):
        html = self.setup_html_for('google_hybrid', key='KEY123')
        self.assertIn('"id": "google_hybrid"', html)
        self.assertIn('"google_key": "KEY123"', html)

    def test_config_html_google_layers(self):
        with patch(ENV, return_value=''):
            self.assertNotIn('google_satellite', self.engine.config_html())
        with patch(ENV, return_value='KEY123'):
            self.assertIn('google_satellite', self.engine.config_html())

    def test_config_html(self):
        html = self.engine.config_html()
        self.assertIn('name="openlayers_mouse_wheel_zoom:boolean"', html)
        self.assertIn('<option value="osm" selected="selected"', html)

    def test_static_files(self):
        base = 'http://localhost/portal/portal_map/%s' % self.engine.getId()
        self.browser.go('%s/%s/ol.css' % (base, OL_FOLDER))
        self.assertEqual(self.browser.get_code(), 200)
        self.assertIn('.ol-viewport', self.browser.get_html())
        self.browser.go('%s/marker_png' % base)
        self.assertEqual(self.browser.get_code(), 200)
        self.assertEqual(OL_FOLDER, 'ol-' + OL_VERSION)

    def test_geocode_nominatim(self):
        result = {'location': {'lat': 50.8, 'lon': 4.3},
                  'boundingbox': {'top': 51, 'bottom': 50, 'left': 4, 'right': 5}}
        request = self.portal.REQUEST
        request.form['address'] = 'Bruxelles'
        with patch('naaya.core.ggeocoding.geocode2', return_value=result):
            data = json.loads(self.engine.geocode_nominatim(request))
        self.assertEqual(data, [{'lat': 50.8, 'lon': 4.3,
                                 'boundingbox': [50, 51, 4, 5]}])
        with patch('naaya.core.ggeocoding.geocode2',
                   side_effect=ggeocoding.GeocoderServiceError('x')):
            self.assertEqual(json.loads(self.engine.geocode_nominatim(request)), [])
