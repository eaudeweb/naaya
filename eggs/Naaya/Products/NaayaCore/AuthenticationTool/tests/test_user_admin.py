import csv
from io import BytesIO, StringIO

import transaction

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.NaayaCore.AuthenticationTool.AuthenticationTool import \
    ValidationError


class UserAdminTest(NaayaTestCase):

    def afterSetUp(self):
        self.acl_users = self.portal.acl_users

    def test_delete_unknown_user(self):
        self.acl_users._doAddUser('gone', 'pw', [], [], 'G', 'One',
                                  'gone@example.com')
        self.acl_users.manage_delUsers(['gone', 'no-such-user'])
        self.assertNotIn('gone', self.acl_users.getUserNames())

    def test_confirm_user(self):
        key = self.acl_users._doAddTempUser(
            name='newbie', password='pw', roles=[], domains=[],
            firstname='New', lastname='Bie', email='newbie@example.com')
        self.assertRaises(ValidationError, self.acl_users.manage_confirmUser,
                          'bogus-key')
        self.acl_users.manage_confirmUser(key)
        self.assertEqual(self.acl_users.getUser('newbie').email,
                         'newbie@example.com')
        self.assertRaises(ValidationError, self.acl_users.manage_confirmUser,
                          key)

    def test_search_users(self):
        found = self.acl_users.search_users('contrib', all_users=False)
        self.assertEqual([u.user_id for u in found], ['contributor'])
        self.assertEqual(self.acl_users.searchUsers('contrib@example'),
                         (1, [('contributor', 'Contributor Test',
                               'contrib@example.com')]))
        self.assertEqual(self.acl_users.searchUsers('example.com', limit=1),
                         (0, []))
        self.assertEqual(self.acl_users.searchUsers(''), (2, []))

    def test_users_with_roles(self):
        self.acl_users.manage_addUsersRoles('user1', ['Contributor'],
                                            location='info')
        with_roles = self.acl_users.getUsersWithRoles()
        self.assertIn((['Contributor'], 'info'), with_roles['user1'])
        self.acl_users._doAddUser('noroles', 'pw', [], [], 'N', 'R',
                                  'noroles@example.com')
        self.assertNotIn('noroles', self.acl_users.getUsersWithRoles())

    def test_revoke_searched_roles(self):
        info = self.portal.info
        info.manage_setLocalRoles('user1', ['Contributor', 'Reviewer'])
        info.manage_setLocalRoles('user2', ['Contributor'])
        self.acl_users.revoke_searched_roles(['user1', 'user2'],
                                            'Contributor', '_all_')
        self.assertEqual(info.get_local_roles_for_userid('user1'),
                         ('Reviewer',))
        self.assertEqual(info.get_local_roles_for_userid('user2'), ())

    def import_users(self, rows):
        output = StringIO()
        csv.writer(output).writerows(rows)
        self.acl_users.manage_importUsers(
            BytesIO(output.getvalue().encode('utf-8')))

    def test_import_users(self):
        header = ['name', 'firstname', 'lastname', 'email', 'password',
                  'roles']
        self.import_users([header,
                           ['New User', 'ann', 'smith', 'Ann@Example.com',
                            'pw', 'Contributor']])
        user = self.acl_users.getUser('new.user')
        self.assertEqual((user.firstname, user.lastname, user.email),
                         ('Ann', 'Smith', 'ann@example.com'))
        self.assertEqual(user.roles, ['Contributor'])

        self.acl_users._doAddUser('Mixed', 'pw', [], [], 'M', 'X',
                                  'mixed@example.com')
        self.import_users([header,
                           ['mixed', 'a', 'b', 'other@example.com', 'pw', ''],
                           ['dupmail', 'a', 'b', 'ann@example.com', 'pw', ''],
                           ['bad name!', 'a', 'b', 'c@example.com', 'pw', '']])
        self.assertNotIn('mixed', self.acl_users.getUserNames())
        self.assertNotIn('dupmail', self.acl_users.getUserNames())
        self.assertEqual(len(self.acl_users.getUserNames()),
                         len(set(self.acl_users.getUserNames())))


class DownloadUsersTest(NaayaFunctionalTestCase):

    def test_download_users_csv(self):
        self.portal.info.manage_setLocalRoles('user1', ['Contributor'])
        transaction.commit()
        url = 'http://localhost/portal/acl_users/downloadUsersCsv'
        self.browser.go(url)
        self.assertAccessDenied()

        self.browser_do_login('admin', '')
        self.browser.go(url)
        self.assertEqual(self.browser.get_code(), 200)
        rows = list(csv.reader(StringIO(self.browser.get_html())))
        self.assertEqual(rows[0][0], 'Username')
        self.assertIn('user1', [row[0] for row in rows[1:]])
        self.browser_do_logout()
