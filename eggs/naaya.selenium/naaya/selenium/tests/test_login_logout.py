from Products.Naaya.tests.SeleniumTestCase import SeleniumTestCase

class LoginLogout(SeleniumTestCase):
    def load_login_page(self):
        self.selenium.open("/portal/login_html", True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        self.assertTrue(self.selenium.is_element_present("__ac_name"))
        self.assertTrue(self.selenium.is_element_present("__ac_password"))

    def test_login_admin(self):
        self.load_login_page()

        self.selenium.type("__ac_name", 'admin')
        self.selenium.type("__ac_password", '')
        self.selenium.click("submit")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)

        self.assertFalse(self.selenium.is_element_present("__ac_name"))
        self.assertFalse(self.selenium.is_element_present("__ac_password"))
        self.assertTrue(self.selenium.is_element_present("link=Logout"))

    def test_logout_admin(self):
        self.login_user(user='admin', password='')
        self.selenium.open("/portal/login_html", True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)

        self.assertTrue(self.selenium.is_element_present("link=Logout"))
        self.selenium.click("link=Logout")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)

        self.assertTrue(self.selenium.is_element_present("__ac_name"))
        self.assertTrue(self.selenium.is_element_present("__ac_password"))
        self.assertFalse(self.selenium.is_element_present("link=Logout"))

    def test_login_non_existent(self):
        self.load_login_page()

        self.selenium.type("__ac_name", "nouser")
        self.selenium.type("__ac_password", "nopassword")
        self.selenium.click("submit")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)

        self.assertTrue(self.selenium.is_element_present("__ac_name"))
        self.assertTrue(self.selenium.is_element_present("__ac_password"))
        self.assertFalse(self.selenium.is_element_present("link=Logout"))

    def test_login_user(self):
        self.load_login_page()

        self.selenium.type("__ac_name", "test_user_1_")
        self.selenium.type("__ac_password", "secret")
        self.selenium.click("submit")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)

        self.assertFalse(self.selenium.is_element_present("__ac_name"))
        self.assertFalse(self.selenium.is_element_present("__ac_password"))
        self.assertTrue(self.selenium.is_element_present("link=Logout"))

    def test_logout_user(self):
        self.login_user(user="test_user_1_", password="secret")
        self.selenium.open("/portal/login_html", True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)

        self.assertTrue(self.selenium.is_element_present("link=Logout"))
        self.selenium.click("link=Logout")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)

        self.assertTrue(self.selenium.is_element_present("__ac_name"))
        self.assertTrue(self.selenium.is_element_present("__ac_password"))
        self.assertFalse(self.selenium.is_element_present("link=Logout"))

