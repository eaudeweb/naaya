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
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from AccessControl.Permission import Permission
from AccessControl.Permissions import change_permissions
from Products.NaayaBase.constants import MESSAGE_SAVEDCHANGES
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import transaction

# Product imports

class NyAccess(SimpleItem):
    security = ClassSecurityInfo()

    title = "Edit permissions"

    def __init__(self, id, permissions):
        assert isinstance(permissions, dict) # old code used a list here
        self.id = id
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
        for zope_perm in self.permissions:
            permission = Permission(zope_perm, (), self.aq_parent)
            if isinstance(permission.getRoles(), list):
                ret.append(zope_perm)
        return ret

    security.declareProtected(change_permissions, 'getPermissionMapping')
    def getPermissionMapping(self):
        """ Return the permission mapping for the parent """
        ret = {}
        for zope_perm in self.permissions:
            permission = Permission(zope_perm, (), self.aq_parent)
            ret[zope_perm] = permission.getRoles()
        return ret

    security.declareProtected(change_permissions, 'setPermissionMapping')
    def setPermissionMapping(self, mapping):
        """
        Change the permission mapping for the parent.
        This leaves the other permissions (not in mapping.keys()) unchanged
        """
        for zope_perm in mapping:
            permission = Permission(zope_perm, (), self.aq_parent)
            permission.setRoles(mapping[zope_perm])

        transaction.commit()

    security.declareProtected(change_permissions, 'savePermissionMapping')
    def savePermissionMapping(self, REQUEST):
        """
        This is called from index_html
        calls setPermissionMapping after converting the arguments
        """

        roles = self.getRoles()

        permissionsWithAcquiredRoles = []

        sorted_zope_perm = sorted(self.permissions.keys())

        mapping = {}
        for zope_perm in self.permissions:
            mapping[zope_perm] = []

        for key in REQUEST.form.keys():
            m = re.match('r(\d+)p(\d+)', key)
            if m is not None:
                groups = m.groups()
                r_i, p_i = int(groups[0]), int(groups[1])

                mapping[sorted_zope_perm[p_i]].append(roles[r_i])
            else:
                m = re.match('aq(\d+)', key)
                groups = m.groups()
                p_i = int(groups[0])

                zope_perm = sorted_zope_perm[p_i]
                permissionsWithAcquiredRoles.append(zope_perm)

        for zope_perm in mapping:
            if zope_perm in permissionsWithAcquiredRoles:
                mapping[zope_perm] = list(mapping[zope_perm])
            else:
                mapping[zope_perm] = tuple(mapping[zope_perm])

        self.setPermissionMapping(mapping)

        self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES,
                                 date=self.utGetTodayDate())
        return REQUEST.RESPONSE.redirect(self.absolute_url())


    security.declareProtected(change_permissions, 'index_html')
    index_html = PageTemplateFile('zpt/ny_access', globals())
