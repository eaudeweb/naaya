import sys
import os
import re
import optparse
from Products.Naaya.tests.SeleniumTestCase import SeleniumTestCase

user_data = {
    'fname': 'Gheorghe',
    'lname': 'Popescu',
    'email': 'Gheorghe_Popescu@example.com',
    'user': 'ghita',
    'password': 'parolaluighita',
}
role_data = {
    'folder': '',
    'role': 'Contributor',
    'email_notification': True,
}


class NaayaUserManagementTest(SeleniumTestCase):
        #This test verifies the next features:
        #1. adding a new role
        #2. adding a new user
        #3. assigning a role
        #4. deleting an user

    def selenium_initialize(self):
        selen = self.selenium
        self.login_user('admin', '')

    def test_user_management(self):
        self.selenium_initialize()
        selen = self.selenium
        selen.open("/portal/admin_users_html", True)

        role = 'JackOfAll'
        self.selenium_add_role(role)
        self.assertFalse(selen.is_text_present('Error'),
                       'Some data crashed adding a new role')
        self.selenium_add_user(user_data)
        self.assertFalse(selen.is_text_present('Error'),
                       'Some data crashed introducing a user')
        self.selenium_assign_role(role_data, user_data)
        self.assertFalse(selen.is_text_present('Error'),
                       'Some data crashed assigning a role')
        #self.selenium_delete_user()
        #self.assertFalse(selen.is_text_present('Error'),
        #               'Some data crashed deleting a user')

    def selenium_add_user(self, user_data):
        selen.open("/portal/admin_users_html", True)
        selen = self.selenium
        selen.click("//input[@value='Add user']")
        selen.wait_for_page_to_load("30000")

        selen.type("firstname", user_data['fname'])
        selen.type("lastname", user_data['lname'])
        selen.type("email", user_data['email'])
        selen.type("name", user_data['user'])
        selen.type("password", user_data['password'])
        selen.type("confirm", user_data['password'])
        selen.click("//input[@value='Add']")
        selen.wait_for_page_to_load("30000")

    def selenium_add_role(self, role):
        selen = self.selenium
        selen.open("/portal/admin_addrole_html", True)

        selen.type("role", role)
        selen.click("//input[@value='Add role']")
        selen.wait_for_page_to_load("30000")

    def selenium_assign_role(self, role_data, user_data):
        selen = self.selenium
        selen.open("/portal/admin_roles_html", True)

        selen.add_selection("names", "label=%s" % user_data['user'])
        selen.add_selection("//select[@name='roles']", role_data['role'])
        if role_data['folder']:
            selen.click("//input[@value='Pick']")
            selen.wait_for_pop_up("wwinn", "30000")
            selen.select_window("name=wwinn")
            selen.click("link=%s" % role_data['folder'])
            selen.select_window("null")
        if role_data['email_notification']:
            selen.click("send_mail")
        selen.click("//input[@value='Assign role']")
        selen.wait_for_page_to_load("3000")

    def selenium_delete_user(self):
        selen = self.selenium
        selen.open("/portal/admin_users_html", True)
        i = 0
        import pdb; pdb.set_trace()
        while True:
            i += 1
            if selen.is_element_present\
            ("//div[4]/form/table/tbody/tr[%d]/td[2]/a[text()='%s']"
             % (i, user_data['user'])):
                selen.check("//div[4]/form/table/tbody/tr[%d]/td/input" %i)
                break
        selen.click("//input[@value='Delete user']")
        selen.wait_for_page_to_load("30000")
        self.assertFalse(selen.is_text_present(user_data['user']))