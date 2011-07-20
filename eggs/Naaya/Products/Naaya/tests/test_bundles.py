import unittest
from naaya.component import bundles
from naaya.component.testing import ITestUtil, MyClass, clean_up_bundle
from Products.Naaya.NySite import NySite


class BundlePortalTest(unittest.TestCase):

    def setUp(self):
        self.bundle_names = []

    def tearDown(self):
        for name in self.bundle_names:
            clean_up_bundle(name)

    def test_set_bundle(self):
        self.bundle_names.append('bundle-for-portal-test')
        bundle = bundles.get('bundle-for-portal-test')
        portal = NySite('portal')
        portal.set_bundle(bundle)
        ob = MyClass()
        bundle.registerUtility(ob)
        portal_site_manager = portal.getSiteManager()
        self.assertTrue(portal_site_manager.getUtility(ITestUtil) is ob)
