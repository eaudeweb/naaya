from Products.Naaya.tests.SeleniumTestCase import SeleniumTestCase

class NaayaPortalPropertiesTest(SeleniumTestCase):
    """This test verifies the next:
    - Portal Properites -- Metadata
    - Portal Properites -- Email Settings
    - Portal Properites -- Other Properties
    - notifications

    """

    def selenium_initialize(self):
        selen = self.selenium
        self.login_user('admin', '')

    def test_portal_metadata(self):
        """portal properties testing"""
        selen = self.selenium
        self.selenium_initialize()
        metadata_feature ={
            'site_title': 'Naaya Test',
            'site_subtitle': 'linking the options',
            'publisher': 'gigi',
            'contributor': 'ghita',
            'rights': '',
        }
        self.selenium_type_metadata(metadata_feature)

        self.assertEqual("%s - %s"
            % (metadata_feature['site_title'],metadata_feature['site_subtitle']),
            selen.get_title(), 'Incorect metadata ')

    def selenium_type_metadata(self,metadata_feature):
        selen = self.selenium
        selen.open("/portal/admin_metadata_html", True)

        selen.type("site_title:utf8:ustring", metadata_feature['site_title'])
        selen.type("site_subtitle:utf8:ustring", metadata_feature['site_subtitle'])
        selen.type("publisher:utf8:ustring", metadata_feature['publisher'])
        selen.type("contributor:utf8:ustring", metadata_feature['contributor'])
        selen.type("rights:utf8:ustring", metadata_feature['rights'])
        selen.click("//input[@value='Save changes']")
        selen.wait_for_page_to_load(self._selenium_page_timeout)

    def test_email_settings(self):
        selen = self.selenium
        self.selenium_initialize()
        user_email_data = {
            'server_name': 'SSL-POP',
            'server_port': 995,
            'address_from': 'gigi@example.com',
            'administrator_email': 'admin@example.com',
            'notify_on_errors_email': 'error@example.com',
        }
        self.selenium_set_email(user_email_data)
        self.assertFalse(selen.is_text_present('Error page'),
                       'Some data crashed introducing Email Settings')

    def selenium_set_email(self, user_email_data):
        selen = self.selenium
        selen.open("/portal/admin_email_html", True)

        selen.type("mail_server_name", user_email_data['server_name'])
        selen.type("mail_server_port", user_email_data['server_port'])
        selen.type("mail_address_from", user_email_data['address_from'])
        selen.type("administrator_email", user_email_data['administrator_email'])
        selen.type("notify_on_errors_email", user_email_data['notify_on_errors_email'])
        selen.click("//input[@value='Save changes']")
        selen.wait_for_page_to_load(self._selenium_page_timeout)

    def test_portal_other_properties(self):
        selen = self.selenium
        self.selenium_initialize()
        portal_other_properties = {
            'show_release': True,
            'rename_id': True,
            'portal_url': '',
            'http_proxy': '',
            'recaptcha_public': '6Le3Y7wSAAAAABHapJLEaFiSqg3jw06KYXOkiKAf',
            'recaptcha_private': '6Le3Y7wSAAAAALT575jRcWVObw8JLzqOhINgcfHN',
            'max_items': 10,
            'switch_language': True,
            'display_contributor': True,
            'display_subobject': True,
        }
        self.selenium_set_other_properties(portal_other_properties)
        self.assertFalse(selen.is_text_present('Error page'),
                         'failed after setting other properties')

    def selenium_set_other_properties(self, other_properties):
        selen = self.selenium
        selen.open("/portal/admin_properties_html", True)

        if other_properties['show_release']:
            selen.check("show_releasedate")
        else:
            selen.uncheck("show_releasedate")
        if other_properties['rename_id']:
            selen.check("rename_id")
        else:
            selen.uncheck("rename_id")
        selen.type("portal_url", other_properties['portal_url'])
        selen.type("http_proxy", other_properties['http_proxy'])
        selen.type("recaptcha_public_key", other_properties['recaptcha_public'])
        selen.type("recaptcha_private_key", other_properties['recaptcha_private'])
        selen.type("rdf_max_items", other_properties['max_items'])
        if other_properties['switch_language']:
            selen.check("switch_language")
        else:
            selen.uncheck("switch_language")
        if other_properties['display_contributor']:
            selen.check("display_contributor")
        else:
            selen.uncheck("display_contributor")
        if other_properties['display_subobject']:
            selen.check("display_subobject_count")
        else:
            selen.uncheck("display_subobject_count")
        selen.click("//input[@value='Save changes']")
        selen.wait_for_page_to_load(self._selenium_page_timeout)

    def test_notifications(self):
        """testing Notifications from the administration menu"""
        self.selenium_initialize()
        selen = self.selenium
        selen.open("portal/portal_notification/admin_html", True)
        self.selenium_add_subscription()
        self.assertFalse(selen.is_text_present('Error page'),
                         'Failed to add subscription')

    def selenium_add_subscription(self):
        """subscribe to instant notifications"""
        selen = self.selenium
        selen.click("enable_instant")
        selen.click("//input[@value='Save changes']")
        selen.wait_for_page_to_load(self._selenium_page_timeout)
        self.assertTrue(selen.is_element_present("notif_type"))
        selen.type("user_id", "contributor")
        selen.type("location", "info")
        selen.click("//input[@value='Subscribe user']")
        selen.wait_for_page_to_load(self._selenium_page_timeout)
