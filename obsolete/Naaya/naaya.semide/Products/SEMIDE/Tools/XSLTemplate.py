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
# The Initial Owner of the Original Code is EMWIS/SEMIDE.
# Code created by Finsiel Romania are
# Copyright (C) EMWIS/SEMIDE. All Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

#Python imports
from os.path import join

#Zope imports
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Globals import InitializeClass

#SEMIDE imports
from Products.SEMIDE.constants import *
from Products.NaayaCore.managers.utils import utils, file_utils

manage_addXSLTemplateForm = PageTemplateFile('zpt/xsltemplate_add', globals())
def manage_addXSLTemplate(self, id='', title='', file='', type='', lang='', notif_type='eflash', REQUEST=None):
    """ add a new Template object """
    content_type = None
    if file != '':
        if file.filename:
            headers = getattr(file, 'headers', None)
            content_type = headers.get('content_type')
    ob = XSLTemplate(id, title, file, content_type)
    self._setObject(id, ob)
    ob = self._getOb(id)
    ob.loadDefaultData(type, lang, notif_type)
    if REQUEST:
        return self.manage_main(self, REQUEST, update_menu=1)


class XSLTemplate(ZopePageTemplate, utils, file_utils):
    """ XSLTemplate class"""

    meta_type = XSLTEMPLATE_METATYPE

    manage_options = (ZopePageTemplate.manage_options)

    security = ClassSecurityInfo()

    def __init__(self, id, title, text, content_type):
        """ initialize the Template """
        ZopePageTemplate.__dict__['__init__'](self, id, text, content_type)
        self.title = title

    def loadDefaultData(self, type, lang, notif_type):
        """ """
        p_text = self.futReadEnc(join(SEMIDE_PRODUCT_PATH, 'skel', 'emails', notif_type, '%s_%s.xml' % (type, lang)))
        self.pt_edit(p_text.encode('utf-8'), 'text/xml')

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

InitializeClass(XSLTemplate)