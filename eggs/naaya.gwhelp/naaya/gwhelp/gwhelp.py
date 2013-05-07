from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

manage_addGWHelp_html = PageTemplateFile('zpt/manage_add', globals())

class GWHelp(Folder):
    """ Eionet Forum and Projects help content"""

    meta_type = 'Eionet Help Content'

    def __init__(self, id, title):
        self.id = id
        self.title = title

    _index_html = PageTemplateFile('zpt/index', globals())
    def index_html(self):
        """ Main Help Page """
        return self._index_html()

    _main_features_html = PageTemplateFile('zpt/main_features', globals())
    def main_features(self):
        """ Main features page """
        return self._main_features_html()

    _content_html = PageTemplateFile('zpt/content', globals())
    def content(self):
        """ Content page """
        return self._content_html()

    _content_folder_html = PageTemplateFile('zpt/content_folder', globals())
    def content_folder(self):
        """ Content type: folder page """
        return self._content_folder_html()

    _ig_admin_html = PageTemplateFile('zpt/ig_admin', globals())
    def ig_admin(self):
        """ IG-Admin page """
        return self._ig_admin_html()

    _user_roles_html = PageTemplateFile('zpt/user_roles', globals())
    def user_roles(self):
        """ User roles page """
        return self._user_roles_html()

def manage_addGWHelp(parent, id, title, REQUEST=None):
    """ instantiate the Help package """
    ob = GWHelp(id, title)
    parent._setObject(id, ob)
    if REQUEST is not None:
        url = '%s/manage_workspace' % parent.absolute_url()
        REQUEST.RESPONSE.redirect(url)
