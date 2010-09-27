import sys
import os
import re
import optparse
import transaction
from Products.Naaya.tests.SeleniumTestCase import SeleniumTestCase

class NaayaUserManagementTest(SeleniumTestCase):
    def afterSetUp(self):
        self.login_user('admin', '')

    def test_add_user(self):
        self.selenium.open("/portal/admin_local_users_html", True)
        self.selenium.click("//input[@value='Add user']")
        self.selenium.wait_for_page_to_load("30000")
        self.selenium.type("firstname:utf8:ustring", 'Gheorghe')
        self.selenium.type("lastname:utf8:ustring", 'Popescu')
        self.selenium.type("email:utf8:ustring",
                           'Gheorghe_Popescu@example.com')
        self.selenium.type("name:utf8:ustring", 'ghita')
        self.selenium.type("password:utf8:ustring", 'parola')
        self.selenium.type("confirm:utf8:ustring", 'parola')
        self.selenium.click("//input[@value='Add']")
        self.selenium.wait_for_page_to_load("30000")
        assert self.selenium.is_text_present('Gheorghe Popescu')
        transaction.abort()
        assert self.portal.acl_users.getUser('ghita').name == 'ghita'

    def test_add_role(self):
        self.selenium.open("/portal/admin_addrole_html", True)
        self.selenium.type("//input[@id='input-role']", "SOMErOLE")
        self.selenium.click("//input[@value='Add role']")
        self.selenium.open("/portal/admin_roles_html?section=roles", True)
        assert self.selenium.is_text_present('SOMErOLE')
        self.selenium.open("/portal/admin_editrole_html?role=SOMErOLE", True)
        assert self.selenium.is_text_present('Edit permissions for SOMErOLE')

    def test_assign_role(self):
        "Assign a role"
        self.selenium.open("/portal/admin_roles_html?section=assign_roles",
                           True)
        self.selenium.add_selection("names", "label=user3")
        self.selenium.add_selection("//select[@name='roles']", 'Manager')
        self.selenium.click("//input[@value='Pick']")

        self.selenium.wait_for_pop_up("wwinn", "30000")
        self.selenium.select_window("name=wwinn")
        self.selenium.click("link=Information")
        self.selenium.select_window("null")

        self.selenium.click("//input[@value='Assign role']")
        self.selenium.wait_for_page_to_load("3000")
        #Check is the user has the assigned roles
        assert self.selenium.get_text(
            "//table[@class='datatable']/tbody/tr[last()]") ==\
            u'user3 Contributor Entire portal Manager Information'

    def test_delete_user(self):
        self.selenium.open("/portal/admin_users_html", True)
        #Check the last user checkbox
        self.selenium.click(
            "//div[@class='datatable']/table/tbody/tr[last()]/td/input")
        username = self.selenium.get_text(
            "//div[@class='datatable']/table/tbody/tr[last()]/td[2]")
        self.selenium.click("//input[@value='Delete user']")
        self.selenium.wait_for_page_to_load("30000")
        assert self.selenium.is_text_present(username) is False
