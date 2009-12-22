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

# Python
from unittest import TestSuite, makeSuite

# Zope
import transaction

# Products
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.NaayaBase.NyRoleManager import NyRoleManager

class TestNyRoleManager(NaayaFunctionalTestCase):
    def afterSetUp(self):
        self.username = 'testuser'
        self.password = 'testuser_password'
        self.email = 'test@testuser.com'
        self.groupname= 'testgroup'

        self.portal.getAuthenticationTool().manage_addUser(name=self.username,
                password=self.password, confirm=self.password,
                firstname=self.username, lastname=self.username,
                email=self.email)
        transaction.commit()

    def beforeTearDown(self):
        self.portal.getAuthenticationTool().manage_delUsers(
                names=[self.username])
        transaction.commit()

    # manage_add/set/delLocalRoles tests
    def test_local_roles_add_remove_raw(self):
        self.browser_do_login('admin', '')

        self.portal.info.setLocalRolesInfo(self.username, ['Manager'])
        additional_info = self.portal.info.getLocalRolesInfo(self.username)
        self.assertTrue(len(additional_info) == 1)
        self.assertTrue(additional_info[0]['roles'] == ['Manager'])
        self.assertTrue(additional_info[0].has_key('date'))
        self.assertTrue(additional_info[0]['user_granting_roles'] == 'admin')

        self.portal.info.addLocalRolesInfo(self.username, ['Reader'])
        additional_info = self.portal.info.getLocalRolesInfo(self.username)
        self.assertTrue(len(additional_info) == 2)
        self.assertTrue(additional_info[0]['roles'] == ['Manager'])
        self.assertTrue(additional_info[0].has_key('date'))
        self.assertTrue(additional_info[0]['user_granting_roles'] == 'admin')
        self.assertTrue(additional_info[1]['roles'] == ['Reader'])
        self.assertTrue(additional_info[1].has_key('date'))
        self.assertTrue(additional_info[1]['user_granting_roles'] == 'admin')

        self.portal.info.delLocalRolesInfo([self.username])
        additional_info = self.portal.info.getLocalRolesInfo(self.username)
        self.assertTrue(additional_info is None)

        self.browser_do_logout()

    def test_wrappers_in_place(self):
        try:
            from Products.Naaya.NySite import NySite
            self.assertTrue(NySite.manage_addLocalRoles == NyRoleManager.manage_addLocalRoles)
            self.assertTrue(NySite.manage_setLocalRoles == NyRoleManager.manage_setLocalRoles)
            self.assertTrue(NySite.manage_delLocalRoles == NyRoleManager.manage_delLocalRoles)
        except ImportError:
            pass

        try:
            from Products.Naaya.NyFolder import NyFolder
            self.assertTrue(NyFolder.manage_addLocalRoles == NyRoleManager.manage_addLocalRoles)
            self.assertTrue(NyFolder.manage_setLocalRoles == NyRoleManager.manage_setLocalRoles)
            self.assertTrue(NyFolder.manage_delLocalRoles == NyRoleManager.manage_delLocalRoles)
        except ImportError:
            pass


    def test_local_roles_add_remove(self):
        self.browser_do_login('admin', '')

        self.portal.info.manage_setLocalRoles(self.username, ['Manager'])
        additional_info = self.portal.info.getLocalRolesInfo(self.username)
        self.assertTrue(len(additional_info) == 1)
        self.assertTrue(additional_info[0]['roles'] == ['Manager'])
        self.assertTrue(additional_info[0].has_key('date'))
        self.assertTrue(additional_info[0]['user_granting_roles'] == 'admin')

        self.portal.info.manage_addLocalRoles(self.username, ['Reader'])
        additional_info = self.portal.info.getLocalRolesInfo(self.username)
        self.assertTrue(len(additional_info) == 2)
        self.assertTrue(additional_info[0]['roles'] == ['Manager'])
        self.assertTrue(additional_info[0].has_key('date'))
        self.assertTrue(additional_info[0]['user_granting_roles'] == 'admin')
        self.assertTrue(additional_info[1]['roles'] == ['Reader'])
        self.assertTrue(additional_info[1].has_key('date'))
        self.assertTrue(additional_info[1]['user_granting_roles'] == 'admin')

        self.portal.info.manage_delLocalRoles([self.username])
        additional_info = self.portal.info.getLocalRolesInfo(self.username)
        self.assertTrue(additional_info is None)

        self.browser_do_logout()

    def _get_roles_from_additional_info(self, additional_info):
        naaya_roles_list = []
        if additional_info is None:
            naaya_roles = set()
        else:
            for ai in additional_info:
                naaya_roles_list.extend(ai['roles'])
            naaya_roles = set(naaya_roles_list)
        return naaya_roles

    def test_match_local_roles_data(self):
        self.browser_do_login('admin', '')

        self.portal.info.manage_setLocalRoles(self.username, ['Manager'])
        info = self.portal.info.get_local_roles_for_userid(self.username)
        additional_info = self.portal.info.getLocalRolesInfo(self.username)
        zope_roles = set(info)
        naaya_roles = self._get_roles_from_additional_info(additional_info)
        self.assertTrue(len(zope_roles.symmetric_difference(naaya_roles)) == 0)

        self.portal.info.manage_addLocalRoles(self.username, ['Reader'])
        info = self.portal.info.get_local_roles_for_userid(self.username)
        additional_info = self.portal.info.getLocalRolesInfo(self.username)
        zope_roles = set(info)
        naaya_roles = self._get_roles_from_additional_info(additional_info)
        self.assertTrue(len(zope_roles.symmetric_difference(naaya_roles)) == 0)

        self.portal.info.manage_delLocalRoles([self.username])
        info = self.portal.info.get_local_roles_for_userid(self.username)
        additional_info = self.portal.info.getLocalRolesInfo(self.username)
        zope_roles = set(info)
        naaya_roles = self._get_roles_from_additional_info(additional_info)
        self.assertTrue(len(zope_roles.symmetric_difference(naaya_roles)) == 0)

        self.browser_do_logout()

    def test_all_local_roles_info(self):
        self.browser_do_login('admin', '')
        self.portal.info.manage_setLocalRoles(self.username, ['Manager'])
        super(NyRoleManager, self.portal.info).manage_addLocalRoles(self.username, ['Reader'])

        all_info = self.portal.info.getAllLocalRolesInfo()
        self.assertTrue(all_info.has_key(self.username))
        user_info = all_info[self.username]
        self.assertTrue(len(user_info) == 2)
        self.assertTrue(user_info[0]['roles'] == ['Manager'])
        self.assertTrue(user_info[0].has_key('date'))
        self.assertTrue(user_info[0]['user_granting_roles'] == 'admin')
        self.assertTrue(user_info[1]['roles'] == ['Reader'])
        self.assertTrue(not user_info[1].has_key('date'))
        self.assertTrue(not user_info[1].has_key('user_granting_roles'))

        self.browser_do_logout()


    # user.roles functions tests
    def test_user_roles_add_remove_raw(self):
        self.browser_do_login('admin', '')

        self.portal.setUserRolesInfo(self.username, ['Manager'])
        additional_info = self.portal.getUserRolesInfo(self.username)
        self.assertTrue(len(additional_info) == 1)
        self.assertTrue(additional_info[0]['roles'] == ['Manager'])
        self.assertTrue(additional_info[0].has_key('date'))
        self.assertTrue(additional_info[0]['user_granting_roles'] == 'admin')

        self.portal.addUserRolesInfo(self.username, ['Reader'])
        additional_info = self.portal.getUserRolesInfo(self.username)
        self.assertTrue(len(additional_info) == 2)
        self.assertTrue(additional_info[0]['roles'] == ['Manager'])
        self.assertTrue(additional_info[0].has_key('date'))
        self.assertTrue(additional_info[0]['user_granting_roles'] == 'admin')
        self.assertTrue(additional_info[1]['roles'] == ['Reader'])
        self.assertTrue(additional_info[1].has_key('date'))
        self.assertTrue(additional_info[1]['user_granting_roles'] == 'admin')

        self.portal.delUserRolesInfo([self.username])
        additional_info = self.portal.getUserRolesInfo(self.username)
        self.assertTrue(additional_info is None)

        self.browser_do_logout()

    def test_user_roles_add_remove(self):
        self.browser_do_login('admin', '')
        auth_tool = self.portal.getAuthenticationTool()
        user = auth_tool.getUser(self.username)

        user.setRoles(self.portal, ['Manager'])
        additional_info = self.portal.getUserRolesInfo(self.username)
        self.assertTrue(len(additional_info) == 1)
        self.assertTrue(additional_info[0]['roles'] == ['Manager'])
        self.assertTrue(additional_info[0].has_key('date'))
        self.assertTrue(additional_info[0]['user_granting_roles'] == 'admin')

        user.addRoles(self.portal, ['Reader'])
        additional_info = self.portal.getUserRolesInfo(self.username)
        self.assertTrue(len(additional_info) == 2)
        self.assertTrue(additional_info[0]['roles'] == ['Manager'])
        self.assertTrue(additional_info[0].has_key('date'))
        self.assertTrue(additional_info[0]['user_granting_roles'] == 'admin')
        self.assertTrue(additional_info[1]['roles'] == ['Reader'])
        self.assertTrue(additional_info[1].has_key('date'))
        self.assertTrue(additional_info[1]['user_granting_roles'] == 'admin')

        user.delRoles(self.portal)
        additional_info = self.portal.getUserRolesInfo(self.username)
        self.assertTrue(additional_info is None)

        self.browser_do_logout()

    def test_match_user_roles_data(self):
        self.browser_do_login('admin', '')
        auth_tool = self.portal.getAuthenticationTool()
        user = auth_tool.getUser(self.username)

        user.setRoles(self.portal, ['Manager'])
        info = auth_tool.getUserRoles(user)
        additional_info = self.portal.getUserRolesInfo(self.username)
        zope_roles = set(info)
        naaya_roles = self._get_roles_from_additional_info(additional_info)
        self.assertTrue(len(zope_roles.symmetric_difference(naaya_roles)) == 0)

        user.addRoles(self.portal, ['Reader'])
        info = auth_tool.getUserRoles(user)
        additional_info = self.portal.getUserRolesInfo(self.username)
        zope_roles = set(info)
        naaya_roles = self._get_roles_from_additional_info(additional_info)
        self.assertTrue(len(zope_roles.symmetric_difference(naaya_roles)) == 0)

        user.delRoles(self.portal)
        info = auth_tool.getUserRoles(user)
        additional_info = self.portal.getUserRolesInfo(self.username)
        zope_roles = set(info)
        naaya_roles = self._get_roles_from_additional_info(additional_info)
        self.assertTrue(len(zope_roles.symmetric_difference(naaya_roles)) == 0)

        self.browser_do_logout()

    def test_all_local_roles_info(self):
        self.browser_do_login('admin', '')
        auth_tool = self.portal.getAuthenticationTool()
        user = auth_tool.getUser(self.username)
        user.setRoles(self.portal, ['Manager'])
        user.roles.extend(['Reader'])

        all_info = self.portal.getAllUserRolesInfo()
        self.assertTrue(all_info.has_key(self.username))
        user_info = all_info[self.username]
        self.assertTrue(len(user_info) == 2)
        self.assertTrue(user_info[0]['roles'] == ['Manager'])
        self.assertTrue(user_info[0].has_key('date'))
        self.assertTrue(user_info[0]['user_granting_roles'] == 'admin')
        self.assertTrue(user_info[1]['roles'] == ['Reader'])
        self.assertTrue(not user_info[1].has_key('date'))
        self.assertTrue(not user_info[1].has_key('user_granting_roles'))

        self.browser_do_logout()


    # ldap group roles functions tests
    def test_group_roles_add_remove_raw(self):
        self.browser_do_login('admin', '')

        additional_info = self.portal.getLDAPGroupRolesInfo(self.groupname)
        self.assertTrue(additional_info is None)

        self.portal.addLDAPGroupRolesInfo(self.groupname, ['Manager'])
        additional_info = self.portal.getLDAPGroupRolesInfo(self.groupname)
        self.assertTrue(len(additional_info) == 1)
        self.assertTrue(additional_info[0]['roles'] == ['Manager'])
        self.assertTrue(additional_info[0].has_key('date'))
        self.assertTrue(additional_info[0]['user_granting_roles'] == 'admin')

        self.portal.removeLDAPGroupRolesInfo(self.groupname, ['Manager'])
        additional_info = self.portal.getLDAPGroupRolesInfo(self.groupname)
        self.assertTrue(additional_info is None)

        self.browser_do_logout()

    def test_group_roles_add_remove(self):
        self.browser_do_login('admin', '')
        satellite = self.portal.acl_satellite

        additional_info = self.portal.getLDAPGroupRolesInfo(self.groupname)
        self.assertTrue(additional_info is None)

        satellite.add_group_roles(self.groupname, ['Manager'])
        additional_info = self.portal.getLDAPGroupRolesInfo(self.groupname)
        self.assertTrue(len(additional_info) == 1)
        self.assertTrue(additional_info[0]['roles'] == ['Manager'])
        self.assertTrue(additional_info[0].has_key('date'))
        self.assertTrue(additional_info[0]['user_granting_roles'] == 'admin')

        satellite.remove_group_roles(self.groupname, ['Manager'])
        additional_info = self.portal.getLDAPGroupRolesInfo(self.groupname)
        self.assertTrue(additional_info is None)

        self.browser_do_logout()

    def test_match_group_roles_data(self):
        self.browser_do_login('admin', '')
        satellite = self.portal.acl_satellite

        additional_info = self.portal.getLDAPGroupRolesInfo(self.groupname)
        self.assertTrue(additional_info is None)

        satellite.add_group_roles(self.groupname, ['Manager'])
        info = satellite.getAllLocalRoles()[self.groupname]
        additional_info = self.portal.getLDAPGroupRolesInfo(self.groupname)
        zope_roles = set(info)
        naaya_roles = self._get_roles_from_additional_info(additional_info)
        self.assertTrue(len(zope_roles.symmetric_difference(naaya_roles)) == 0)

        satellite.remove_group_roles(self.groupname, ['Manager'])
        info = satellite.getAllLocalRoles().get(self.groupname, [])
        additional_info = self.portal.getLDAPGroupRolesInfo(self.groupname)
        zope_roles = set(info)
        naaya_roles = self._get_roles_from_additional_info(additional_info)
        self.assertTrue(len(zope_roles.symmetric_difference(naaya_roles)) == 0)

        self.browser_do_logout()

    def test_all_group_roles_info(self):
        self.browser_do_login('admin', '')
        satellite = self.portal.acl_satellite

        additional_info = self.portal.getLDAPGroupRolesInfo(self.groupname)
        self.assertTrue(additional_info is None)

        satellite.add_group_roles(self.groupname, ['Manager'])
        satellite.add_group_roles(self.groupname, ['Reader'])

        all_info = self.portal.getAllLDAPGroupRolesInfo()
        self.assertTrue(all_info.has_key(self.groupname))
        group_info = all_info[self.groupname]
        self.assertTrue(len(group_info) == 2)
        self.assertTrue(group_info[0]['roles'] == ['Manager'])
        self.assertTrue(group_info[0].has_key('date'))
        self.assertTrue(group_info[0]['user_granting_roles'] == 'admin')
        self.assertTrue(group_info[1]['roles'] == ['Reader'])
        self.assertTrue(group_info[1].has_key('date'))
        self.assertTrue(group_info[1]['user_granting_roles'] == 'admin')

        self.browser_do_logout()


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestNyRoleManager))
    return suite
