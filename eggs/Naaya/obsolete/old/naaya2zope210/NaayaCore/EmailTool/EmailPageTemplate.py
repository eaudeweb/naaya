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
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alex Morega, Eau de Web

import re
import os.path

from zope import interface
from Globals import package_home
from OFS.interfaces import ITraversable
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplate import PageTemplate
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate

def manage_addEmailPageTemplate(self, id, text):
    ept = EmailPageTemplate(id, text)
    self._setObject(id, ept)
    return id

class EmailPageTemplate(SimpleItem, ZopePageTemplate):
    meta_type = 'Naaya Email Page Template'

    manage_options = (
        {'label':'Edit', 'action':'pt_editForm',
         'help': ('PageTemplates', 'PageTemplate_Edit.stx')},
        {'label':'Test', 'action':'ZScriptHTML_tryForm'},
        ) + SimpleItem.manage_options

    def __init__(self, id, text):
        super(EmailPageTemplate, self).__init__(id, text)

    def render_email(self, **kwargs):
        text = self.pt_render(extra_context={'options': TraversableDict(kwargs)})

        def get_section(name):
            try:
                start = text.index('<%s>' % name) + len(name) + 2
                end = text.index('</%s>' % name, start)
            except ValueError:
                raise ValueError('Section "%s" not found in '
                    'email template output' % name)
            return text[start:end].strip()

        return {
            'subject': get_section('subject'),
            'body_text': get_section('body_text'),
        }

    pt_getContext = PageTemplate.pt_getContext

def EmailPageTemplateFile(filename, _prefix):
    if _prefix:
        if isinstance(_prefix, str):
            filename = os.path.join(_prefix, filename)
        else:
            filename = os.path.join(package_home(_prefix), filename)
    f = open(filename)
    content = f.read()
    f.close()
    id = os.path.basename(filename)
    return EmailPageTemplate(id, content)

class TraversableDict(dict):
    """
    `dict` subclass that implements the restrictedTraverse method to make the
    zope template engine happy
    """
    interface.implements(ITraversable)
    def restrictedTraverse(self, name, default=None):
        return self.get(name, default)
