import simplejson as json
from zope.publisher.browser import BrowserPage
from Products.PageTemplates.PageTemplateFile import PageTemplateFile \
                                             as z2_PageTemplateFile
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from naaya.ew_aoa_library.jsmap import get_document_types
from naaya.ew_aoa_library.jsmap import search_map_initial_data
from naaya.ew_aoa_library.jsmap import tiles_url


def portlet_template_options(site):
    search_url = site.absolute_url() + '/jsmap_search_map_documents'
    country_fiche_prefix = site.absolute_url() + '/viewer_aggregator/'
    aoa_config = search_map_initial_data(site)

    map_config = {
        'tiles_url': tiles_url,
        'search_url': search_url,
        'country_fiche_prefix': country_fiche_prefix,
        'debug': True,
        'www_prefix': "++resource++eea.aoamap",
    }
    map_config.update(aoa_config)

    return {
        'map_config': json.dumps(map_config),
        'filter_options': {
            'themes': [u"Water", u"Green economy"],
            'document_types': get_document_types(site),
        },
    }


map_template = PageTemplateFile('map.pt', globals())

def render_map_html(site):
    options = portlet_template_options(site)
    return map_template(**options)


naaya_map_template = z2_PageTemplateFile('naaya_map.zpt', globals())

class SearchMap(BrowserPage):
    def __call__(self):
        context = self.aq_parent
        site = context.getSite()
        options = {
            'map_html': render_map_html(site),
        }
        return naaya_map_template.__of__(context)(**options)
