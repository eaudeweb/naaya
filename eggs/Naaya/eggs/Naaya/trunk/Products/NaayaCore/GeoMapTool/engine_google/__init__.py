import simplejson as json

from App.ImageFile import ImageFile
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.NaayaCore.GeoMapTool.GeoMapTool import register_map_engine


# restricted to eea.europa.eu and eionet.europa.eu, for other domains
# configure your own from Administration, Map Management.
# DEFAULT_API_KEY = 'AIzaSyCV-BfmY6xxmO0V3JAvRbvB30fwKHjaa9s'


class GoogleMapEngine(SimpleItem):
    """
    Google maps plugin for Naaya GeoMapTool
    """

    name = "google"
    title = u"Google maps"

    security = ClassSecurityInfo()

    def __init__(self, id):
        super(GoogleMapEngine, self).__init__()
        self._setId(id)
        # self.api_keys = DEFAULT_API_KEY
        self.base_layer = 'map'
        self.allow_mouse_scroll = True
        self.portal_map_zoom = None

    _html_setup = PageTemplateFile('setup', globals())
    security.declarePrivate('html_setup')

    def html_setup(self, request, global_config):
        js_config = {
            'base_layer': self.base_layer,
            'allow_mouse_scroll': self.allow_mouse_scroll,
            'portal_map_zoom': self.portal_map_zoom,
        }
        js_config.update(global_config)
        options = {
            #  'apikey': pick_api_key(self.api_keys, request),
            'js_config': json.dumps(js_config),
        }
        return self._html_setup(**options)

    _config_html = PageTemplateFile('configure', globals())
    security.declarePrivate('config_html')

    def config_html(self):
        return self._config_html(all_layers=[
            {'name': 'map', 'label': "Streets"},
            {'name': 'hybrid', 'label': "Hybrid"},
            {'name': 'physical', 'label': "Physical"},
            {'name': 'satellite', 'label': "Satellite"}])

    security.declarePrivate('save_config')

    def save_config(self, form_data):
        # self.api_keys = form_data['google_api_keys']
        self.allow_mouse_scroll = form_data.get(
            'google_allow_mouse_scroll', False)
        self.base_layer = form_data['google_base_layer']
        try:
            zoom = int(form_data.get('initial_zoom', None))
        except:
            zoom = None
        self.portal_map_zoom = zoom

    security.declareProtected(view, 'naaya_google_js')
    naaya_google_js = ImageFile('naaya_google.js', globals())


def pick_api_key(key_data, request):
    """Return the API key for the current domain"""
    current_domain = getattr(request, 'other')['SERVER_URL']

    for line in key_data.split('\n'):
        line = line.strip()
        if '::' not in line:
            return line
        else:
            domain, key = line.split('::')
            if domain == current_domain:
                return key
    else:
        return ''


def register():
    register_map_engine(GoogleMapEngine)
