# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

#Python imports

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
import Products
from OFS.Folder import Folder
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from Products.NaayaCore.constants import *
from managers.portlets_templates import *
from Products.Localizer.LocalPropertyManager import LocalPropertyManager, LocalProperty

manage_addHTMLPortlet_html = PageTemplateFile('zpt/htmlportlet_manage_add', globals())
def addHTMLPortlet(self, id='', title='', body='', portlettype='0', lang=None, REQUEST=None):
    """ """
    id = self.utCleanupId(id)
    if not id: id = PREFIX_PORTLET + self.utGenRandomId(6)
    content_type = 'text/html'
    try: portlettype = abs(int(portlettype))
    except: portlettype = 0
    if lang is None: lang = self.gl_get_selected_language()
    ob = HTMLPortlet(id, title, body, portlettype, lang)
    for lang_rec in self.gl_get_languages_mapping():
        ob.add_language(lang_rec['code'])
        if lang_rec['default']: ob.manage_changeDefaultLang(lang_rec['code'])
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
