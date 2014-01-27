import urllib
import urllib2
import simplejson as json
import logging

from naaya.core.backport import all

from App.ImageFile import ImageFile
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.NaayaCore.GeoMapTool.GeoMapTool import register_map_engine
from naaya.core.StaticServe import StaticServeFromFolder

log = logging.getLogger(__name__)


NOMINATIM_URL = "http://nominatim.openstreetmap.org/search?"
NOMINATIM_USER_AGENT = "Naaya OpenLayers map engine"
DEFAULT_ADDRESS = 'Europe'
DEFAULT_BBOX = [36, 62, -10, 40] # bottom, top, left, right


BASE_LAYERS = [

    {'id': 'osm',
     'label': "OpenStreetMap",
     'factory': 'NaayaOpenLayers.osm_layer'},

    {'id': 'google_streets',
     'label': "Google Streets",
     'factory': 'NaayaOpenLayers.google_layer',
     'google_map_type': 'roadmap',
     'google_api': True},

    {'id': 'google_satellite',
     'label': "Google Satellite",
     'factory': 'NaayaOpenLayers.google_layer',
     'google_map_type': 'satellite',
     'google_api': True},

    {'id': 'google_hybrid',
     'label': "Google Hybrid",
     'factory': 'NaayaOpenLayers.google_layer',
     'google_map_type': 'hybrid',
     'google_api': True},

    {'id': 'google_terrain',
     'label': "Google Terrain",
     'factory': 'NaayaOpenLayers.google_layer',
     'google_map_type': 'terrain',
     'google_api': True},

    {'id': 'bing_road',
     'label': "Bing Road",
     'bing_map_type': 'Road',
     'factory': 'NaayaOpenLayers.bing_layer'},

    {'id': 'bing_aerial',
     'label': "Bing Aerial",
     'bing_map_type': 'Aerial',
     'factory': 'NaayaOpenLayers.bing_layer'},

    {'id': 'bing_aerial_with_labels',
     'label': "Bing Aerial with labels",
     'bing_map_type': 'AerialWithLabels',
     'factory': 'NaayaOpenLayers.bing_layer'},

]


class OpenLayersMapEngine(SimpleItem):
    """
    Openlayers maps plugin for Naaya GeoMapTool
    """

    name = "openlayers"
    title = u"OpenLayers maps"
    _initial_address = DEFAULT_ADDRESS
    _initial_bounding_box = DEFAULT_BBOX
    mouse_wheel_zoom = True;
    base_layer = 'google_hybrid';

    security = ClassSecurityInfo()

    def __init__(self, id):
        super(OpenLayersMapEngine, self).__init__()
        self._setId(id)

    _html_setup = PageTemplateFile('setup', globals())
    security.declarePrivate('html_setup')
    def html_setup(self, request, global_config):
        [base_layer] = [layer for layer in BASE_LAYERS
                        if layer['id'] == self.base_layer]
        js_config = {
            'server_url': self.absolute_url(),
            'initial_bounding_box': self._initial_bounding_box,
            'mouse_wheel_zoom': self.mouse_wheel_zoom,
            'base_layer': base_layer,
        }
        js_config.update(global_config)
        js_config['base_layer'] = base_layer    # this is more then a string
        options = {
            'js_config': json.dumps(js_config),
            'base_layer': base_layer,
        }
        return self._html_setup(**options)

    _config_html = PageTemplateFile('configure', globals())
    security.declarePrivate('config_html')
    def config_html(self):
        return self._config_html(base_layers=BASE_LAYERS)

    security.declarePrivate('save_config')
    def save_config(self, form_data):
        initial_address = form_data.get('initial_address', DEFAULT_ADDRESS)
        initial_address = initial_address.strip()

        if self._initial_address != initial_address:
            bounding_box = DEFAULT_BBOX

            if (initial_address and
                initial_address.lower() != DEFAULT_ADDRESS.lower()):

                response = self._geocode_nominatim_request(initial_address)
                for result in json.loads(response):
                    if (result['class'] == "place" and
                        result['type'] == "country"):
                        # this is a hand-placed country marker; skip it
                        continue

                    bounding_box = [float(v) for v in result['boundingbox']]
                    break

                else:
                    log.warn("Could not determine bounding box for "
                             "initial address %r", initial_address)

            self._initial_address = initial_address
            self._initial_bounding_box = bounding_box

        self.mouse_wheel_zoom = form_data.get('openlayers_mouse_wheel_zoom', False)
        self.base_layer = form_data['base_layer']

    security.declareProtected(view, 'naaya_openlayers_js')
    naaya_openlayers_js = ImageFile('naaya_openlayers.js', globals())

    security.declareProtected(view, 'naaya_openlayers_css')
    naaya_openlayers_css = ImageFile('naaya_openlayers.css', globals())

    def _geocode_nominatim_request(self, address):
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', NOMINATIM_USER_AGENT)]

        query = {'q': address, 'format': 'json'}

        f = opener.open(NOMINATIM_URL + urllib.urlencode(query.items()))

        try:
            return f.read()

        finally:
            f.close()

    security.declareProtected(view, 'geocode_nominatim')
    def geocode_nominatim(self, REQUEST):
        """ perform geocoding using OSM Nominatim """

        address = REQUEST.form['address']

        data = self._geocode_nominatim_request(address)

        REQUEST.RESPONSE.setHeader('Content-type', 'application/json')
        return data

setattr(OpenLayersMapEngine, 'OpenLayers-2.12',
        StaticServeFromFolder('OpenLayers-2.12', globals()))

def register():
    register_map_engine(OpenLayersMapEngine)
