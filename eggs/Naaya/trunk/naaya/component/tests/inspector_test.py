from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from naaya.component import bundles
from naaya.component.testing import MyClass, ITestUtil
import transaction

class InspectorViewTestCase(NaayaFunctionalTestCase):
    """ Functional tests for inspector navigation """
    def afterSetUp(self):
        self.browser_do_login('admin', '')

    def test_view_inspector(self):
        """ Display the page. Make sure all the elements are there.
        Make sure the tab is there

        """
        self.browser.go(self.portal.absolute_url() + '/inspector_view')
        self.assertTrue('<select name="interface">' in self.browser.get_html())

    def test_registered_templates(self):
        """ View registered ITemplate utilities """
        self.browser.go(self.portal.absolute_url() +
                '/inspector_view?interface=ITemplate')
        self.assertTrue('<span class="utility_name">site_index</span>' in
                self.browser.get_html())

    def test_modified_utilities(self):
        """ Check that templates registered in component registries show up """
        lsm = self.portal.getSiteManager()
        lsm.registerUtility(MyClass, ITestUtil, 'test_utility')
        transaction.commit()

        naaya_bundle = bundles.get("Naaya")
        naaya_bundle.registerUtility(MyClass, ITestUtil, 'test_utility')
        self.browser.go(self.portal.absolute_url() +
                '/inspector_view?interface=ITestUtil')
        self.assertEqual(self.browser.get_html().count('title="provides"'), 2)

    def test_permission(self):
        """ Make sure anonymous users can't get in. """
        self.browser_do_logout()
        self.browser.go(self.portal.absolute_url() + '/inspector_view')
        self.assertTrue('Login' in self.browser.get_html())

