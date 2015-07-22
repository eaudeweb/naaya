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

manage_addPortlet_html = PageTemplateFile('zpt/portlet_manage_add', globals())
def addPortlet(self, id='', title='', portlettype='0', REQUEST=None):
    """ """
    id = self.utCleanupId(id)
    if not id: id = PREFIX_PORTLET + self.utGenRandomId(6)
    content_type = 'text/html'
    try: portlettype = abs(int(portlettype))
    except: portlettype = 0
    body = PORTLETS_BODIES.get(portlettype, 0)
    ob = Portlet(id, title, body, content_type, portlettype)
    self._setObject(id, ob)
    if REQUEST:
        return self.manage_main(self, REQUEST, update_menu=1)

class Portlet(Folder, ZopePageTemplate):
    """ """

    meta_type = METATYPE_PORTLET
    icon = 'misc_/NaayaCore/Portlet.gif'

    manage_options = (
        (
            Folder.manage_options[0],
        )
        +
        ZopePageTemplate.manage_options
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

    def __init__(self, id, title, text, content_type, portlettype):
        #constructor
        ZopePageTemplate.__dict__['__init__'](self, id, text, content_type)
        self.title = title
        self.portlettype = portlettype

    def __call__(self, context={}, *args):
        """ """
        keyset = None
        if self.ZCacheable_isCachingEnabled():
            keyset = {'here': context['here']}
            result = self.ZCacheable_get(keywords=keyset)
            if result is not None:
                #return from cache
                return result
        if not context.has_key('args'):
            context['args'] = args
        context['skin_files_path'] = self.getLayoutTool().getSkinFilesPath()
        result = self.pt_render(extra_context=context)
        if keyset is not None:
            # Store the result in the cache.
            self.ZCacheable_set(result, keywords=keyset)
        return result

    def om_icons(self):
        """ """
        icons = ({'path': self.icon, 'alt': self.meta_type, 'title': self.meta_type},)
        if self._v_errors:
            icons = icons + ({'path': 'misc_/PageTemplates/exclamation.gif', 'alt': 'Error', 'title': 'This template has an error'},)
        return icons

    def get_type_label(self):
        #returns the label for the portlet type
        return PORTLETS_TYPES[self.portlettype]

    def getStaticHTML(self):
        #returns only the static HTML inside the object
        return self.document_src().replace(DEFAULT_PORTLET_HEADER, '').replace(DEFAULT_PORTLET_FOOTER, '')

InitializeClass(Portlet)
