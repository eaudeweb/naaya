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
from zope.pagetemplate.pagetemplate import PageTemplate as Z3_PageTemplate
from zope.tales.tales import Context

from zope.i18n import interpolate

def manage_addEmailPageTemplate(self, id, text):
    ept = EmailPageTemplate(id, text)
    self._setObject(id, ept)
    return id

class EmailPageTemplate(SimpleItem, Z3_PageTemplate):
    meta_type = 'Naaya Email Page Template'

    manage_options = (
        {'label':'Edit', 'action':'pt_editForm',
         'help': ('PageTemplates', 'PageTemplate_Edit.stx')},
        {'label':'Test', 'action':'ZScriptHTML_tryForm'},
        ) + SimpleItem.manage_options

    def __init__(self, id, text):
        self._text = text

    def render_email(self, **kwargs):
        text = self.pt_render({'options': kwargs})

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

    def pt_getEngineContext(self, namespace):
        return CustomI18nContext(self.pt_getEngine(), namespace)

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

class CustomI18nContext(Context):
    def __init__(self, engine, contexts):
        super(CustomI18nContext, self).__init__(engine, contexts)

    def translate(self, msgid, domain=None, mapping=None, default=None):
        options = self.contexts['options']

        lang = options.get('_lang', None)
        translate = options.get('_translate', None)
        if translate is None:
            translate = lambda msgid, lang: msgid

        msg = translate(msgid, lang)
        return interpolate(msg, mapping)
