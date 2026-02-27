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
