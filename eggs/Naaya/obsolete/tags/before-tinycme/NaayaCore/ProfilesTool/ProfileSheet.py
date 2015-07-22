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

"""
This module contains the class that implements the profile sheet.
"""

#Python imports

#Zope imports
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

#Product imports
from Products.NaayaCore.constants import *
from Products.NaayaCore.managers.utils import utils

def manage_addProfileSheet(self, id, title='', instance_identifier='', REQUEST=None):
    """ """
    ob = ProfileSheet(id, title, instance_identifier)
    self._setObject(id, ob)
    if REQUEST: return self.manage_main(self, REQUEST, update_menu=1)

class ProfileSheet(PropertyManager, SimpleItem, utils):
    """
    Class that implements the profile sheet.
    """

    meta_type = METATYPE_PROFILESHEET
    icon = 'misc_/NaayaCore/ProfileSheet.gif'

    manage_options = (
        PropertyManager.manage_options +
        SimpleItem.manage_options
    )

    _properties=(
        {'id':'title', 'type': 'string', 'mode': 'w'},
        {'id':'instance_identifier', 'type': 'string', 'mode': 'w'},
    )

    security = ClassSecurityInfo()

    def __init__(self, id, title, instance_identifier):
        """
        Initialize variables:

        B{id} - id of the sheet

        B{title} - title of the sheet

        B{instanced_identifier} - stores a reference to the object
        associated with this sheet; based on this value the object
        can be accessed.
        """
        self.id = id
        self.title = title
        self.instance_identifier = instance_identifier

InitializeClass(ProfileSheet)
