from naaya.groupware.tests import GWFunctionalTestCase


class TraversalErrorPageTest(GWFunctionalTestCase):
    """ The groupware standard_template reads request.AUTHENTICATED_USER """

    def test_not_found_under_manage_add_product(self):
        self.browser.go(self.portal.absolute_url() +
                        '/manage_addProduct/Naaya/no_such_thing')
        self.assertEqual(self.browser.get_code(), 404)
        html = self.browser.get_html()
        self.assertNotIn('Error displaying the error page', html)
        self.assertIn('id="breadcrumbtrail"', html)
        self.assertIn('<h1>Error page</h1>', html)
