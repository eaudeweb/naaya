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
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Andrei Laza, Eau de Web

#Python imports
from datetime import datetime

#Zope imports
from AccessControl.Role import RoleManager
from zope import event
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from AccessControl import getSecurityManager
from zope.annotation.interfaces import IAnnotations
from zope.event import notify

#Products imports
from events import NyAddLocalRoleEvent, NySetLocalRoleEvent, NyDelLocalRoleEvent

class NyRoleManager(RoleManager):
    """ notifies on local role modifications """

    # manage_add/set/delLocalRoles wrappers
    def manage_addLocalRoles(self, userid, roles, *args):
        notify(NyAddLocalRoleEvent(self, userid, roles))
        return super(NyRoleManager, self).manage_addLocalRoles(userid, roles, *args)

    def manage_setLocalRoles(self, userid, roles, *args):
        notify(NySetLocalRoleEvent(self, userid, roles))
        return super(NyRoleManager, self).manage_setLocalRoles(userid, roles, *args)

    def manage_delLocalRoles(self, userids, *args):
        notify(NyDelLocalRoleEvent(self, userids))
        return super(NyRoleManager, self).manage_delLocalRoles(userids, *args)

    # utility functions
    def _getAuthenticatedUserUID(self):
        uid = '__unknown__'
        user = getSecurityManager().getUser()
        if hasattr(user, 'uid'):
            uid = user.uid
        elif hasattr(user, 'name'):
            uid = user.name
        return uid

    def _removeOldAttributes(self):
        old_attr = '__Naaya_additional_ac_local_roles_info__'
        if hasattr(self, old_attr):
            delattr(self, old_attr)
        old_log_attr = '__Naaya_ac_local_roles_log__'
        if hasattr(self, old_log_attr):
            delattr(self, old_log_attr)
        old_state_attr = '__Naaya_ac_local_roles_state__'
        if hasattr(self, old_state_attr):
            delattr(self, old_state_attr)
        old_attr2 = '__Naaya_ac_local_roles__'
        if hasattr(self, old_attr2):
            delattr(self, old_attr2)

    # manage_add/set/delLocalRoles additionalInfo
    def _getStorage4LocalRolesInfo(self):
        self._removeOldAttributes()

        attr = '__Naaya_ac_local_roles__'
        annotations = IAnnotations(self)
        if not annotations.has_key(attr):
            annotations[attr] = PersistentDict()
        return annotations[attr]


    def addLocalRolesInfo(self, userid, roles):
        state = self._getStorage4LocalRolesInfo()

        current_date = datetime.utcnow()
        auth_user = self._getAuthenticatedUserUID()
        state[userid].append(PersistentDict({
            'roles': roles,
            'date': current_date,
            'user_granting_roles': auth_user
            }))

    def setLocalRolesInfo(self, userid, roles):
        state = self._getStorage4LocalRolesInfo()

        current_date = datetime.utcnow()
        auth_user = self._getAuthenticatedUserUID()
        state[userid] = PersistentList()
        state[userid].append(PersistentDict({
            'roles': roles,
            'date': current_date,
            'user_granting_roles': auth_user
            }))


    def delLocalRolesInfo(self, userids):
        state = self._getStorage4LocalRolesInfo()

        current_date = datetime.utcnow()
        auth_user = self._getAuthenticatedUserUID()
        for userid in userids:
            del state[userid]

    def getLocalRolesInfo(self, userid, default=None):
        state = self._getStorage4LocalRolesInfo()
        if not state.has_key(userid):
            return default
        return state[userid]

    def getAllLocalRolesInfo(self):
        state = self._getStorage4LocalRolesInfo()

        # add RoleManager info
        for userid, roles in self.get_local_roles():
            if not state.has_key(userid):
                state[userid] = PersistentList()

            unsaved_roles = []
            for r in roles:
                has_role = False
                for su in state[userid]:
                    if r in su['roles']:
                        has_role = True
                        break
                if not has_role:
                    unsaved_roles.append(r)
            if unsaved_roles != []:
                state[userid].append(PersistentDict({'roles': unsaved_roles}))

        return state


    # user.roles additionalInfo
    def _getStorage4UserRolesInfo(self):
        self._removeOldAttributes()

        attr = '__Naaya_ac_user_roles__'
        annotations = IAnnotations(self)
        if not annotations.has_key(attr):
            annotations[attr] = PersistentDict()
        return annotations[attr]


    def addUserRolesInfo(self, userid, roles):
        state = self._getStorage4UserRolesInfo()

        current_date = datetime.utcnow()
        auth_user = self._getAuthenticatedUserUID()
        dict = {
            'roles': PersistentList(roles),
            'date': current_date,
            'user_granting_roles': auth_user
            }
        state[userid].append(PersistentDict(dict))

    def setUserRolesInfo(self, userid, roles):
        state = self._getStorage4UserRolesInfo()

        current_date = datetime.utcnow()
        auth_user = self._getAuthenticatedUserUID()
        state[userid] = PersistentList()
        dict = {
            'roles': PersistentList(roles),
            'date': current_date,
            'user_granting_roles': auth_user
            }
        state[userid].append(PersistentDict(dict))

    def delUserRolesInfo(self, userids):
        state = self._getStorage4UserRolesInfo()

        current_date = datetime.utcnow()
        auth_user = self._getAuthenticatedUserUID()
        for userid in userids:
            del state[userid]

    def getUserRolesInfo(self, userid, default=None):
        state = self._getStorage4UserRolesInfo()

        if not state.has_key(userid):
            return default
        return state[userid]

    def getAllUserRolesInfo(self):
        state = self._getStorage4UserRolesInfo()
        auth_tool = self.getAuthenticationTool()

        # add user.roles info
        for user in auth_tool.getUsers():
            userid = user.name
            roles = user.roles
            if not state.has_key(userid):
                state[userid] = PersistentList()

            unsaved_roles = []
            for r in roles:
                has_role = False
                for su in state[userid]:
                    if r in su['roles']:
                        has_role = True
                        break
                if not has_role:
                    unsaved_roles.append(r)
            if unsaved_roles != []:
                unsaved_roles = PersistentList(unsaved_roles)
                state[userid].append(PersistentDict({'roles': unsaved_roles}))

        return state

