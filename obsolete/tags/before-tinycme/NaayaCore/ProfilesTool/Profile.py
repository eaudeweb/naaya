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
This module contains the class that implements the user profile.
"""

#Python imports

#Zope imports
from OFS.Folder import Folder
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

#Product imports
from Products.NaayaCore.constants import *
from Products.NaayaCore.managers.utils import utils

def manage_addProfile(self, id, title='', REQUEST=None):
    """ """
    ob = Profile(id, title)
    self._setObject(id, ob)
    self.loadProfileSheets(self._getOb(id))
    if REQUEST: return self.manage_main(self, REQUEST, update_menu=1)

class Profile(Folder, utils):
    """
    Class that implements the user profile.
    """

    meta_type = METATYPE_PROFILE
    icon = 'misc_/NaayaCore/Profile.gif'

    manage_options = (
        Folder.manage_options
    )

    meta_types = ()
    all_meta_types = meta_types

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        """
        Initialize variables:

        B{id} - id of the sheet

        B{title} - title of the sheet
        """
        self.id = id
        self.title = title

    #api
    def getSheets(self):
        """
        Returns a list with all profile sheets.
        """
        return self.objectValues(METATYPE_PROFILESHEET)

    def getSheetById(self, id):
        """
        Returns a sheet object with the given id.
        @param lang: the index language
        @type lang: string
        @return:
            - the object is exists
            - None otherwise
        """
        return self._getOb(id, None)

InitializeClass(Profile)
