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
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from Products.NaayaCore.constants import *

manage_addStyle_html = PageTemplateFile('zpt/style_add', globals())
def manage_addStyle(self, id='', title='', file='', REQUEST=None):
    """ """
    if file == '':
        file = '<span tal:replace="python:request.RESPONSE.setHeader(\'content-type\', \'text/css\')"/>'
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

    def __call__(self, context={}, *args):
        """ """
        if not context.has_key('args'):
            context['args'] = args
        self.REQUEST.RESPONSE.setHeader('content-type', 'text/css')
        return self.pt_render(extra_context=context)

    def om_icons(self):
        """ """
        icons = ({'path': self.icon, 'alt': self.meta_type, 'title': self.meta_type},)
        if self._v_errors:
            icons = icons + ({'path': 'misc_/PageTemplates/exclamation.gif', 'alt': 'Error', 'title': 'This template has an error'},)
        return icons

InitializeClass(Style)
