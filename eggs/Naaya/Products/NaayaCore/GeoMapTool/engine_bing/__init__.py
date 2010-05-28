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

    def __init__(self, id):
        super(BingMapEngine, self).__init__()
        self._setId(id)

    _html_setup = PageTemplateFile('setup', globals())
    security.declarePrivate('html_setup')
    def html_setup(self, request, global_config):
        return self._html_setup(js_config=json.dumps(global_config))

    security.declarePrivate('config_html')
    def config_html(self):
        return ""

    security.declarePrivate('save_config')
    def save_config(self, form_data):
        pass

    security.declareProtected(view, 'naaya_bing_js')
    naaya_bing_js = ImageFile('naaya_bing.js', globals())

def register():
    register_map_engine(BingMapEngine)
