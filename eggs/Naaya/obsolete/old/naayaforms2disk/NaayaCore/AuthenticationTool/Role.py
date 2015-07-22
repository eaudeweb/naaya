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

#Python imports

#Zope imports
from AccessControl.Role import RoleManager
from Globals import MessageDialog, InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view

#Product imports
from Products.NaayaBase.constants import *
from Products.NaayaCore.managers.utils import utils

class Role(RoleManager, utils):
    """ """

    security = ClassSecurityInfo()

    def __init__(self):
        """
        Initialize variables.
        """
        self._permissions = {}  #{permission_name:{'description':permission_description, 'permissions':[list_of_zope_permissions]}, ....}
        self._roles = {}    # {role_name:[list_of_zope_permissions]}
        self._roles_permissions = {}    # {role_name:[list_of_permissions_name]}
        utils.__dict__['__init__'](self)

    def _addRole(self, role):
        """
        Creates a new role in the current portal.
        """
        site = self.getSite()
        data = list(site.__ac_roles__)
        data.append(role)
        site.__ac_roles__ = tuple(data)

    def _delRole(self, roles):
        """
        Delete one or more roles.
        @param roles: list of roles
        @type roles: list
        """
        site = self.getSite()
        data = list(site.__ac_roles__)
        for role in roles:
            del self._roles[role]
            del self._roles_permissions[role]
            self._p_changed = 1
            try: data.remove(role)
            except: pass
        site.__ac_roles__ = tuple(data)

    def addRole(self, role='', permissions=[], REQUEST=None):
        """add role"""
        if REQUEST is not None and REQUEST.has_key('CancelButton'):
            return REQUEST.RESPONSE.redirect('manage_roles_html')
        zope_permissions = {}
        if not role:
            raise Exception, 'You must specify a role name'
        if role in self.__ac_roles__ or role in self._roles.keys():
            raise Exception, 'The given role is already defined'
        permissions = self.utConvertToList(permissions)
        self.getSite()._addRole(role)
        for permission in permissions:
            values = self.getPermission(permission)
            for v in values['permissions']:
                zope_permissions[v] = ""    #remove duplicates
        self._roles[role] = zope_permissions.keys()
        self._roles_permissions[role] = permissions
        self._p_changed = 1
        self.getSite().manage_role(role, zope_permissions.keys())   #call the manage_role with real permissions
        if REQUEST is not None: 
            return REQUEST.RESPONSE.redirect('manage_roles_html')

    def delRole(self, roles=[], REQUEST=None):
        """ delete role"""
        if not roles:
            raise Exception, 'You must specify a role name'
        roles = self.utConvertToList(roles)
        self._delRole(roles)
        if REQUEST is not None: 
            return REQUEST.RESPONSE.redirect('manage_roles_html')

    def editRole(self, role, permissions=[], REQUEST=None):
        """ """
        if REQUEST is not None and REQUEST.has_key('CancelButton'):
            return REQUEST.RESPONSE.redirect(REQUEST['destination'])
        zope_permissions = {}
        permissions = self.utConvertToList(permissions)
        for permission in permissions:
            values = self.getPermission(permission)
            for v in values['permissions']:
                zope_permissions[v] = ""    #remove duplicates
        self._roles[role] = zope_permissions.keys()
        self._roles_permissions[role] = permissions
        self._p_changed = 1
        self.getSite().manage_role(role, zope_permissions.keys())   #call the manage_role with real permissions

        if REQUEST is not None and REQUEST.has_key('destination'):
            return REQUEST.RESPONSE.redirect(REQUEST['destination'])

    def getRolePermissions(self, role):
        """ return the permissions coresponding with role"""
        if not self._roles.has_key(role):
            self._roles[role] = []
            self._p_changed = 1
        if not self._roles_permissions.has_key(role):
            self._roles_permissions[role] = []
            self._p_changed = 1
        temp = []
        for k in self._permissions.keys():
            temp.append(k)
        #update the role's permission list
        for permission in self._roles_permissions[role]:
            if permission not in temp:
                self._roles_permissions[role].remove(permission)
                self._p_changed = 1
        return self._roles_permissions[role]

    security.declareProtected(view_management_screens, 'list_all_roles')
    def list_all_roles(self):
        """
        Returns a list with all roles.
        """
        return list(self.getSite().valid_roles())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'display_defined_roles')
    def display_defined_roles(self, skey='', rkey=''):
        """
        Returns a list with user defined roles to be displayed
        in the administration area.
        """
        roles = list(self.getSite().valid_roles())
        filter(roles.remove, ['Anonymous', 'Manager', 'Owner'])
        if skey == 'name':
            roles.sort()
            if rkey: roles.reverse()
        return roles

    def list_valid_roles(self):
        """ """
        roles = list(self.getSite().valid_roles())
        filter(roles.remove, ['Anonymous', 'Authenticated', 'Owner'])
        return roles

    def getLocalRoles(self, local_roles):
        tmplist = []
        for role in list(local_roles):
            if role not in ['Owner', 'Authenticated']:
                tmplist.append(role)
        return tmplist

    def _addPermission(self, name, description, permissions):
        self._permissions[name] = {'description':description, 'permissions':list(permissions)}
        self._p_changed = 1

    def _editPermission(self, name, description, permissions):
        self._permissions[name] = {'description':description, 'permissions':list(permissions)}
        for x in self._roles_permissions.keys():
            self.editRole(x, self._roles_permissions[x])
        self._p_changed = 1

    def _delPermissions(self, name):
        for k in self._permissions.keys():
            if k in name:
                del self._permissions[k]
        self._p_changed = 1

    def addPermission(self, name='', description='', permissions=[], REQUEST=None):
        """ add permission """
        if REQUEST and REQUEST.has_key('CancelButton'):
            return REQUEST.RESPONSE.redirect('manage_permissions_html')
        if not name:
            return MessageDialog(title  ='Incomplete', message='You must specify a permission name', action ='manage_addPermission_html')
        permissions = self.utConvertToList(permissions)
        self._addPermission(name, description, permissions)
        if REQUEST is not None: 
            return REQUEST.RESPONSE.redirect('manage_permissions_html')

    def delPermission(self, name=[], REQUEST=None):
        """ """
        name = self.utConvertToList(name)
        if not name:
            return MessageDialog(title  ='Incomplete', message='You must specify at least a permission', action ='manage_permissions_html')
        self._delPermissions(name)
        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect('manage_permissions_html')

    def editPermission(self, name, description='', permissions=[], REQUEST=None):
        """ add permission """
        if REQUEST and REQUEST.has_key('CancelButton'):
            return REQUEST.RESPONSE.redirect('manage_permissions_html')
        permissions = self.utConvertToList(permissions)
        self._editPermission(name, description, permissions)
        if REQUEST is not None: 
            return REQUEST.RESPONSE.redirect('manage_editPermission_html?name='+str(name))

    def getPermission(self, name):
        return self._permissions[name]

    def getPermissionName(self, name):
        for k in self._permissions.keys():
            if k == name:
                return name
        return None

    def getPermissionDescription(self, name):
        tmp = self._permissions.get(name, '')
        return tmp.get('description', '')

    def getZopePermissions(self, name):
        tmp = self._permissions.get(name, '')
        return tmp.get('permissions', '')

    def listPermissions(self):
        """ return all permissions"""
        return self._permissions

    def checkGroupPermission(self, name, context):
        #check group of permissions
        for p in self.getPermission(name).get('permissions', []):
            if not context.checkPermission(p): return 0
        return 1

    def list_zope_permissions(self):
        """ """
        #split the permissions dictionary in three lists
        first = []
        second = []
        third = []
        permissions = self.getSite().permission_settings()
        i = 0
        for permission in permissions:
            i = i + 1
            if i%3 == 1:
                first.append(permission['name'])
            elif i%3 == 2:
                second.append(permission['name'])
            elif i%3 == 0:
                third.append(permission['name'])
        return map(None, first, second, third)  #return [(first[0], second[0], third[0]), ...]

InitializeClass(Role)
