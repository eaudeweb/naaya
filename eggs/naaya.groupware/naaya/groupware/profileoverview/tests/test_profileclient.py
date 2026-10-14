import unittest
from unittest.mock import patch

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from naaya.groupware.groupware_site import manage_addGroupwareSite

from naaya.groupware.profileoverview.profile import ProfileClient


def common_setup(zope_app):
    zope_app.acl_users._doAddUser('nick', 'nick', [], '')

class InterestGroupsTestCase(NaayaTestCase):

    def setUp(self):
        super(InterestGroupsTestCase, self).setUp()
        common_setup(self.app)
        manage_addGroupwareSite(self.app, 'ig1', 'ig1')
        manage_addGroupwareSite(self.app, 'ig2', 'ig2')
        manage_addGroupwareSite(self.app, 'ig3', 'ig3')

    @patch('naaya.groupware.profileoverview.profile.agent_from_uf')
    def test_igaccess(self, mock_get_agent):
        client = ProfileClient(self.app, self.app.acl_users.getUser('nick'))
        ac = client.access_in_igs()
        self.assertEqual(set(ac.keys()), set(['viewer']))
        self.assertEqual(len(ac['viewer']), 3)


class ProfileViewAnonymousTest(unittest.TestCase):

    def test_anonymous_redirects_to_login(self):
        from unittest.mock import MagicMock
        from naaya.groupware.profileoverview.profile import ProfileView
        request = MagicMock()
        request.get.return_value.has_role.return_value = False
        request.form = {'user': 'anne'}
        self.assertIsNone(ProfileView(MagicMock(), request))
        url = request.response.redirect.call_args[0][0]
        self.assertEqual(url, '/login/login_form?came_from='
                              '%2Fprofile_overview%3Fuser%3Danne')
