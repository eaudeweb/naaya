from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase


class TestUserAdmin(NaayaFunctionalTestCase):
    """ Testing admin views, handled by methods of NySite """

    def test_setting_permissions_on_role(self):
        """ set a permission, then reset permissions """
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/admin_editrole_html?role=Authenticated')
        form = self.browser.get_form('editRole')
        field = form['zope_perm_list:list']
        initial = set(field)
        form['zope_perm_list:list'] = ['View']
        self.browser.clicked(form, field)
        self.browser.submit()
        self.browser.go('http://localhost/portal/admin_editrole_html?role=Authenticated')
        form = self.browser.get_form('editRole')
        field = form['zope_perm_list:list']
        self.assertEqual(set(field), set(['View']))
        self.browser.go('http://localhost/portal/admin_resetrole_html?role=Authenticated')
        form = self.browser.get_form('editRole')
        field = form['zope_perm_list:list']
        self.assertEqual(set(field), initial)

    def test_reset_role_without_security_in_skel(self):
        """ sites whose own skel has no <security> (EnviroWindows) reset from the Naaya skel """
        from unittest import mock
        site_class = type(self.portal.aq_base)
        original = site_class.get_skel_handler
        calls = []

        def get_skel_handler(site, product_path, enable_cache=True):
            calls.append(product_path)
            if len(calls) == 1:
                return mock.Mock(root=mock.Mock(security=None))
            return original(site, product_path, enable_cache)

        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/admin_editrole_html?role=Authenticated')
        initial = set(self.browser.get_form('editRole')['zope_perm_list:list'])
        with mock.patch.object(site_class, 'get_skel_handler', get_skel_handler):
            self.browser.go('http://localhost/portal/admin_resetrole_html?role=Authenticated')
        self.assertEqual(len(calls), 2)
        field = self.browser.get_form('editRole')['zope_perm_list:list']
        self.assertEqual(set(field), initial)
