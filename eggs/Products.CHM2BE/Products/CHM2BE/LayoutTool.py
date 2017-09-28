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


def get_skin_files_path(self):
    ftool = self.getFormsTool()
    refferer = self.REQUEST.URL0.split('/')[-1]
    custom_forms = getattr(ftool, 'custom_forms', ())

    if isCustom(refferer, custom_forms):
        custom_skin = getattr(ftool, 'custom_skin', '')
        custom_skin_id, custom_schema = custom_skin.split('.')
        custom_skin = self._getOb(custom_skin_id)
        return '%s/%s' % (custom_skin.absolute_url(), custom_schema)
    return '%s/%s' % (self.get_current_skin().absolute_url(), self.getCurrentSkinSchemeId())

def get_current_skin(self):
    ftool = self.getFormsTool()
    refferer = self.REQUEST.URL0.split('/')[-1]
    custom_forms = getattr(ftool, 'custom_forms', ())

    if isCustom(refferer, custom_forms):
        custom_skin = getattr(ftool, 'custom_skin', '')
        custom_skin_id = custom_skin.split('.')[0]
        return self._getOb(custom_skin_id)
    return self._getOb(self.getCurrentSkinId())


LayoutTool.get_skin_files_path = get_skin_files_path
LayoutTool.get_current_skin = get_current_skin

from Products.NaayaCore.LayoutTool.DiskFile import allow_path
allow_path('Products.CHM2BE:skel')
