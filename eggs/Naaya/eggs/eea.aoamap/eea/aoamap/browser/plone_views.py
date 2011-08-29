import simplejson as json
import urllib
import logging
from App.config import getConfiguration
from Products.Five.browser import BrowserView
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

log = logging.getLogger(__name__)

tiles_url = getConfiguration().environment.get('AOA_MAP_TILES', '')
aoa_url = getConfiguration().environment.get('AOA_PORTAL_URL', '')


map_template = PageTemplateFile('map.pt', globals())

class AoaMap(BrowserView):
    """
    The "AoA map search" page.
    """

    def _get_search_url(self):
        return self.context.absolute_url() + '/aoa-map-search'

    def get_map_html(self):
        map_config = {
            'tiles_url': tiles_url,
            'search_url': self._get_search_url(),
            'country_fiche_prefix': aoa_url + '/viewer_aggregator/',
            'debug': True,
            'www_prefix': "++resource++eea.aoamap",
        }

        options = {
            'map_config': json.dumps(map_config),
            'filter_options': {
                'themes': [u"Water", u"Green economy"],
            },
        }

        return map_template.__of__(self.aq_parent)(**options)


def get_aoa_response(relative_url):
    response = urllib.urlopen(aoa_url + relative_url)
    try:
        return response.read()
    finally:
        response.close()


class AoaMapSearch(BrowserView):
    """
    Proxy search requests to the AoA portal.
    """

    def __call__(self):
        json_response = get_aoa_response('jsmap_search_map_documents')
        self.request.RESPONSE.setHeader('Content-Type', 'application/json')
        return json_response


class AddToVirtualLibrary(BrowserView):
    """
    Add entries to the Virtual Library
    """

    def get_vl_form_url(self):
        return (aoa_url + 'tools/virtual_library/'
                'bibliography-details-each-assessment?iframe=on')
