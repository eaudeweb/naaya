import unittest


class EwPortalTest(unittest.TestCase):

    def test_create_portal_instance(self):
        from Products.EnviroWindows.EnviroWindowsSite import EnviroWindowsSite
        portal = EnviroWindowsSite('my-test-portal')
        self.assertEqual(portal.getId(), 'my-test-portal')
