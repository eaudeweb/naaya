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
# Copyright (C) European Environment Agency. All
# Rights Reserved.
#
# Authors:
# Alexandru Ghica, Adriana Baciu - Finsiel Romania

#Zope imports
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Globals import InitializeClass

def manage_addTemplate(self, id='', title='', file='', REQUEST=None):
    """ add a new Template object """
    content_type = None
    if file != '':
        if file.filename:
            headers = getattr(file, 'headers', None)
            content_type = headers.get('content_type')
    ob = EmailTemplate(id, title, file, content_type)
    self._setObject(id, ob)
    if REQUEST:
        return self.manage_main(self, REQUEST, update_menu=1)

class EmailTemplate(ZopePageTemplate):
    """ EmailTemplate class"""

    meta_type = 'EmailTemplate'

    manage_options = (ZopePageTemplate.manage_options)

    security = ClassSecurityInfo()

    def __init__(self, id, title, text, content_type):
        """ initialize the Template """
        ZopePageTemplate.__dict__['__init__'](self, id, text, content_type)
        self.title = title

    def __call__(self, *args, **kwargs):
        if not kwargs.has_key('args'):
            kwargs['args'] = args
        return self.pt_render(extra_context={'options': kwargs})

    def om_icons(self):
        """ """
        icons = ({'path': self.icon, 'alt': self.meta_type, 'title': self.meta_type},)
        if self._v_errors:
            icons = icons + ({'path': 'misc_/PageTemplates/exclamation.gif', 'alt': 'Error', 'title': 'This template has an error'},)
        return icons

    def edit_template(self, title, text, REQUEST=None):
        """ """
        self.pt_setTitle(title)
        self.pt_edit(text, self.content_type)
        if REQUEST:
            REQUEST.RESPONSE.redirect('edit_html')

InitializeClass(EmailTemplate)
