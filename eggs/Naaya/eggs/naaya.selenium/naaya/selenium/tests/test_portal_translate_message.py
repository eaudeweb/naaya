# -*- coding: UTF-8 -*-
import sys
import os
import re
import optparse
from Products.Naaya.tests.SeleniumTestCase import SeleniumTestCase


class NaayaPortal_translate_messageTest(SeleniumTestCase):
#This test case verifies the following Naaya features:
#    1. introduce a traslation with usual chars from english to french for 'Translate message'
#    2. introduce a traslation empty from english to french for 'Translate message'
#    3. introduce a traslation utf8 chars from english to french for 'Translate message'
#    4. introduce a traslation special chars from english to french for 'Translate message'
#    5. introduce a traslation with a html tag from english to french for 'Translate message'
    def afterSetUp(self):
        selen = self.selenium
        self.login_user('admin', '')
        selen.open('/portal/admin_translations_html', True)
        selen.wait_for_page_to_load("30000")

    def load_translate_page(self):
        selen = self.selenium
        language = {'tag1': 'en',
                    'tag2': 'fr'}
        selen.open('/portal/admin_translations_html', True)
        selen.wait_for_page_to_load("30000")
        self.selenium_add_language(language['tag2'])
        selen.open('/portal/admin_translations_html', True)
        selen.click("link=%s" % language['tag1'])
        selen.wait_for_page_to_load("30000")

        self.assertTrue(selen.is_element_present("//div"
                                "[@id='center_content']/form/span/label"))
        self.assertTrue(selen.is_element_present("link=Messages"))

        selen.type("//input[@name='query' and @value='']", "Translate message")
        selen.click("//input[@value='Go']")
        selen.wait_for_page_to_load("30000")

        self.assertFalse(selen.is_element_present("link=Translate message"))
        selen.click("link=Translate messages")
        selen.wait_for_page_to_load("30000")
        selen.click("link=Back to translation form")
        selen.wait_for_page_to_load("30000")
        self.assertTrue(selen.is_element_present("link=Translate message"))

        selen.click("link=Translate message")
        selen.wait_for_page_to_load("30000")

        self.assertEqual("Original label in English language.",
        selen.get_text("//div[@id='center_content']/fieldset[1]/legend"))

        selen.click("link=%s" % language['tag2'])
        selen.wait_for_page_to_load("30000")

    def test_normal_translation(self):
        """normal translation from english to french"""
        self.load_translate_page()
        selen = self.selenium
        translation = "translation du mot"
        selen.type("translation:utf8:ustring", translation)
        selen.click("//input[@value='Save changes']")
        selen.wait_for_page_to_load("30000")

        self.selenium_verify_error_page()
        self.selenium_verify_translation(translation)

    def test_empty_translation(self):
        """empty translation from english to french"""
        self.load_translate_page()
        selen = self.selenium
        translation = ""
        selen.type("translation:utf8:ustring", translation)
        selen.click("//input[@value='Save changes']")
        selen.wait_for_page_to_load("30000")

        self.selenium_verify_error_page()
        out_str = selen.get_text("//div[@id='center_content']/h1")
        self.assertEqual(out_str, 'Translate message')

    def test_utf8_translation(self):
        """cyrilic characters in a translation from english to french"""
        self.load_translate_page()
        selen = self.selenium
        translation = u"стуўфхцчшщъыьэюяабвгґдеёжӂзіийј"
        selen.type("translation:utf8:ustring", translation)
        selen.click("//input[@value='Save changes']")
        selen.wait_for_page_to_load("30000")

        self.selenium_verify_error_page()
        self.selenium_verify_translation(translation)

    def test_special_translation(self):
        """special characters in a translation from english to french"""
        self.load_translate_page()
        selen = self.selenium
        translation = "!@#$%^&*()"
        selen.type("translation:utf8:ustring", translation)
        selen.click("//input[@value='Save changes']")
        selen.wait_for_page_to_load("30000")

        self.selenium_verify_error_page()
        self.selenium_verify_translation(translation)

    def test_html_tag_translation(self):
        """special characters in a translation from english to french"""
        self.load_translate_page()
        selen = self.selenium
        translation = "<b>"
        selen.type("translation:utf8:ustring", translation)
        selen.click("//input[@value='Save changes']")
        selen.wait_for_page_to_load("30000")

        self.selenium_verify_error_page()
        out_str = selen.get_text("//div[@id='center_content']/h1")
        self.assertNotEqual(out_str, translation)

    def selenium_add_language(self, lang):
        """This function works only if you are an administrator"""
        selen = self.selenium
        selen.open("/portal/portal_properties/manage_languages_html", True)
        if lang == 'fr':
            selen.select("language", "label=French [fr]")
            selen.click("//input[@value='Add']")

    def selenium_verify_error_page(self):
        """checks if there had been an eror page and compares the input with output"""
        selen = self.selenium
        if selen.is_element_present("//div[@id='middle_port']/"
                                      "h1[text()='Error page']"):
            return self.fail('Crashed while delivering the translation')

    def selenium_verify_translation(self, in_str):
        selen = self.selenium
        out_str = selen.get_text("//div[@id='center_content']/h1")
        return self.assertEqual(out_str, in_str)
