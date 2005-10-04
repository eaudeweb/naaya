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
# The Original Code is EEAWebUpdate version 0.1
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by CMG and Finsiel Romania are
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

class NyItem(SimpleItem, NyComments, NyBase, NyPermissions):
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

    def manage_afterAdd(self, item, container):
        """
        This method is called, whenever _setObject in ObjectManager gets called.
        """
        SimpleItem.inheritedAttribute('manage_afterAdd')(self, item, container)
        self.catalogNyObject(self)
        l_emails = self.getMaintainersEmails(container)
        if len(l_emails) > 0:
            self.notifyMaintainerEmail(l_emails, self.administrator_email, item.id, self.absolute_url(), '%s/basketofapprovals_html' % container.absolute_url())

    def manage_beforeDelete(self, item, container):
        """
        This method is called, when the object is deleted.
        """
        SimpleItem.inheritedAttribute('manage_beforeDelete')(self, item, container)
        self.uncatalogNyObject(self)

InitializeClass(NyItem)
