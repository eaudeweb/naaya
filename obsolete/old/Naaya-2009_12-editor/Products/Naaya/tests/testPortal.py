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
# David Batranu, Eau de Web
# Alin Voinea, Eau de Web

from Products.Naaya.tests import NaayaTestCase

class NaayaTests(NaayaTestCase.NaayaTestCase):

    def afterSetUp(self):
        self.login()
        
    def beforeTearDown(self):
        self.logout()

    def testChangeSiteTitle(self):
        lang = self._portal().gl_get_selected_language()
        self._portal()._setLocalPropValue('title', lang, 'portal_title')
        self._portal()._setLocalPropValue('site_title', lang, 'site_title')
        self._portal()._setLocalPropValue('title', 'fr', 'portal_title_fr')
        self._portal()._setLocalPropValue('site_title', 'fr', 'site_title_fr')
        self._portal()._p_changed = 1
        self.assertEqual(self._portal().getLocalProperty('title', lang), 'portal_title')
        self.assertEqual(self._portal().getLocalProperty('title', 'fr'), 'portal_title_fr')

    def testChangeEmailServer(self):
        new_server = 'newMailServer'
        self._portal().getEmailTool().manageSettings(mail_server_name=new_server)
        self.assertEqual(self._portal().mail_server_name, new_server)

    def test_userManagement(self):
        """ Add, Find, Edit and Delete a User"""
        usr_name = 'test2user'
        usr_pwd = 'test-user-password'
        usr_mail = 'test@test-email.com'
        
        #Add user.
        self._portal().getAuthenticationTool().manage_addUser(name=usr_name, password=usr_pwd, confirm=usr_pwd, firstname=usr_name, lastname=usr_name, email=usr_mail)
        
        #get user object
        usr_obj = self._portal().getAuthenticationTool().getUser(usr_name)
        self.assertEqual(usr_obj.name, usr_name)
        
        #change user email
        self._portal().getAuthenticationTool().manage_changeUser(name=usr_name, password=usr_pwd, confirm=usr_pwd, 
                                                              email='changed@test-user-email.com', firstname=usr_name, lastname=usr_name)
        self.assertEqual(usr_obj.email, 'changed@test-user-email.com')
        
        #add user roles
        self._portal().getAuthenticationTool().manage_addUsersRoles(name=usr_obj.name, roles=['Administrator', 'Manager', 'Contributor'])
        self.assertEqual(usr_obj.roles, ['Administrator', 'Manager', 'Contributor'])
        
        #revoke user roles
        self._portal().getAuthenticationTool().manage_revokeUsersRoles('%s||' % usr_obj.name)
        self.assertEqual(usr_obj.roles, [])
        
        #delete user
        self._portal().getAuthenticationTool().manage_delUsers(names=[usr_obj.name])
        self.assertEqual(self._portal().getAuthenticationTool().getUser(usr_name), None)

    def test_roles(self):
        """ Add, Edit and Delete a Role """
        new_role = 'Test Role'
        permissions = ['Add content', 'Edit content']
        permission = ['Edit content']
        initial_roles = self._portal().getAuthenticationTool().list_all_roles()
        modified_roles = initial_roles[:]
        modified_roles.append(new_role)
        
        #add Role
        test_role = self._portal().getAuthenticationTool().addRole(new_role)
        get_permissions = self._portal().getAuthenticationTool().getRolePermissions(new_role)
        list_roles = self._portal().getAuthenticationTool().list_all_roles()
        self.assertEqual(get_permissions, [])
        self.assertEqual(list_roles, modified_roles)
        
        #add Permisions to role
        edit_permissions = self._portal().getAuthenticationTool().editRole(new_role, permissions)
        get_permissions = self._portal().getAuthenticationTool().getRolePermissions(new_role)
        self.assertEqual(get_permissions, permissions)
        
        #remove permission from role
        edit_permissions = self._portal().getAuthenticationTool().editRole(new_role, permission)
        get_permissions = self._portal().getAuthenticationTool().getRolePermissions(new_role)
        self.assertEqual(get_permissions, permission)
        
        #remove all permissions from role
        edit_permissions = self._portal().getAuthenticationTool().editRole(new_role)
        get_permissions = self._portal().getAuthenticationTool().getRolePermissions(new_role)
        self.assertEqual(get_permissions, [])
        
        #delete role
        self._portal().getAuthenticationTool().delRole(new_role)
        list_roles = self._portal().getAuthenticationTool().list_all_roles()
        self.assertEqual(list_roles, initial_roles)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(NaayaTests))
    return suite
