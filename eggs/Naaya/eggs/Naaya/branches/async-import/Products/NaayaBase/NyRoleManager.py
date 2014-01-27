from datetime import datetime

from AccessControl.Role import RoleManager
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from Globals import InitializeClass
from AccessControl import getSecurityManager, ClassSecurityInfo
from AccessControl.Permissions import change_permissions
from zope.annotation.interfaces import IAnnotations
from zope.event import notify

from events import NyAddLocalRoleEvent, NySetLocalRoleEvent, NyDelLocalRoleEvent

class NyRoleManager(RoleManager):
    """ Notifies on local role modifications """

    security = ClassSecurityInfo()

    # manage_add/set/delLocalRoles wrappers
    security.declareProtected(change_permissions, 'manage_delLocalRoles')
    def manage_addLocalRoles(self, userid, roles, REQUEST=None):
        """ Override Role.manage_addLocalRoles """

        notify(NyAddLocalRoleEvent(self, userid, roles))
        return super(NyRoleManager, self).manage_addLocalRoles(userid, roles, REQUEST)

    security.declareProtected(change_permissions, 'manage_delLocalRoles')
    def manage_setLocalRoles(self, userid, roles, REQUEST=None):
        """ Override Role.manage_setLocalRoles """

        notify(NySetLocalRoleEvent(self, userid, roles))
        return super(NyRoleManager, self).manage_setLocalRoles(userid, roles, REQUEST)

    security.declareProtected(change_permissions, 'manage_delLocalRoles')
    def manage_delLocalRoles(self, userids, REQUEST=None):
        """ Override Role.manage_delLocalRoles """

        notify(NyDelLocalRoleEvent(self, userids))
        return super(NyRoleManager, self).manage_delLocalRoles(userids, REQUEST)

InitializeClass(NyRoleManager)

class RoleLogger(object):
    def __init__(self, context):
        self.context = context

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
        if hasattr(self.context, old_attr):
            delattr(self.context, old_attr)
        old_log_attr = '__Naaya_ac_local_roles_log__'
        if hasattr(self.context, old_log_attr):
            delattr(self.context, old_log_attr)
        old_state_attr = '__Naaya_ac_local_roles_state__'
        if hasattr(self.context, old_state_attr):
            delattr(self.context, old_state_attr)
        old_attr2 = '__Naaya_ac_local_roles__'
        if hasattr(self.context, old_attr2):
            delattr(self.context, old_attr2)

    # manage_add/set/delLocalRoles additionalInfo
    def _getStorage4LocalRolesInfo(self):
        self._removeOldAttributes()

        attr = '__Naaya_ac_local_roles__'
        annotations = IAnnotations(self.context)
        if attr not in annotations:
            annotations[attr] = PersistentDict()
        return annotations[attr]


    def addLocalRolesInfo(self, userid, roles):
        state = self._getStorage4LocalRolesInfo()
        if userid not in state:
            state[userid] = PersistentList()

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

        for userid in userids:
            if userid in state:
                del state[userid]

    def getLocalRolesInfo(self, userid, default=None):
        state = self._getStorage4LocalRolesInfo()
        if userid not in state:
            return default
        return state[userid]

    def getAllLocalRolesInfo(self):
        state = self._getStorage4LocalRolesInfo()

        # add RoleManager info
        for userid, roles in self.context.get_local_roles():
            if userid not in state:
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
        annotations = IAnnotations(self.context)
        if attr not in annotations:
            annotations[attr] = PersistentDict()
        return annotations[attr]


    def addUserRolesInfo(self, userid, roles):
        state = self._getStorage4UserRolesInfo()
        if userid not in state:
            state[userid] = PersistentList()

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

        for userid in userids:
            if userid in state:
                del state[userid]

    def getUserRolesInfo(self, userid, default=None):
        state = self._getStorage4UserRolesInfo()

        if userid not in state:
            return default
        return state[userid]

    def getAllUserRolesInfo(self):
        state = self._getStorage4UserRolesInfo()
        auth_tool = self.context.getAuthenticationTool()

        # add user.roles info
        for user in auth_tool.getUsers():
            userid = user.name
            roles = user.roles
            if userid not in state:
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

    # ldap groups roles additionalInfo
    def _getStorage4LDAPGroupRolesInfo(self):
        self._removeOldAttributes()

        attr = '__Naaya_ac_ldap_group_roles__'
        annotations = IAnnotations(self.context)
        if attr not in annotations:
            annotations[attr] = PersistentDict()
        return annotations[attr]


    def addLDAPGroupRolesInfo(self, group, roles):
        state = self._getStorage4LDAPGroupRolesInfo()
        if group not in state:
            state[group] = PersistentList()

        current_date = datetime.utcnow()
        auth_user = self._getAuthenticatedUserUID()
        dict = {
            'roles': PersistentList(roles),
            'date': current_date,
            'user_granting_roles': auth_user
            }
        state[group].append(PersistentDict(dict))

    def removeLDAPGroupRolesInfo(self, group, roles):
        state = self._getStorage4LDAPGroupRolesInfo()

        if group in state:
            for dict in state[group]:
                for r in roles:
                    if r in dict['roles']:
                        dict['roles'].remove(r)
                if dict['roles'] == []:
                    state[group].remove(dict)
            if state[group] == []:
                del state[group]

    def getLDAPGroupRolesInfo(self, group, default=None):
        state = self._getStorage4LDAPGroupRolesInfo()

        if group not in state:
            return default
        return state[group]

    def getAllLDAPGroupRolesInfo(self):
        state = self._getStorage4LDAPGroupRolesInfo()
        auth_tool = self.context.getAuthenticationTool()

        if not hasattr(self.context, 'acl_satellite'):
            return state

        mapped_roles = self.context.acl_satellite.getAllLocalRoles()
        for group in mapped_roles:
            roles = mapped_roles[group]
            if group not in state:
                state[group] = PersistentList()

            unsaved_roles = []
            for r in roles:
                has_role = False
                for sg in state[group]:
                    if r in sg['roles']:
                        has_role = True
                        break
                if not has_role:
                    unsaved_roles.append(r)
            if unsaved_roles != []:
                unsaved_roles = PersistentList(unsaved_roles)
                state[group].append(PersistentDict({'roles': unsaved_roles}))

        return state
