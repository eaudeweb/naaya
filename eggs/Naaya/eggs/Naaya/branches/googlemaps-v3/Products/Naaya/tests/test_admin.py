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
