from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import plone_views


naaya_map_template = PageTemplateFile('naaya_map.zpt', globals())


class SearchMap(plone_views.AoaMap):

    def _get_search_url(self):
        site = self.aq_parent.getSite()
        return site.absolute_url() + '/jsmap_search_map_documents'

    def __call__(self):
        options = {
            'map_html': self.get_map_html(),
        }
        return naaya_map_template.__of__(self.aq_parent)(**options)
