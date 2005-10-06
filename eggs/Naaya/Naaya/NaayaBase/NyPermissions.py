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
This module contains the class that implements permissions and rights checking.
"""

#Python imports

#Zope imports
from AccessControl import ClassSecurityInfo, getSecurityManager
from Globals import InitializeClass

#Product imports
from constants import *

class NyPermissions:
    """
    Class that implements permissions and rights checking.
    """

    security = ClassSecurityInfo()

    def getObjectOwner(self):
        """
        Returns the name of the user that owns the object.
        """
        o = None
        o = self.owner_info()
        if hasattr(o, "has_key") and o.has_key('id'):
            o = o['id']
        return o

    def checkPermission(self, p_permission):
        """
        Generic function to check a given permission on the current object.
        @param p_permission: permissions name
        @type p_permission: string
        @return:
            - B{1} if the current user has the permission
            - B{None} otherwise
        """
        return getSecurityManager().checkPermission(p_permission, self) is not None

    def checkPermissionAdministrate(self):
        """
        Check the access to the administrative area.
        """
        return self.checkPermission(PERMISSION_ADMINISTRATE)

    def checkPermissionValidateObjects(self):
        """
        Check the access to objects validation area.
        """
        return self.checkPermission(PERMISSION_VALIDATE_OBJECTS)

    def checkPermissionTranslatePages(self):
        """
        Check the access to translations area.
        """
        return self.checkPermission(PERMISSION_TRANSLATE_PAGES)

    def checkPermissionAddObjects(self):
        """
        Check the permissions to add different types of objects.
        """
        return self.checkPermission(PERMISSION_ADMINISTRATE)

    def checkPermissionEditObjects(self):
        """
        Check the permissions to edit different type of objects.
        """
        return self.checkPermission(PERMISSION_EDIT_OBJECTS)

    def checkPermissionPublishObjects(self):
        """
        Check the permissions to publish objects.
        """
        return self.checkPermission(PERMISSION_PUBLISH_OBJECTS)

    def checkPermissionCopyObjects(self):
        """
        Check the permissions to copy objects.
        """
        return self.checkPermission(PERMISSION_COPY_OBJECTS)

    def checkPermissionCutObjects(self):
        """
        Check the permissions to cut objects.
        """
        return self.checkPermission(PERMISSION_COPY_OBJECTS) and \
            self.checkPermission(PERMISSION_DELETE_OBJECTS)

    def checkPermissionPasteObjects(self):
        """
        Check the permissions to paste objects.
        """
        return self.checkPermissionAddObjects()

    def checkPermissionDeleteObjects(self):
        """
        Check the permissions to delete objects.
        """
        return self.checkPermission(PERMISSION_DELETE_OBJECTS)

    def checkPermissionEditObject(self):
        """
        Check the permissions to edit a single object. The user must have
        the edit objects permission and to be the object's owner or to have
        the publish permission.
        """
        return self.checkPermissionEditObjects()

    def checkPermissionDeleteObject(self):
        """
        Check the permissions to delete a single object. The user must have
        the delete objects permission and to be the object's owner or to have
        the publish permission.
        """
        return self.checkPermissionDeleteObjects()

    def checkPermissionCopyObject(self):
        """
        Check the permissions to copy a single object. The user must have
        the copy objects permission.
        """
        return self.checkPermissionCopyObjects()

InitializeClass(NyPermissions)
