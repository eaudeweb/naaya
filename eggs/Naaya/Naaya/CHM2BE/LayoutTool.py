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
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alin Voinea, Eau de Web

"""
Patch for LayoutTool
"""

#Python imports

#Zope imports
from utils import isCustom
from Products.NaayaCore.LayoutTool.LayoutTool import LayoutTool

def getContent(self, p_context={}, p_page=None):
    context = self.REQUEST.PARENTS[0]
    ftool = self.getFormsTool()
    refferer = self.REQUEST.URL0.split('/')[-1]
    custom_forms = getattr(ftool, 'custom_forms', ())
    
    custom_skin = self._getOb(self.getCurrentSkinId())
    custom_schema = self.getCurrentSkinSchemeId()
    
    if isCustom(refferer, custom_forms):
        custom_skin = getattr(ftool, 'custom_skin', '')
        custom_skin_id, custom_schema = custom_skin.split('.')
        custom_skin = self._getOb(custom_skin_id)

    p_context['skin_files_path'] = '%s/%s' % (custom_skin.absolute_url(), custom_schema)
    return custom_skin._getOb(p_page)(p_context)

LayoutTool.getContent = getContent
