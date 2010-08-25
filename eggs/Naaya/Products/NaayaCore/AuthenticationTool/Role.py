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
from copy import deepcopy

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

    def _addRole(self, role):
        """
        Creates a new role in the current portal.
        """
        site = self.getSite()
        site.__ac_roles__ = tuple(set(site.__ac_roles__) + set([role]))

    def _delRole(self, roles):
        """
        Delete one or more roles.
        @param roles: list of roles
        @type roles: list
        """
        site = self.getSite()
        site.__ac_roles__ = tuple(set(site.__ac_roles__) - set(roles))

    def addRole(self, role='', REQUEST=None):
        """add role"""
        if REQUEST is not None and REQUEST.has_key('CancelButton'):
            return REQUEST.RESPONSE.redirect('manage_roles_html')

        if not role:
            raise Exception, 'You must specify a role name'
        if role in self.__ac_roles__:
            raise Exception, 'The role %r is already defined' % role

        self.getSite()._addRole(role)

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

InitializeClass(Role)
