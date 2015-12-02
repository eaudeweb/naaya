from AccessControl.Role import RoleManager
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.NaayaBase.constants import *
from Products.NaayaCore.managers.utils import utils
from naaya.core.exceptions import ValidationError


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
        if REQUEST is not None and 'CancelButton' in REQUEST:
            return REQUEST.RESPONSE.redirect('manage_roles_html')

        if not role:
            raise ValidationError, 'You must specify a role name'
        if role in self.__ac_roles__:
            raise ValidationError, 'The role %r is already defined' % role

        self.getSite()._addRole(role)

        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect('manage_roles_html')

    def delRole(self, roles=[], REQUEST=None):
        """ delete role"""
        if not roles:
            raise ValidationError, 'You must specify a role name'
        roles = self.utConvertToList(roles)
        self._delRole(roles)
        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect('manage_roles_html')

    def list_all_roles(self):
        """
        Returns a list with all roles.
        """
        return list(self.getSite().valid_roles())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS,
                              'display_defined_roles')

    def display_defined_roles(self, skey='', rkey=''):
        """
        Returns a list with user defined roles to be displayed
        in the administration area.
        """
        roles = list(self.getSite().valid_roles())
        filter(roles.remove, ['Anonymous', 'Manager', 'Owner'])
        if skey == 'name':
            roles.sort()
            if rkey:
                roles.reverse()
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
