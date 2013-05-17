from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view, view_management_screens

manage_addGWHelp_html = PageTemplateFile('zpt/manage_add', globals())

class GWHelp(Folder):
    """ Eionet Forum and Projects help content"""

    meta_type = 'Eionet Help Content'

    def __init__(self, id, title):
        self.id = id
        self.title = title

    security = ClassSecurityInfo()

    security.declareProtected(view, 'help_index_html')
    help_index_html = PageTemplateFile('zpt/index', globals())
    security.declareProtected(view, 'index_html')
    def index_html(self):
        """ Main Help Page """
        return self.help_index_html()

    _main_features_html = PageTemplateFile('zpt/main_features', globals())
    security.declareProtected(view, 'main_features')
    def main_features(self):
        """ Main features page """
        return self._main_features_html()

    _content_html = PageTemplateFile('zpt/content', globals())
    security.declareProtected(view, 'content')
    def content(self):
        """ Content page """
        return self._content_html()

    _content_folder_html = PageTemplateFile('zpt/content_folder', globals())
    security.declareProtected(view, 'content_folder')
    def content_folder(self):
        """ Content type: folder page """
        return self._content_folder_html()

    _content_forum_html = PageTemplateFile('zpt/content_forum', globals())
    security.declareProtected(view, 'content_forum')
    def content_forum(self):
        """ Content type: forum page """
        return self._content_forum_html()

    _content_file_html = PageTemplateFile('zpt/content_file', globals())
    security.declareProtected(view, 'content_file')
    def content_file(self):
        """ Content type: file page """
        return self._content_file_html()

    _content_survey_html = PageTemplateFile('zpt/content_survey', globals())
    security.declareProtected(view, 'content_survey')
    def content_survey(self):
        """ Content type: survey page """
        return self._content_survey_html()

    _content_consultation_html = PageTemplateFile('zpt/content_consultation', globals())
    security.declareProtected(view, 'content_consultation')
    def content_consultation(self):
        """ Content type: consultation page """
        return self._content_consultation_html()

    _content_meeting_html = PageTemplateFile('zpt/content_meeting', globals())
    security.declareProtected(view, 'content_meeting')
    def content_meeting(self):
        """ Content type: meeting page """
        return self._content_meeting_html()

    _ig_admin_html = PageTemplateFile('zpt/ig_admin', globals())
    security.declareProtected(view, 'ig_admin')
    def ig_admin(self):
        """ IG-Admin page """
        return self._ig_admin_html()

    _user_management_html = PageTemplateFile('zpt/user_management', globals())
    security.declareProtected(view, 'user_management')
    def user_management(self):
        """ User management page """
        return self._user_management_html()

def manage_addGWHelp(parent, id, title, REQUEST=None):
    """ instantiate the Help package """
    ob = GWHelp(id, title)
    parent._setObject(id, ob)
    if REQUEST is not None:
        url = '%s/manage_workspace' % parent.absolute_url()
        REQUEST.RESPONSE.redirect(url)
