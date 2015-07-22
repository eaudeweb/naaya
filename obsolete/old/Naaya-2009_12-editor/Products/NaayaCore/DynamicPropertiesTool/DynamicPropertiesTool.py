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
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view

#Product imports
from Products.NaayaCore.constants import *
from Products.NaayaCore.managers.utils import utils
import DynamicPropertiesItem

def manage_addDynamicPropertiesTool(self, REQUEST=None):
    """ """
    ob = DynamicPropertiesTool(ID_DYNAMICPROPERTIESTOOL, TITLE_DYNAMICPROPERTIESTOOL)
    self._setObject(ID_DYNAMICPROPERTIESTOOL, ob)
    if REQUEST:
        return self.manage_main(self, REQUEST, update_menu=1)

class DynamicPropertiesTool(Folder, utils):
    """ DynamicPropertiesTool class """

    meta_type = METATYPE_DYNAMICPROPERTIESTOOL
    icon = 'misc_/NaayaCore/DynamicPropertiesTool.gif'

    manage_options = (
        Folder.manage_options
    )

    meta_types = (
        {'name': METATYPE_DYNAMICPROPERTIESITEM, 
         'action': 'manage_addDynamicPropertiesItemForm', 
         'permission': view_management_screens},
    )
    all_meta_types = meta_types

    manage_addDynamicPropertiesItemForm = DynamicPropertiesItem.manage_addDynamicPropertiesItemForm
    manage_addDynamicPropertiesItem = DynamicPropertiesItem.manage_addDynamicPropertiesItem

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        """ """
        self.id = id
        self.title = title
        utils.__dict__['__init__'](self)

    security.declareProtected(view, 'getDynamicProperties')
    def getDynamicProperties(self, p_metatype):
        l_dp_item = self._getOb(p_metatype, None)
        if l_dp_item: return self.utSortObjsListByAttr(l_dp_item.getDynamicProperties(), 'order', 0)
        else: return []

    security.declareProtected(view, 'getDynamicSearchableProperties')
    def getDynamicSearchableProperties(self, p_metatype):
        l_dp_item = self._getOb(p_metatype, None)
        if l_dp_item: return [x for x in l_dp_item.getDynamicProperties() if x.searchable==1]
        else: return []

InitializeClass(DynamicPropertiesTool)
