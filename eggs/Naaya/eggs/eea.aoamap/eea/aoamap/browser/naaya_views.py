from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import plone_views


naaya_map_template = PageTemplateFile('naaya_map.zpt', globals())


class SearchMap(plone_views.AoaMap):

    def _get_search_url(self):
        site = self.aq_parent.getSite()
        return site.absolute_url() + '/jsmap_search_map_documents'

    def _get_current_language(self):
        return self.aq_parent.gl_get_selected_language()

    def _get_root_url(self):
        return ''

    def __call__(self):
        options = {
            'map_html': self.get_map_html(),
        }
        return naaya_map_template.__of__(self.aq_parent)(**options)
