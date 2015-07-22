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
# The Original Code is Naaya version 1.0
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
This module contains the class that implements the Naaya simple item type of object.
All types of objects that are not containers must extend this class.
"""

#Python imports

#Zope imports
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

#Product imports
from NyBase import NyBase
from NyPermissions import NyPermissions
from NyComments import NyComments
from NyDublinCore import NyDublinCore

class NyItem(SimpleItem, NyComments, NyBase, NyPermissions, NyDublinCore):
    """
    Class that implements the Naaya simple item type of object.
    """

    manage_options = (
        SimpleItem.manage_options
    )

    security = ClassSecurityInfo()

    def __init__(self):
        """
        Constructor.
        """
        NyBase.__dict__['__init__'](self)
        NyComments.__dict__['__init__'](self)
        NyDublinCore.__dict__['__init__'](self)

    def manage_afterAdd(self, item, container):
        """
        This method is called, whenever _setObject in ObjectManager gets called.
        """
        SimpleItem.inheritedAttribute('manage_afterAdd')(self, item, container)
        self.catalogNyObject(self)

    def manage_beforeDelete(self, item, container):
        """
        This method is called, when the object is deleted.
        """
        SimpleItem.inheritedAttribute('manage_beforeDelete')(self, item, container)
        self.uncatalogNyObject(self)

InitializeClass(NyItem)
