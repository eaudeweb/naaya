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
import re

# Zope imports
from Acquisition import Implicit
from AccessControl import ClassSecurityInfo
from AccessControl.Permission import Permission
from AccessControl.Permissions import change_permissions
import transaction
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# Product imports

class NyAccess(Implicit):
    security = ClassSecurityInfo()

    def __init__(self, permissions):
        self.permissions = permissions

    security.declareProtected(change_permissions, 'getRoles')
    def getRoles(self):
        """ """
        roles_to_remove = ['Owner', 'Manager']
        return [role for role in self.aq_parent.validRoles() if role not in roles_to_remove]


    security.declareProtected(change_permissions, 'getPermissionMapping')
    def getPermissionsWithAcquiredRoles(self):
        """ Return the permissions which acquire roles from their parents """
        ret = []
        for p_name in self.permissions:
            permission = Permission(p_name, (), self.aq_parent)
            if isinstance(permission.getRoles(), list):
                ret.append(p_name)
        return ret

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

    security.declareProtected(change_permissions, 'savePermissionMapping')
    def savePermissionMapping(self, REQUEST=None):
        """
        This is called from index_html
        calls setPermissionMapping after converting the arguments
        """
        if REQUEST is None:
            return

        roles = self.getRoles()

        permissionsWithAcquiredRoles = []

        mapping = {}
        for p in self.permissions:
            mapping[p] = []

        for key in REQUEST.form.keys():
            m = re.match('r(\d+)p(\d+)', key)
            if m is not None:
                groups = m.groups()
                r_i, p_i = int(groups[0]), int(groups[1])

                mapping[self.permissions[p_i]].append(roles[r_i])
            else:
                m = re.match('aq(\d+)', key)
                groups = m.groups()
                p_i = int(groups[0])

                permissionsWithAcquiredRoles.append(self.permissions[p_i])

        for p in mapping:
            if p in permissionsWithAcquiredRoles:
                mapping[p] = list(mapping[p])
            else:
                mapping[p] = tuple(mapping[p])

        self.setPermissionMapping(mapping)


    security.declareProtected(change_permissions, 'index_html')
    index_html = PageTemplateFile('zpt/ny_access', globals())

