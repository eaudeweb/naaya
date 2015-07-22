
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.NaayaCore.constants import *

manage_addStyle_html = PageTemplateFile('zpt/style_add', globals())
def manage_addStyle(self, id='', title='', file='', REQUEST=None):
    """ """
    if file == '':
        file = '/* stylesheet! */'
    ob = Style(id, title, file)
    self._setObject(id, ob)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class Style(ZopePageTemplate):
    """ """

    meta_type = METATYPE_STYLE
    icon = 'misc_/NaayaCore/Style.gif'

    security = ClassSecurityInfo()

    def __init__(self, id, title, text):
        """ """
        ZopePageTemplate.__dict__['__init__'](self, id, text, 'text/html')
        self.title = title

    def index_html(self, REQUEST):
        """ """
        REQUEST.RESPONSE.setHeader('content-type', 'text/css')
        return self(REQUEST)

    def om_icons(self):
        """ """
        icons = ({'path': self.icon, 'alt': self.meta_type, 'title': self.meta_type},)
        if self._v_errors:
            icons = icons + ({'path': 'misc_/PageTemplates/exclamation.gif', 'alt': 'Error', 'title': 'This template has an error'},)
        return icons

InitializeClass(Style)
