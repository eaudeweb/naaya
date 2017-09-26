import unittest


class GwPortalTest(unittest.TestCase):

    def test_create_portal_instance(self):
        from naaya.groupware.groupware_site import GroupwareSite
        portal = GroupwareSite('my-test-portal')
        self.assertEqual(portal.getId(), 'my-test-portal')
