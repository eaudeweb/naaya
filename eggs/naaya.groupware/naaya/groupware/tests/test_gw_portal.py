import unittest

from naaya.groupware.tests import GWTestCase


class GwPortalTest(unittest.TestCase):

    def test_create_portal_instance(self):
        from naaya.groupware.groupware_site import GroupwareSite
        from naaya.groupware.constants import METATYPE_GROUPWARESITE
        portal = GroupwareSite('my-test-portal')
        self.assertEqual(portal.getId(), 'my-test-portal')
        self.assertEqual(portal.meta_type, METATYPE_GROUPWARESITE)


class RestrictedPortalTest(GWTestCase):

    def test_toggle_restricted(self):
        self.assertFalse(self.portal.portal_is_restricted)
        self.portal.toggle_portal_restricted(True)
        self.assertTrue(self.portal.portal_is_restricted)
        self.assertNotIn('Anonymous', self.portal._View_Permission)
        self.assertIn('Contributor', self.portal._View_Permission)
        self.portal.toggle_portal_restricted(False)
        self.assertFalse(self.portal.portal_is_restricted)
        self.assertIn('Anonymous', self.portal._View_Permission)

    def test_anonymous_access_when_restricted(self):
        nobody = self.app.acl_users._nobody
        self.assertEqual(self.portal.get_user_access(nobody), 'viewer')
        self.portal.toggle_portal_restricted(True)
        self.assertEqual(self.portal.get_user_access(nobody), 'restricted')

    def test_logout_html(self):
        from unittest.mock import Mock
        request = Mock()
        self.portal.logout_html(request)
        request.RESPONSE.redirect.assert_called_once_with(
            self.portal.absolute_url() + '/login/logout')
