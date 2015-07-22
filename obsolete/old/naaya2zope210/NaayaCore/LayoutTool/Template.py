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
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate

#Product imports
from Products.NaayaCore.constants import *

manage_addTemplateForm = PageTemplateFile('zpt/template_add', globals())
def manage_addTemplate(self, id='', title='', file='', content_type='text/html', REQUEST=None):
    """ """
    file_content = ''
    if file != '':
        if file.filename:
            headers = getattr(file, 'headers', None)
            content_type = content_type or headers.get('content-type')
            file_content = file.read()
            id = id or file.filename.split('.')[0]
    ob = Template(id, title, file_content, content_type)
    self._setObject(id, ob)
    if REQUEST:
        return self.manage_main(self, REQUEST, update_menu=1)

class Template(ZopePageTemplate):
    """ """

    meta_type = METATYPE_TEMPLATE
    icon = 'misc_/NaayaCore/Template.gif'

    manage_options = (
        ZopePageTemplate.manage_options
    )

    security = ClassSecurityInfo()

    def __init__(self, id, title, text, content_type):
        """ """
        ZopePageTemplate.__dict__['__init__'](self, id, text, content_type)
        self.title = title

    def __call__(self, context={}, *args):
        """ """
        if not context.has_key('args'):
            context['args'] = args
        return self.pt_render(extra_context=context)

    def om_icons(self):
        """ """
        icons = ({'path': self.icon, 'alt': self.meta_type, 'title': self.meta_type},)
        if self._v_errors:
            icons = icons + ({'path': 'misc_/PageTemplates/exclamation.gif', 'alt': 'Error', 'title': 'This template has an error'},)
        return icons

InitializeClass(Template)
