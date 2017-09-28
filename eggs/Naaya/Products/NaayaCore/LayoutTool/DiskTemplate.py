"""
DiskTemplate is a lightweight ZODB object that loads a template from disk
and behaves like a read-only PageTemplate object.
"""

from os import path

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.NaayaCore.constants import METATYPE_DISKTEMPLATE
from DiskFile import list_available_pathspecs, resolve

manage_addDiskTemplate_html = PageTemplateFile('zpt/disk_template_add',
                                               globals())
manage_addDiskTemplate_html.list_available_pathspecs = list_available_pathspecs

def manage_addDiskTemplate(self, id='', pathspec='', REQUEST=None):
    """ """
    fs_path = resolve(pathspec)
    if not path.isfile(fs_path):
        raise ValueError("File not found %r (resolved to %r)" %
                         (pathspec, fs_path))

    if id == '':
        filename = path.basename(fs_path)
        id = path.splitext(filename)[0]

    ob = DiskTemplate(id, pathspec)
    self._setObject(id, ob)

    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class DiskTemplate(SimpleItem):
    meta_type = METATYPE_DISKTEMPLATE
    icon = 'misc_/NaayaCore/DiskTemplate.gif'

    manage_options = ( (
        {'label': 'Contents', 'action': 'manage_main'},
        {'label': 'View', 'action': ''},
    ) + SimpleItem.manage_options)

    security = ClassSecurityInfo()

    title = ''

    def __init__(self, id, pathspec):
        self._setId(id)
        self.pathspec = pathspec

    def _get_template(self):
        if not hasattr(self, '_v_template'):
            self._v_template = PageTemplateFile(resolve(self.pathspec))
        return self._v_template

    @property
    def macros(self):
        """ proxy for the template's `macros` property """
        return self._get_template().macros

    def __call__(self, *args, **kwargs):
        # we want our template to have the exact same acquisition context
        # as ourselves, so we don't use aq_inner
        parent = self.aq_parent
        template = self._get_template().__of__(parent)
        return template(*args, **kwargs)

    security.declarePublic('index_html')
    def index_html(self, REQUEST, RESPONSE):
        """ return the data """
        return self.__call__(REQUEST)

    _manage_main = PageTemplateFile('zpt/disk_template_manage', globals())
    security.declareProtected(view_management_screens, 'manage_main')
    def manage_main(self, REQUEST):
        """ """
        options = {
            'fs_path': resolve(self.pathspec),
            'template_data': self._get_template()._text,
        }
        return self._manage_main(REQUEST, **options)
