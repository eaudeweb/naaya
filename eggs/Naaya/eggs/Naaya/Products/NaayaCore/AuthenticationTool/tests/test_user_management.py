from unittest import TestSuite, makeSuite
from Products.Naaya.tests import NaayaTestCase

class NaayaUserManagementTests(NaayaTestCase.NaayaTestCase):
    def afterSetUp(self):
        self.login()

    def beforeTearDown(self):
        self.logout()

    def test_userManagement(self):
        """ Add, Find, Edit and Delete a User"""
        usr_name = 'test2user'
        usr_pwd = 'test-user-password'
        usr_mail = 'test@test-email.com'

        #Add user.
        self._portal().getAuthenticationTool().manage_addUser(name=usr_name,
                    password=usr_pwd, confirm=usr_pwd, firstname=usr_name,
                    lastname=usr_name, email=usr_mail)

        #get user object
        usr_obj = self._portal().getAuthenticationTool().getUser(usr_name)
        self.assertEqual(usr_obj.name, usr_name)

        #change user email
        self._portal().getAuthenticationTool().manage_changeUser(name=usr_name,
                        password=usr_pwd, confirm=usr_pwd,
                        email='changed@test-user-email.com',
                        firstname=usr_name, lastname=usr_name)
        self.assertEqual(usr_obj.email, 'changed@test-user-email.com')

        #add user roles
        self._portal().getAuthenticationTool().manage_addUsersRoles(
            name=usr_obj.name,
            roles=['Administrator', 'Manager', 'Contributor'])
        self.assertEqual(usr_obj.roles, ['Administrator', 'Manager',
                                         'Contributor'])

        #revoke user roles
        self._portal().getAuthenticationTool().manage_revokeUserRole(
            user=usr_obj.name, location='')
        self.assertEqual(usr_obj.roles, [])

        #delete user
        self._portal().getAuthenticationTool().manage_delUsers(
            names=[usr_obj.name])
        self.assertEqual(self._portal().getAuthenticationTool().getUser(
                                                            usr_name), None)

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NaayaUserManagementTests))
    return suite
