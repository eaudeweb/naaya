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
# Cornel Nitu, Eau de Web
# Valentin Dumitru, Eau de Web

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

def addEmailTemplate(self, id='', title='', text='', REQUEST=None):
    """ """
    ob = EmailTemplate(id, title, text)
    self._setObject(id, ob)
    if REQUEST:
        return self.manage_main(self, REQUEST, update_menu=1)

class EmailTemplate(ZopePageTemplate):
    """ """

    meta_type = 'EmailTemplate'
    security = ClassSecurityInfo()

    def __init__(self, id, title, text):
        ZopePageTemplate.__dict__['__init__'](self, id, text)
        self.title = title

    def __call__(self, context={}, *args):
        """ """
        keyset = None
        if self.ZCacheable_isCachingEnabled():
            if not context:
                context['here'] = self
            keyset = {'here': context['here']}
            result = self.ZCacheable_get(keywords=keyset)
            if result is not None:
                #return from cache
                return result
        if not context.has_key('args'):
            context['args'] = args
        result = self.pt_render(extra_context=context)
        if keyset is not None:
            # Store the result in the cache.
            self.ZCacheable_set(result, keywords=keyset)
        return result

InitializeClass(EmailTemplate)