import re
from time import sleep
import transaction
from Products.Naaya.tests.SeleniumTestCase import SeleniumTestCase
from Products.NaayaCore.AuthenticationTool.tests.test_auth_unit import \
                                                            LDAPBaseUnitTest
class NaayaUserManagementTest(SeleniumTestCase, LDAPBaseUnitTest):
    def afterSetUp(self):
        LDAPBaseUnitTest.afterSetUp(self)
        self.login_user('admin', 'mypass')

    def test_add_user(self):
        self.selenium.open("/portal/admin_adduser_html", True)
        self.selenium.type("firstname:utf8:ustring", 'Gheorghe')
        self.selenium.type("lastname:utf8:ustring", 'Popescu')
        self.selenium.type("email:utf8:ustring",
                           'Gheorghe_Popescu@example.com')
        self.selenium.type("name:utf8:ustring", 'ghita')
        self.selenium.type("password:utf8:ustring", 'parola')
        self.selenium.type("confirm:utf8:ustring", 'parola')
        self.selenium.click('//input[@type="submit"]')
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present('Gheorghe Popescu')
        transaction.abort()
        assert self.portal.acl_users.getUser('ghita').name == 'ghita'

        self.selenium.open("/portal/admin_adduser_html", True)
        self.selenium.click('//input[@type="submit"]')
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present('The first name must be specified')

        self.selenium.type("firstname:utf8:ustring", 'Gheorghe')
        self.selenium.type("lastname:utf8:ustring", 'Popescu')
        self.selenium.type("email:utf8:ustring",
                           'broken')
        self.selenium.type("name:utf8:ustring", 'ghita')
        self.selenium.type("password:utf8:ustring", 'parola')
        self.selenium.type("confirm:utf8:ustring", 'parola')
        self.selenium.click('//input[@type="submit"]')
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present('Invalid email address.')

        self.selenium.type("firstname:utf8:ustring", 'Gheorghe')
        self.selenium.type("lastname:utf8:ustring", 'Popescu')
        self.selenium.type("email:utf8:ustring",
                           'mail@mail.com')
        self.selenium.type("name:utf8:ustring", 'ghita')
        self.selenium.type("password:utf8:ustring", 'parola')
        self.selenium.type("confirm:utf8:ustring", 'parola')
        self.selenium.click('//input[@type="submit"]')
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present('Username ghita already in use')

        self.selenium.type("firstname:utf8:ustring", 'Gheorghe')
        self.selenium.type("lastname:utf8:ustring", 'Popescu')
        self.selenium.type("email:utf8:ustring",
                           'mail@mail.com')
        self.selenium.type("name:utf8:ustring", 'ghita1')
        self.selenium.type("password:utf8:ustring", 'parola')
        self.selenium.type("confirm:utf8:ustring", 'parola1')
        self.selenium.click('//input[@type="submit"]')
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present(
            'Password and confirmation do not match')


    def test_edit_user(self):
        #Change the firstname of the contributor user and save
        self.selenium.open("/portal/admin_edituser_html?name=contributor",
                           True)
        self.selenium.type('//input[@name="lastname:utf8:ustring"]', 'Lastname')
        self.selenium.click('//input[@type="submit"]')
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        self.selenium.open("/portal/admin_edituser_html?name=contributor",
                           True)
        assert self.selenium.get_value(
            '//input[@name="lastname:utf8:ustring"]') == u'Lastname'

        #Empty form
        self.selenium.type("firstname:utf8:ustring", '')
        self.selenium.type("lastname:utf8:ustring", '')
        self.selenium.type("email:utf8:ustring", '')
        self.selenium.type("password:utf8:ustring", '')
        self.selenium.type("confirm:utf8:ustring", '')
        self.selenium.click('//input[@type="submit"]')
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present('The first name must be specified')

        #Check e-mail validation
        email = self.selenium.get_value('//input[@name="email:utf8:ustring"]')
        self.selenium.type('//input[@name="email:utf8:ustring"]', 'broken_email')
        self.selenium.click('//input[@type="submit"]')
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.get_value(
            '//input[@name="email:utf8:ustring"]') == email
        assert self.selenium.is_text_present('Invalid email address.')

        self.selenium.type('//input[@name="email:utf8:ustring"]',
                           'reviewer@example.com')
        self.selenium.click('//input[@type="submit"]')
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present(
        'A user with the specified email already exists, username reviewer')

        self.selenium.type("password:utf8:ustring", 'parola')
        self.selenium.type("confirm:utf8:ustring", 'parola1')
        self.selenium.click('//input[@type="submit"]')
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present(
            'Password and confirmation do not match')

    def test_delete_user(self):
        self.selenium.open("/portal/admin_local_users_html", True)
        #Check the last user checkbox
        last_row = "//table[contains(@class, 'datatable')]/tbody/tr[last()]"
        self.selenium.click("%s/td/input" % last_row)
        username = self.selenium.get_text("%s/td[2]" % last_row)
        self.selenium.click("css=.deluser")
        assert re.search(r"^Are you sure[\s\S]$",
                         self.selenium.get_confirmation())
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present(username) is False

    def test_search_local_users(self):
        """Search users using jquery ui autocomplete and normal search using
        form

        """
        def check_result(user):
            "Check if the user is alone in the result list"
            #Also check if the the results are right
            assert self.selenium.get_text(\
                "//table[contains(@class, 'datatable')]/tbody/tr[last()]//td[2]") ==\
            user
        #Text search contributor string
        self.selenium.open("/portal/admin_local_users_html", True)
        self.selenium.type('id=autocomplete-query', 'contributor')
        self.selenium.click('//input[@value="Search"]')
        self.selenium.wait_for_condition('window.selenium_ready == true',
                                         self._selenium_page_timeout)
        check_result(u'contributor')

        #Empty string search
        self.selenium.type('id=autocomplete-query', '')
        self.selenium.click('//input[@value="Search"]')
        self.selenium.wait_for_condition('window.selenium_ready == true',
                                         self._selenium_page_timeout)
        assert int(self.selenium.\
            get_xpath_count('//table[contains(@class, "datatable")]/tbody/tr')) > 2

        #Filtering by Manager role
        self.selenium.select("id=filter-roles", 'Manager')
        self.selenium.click('//input[@value="Search"]')
        self.selenium.wait_for_condition('window.selenium_ready == true',
                                         self._selenium_page_timeout)
        check_result(u'test_user_1_')

        #Check filtering by role combined with text search
        self.selenium.type('id=autocomplete-query', 'contrib')
        self.selenium.select("id=filter-roles", 'Contributor')
        self.selenium.click('//input[@value="Search"]')
        self.selenium.wait_for_condition('window.selenium_ready == true',
                                         self._selenium_page_timeout)
        check_result(u'contributor')

    def test_add_role(self):
        self.selenium.open("/portal/admin_roles_html", True)
        self.selenium.type("//input[@id='input-role']", "SOMErOLE")
        self.selenium.click("//input[@value='Add']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present('SOMErOLE')
        self.selenium.open("/portal/admin_editrole_html?role=SOMErOLE", True)
        assert self.selenium.is_text_present('Edit permissions for SOMErOLE')

    def test_edit_role(self):
        self.selenium.open("/portal/admin_editrole_html?role=Administrator",
                           True)
        self.selenium.click('id=inperm-1')
        self.selenium.click('id=inperm-2')
        self.selenium.click('//form/input[@type="submit"]')
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        self.selenium.open("/portal/admin_editrole_html?role=Administrator",
                           True)
        assert self.selenium.get_value('id=inperm-1') == u'off'
        assert self.selenium.get_value('id=inperm-2') == u'off'

    def test_assign_role(self):
        """Assign a role
        XXX: Do the jstree click
        """
        self.selenium.open("/portal/admin_assignroles_html", True)
        self.selenium.add_selection("names", "label=User Three (user3)")
        self.selenium.add_selection("//select[@name='roles']", 'Manager')
        self.selenium.type('location', "info")
        self.selenium.click("send_mail")
        self.selenium.click("//input[@value='Assign role']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)

        self.selenium.open("/portal/admin_local_users_html", True)
        #Check is the user has the assigned roles.
        last_row = "//table[contains(@class, 'datatable')]/tbody/tr[last()]"
        assert self.selenium.get_text('%s/td[2]' % last_row) == u'user3'
        assert (self.selenium.get_text("%s/td/div[@class='user-role'][1]" %
                                      last_row).replace("\n", '')
                == u'Contributor in portal')
        assert (self.selenium.get_text("%s/td/div[@class='user-role'][2]" %
                                      last_row).replace("\n", '')
                == u'Manager in Information')

    def test_revoke_role(self):
        "Revoke Contributor to user3"
        self.selenium.open("/portal/admin_local_users_html", True)
        last_row = "//table[contains(@class, 'datatable')]/tbody/tr[last()]"
        assert self.selenium.get_text('%s/td[2]' % last_row) == u'user3'
        self.selenium.click("%s/td/div[@class='user-role-revoke']/a" % last_row)
        assert re.search(r"^Are you sure[\s\S]$",
                         self.selenium.get_confirmation())
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.get_text('%s/td[last()]' % last_row) == u''
