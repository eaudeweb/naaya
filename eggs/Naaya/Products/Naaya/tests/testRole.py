from unittest import TestSuite, makeSuite

import transaction
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

class RoleTest(NaayaFunctionalTestCase):
    """ test admin role pages """

    def test_add_role(self):
        assert "CoolPeople" not in self.portal.acl_users.list_all_roles()

        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/admin_addrole_html')
        form = self.browser.get_form('addrole')
        form['role'] = "CoolPeople"
        self.browser.clicked(form, self.browser.get_form_field(form, 'role'))
        self.browser.submit()

        assert "CoolPeople" in self.portal.acl_users.list_all_roles()

        # clean up
        p = self.portal
        p.__ac_roles__ = tuple(set(p.__ac_roles__) - set(["CoolPeople"]))
        transaction.commit()

        self.browser_do_logout()

    def test_change_role_permissions(self):
        p = self.portal
        orig_perm = (p._Naaya___Add_Naaya_URL_objects_Permission,
                     p._Naaya___Edit_content_Permission)

        assert 'Contributor' in p._Naaya___Add_Naaya_URL_objects_Permission
        assert 'Contributor' not in p._Naaya___Edit_content_Permission

        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/admin_editrole_html?'
                        'role=Contributor')

        assert ("Edit permissions for <i>Contributor</i>" in
                self.browser.get_html())

        form = self.browser.get_form('editRole')
        selected = set(form['zope_perm_list:list'])
        assert 'Naaya - Add Naaya URL objects' in selected
        assert 'Naaya - Translate pages' not in selected
        selected.remove('Naaya - Add Naaya URL objects')
        selected.add('Naaya - Edit content')
        form['zope_perm_list:list'] = list(selected)
        self.browser.clicked(form, self.browser.get_form_field(form,
                                        'zope_perm_list:list'))
        self.browser.submit()

        assert 'Contributor' not in p._Naaya___Add_Naaya_URL_objects_Permission
        assert 'Contributor' in p._Naaya___Edit_content_Permission

        self.browser_do_logout()

        (p._Naaya___Add_Naaya_URL_objects_Permission,
         p._Naaya___Edit_content_Permission) = orig_perm


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(RoleTest))
    return suite
