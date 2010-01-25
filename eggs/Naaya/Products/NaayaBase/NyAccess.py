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
# Andrei Laza, Eau de Web

# Python imports

# Zope imports
from Acquisition import Implicit
from AccessControl import ClassSecurityInfo
from AccessControl.Permission import Permission
from AccessControl.Permissions import change_permissions
import transaction

# Product imports

class NyAccess(Implicit):
    security = ClassSecurityInfo()

    def __init__(self, permissions):
        self.permissions = permissions

    security.declareProtected(change_permissions, 'getPermissionMapping')
    def getPermissionMapping(self):
        """ Return the permission mapping for the parent """
        ret = {}
        for p_name in self.permissions:
            permission = Permission(p_name, (), self.aq_parent)
            ret[p_name] = permission.getRoles()
        return ret

    security.declareProtected(change_permissions, 'setPermissionMapping')
    def setPermissionMapping(self, mapping):
        """
        Change the permission mapping for the parent.
        This leaves the other permissions (not in mapping.keys()) unchanged
        """
        for p_name in mapping:
            permission = Permission(p_name, (), self.aq_parent)
            permission.setRoles(mapping[p_name])

        transaction.commit()

