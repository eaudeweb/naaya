# -*- coding: utf-8 -*-
from nose.plugins.skip import SkipTest
from Products.Naaya.tests.SeleniumTestCase import SeleniumTestCase
from itertools import count


class NaayaPortal_translate_messageTest(SeleniumTestCase):
    """This test case verifies the following Naaya features:
    -traslation with usual chars from english to french for 'Translate message'
    -traslation empty from english to french for 'Translate message'
    -traslation utf8 chars from english to french for 'Translate message'
    -traslation special chars from english to french for 'Translate message'
    -traslation with a html tag from english to french for 'Translate message'

    """
    def afterSetUp(self):
        "login as admin"
        self.login_user('admin', '')

    def load_translate_page(self):
        """open's the translation page, adds a new language,
        loads the page where the translation for 'Translate message'
        must be defined

        """
        selen = self.selenium
        selen.open('/portal/admin_translations_html', True)
        selen.wait_for_page_to_load(self._selenium_page_timeout)
        language = {'tag1': 'en',
                    'tag2': 'fr'}
        selen.open('/portal/admin_translations_html', True)
        selen.wait_for_page_to_load(self._selenium_page_timeout)
        self.selenium_add_language(language['tag2'])
        selen.open('/portal/admin_translations_html', True)
        selen.click("link=%s" % language['tag1'])
        selen.wait_for_page_to_load(self._selenium_page_timeout)

        self.assertTrue(selen.is_element_present("//div"
                                "[@id='center_content']/form/span/label"))
        self.assertTrue(selen.is_element_present("link=Messages"))

        selen.type("//input[@name='query' and @value='']", "Translate message")
        selen.click("//input[@value='Go']")
        selen.wait_for_page_to_load(self._selenium_page_timeout)

        self.assertFalse(selen.is_element_present("link=Translate message"))
        selen.click("link=Translate messages")
        selen.wait_for_page_to_load(self._selenium_page_timeout)
        selen.click("link=Back to translation form")
        selen.wait_for_page_to_load(self._selenium_page_timeout)
        self.assertTrue(selen.is_element_present("link=Translate message"))

        selen.click("link=Translate message")
        selen.wait_for_page_to_load(self._selenium_page_timeout)

        self.assertEqual(u"Original label in English",
        selen.get_text("//div[@id='center_content']/fieldset[1]/legend"))

        selen.click("link=%s" % language['tag2'])
        selen.wait_for_page_to_load(self._selenium_page_timeout)

    def test_normal_translation(self):
        """insert a normal translation from english to french"""
        self.load_translate_page()
        selen = self.selenium
        translation = "translation du mot"
        selen.type("translation:utf8:ustring", translation)
        selen.click("//input[@value='Save changes']")
        selen.wait_for_page_to_load(self._selenium_page_timeout)

        self.selenium_verify_error_page()
        self.selenium_verify_translation(translation)
        self.selenium_verify_translated_sign()

    def test_space_as_translation(self):
        """insert a space as translation from english to french"""
        raise SkipTest("https://pivo.edw.ro/trac/ticket/44")

        self.load_translate_page()
        selen = self.selenium
        translation = " "
        selen.type("translation:utf8:ustring", translation)
        selen.click("//input[@value='Save changes']")
        selen.wait_for_page_to_load(self._selenium_page_timeout)

        self.selenium_verify_error_page()
        try:
            self.selenium_verify_translation(translation)
        except:
            self.fail("#TODO https://pivo.edw.ro/trac/ticket/44")
        self.selenium_verify_translated_sign_not_present()

    def test_empty_translation(self):
        """insert a empty translation from english to french"""
        self.load_translate_page()
        selen = self.selenium
        translation = ""
        selen.type("translation:utf8:ustring", translation)
        selen.click("//input[@value='Save changes']")
        selen.wait_for_page_to_load(self._selenium_page_timeout)

        self.selenium_verify_error_page()
        #verify output
        out_str = selen.get_text("//div[@id='center_content']/h1")
        self.assertEqual(out_str, 'Translate message')

        self.selenium_verify_translated_sign_not_present()

    def test_utf8_translation(self):
        """cyrilic characters in a translation from english to french"""
        self.load_translate_page()
        selen = self.selenium
        translation = u"стуўфх"
        selen.type("translation:utf8:ustring", translation)
        selen.click("//input[@value='Save changes']")
        selen.wait_for_page_to_load(self._selenium_page_timeout)

        self.selenium_verify_error_page()
        self.selenium_verify_translation(translation)
        self.selenium_verify_translated_sign()

    def test_special_translation(self):
        """insert special characters in a translation from english to french"""
        self.load_translate_page()
        selen = self.selenium
        translation = "!@#$%^&*()"
        selen.type("translation:utf8:ustring", translation)
        selen.click("//input[@value='Save changes']")
        selen.wait_for_page_to_load(self._selenium_page_timeout)

        self.selenium_verify_error_page()
        self.selenium_verify_translation(translation)
        self.selenium_verify_translated_sign()

    def test_html_tag_translation(self):
        """insert a html tag in a translation from english to french"""
        raise SkipTest("https://pivo.edw.ro/trac/ticket/44")

        self.load_translate_page()
        selen = self.selenium
        translation = "<b>"
        selen.type("translation:utf8:ustring", translation)
        selen.click("//input[@value='Save changes']")
        selen.wait_for_page_to_load(self._selenium_page_timeout)

        self.selenium_verify_error_page()
        out_str = selen.get_text("//div[@id='center_content']/h1")
        self.assertNotEqual(out_str, translation)
        try:
            self.selenium_verify_translated_sign_not_present()
        except:
            self.fail("#TODO https://pivo.edw.ro/trac/ticket/44")

    def selenium_add_language(self, lang):
        """This function works only if you are an administrator"""
        selen = self.selenium
        selen.open("/portal/portal_properties/manage_languages_html", True)
        if lang == 'fr':
            selen.select("language", "label=French [fr]")
            selen.click("//input[@value='Add']")

    def selenium_verify_error_page(self):
        """Checks if there had been an eror page and compares the input with
        output

        """
        selen = self.selenium
        if selen.is_element_present("//div[@id='middle_port']/"
                                    "h1[text()='Error page']"):
            return self.fail('Crashed while delivering the translation')

    def selenium_verify_translation(self, in_str):
        """compares displayed translation with the typed one"""
        selen = self.selenium
        out_str = selen.get_text("//div[@id='center_content']/h1")
        self.assertEqual(out_str, in_str)

    def selenium_verify_translated_sign(self):
        """verifies the translated "check sign" in the table"""
        selen = self.selenium
        selen.click("link=Back to translation form")
        selen.wait_for_page_to_load(self._selenium_page_timeout)
        for i in count(1):
            try:
                translated = selen.get_text("css=#center_content>table.datatable"
                                            ">tbody>tr:nth-child(%s)>td:nth-chil"
                                            "d(2)>a" % i)
            except:
                break
            if (translated == 'Translate message'):
                self.assertTrue(
                    selen.is_element_present("css=#center_content>"
                                             "table.datatable>tbody>"
                                             "tr:nth-child(%s)>td:nth-child(3)>"
                                             "img[alt='Translated']" % i))

    def selenium_verify_translated_sign_not_present(self):
        """verifies if the translated "check sign" in the table is not present"""
        selen = self.selenium
        selen.click("link=Back to translation form")
        selen.wait_for_page_to_load(self._selenium_page_timeout)
        for i in count(1):
            try:
                translated = selen.get_text("css=#center_content>table.datatable"
                                            ">tbody>tr:nth-child(%s)>td:nth-chil"
                                            "d(2)>a" % i)
            except:
                break
            if (translated == 'Translate message'):
                self.assertFalse(
                    selen.is_element_present("css=#center_content>"
                                             "table.datatable>tbody>"
                                             "tr:nth-child(%s)>td:nth-child(3)>"
                                             "img[alt='Translated']" % i))
