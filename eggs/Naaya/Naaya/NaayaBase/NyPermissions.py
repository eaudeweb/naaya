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

#Python imports

#Zope imports
from AccessControl import ClassSecurityInfo, getSecurityManager
from Globals import InitializeClass

#Product imports
from constants import *

class NyPermissions:
    """ """

    security = ClassSecurityInfo()

    security.declarePrivate('getObjectOwner')
    def getObjectOwner(self):
        ownerid = None
        ownerinfo = self.owner_info()
        if hasattr(ownerinfo, "has_key") and ownerinfo.has_key('id'):
            ownerid = ownerinfo['id']
        return ownerid

    def checkPermission(self, p_permission):
        return getSecurityManager().checkPermission(p_permission, self)

    def checkPermissionAddObjects(self):
        return self.checkPermission(PERMISSION_ADMINISTRATE)

    def checkPermissionEditObjects(self):
        return self.checkPermission(PERMISSION_EDIT_OBJECTS)

    def checkPermissionPublishObjects(self):
        return self.checkPermission(PERMISSION_PUBLISH_OBJECTS)

    def checkPermissionCopyObjects(self):
        return self.checkPermission(PERMISSION_PUBLISH_OBJECTS)

    def checkPermissionCutObjects(self):
        return self.checkPermission(PERMISSION_PUBLISH_OBJECTS)

    def checkPermissionPasteObjects(self):
        return self.checkPermission(PERMISSION_PUBLISH_OBJECTS)

    def checkPermissionDeleteObjects(self):
        return self.checkPermission(PERMISSION_DELETE_OBJECTS)

    def checkPermissionEditObject(self):
        return self.checkPermissionEditObjects() and (self.checkPermissionPublishObjects() or (self.getObjectOwner() == self.REQUEST.AUTHENTICATED_USER.getUserName()))

    def checkPermissionDeleteObject(self):
        return self.checkPermissionDeleteObjects() and (self.checkPermissionPublishObjects() or (self.getObjectOwner() == self.REQUEST.AUTHENTICATED_USER.getUserName()))

InitializeClass(NyPermissions)
