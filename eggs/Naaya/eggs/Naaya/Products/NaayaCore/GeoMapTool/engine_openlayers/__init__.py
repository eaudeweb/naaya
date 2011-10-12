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

class OpenLayersMapEngine(SimpleItem):
    """
    Openlayers maps plugin for Naaya GeoMapTool
    """

    name = "openlayers"
    title = u"OpenLayers maps"
    _initial_address = DEFAULT_ADDRESS
    _initial_bounding_box = DEFAULT_BBOX

    security = ClassSecurityInfo()

    def __init__(self, id):
        super(OpenLayersMapEngine, self).__init__()
        self._setId(id)

    _html_setup = PageTemplateFile('setup', globals())
    security.declarePrivate('html_setup')
    def html_setup(self, request, global_config):
        js_config = {
            'server_url': self.absolute_url(),
            'initial_bounding_box': self._initial_bounding_box,
        }
        js_config.update(global_config)
        options = {
            'js_config': json.dumps(js_config),
        }
        return self._html_setup(**options)

    _config_html = PageTemplateFile('configure', globals())
    security.declarePrivate('config_html')
    def config_html(self):
        return self._config_html()

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

    security.declareProtected(view, 'naaya_openlayers_js')
    naaya_openlayers_js = ImageFile('naaya_openlayers.js', globals())

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

setattr(OpenLayersMapEngine, 'OpenLayers-2.11',
        StaticServeFromFolder('OpenLayers-2.11', globals()))

def register():
    register_map_engine(OpenLayersMapEngine)
