import simplejson as json

from App.ImageFile import ImageFile
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.NaayaCore.GeoMapTool.GeoMapTool import register_map_engine

class YahooMapEngine(SimpleItem):
    """
    Yahoo maps plugin for Naaya GeoMapTool
    """

    name = "yahoo"
    title = u"Yahoo maps"

    security = ClassSecurityInfo()

    def __init__(self, id):
        super(YahooMapEngine, self).__init__()
        self._setId(id)
        self.api_keys = ("m.6kzBLV34FOaYaMCfIKBRHIIYE8zCf6c6"
                         "yxcc5rZCWkCilWFPzAhcyQEcRTgYKy5g--")
        self.base_layer = 'map'

    _html_setup = PageTemplateFile('setup', globals())
    security.declarePrivate('html_setup')
    def html_setup(self, request, global_config):
        js_config = {
            'base_layer': self.base_layer,
        }
        js_config.update(global_config)
        options = {
            'apikey': pick_api_key(self.api_keys, request),
            'js_config': json.dumps(js_config),
        }
        return self._html_setup(**options)

    _config_html = PageTemplateFile('configure', globals())
    security.declarePrivate('config_html')
    def config_html(self):
        return self._config_html(all_layers=[
                {'name': 'map', 'label': "Streets"},
                {'name': 'hybrid', 'label': "Hybrid"},
                {'name': 'satellite', 'label': "Satellite"}])

    security.declarePrivate('save_config')
    def save_config(self, form_data):
        self.base_layer = form_data['yahoo_base_layer']
        self.api_keys = form_data['yahoo_api_keys']

    security.declareProtected(view, 'naaya_yahoo_js')
    naaya_yahoo_js = ImageFile('naaya_yahoo.js', globals())

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
    register_map_engine(YahooMapEngine)
