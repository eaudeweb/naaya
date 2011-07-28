import simplejson as json
import urllib
import logging
from App.config import getConfiguration
from Products.Five.browser import BrowserView
from zope.pagetemplate.pagetemplatefile import PageTemplateFile

log = logging.getLogger(__name__)

document_types = [
    u'Country profiles',
    u'Environmental compendium',
    u'Environmental indicator set \u2013 National',
    u'Environmental indicator set \u2013 Regional',
    u'Environmental indicator set \u2013 Sub-national',
    u'Environmental statistics',
    u'Library services',
    u'National Institution dealing with green economy',
    u'National Institution dealing with water',
    u'Section in environmental performance review',
    u'Sectorial report',
    u'State of green economy assessment/report \u2013 National level',
    u'State of green economy assessment/report \u2013 Regional/Global level',
    u'State of green economy assessment/report \u2013 Sub-national level',
    u'State of water assessment/report \u2013 National level',
    u'State of water assessment/report \u2013 Regional/Global level',
    u'State of water assessment/report \u2013 Sub-national level',
    u'Water indicator set',
    u'Water sector or NGOs report',
    u'Water statistics',
    u'Website',
]

tiles_url = getConfiguration().environment.get('AOA_MAP_TILES', '')
aoa_url = getConfiguration().environment.get('AOA_PORTAL_URL', '')


map_template = PageTemplateFile('map.pt', globals())

class AoaMap(BrowserView):

    def get_map_html(self):
        # TODO helpful error when AoA portal is down
        try:
            aoa_data = urllib.urlopen(aoa_url + 'jsmap_search_map_config')
            aoa_config = json.load(aoa_data)
            aoa_data.close()
        except:
            log.exception("Could not load configuration for AoA search map")
            return "Error loading configuration for AoA search map"

        map_config = {
            'tiles_url': tiles_url,
            'search_url': self.context.absolute_url() + '/aoa-map-search',
            'debug': True,
            'www_prefix': "++resource++eea.aoamap",
        }
        map_config.update(aoa_config)

        options = {
            'map_config': json.dumps(map_config),
            'filter_options': {
                'themes': [u"Water", u"Green economy"],
                'document_types': document_types,
            },
        }

        return map_template(**options)


class AoaMapSearch(BrowserView):

    def __call__(self):
        search_url = (aoa_url + 'jsmap_search_map_documents?' +
                      self.request.QUERY_STRING)
        json_response = urllib.urlopen(search_url).read()
        self.request.RESPONSE.setHeader('Content-Type', 'application/json')
        return json_response
