import transaction
from AccessControl.Permissions import view
from AccessControl.Permission import Permission

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
        portal_url = 'http://localhost/portal'

        self.browser.go(portal_url)
        self.assertNotEqual(portal_url, self.browser.get_url())

    def test_user_can_view_folder(self):
        folder_url = 'http://localhost/portal/info'

        self.browser.go(folder_url)
        self.assertEqual(folder_url, self.browser.get_url())

