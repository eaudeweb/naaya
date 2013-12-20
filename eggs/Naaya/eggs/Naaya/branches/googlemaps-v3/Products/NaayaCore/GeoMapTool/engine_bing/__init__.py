import simplejson as json

from App.ImageFile import ImageFile
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.NaayaCore.GeoMapTool.GeoMapTool import register_map_engine

class BingMapEngine(SimpleItem):
    """
    Bing maps plugin for Naaya GeoMapTool
    """

    name = "bing"
    title = u"Bing maps"

    security = ClassSecurityInfo()

    # default values
    base_layer = 'Road'

    def __init__(self, id):
        super(BingMapEngine, self).__init__()
        self._setId(id)

    _html_setup = PageTemplateFile('setup', globals())
    security.declarePrivate('html_setup')
    def html_setup(self, request, global_config):
        js_config = {
            'base_layer': self.base_layer,
        }
        js_config.update(global_config)
        options = {
            'js_config': json.dumps(js_config),
        }
        return self._html_setup(**options)

    _config_html = PageTemplateFile('configure', globals())
    security.declarePrivate('config_html')
    def config_html(self):
        return self._config_html(all_layers=[
                {'name': 'Road', 'label': "Road"},
                {'name': 'Hybrid', 'label': "Hybrid"},
                {'name': 'Aerial', 'label': "Aerial"}])

    security.declarePrivate('save_config')
    def save_config(self, form_data):
        self.base_layer = form_data['bing_base_layer']

    security.declareProtected(view, 'naaya_bing_js')
    naaya_bing_js = ImageFile('naaya_bing.js', globals())

def register():
    register_map_engine(BingMapEngine)
