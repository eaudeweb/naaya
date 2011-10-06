import unittest
from naaya.component import bundles
from naaya.component.testing import ITestUtil, MyClass, clean_up_bundle
from Products.Naaya.NySite import NySite
from NaayaFunctionalTestCase import NaayaFunctionalTestCase


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

class BundleFunctionalTest(NaayaFunctionalTestCase):
    """ Functional test cases for bundles """

    def test_set_bundle_by_privileged_users(self):
        """ Testing whether any type of users can set bundles """

        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/manage_bundle')
        self.failUnless('Access denied' in self.browser.get_html())
        self.browser_do_logout()

        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/manage_bundle')
        self.failUnless('Please enter the bundle to be set' in
                        self.browser.get_html())

        self.browser_do_logout()

    def test_set_bundle(self):
        """ """

        bundle_name = 'CHM Bundle'
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/manage_bundle')

        html = self.browser.get_html()
        self.assertTrue('<p>Please enter the bundle to be set</p>' in html)

        form = self.browser.get_form('set-bundle')
        expected_controls = set(['bundle'])
        found_controls = set(c.name for c in form.controls)
        self.assertTrue(expected_controls.issubset(found_controls))

        form['bundle'] = bundle_name
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless("Success!" in html)

        form = self.browser.get_form('set-bundle')
        current_bundle = form.get_value('bundle')
        self.assertEqual(current_bundle, bundle_name)

    def test_set_empty_bundle_name(self):
        """ Cannot set bundle with empty name for any site """

        bundle_name = ''
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/manage_bundle')

        html = self.browser.get_html()
        self.assertTrue('<p>Please enter the bundle to be set</p>' in html)

        form = self.browser.get_form('set-bundle')
        expected_controls = set(['bundle'])
        found_controls = set(c.name for c in form.controls)
        self.assertTrue(expected_controls.issubset(found_controls))

        form['bundle'] = bundle_name
        self.browser.submit()

        expected_output = 'Bundle name cannot be empty!'
        html = self.browser.get_html()
        self.failUnless(expected_output in html)

        self.browser_do_logout()

    def test_default_bundle(self):
        """ Default bundle name for Naaya sites should be Naaya"""

        default_bundle = 'Naaya'

        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/manage_bundle')
        form = self.browser.get_form('set-bundle')

        found_bundle = form['bundle']
        self.assertEqual(default_bundle, found_bundle)
