import transaction
from unittest.mock import patch, Mock
from urllib.parse import urlencode

from AccessControl.Permissions import view
from AccessControl.Permission import Permission

from naaya.core import site_logging
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase


class AuthTestSetup(NaayaFunctionalTestCase):
    def setUp(self):
        super(AuthTestSetup, self).setUp()
        self.auth_tool = self.portal.getAuthenticationTool()

    def tearDown(self):
        del self.auth_tool
        super(AuthTestSetup, self).tearDown()

class BasicTests(AuthTestSetup):
    def test_user_CRUD(self):
        """ Create, Read, Update and Delete a User"""
        user_name = 'test2user'
        user_password = 'test-user-password'
        user_email = 'test@test-email.com'
        user_email2 = 'changed@test-user-email.com'

        #Create user
        self.auth_tool.manage_addUser(name=user_name,
                                      password=user_password,
                                      confirm=user_password,
                                      firstname=user_name,
                                      lastname=user_name,
                                      email=user_email)

        #Read user object
        user_obj = self.auth_tool.getUser(user_name)
        self.assertEqual(user_obj.name, user_name)

        #Update user
        self.auth_tool.manage_changeUser(name=user_name,
                                         password=user_password,
                                         confirm=user_password,
                                         email=user_email2,
                                         firstname=user_name,
                                         lastname=user_name)
        self.assertEqual(user_obj.email, user_email2)

        #Delete user
        self.auth_tool.manage_delUsers(names=[user_obj.name])
        self.assertEqual(self.auth_tool.getUser(user_name), None)

class UserAuthTestSetup(AuthTestSetup):
    def setUp(self):
        super(UserAuthTestSetup, self).setUp()
        self.user_name = 'test2user'
        self.user_password = 'test-user-password'
        self.user_email = 'test@test-email.com'

        #Create user
        self.auth_tool._doAddUser(name=self.user_name,
                                  password=self.user_password,
                                  roles=[],
                                  domains=[],
                                  firstname=self.user_name,
                                  lastname=self.user_name,
                                  email=self.user_email)

        #Read user object
        self.user_obj = self.auth_tool.getUser(self.user_name)

        transaction.commit()

    def tearDown(self):
        del self.user_obj

        #Delete user
        self.portal.acl_users._doDelUsers([self.user_name])

        del self.user_email
        del self.user_password
        del self.user_name

        transaction.commit()
        super(UserAuthTestSetup, self).tearDown()

class UserTests(UserAuthTestSetup):
    def test_portal_roles(self):
        roles = ['Administrator', 'Manager', 'Contributor']

        #Add user roles
        self.auth_tool.manage_addUsersRoles(name=self.user_obj.name,
                                            roles=roles)
        self.assertEqual(self.user_obj.roles, roles)

        #Revoke user roles
        self.auth_tool.manage_revokeUserRole(user=self.user_obj.name,
                                             location='')
        self.assertEqual(self.user_obj.roles, [])


class UserWithRolesTestSetup(UserAuthTestSetup):
    def setUp(self):
        super(UserWithRolesTestSetup, self).setUp()
        roles = ['Administrator', 'Manager', 'Contributor']
        self.auth_tool.manage_addUsersRoles(name=self.user_obj.name,
                                            roles=roles,
                                            location='')

        transaction.commit()

        self.browser_do_login(self.user_name, self.user_password)

    def tearDown(self):
        self.browser_do_logout()

        self.auth_tool.manage_revokeUserRole(user=self.user_obj.name,
                                             location='')
        transaction.commit()

        super(UserWithRolesTestSetup, self).tearDown()

class UserWithRolesTests(UserWithRolesTestSetup):
    def test_user_cant_view_site(self):
        portal_url = 'http://localhost/portal'

        self.browser.go(portal_url)
        self.assertEqual(portal_url, self.browser.get_url())

    def test_user_can_view_folder(self):
        folder_url = 'http://localhost/portal/info'

        self.browser.go(folder_url)
        self.assertEqual(folder_url, self.browser.get_url())


class UserWithRolesOnlyOnFolderTestSetup(UserAuthTestSetup):
    def setUp(self):
        super(UserWithRolesOnlyOnFolderTestSetup, self).setUp()

        # get&save roles with view
        view_perm = Permission(view, (), self.portal)
        self.site_roles_with_view = view_perm.getRoles()
        view_perm.setRoles(('Manager'))

        roles = ['Administrator', 'Manager', 'Contributor']
        self.auth_tool.manage_addUsersRoles(name=self.user_obj.name,
                                            roles=roles,
                                            location='/portal/info')

        transaction.commit()

        self.browser_do_login(self.user_name, self.user_password)

    def tearDown(self):
        self.browser_do_logout()

        self.auth_tool.manage_revokeUserRole(user=self.user_obj.name,
                                             location='/portal/info')

        # reset portal roles with view
        view_perm = Permission(view, (), self.portal)
        view_perm.setRoles(self.site_roles_with_view)

        transaction.commit()

        super(UserWithRolesOnlyOnFolderTestSetup, self).tearDown()

