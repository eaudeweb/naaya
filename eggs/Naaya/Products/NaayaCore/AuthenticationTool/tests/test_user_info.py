from copy import copy
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase

USER_INFO_FIXTURE = {
    'user_id': '',
    'first_name': u"",
    'last_name': u"",
    'full_name': u"",
    'email': u"",
    'organisation': u"",
    '_get_zope_user': lambda: None,
    '_source': None,
}

class UserInfoTest(NaayaTestCase):
    def test_valid_user_info(self):
        from Products.NaayaCore.AuthenticationTool.AuthenticationTool \
                import UserInfo

        try:
            UserInfo(**USER_INFO_FIXTURE)
        except Exception as e:
            self.fail("Exception raised: %r (%s)" % (e, e))

    def test_mandatory_fields(self):
        from Products.NaayaCore.AuthenticationTool.AuthenticationTool \
                import UserInfo

        # blank
        self.assertRaises(AssertionError, UserInfo)

        missing_firstname = copy(USER_INFO_FIXTURE)
        del missing_firstname['first_name']
        self.assertRaises(AssertionError, UserInfo, **missing_firstname)

        missing_email = copy(USER_INFO_FIXTURE)
        del missing_email['email']
        self.assertRaises(AssertionError, UserInfo, **missing_email)

    # test_field_types removed: tested Python 2 str/unicode distinction
    # that doesn't exist in Python 3 (str IS unicode)

    def test_user_info_from_user(self):
        user_info = self.portal.acl_users.get_local_user_info('contributor')
        self.assertEqual(user_info.user_id, 'contributor')
        self.assertEqual(user_info.first_name, "Contributor")
        self.assertEqual(user_info.last_name, "Test")
        self.assertEqual(user_info.full_name, "Contributor Test")
        self.assertEqual(user_info.email, "contrib@example.com")
        self.assertEqual(user_info._source, self.portal.acl_users)
        user_ob = self.portal.acl_users.getUser('contributor')
        self.assertEqual(user_info._get_zope_user(), user_ob)

    def test_user_info_any_source(self):
        acl_users = self.portal.acl_users

        local_user_info = acl_users.get_user_info('contributor')
        self.assertEqual(local_user_info.full_name, "Contributor Test")
        self.assertEqual(local_user_info._source, acl_users)

        self.assertRaises(KeyError, acl_users.get_user_info, 'blah')

    def test_user_info_from_ldap_user(self):
        from unittest.mock import Mock
        try:
            from Products.LDAPUserFolder.LDAPUser import LDAPUser
        except ImportError:
            self.skipTest('Products.LDAPUserFolder is not installed')
        from Products.NaayaCore.AuthenticationTool.plugins.plugLDAPUserFolder \
                import user_info_from_zope_user

        dn = 'uid=anne,ou=Users,o=EIONET,l=Europe'
        attrs = {'cn': [b'Anne Tester'], 'givenName': [b'Anne'],
                 'sn': [b'Tester'], 'mail': [b'anne@example.com'],
                 'o': [b'K\xc3\xb8benhavn club']}
        user = LDAPUser('anne', 'anne', '', [], [], dn, attrs, [])
        info = user_info_from_zope_user(Mock(), user, 'utf-8')
        self.assertEqual(info.user_id, 'anne')
        self.assertEqual(info.full_name, 'Anne Tester')
        self.assertEqual(info.first_name, 'Anne')
        self.assertEqual(info.last_name, 'Tester')
        self.assertEqual(info.email, 'anne@example.com')
        self.assertEqual(info.organisation, 'K\xf8benhavn club')
        self.assertEqual(info.dn, dn)


class UserEmailTest(NaayaTestCase):

    def test_user_email(self):
        from AccessControl.users import User
        auth_tool = self.portal.getAuthenticationTool()
        user = User('root', 'pw', ['Manager'], [])
        # Zope root users have no email
        self.assertEqual(auth_tool.getUserEmail(user), '')
        user.mail = 'root@example.com'
        self.assertEqual(auth_tool.getUserEmail(user), 'root@example.com')
        user.email = 'other@example.com'
        self.assertEqual(auth_tool.getUserEmail(user), 'other@example.com')
