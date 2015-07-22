from mock import patch
from unittest import TestSuite, makeSuite
import transaction
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

class RoleTest(NaayaFunctionalTestCase):
    """ test admin role pages """

    def test_add_role(self):
        assert "CoolPeople" not in self.portal.acl_users.list_all_roles()

        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/admin_roles_html')
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

    @patch('Products.NaayaCore.AuthenticationTool.AuthenticationTool.get_zope_env')
    @patch('naaya.core.zope2util.get_zope_env')
    def test_mark_new_users(self, get_zope_env_atool, get_zope_env_zope2util):
        get_zope_env_atool.return_value = 'noteionet'
        get_zope_env_zope2util.return_value = 'noteionet'
        p = self.portal

        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/admin_assignroles_html')

        assert ("Assign roles to local users" in self.browser.get_html())
        assert ("User One (user1) *" in self.browser.get_html())

        self.browser_do_logout()

    @patch('Products.NaayaCore.AuthenticationTool.AuthenticationTool.get_zope_env')
    @patch('naaya.core.zope2util.get_zope_env')
    def test_mark_new_users_off(self, get_zope_env_atool, get_zope_env_zope2util):
        get_zope_env_atool.return_value = 'eionet'
        get_zope_env_zope2util.return_value = 'eionet'
        p = self.portal

        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/admin_assignroles_html')

        assert ("Assign roles to local users" in self.browser.get_html())
        assert ("User One (user1) *" not in self.browser.get_html())

        self.browser_do_logout()
