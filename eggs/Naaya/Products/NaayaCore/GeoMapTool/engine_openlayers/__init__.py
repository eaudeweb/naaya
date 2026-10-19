import urllib.parse
import urllib.request
import urllib.error
import json
import logging

from naaya.core.backport import all

from App.ImageFile import ImageFile
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.NaayaCore.GeoMapTool.GeoMapTool import register_map_engine
from naaya.core.StaticServe import StaticServeFromFolder
from naaya.core import ggeocoding
from naaya.core.zope2util import get_zope_env

log = logging.getLogger(__name__)


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search?"
NOMINATIM_USER_AGENT = "Naaya OpenLayers map engine"
DEFAULT_ADDRESS = 'Europe'
DEFAULT_BBOX = [36, 62, -10, 40] # bottom, top, left, right


# Vendored from the npm package ol@10.11.0 (dist/ol.js, ol.css).
OL_VERSION = '10.11.0'
OL_FOLDER = 'ol-' + OL_VERSION

GOOGLE_KEY_ENV = 'GOOGLE_MAPS_API_KEY'

# Google layers need GOOGLE_MAPS_API_KEY with the Map Tiles API enabled
BASE_LAYERS = [

    {'id': 'osm',
     'label': "OpenStreetMap",
     'factory': 'osm_layer'},

    {'id': 'esri_imagery',
     'label': "Esri World Imagery (satellite)",
     'factory': 'esri_imagery_layer'},

    {'id': 'google_streets',
     'label': "Google Streets",
     'factory': 'google_layer',
     'google_map_type': 'roadmap',
     'fallback': 'osm'},

    {'id': 'google_satellite',
     'label': "Google Satellite",
     'factory': 'google_layer',
     'google_map_type': 'satellite',
     'fallback': 'esri_imagery'},

    {'id': 'google_hybrid',
     'label': "Google Hybrid",
     'factory': 'google_layer',
     'google_map_type': 'satellite',
     'google_layer_types': ['layerRoadmap'],
     'fallback': 'esri_imagery'},

    {'id': 'google_terrain',
     'label': "Google Terrain",
     'factory': 'google_layer',
     'google_map_type': 'terrain',
     'google_layer_types': ['layerRoadmap'],
     'fallback': 'osm'},

]
DEFAULT_BASE_LAYER = 'osm'
# Ids saved by removed engines or layers
REPLACED_LAYERS = {'bing_road': 'osm', 'bing_aerial': 'esri_imagery',
                   'bing_aerial_with_labels': 'esri_imagery'}


def google_key():
    return get_zope_env(GOOGLE_KEY_ENV) or ''


def available_base_layers():
    has_key = bool(google_key())
    return [layer for layer in BASE_LAYERS
            if has_key or layer['factory'] != 'google_layer']


def get_base_layer(layer_id):
    """ Base layer info for `layer_id`, or its replacement if unavailable """
    layer_id = REPLACED_LAYERS.get(layer_id, layer_id)
    by_id = dict((layer['id'], layer) for layer in BASE_LAYERS)
    available = [layer['id'] for layer in available_base_layers()]
    while layer_id in by_id and layer_id not in available:
        layer_id = by_id[layer_id].get('fallback')
    return by_id.get(layer_id, BASE_LAYERS[0])


class OpenLayersMapEngine(SimpleItem):
    """
    Openlayers maps plugin for Naaya GeoMapTool
    """

    name = "openlayers"
    title = u"OpenLayers maps"
    _initial_address = DEFAULT_ADDRESS
    _initial_bounding_box = DEFAULT_BBOX
    mouse_wheel_zoom = True
    base_layer = DEFAULT_BASE_LAYER

    security = ClassSecurityInfo()

    def __init__(self, id):
        super(OpenLayersMapEngine, self).__init__()
        self._setId(id)

    _html_setup = PageTemplateFile('setup', globals())
    security.declarePrivate('html_setup')
    def html_setup(self, request, global_config):
        base_layer = get_base_layer(self.base_layer)
        js_config = {
            'server_url': self.absolute_url(),
            'initial_bounding_box': self._initial_bounding_box,
            'mouse_wheel_zoom': self.mouse_wheel_zoom,
            'base_layer': base_layer,
            'saved_address': self._initial_address,
        }
        js_config.update(global_config)
        js_config['base_layer'] = base_layer    # this is more then a string
        if base_layer['factory'] == 'google_layer':
            js_config['google_key'] = google_key()
        options = {
            'js_config': json.dumps(js_config),
            'ol_url': '%s/%s' % (self.absolute_url(), OL_FOLDER),
        }
        return self._html_setup(**options)

    _config_html = PageTemplateFile('configure', globals())
    security.declarePrivate('config_html')
    def config_html(self):
        return self._config_html(base_layers=available_base_layers(),
                                 current_base_layer=get_base_layer(
                                     self.base_layer)['id'])

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
        self.base_layer = get_base_layer(form_data.get('base_layer'))['id']

    security.declareProtected(view, 'naaya_openlayers_js')
    naaya_openlayers_js = ImageFile('naaya_openlayers.js', globals())

    security.declareProtected(view, 'naaya_openlayers_css')
    naaya_openlayers_css = ImageFile('naaya_openlayers.css', globals())

    security.declareProtected(view, 'marker_png')
    marker_png = ImageFile('marker.png', globals())

    def _geocode_nominatim_request(self, address):
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', NOMINATIM_USER_AGENT)]

        query = {'q': address, 'format': 'json'}

        f = opener.open(NOMINATIM_URL + urllib.parse.urlencode(query))

        try:
            return f.read()

        finally:
            f.close()

    security.declareProtected(view, 'geocode_nominatim')
    def geocode_nominatim(self, REQUEST):
        """ geocode an address; a Nominatim style list with one or no result """
        # naaya.core.ggeocoding caches the results and keeps to 1 request/s
        try:
            result = ggeocoding.geocode2(REQUEST.form['address'])
        except ggeocoding.GeocoderServiceError as e:
            log.info("Geocoding %r failed: %s", REQUEST.form['address'], e)
            data = []
        else:
            bb = result['boundingbox']
            data = [{'lat': result['location']['lat'],
                     'lon': result['location']['lon'],
                     'boundingbox': [bb['bottom'], bb['top'],
                                     bb['left'], bb['right']]}]
        REQUEST.RESPONSE.setHeader('Content-type', 'application/json')
        return json.dumps(data)

setattr(OpenLayersMapEngine, OL_FOLDER,
        StaticServeFromFolder(OL_FOLDER, globals()))

def register():
    register_map_engine(OpenLayersMapEngine)
