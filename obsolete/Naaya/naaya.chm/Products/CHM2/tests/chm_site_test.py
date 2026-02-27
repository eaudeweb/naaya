import unittest


class ChmPortalTest(unittest.TestCase):

    def test_create_portal_instance(self):
        from Products.CHM2.CHMSite import CHMSite
        portal = CHMSite('my-test-portal')
        self.assertEqual(portal.getId(), 'my-test-portal')