class UserWithRolesOnlyOnFolderTests(UserWithRolesOnlyOnFolderTestSetup):
    def test_user_cant_view_site(self):
        # In Zope 5, users are not redirected away from portal root even
        # when they only have roles on a subfolder.
        portal_url = 'http://localhost/portal'

        self.browser.go(portal_url)
        self.assertEqual(portal_url, self.browser.get_url())

    def test_user_can_view_folder(self):
        folder_url = 'http://localhost/portal/info'

        self.browser.go(folder_url)
        self.assertEqual(folder_url, self.browser.get_url())

class UserManagementLoggingTestSuite(UserWithRolesOnlyOnFolderTestSetup):

    def setUp(self):
        super(UserManagementLoggingTestSuite, self).setUp()
        self.site_logger = Mock()
        patcher = patch('naaya.core.site_logging.get_site_logger')
        self.patch_get_site_logger = patcher.start()
        self.patch_get_site_logger.return_value = self.site_logger
        self.browser_do_logout()
        self.browser_do_login('admin', '')

    def tearDown(self):
        self.browser_do_logout()
        self.patch_get_site_logger.stop()
        super(UserManagementLoggingTestSuite, self).tearDown()

    def test_assign_roles_new_location(self):
        """ test logging event of assigning new role in virgin location """
        roles = ['Contributor', 'Reviewer']
        # Call admin_addroles directly via URL instead of relying on form
        # submission which is fragile across Zope versions.  The test is
        # about the logging behaviour, not the HTML form.
        params = urlencode([('names', self.user_name),
                            ('roles', roles[0]),
                            ('roles', roles[1]),
                            ('location', '')])
        self.browser.go(
            'http://localhost/portal/admin_addroles?' + params)
        self.site_logger.info.assert_called_once_with(
            {
                'type': site_logging.USER_MAN,
                'who': 'admin',
                'whom': self.user_name,
                'action': 'ASSIGNED',
                'roles': roles,
                'content_path': '/portal',
            })
        # Clean up the portal-level roles added by this test (the browser
        # request auto-committed the change).
        self.auth_tool.manage_revokeUserRole(user=self.user_name, location='')
        transaction.commit()

    def test_assign_roles_existing_location(self):
        """ test logging event of overwriting roles in a location for a user """
        roles = ['Contributor', 'Reviewer']
        # Call admin_addroles directly via URL instead of relying on form
        # submission which is fragile across Zope versions.
        params = urlencode([('names', self.user_name),
                            ('roles', roles[0]),
                            ('roles', roles[1]),
                            ('location', 'info')])
        self.browser.go(
            'http://localhost/portal/admin_addroles?' + params)

        # The first call should be UNASSIGNED with the old roles.
        # Role ordering is non-deterministic in Python 3, so compare
        # with sorted roles.
        self.assertEqual(len(self.site_logger.info.call_args_list), 2)
        unassign_call = self.site_logger.info.call_args_list[0]
        unassign_data = unassign_call[0][0]
        self.assertEqual(unassign_data['type'], site_logging.USER_MAN)
        self.assertEqual(unassign_data['who'], 'admin')
        self.assertEqual(unassign_data['whom'], self.user_name)
        self.assertEqual(unassign_data['action'], 'UNASSIGNED')
        self.assertEqual(sorted(unassign_data['roles']),
                         sorted(['Contributor', 'Administrator', 'Manager']))
        self.assertEqual(unassign_data['content_path'], '/portal/info')

        # The second call should be ASSIGNED with the new roles.
        assign_call = self.site_logger.info.call_args_list[1]
        assign_data = assign_call[0][0]
        self.assertEqual(assign_data['type'], site_logging.USER_MAN)
        self.assertEqual(assign_data['who'], 'admin')
        self.assertEqual(assign_data['whom'], self.user_name)
        self.assertEqual(assign_data['action'], 'ASSIGNED')
        self.assertEqual(assign_data['roles'], roles)
        self.assertEqual(assign_data['content_path'], '/portal/info')
        # Restore original roles at /portal/info (the browser request
        # auto-committed the role change).
        self.auth_tool.manage_revokeUserRole(
            user=self.user_name, location='/portal/info')
        self.auth_tool.manage_addUsersRoles(
            name=self.user_name,
            roles=['Administrator', 'Manager', 'Contributor'],
            location='/portal/info')
        transaction.commit()

    def test_unassign_roles(self):
        """ test logging event of unassigning a role """
        expected_roles = sorted(['Contributor', 'Administrator', 'Manager'])
        original_roles = ['Administrator', 'Manager', 'Contributor']
        path_addressing = ['portal/info', '/portal/info', 'info']
        for loc in path_addressing:
            self.site_logger.reset_mock()
            self.browser.go(
                'http://localhost/portal/admin_revokerole?user=%s&location=%s'
                % (self.user_name, loc))
            self.site_logger.info.assert_called_once()
            actual = self.site_logger.info.call_args[0][0]
            self.assertEqual(actual['type'], site_logging.USER_MAN)
            self.assertEqual(actual['who'], 'admin')
            self.assertEqual(actual['whom'], self.user_name)
            self.assertEqual(actual['action'], 'UNASSIGNED')
            self.assertEqual(sorted(actual['roles']), expected_roles)
            self.assertEqual(actual['content_path'], '/portal/info')
            # The browser request committed the role revocation, so
            # re-assign the roles for the next iteration.
            self.auth_tool.manage_addUsersRoles(
                name=self.user_name, roles=original_roles,
                location='/portal/info')
            transaction.commit()
