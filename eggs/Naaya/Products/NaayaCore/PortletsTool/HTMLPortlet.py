
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
import Products
from OFS.Folder import Folder
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.NaayaCore.constants import *
from managers.portlets_templates import *
from naaya.i18n.LocalPropertyManager import LocalPropertyManager, LocalProperty

manage_addHTMLPortlet_html = PageTemplateFile('zpt/htmlportlet_manage_add', globals())
def addHTMLPortlet(self, id='', title='', body='', portlettype='0', lang=None, REQUEST=None):
    """ """
    id = self.utSlugify(id)
    if not id: id = PREFIX_PORTLET + self.utGenRandomId(6)
    content_type = 'text/html'
    try: portlettype = abs(int(portlettype))
    except: portlettype = 0
    if lang is None: lang = self.gl_get_selected_language()
    ob = HTMLPortlet(id, title, body, portlettype, lang)
    self._setObject(id, ob)
    if REQUEST:
        return self.manage_main(self, REQUEST, update_menu=1)

class HTMLPortlet(LocalPropertyManager, Folder):
    """ """

    meta_type = METATYPE_HTMLPORTLET
    icon = 'misc_/NaayaCore/HTMLPortlet.gif'

    manage_options = (
        ({'label': 'Properties Ex', 'action': 'manage_properties_html'},)
        + (Folder.manage_options[0],)
        + Folder.manage_options[3:]
    )

    def all_meta_types(self, interfaces=None):
        """ """
        y = []
        additional_meta_types = ['Image', 'File']
        for x in Products.meta_types:
            if x['name'] in additional_meta_types:
                y.append(x)
        return y

    security = ClassSecurityInfo()

    title = LocalProperty('title')
    body = LocalProperty('body')

    def __init__(self, id, title, body, portlettype, lang):
        #constructor
        self.id = id
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('body', lang, body)
        self.portlettype = portlettype
        self.template = ZopePageTemplate('', HTML_PORTLET_TEMPLATE, 'text/html')

    def __call__(self, context={}, *args):
        """ """
        if not context.has_key('args'):
            context['args'] = args
        context['skin_files_path'] = self.getLayoutTool().getSkinFilesPath()
        wrappedTemplate = self.template.__of__(self)
        context['here'] = self
        return wrappedTemplate.pt_render(extra_context=context)

    def get_type_label(self):
        #returns the label for the portlet type
        return PORTLETS_TYPES[self.portlettype]

    #zmi actions
    security.declareProtected(view_management_screens, 'manage_properties_html')
    def manage_properties(self, title='', body='', lang=None, REQUEST=None):
        """ """
        if lang is None: lang = self.gl_get_selected_language()
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('body', lang, body)
        self._p_changed = 1
        if REQUEST: REQUEST.RESPONSE.redirect('manage_properties_html?save=ok')

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_properties_html')
    manage_properties_html = PageTemplateFile('zpt/htmlportlet_manage_properties', globals())

InitializeClass(HTMLPortlet)
