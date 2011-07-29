from Products.PageTemplates.PageTemplateFile import PageTemplateFile \
                                             as z2_PageTemplateFile
from naaya.ew_aoa_library.jsmap import search_map_initial_data
import plone_views


naaya_map_template = z2_PageTemplateFile('naaya_map.zpt', globals())


class SearchMap(plone_views.AoaMap):

    def _get_aoa_config(self):
        site = self.aq_parent.getSite()
        return search_map_initial_data(site)

    def _get_search_url(self):
        site = self.aq_parent.getSite()
        return site.absolute_url() + '/jsmap_search_map_documents'

    def __call__(self):
        options = {
            'map_html': self.get_map_html(),
        }
        return naaya_map_template.__of__(self.aq_parent)(**options)
