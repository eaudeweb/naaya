
import re
from lxml.html.soupparser import fromstring

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

class TestManageMessagesInZmi(NaayaFunctionalTestCase):

    def afterSetUp(self):
        self.browser_do_login('admin', '')
        # add a second language:
        self.portal.getPortalI18n().add_language('de')
        # and a msgid
        self.portal.getPortalI18n().get_message_catalog().clear()
        self.portal.getPortalI18n().get_message_catalog()\
                                   .gettext('${cnt} cats', 'de')
        import transaction; transaction.commit()

    def test_msgid_exists(self):
        self.browser.go('http://localhost/portal/portal_i18n/manage_messages?lang=de')
        dom = fromstring(re.sub(r'\s+', ' ', self.browser.get_html()))
        results = dom.xpath('//table[@id="message_results"]/tr/td/small/a')
        found = None
        for result in results:
            if result.text == '${cnt} cats':
                found = result
                break
        self.assertTrue(found is not None)

    def test_search_msgid(self):
        self.browser.go('http://localhost/portal/portal_i18n/manage_messages?lang=de')
        form = self.browser.get_form('search_messages')
        form['empty'] = [] #untranslated
        form['regex'] = ' cats'
        self.browser.clicked(form, self.browser.get_form_field(form, 'regex'))
        self.browser.submit()
        dom = fromstring(re.sub(r'\s+', ' ', self.browser.get_html()))
        results = dom.xpath('//table[@id="message_results"]/tr/td/small/a')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].text, '${cnt} cats')

    def test_translate(self):
        self.browser.go('http://localhost/portal/portal_i18n/manage_messages?lang=de')
        dom = fromstring(re.sub(r'\s+', ' ', self.browser.get_html()))
        results = dom.xpath('//table[@id="message_results"]/tr/td/small/a')
        found = None
        for result in results:
            if result.text == '${cnt} cats':
                found = result
                break
        self.browser.go(found.attrib['href'])
        form = self.browser.get_form('translate_message')
        self.browser.clicked(form,
                  self.browser.get_form_field(form, 'translation:utf8:string'))
        form['translation:utf8:string'] = '${cnt} Katzen'
        self.browser.submit(fieldname='manage_editMessage:method')
        self.assertEqual('${cnt} Katzen',
         self.portal.getPortalI18n().get_message_catalog()\
                                    .gettext('${cnt} cats', 'de'))

    def test_delete_msgid(self):
        self.browser.go('http://localhost/portal/portal_i18n/manage_messages?lang=de')
        dom = fromstring(re.sub(r'\s+', ' ', self.browser.get_html()))
        results = dom.xpath('//table[@id="message_results"]/tr/td/small/a')
        found = None
        for result in results:
            if result.text == '${cnt} cats':
                found = result
                break
        self.browser.go(found.attrib['href'])

        form = self.browser.get_form('translate_message')
        self.browser.clicked(form,
                  self.browser.get_form_field(form, 'translation:utf8:string'))
        self.browser.submit(fieldname='manage_delMessage:method')

        self.browser.go('http://localhost/portal/portal_i18n/manage_messages?lang=de')
        dom = fromstring(re.sub(r'\s+', ' ', self.browser.get_html()))
        results = dom.xpath('//table[@id="message_results"]/tr/td/small/a')
        found = None
        for result in results:
            if result.text == '${cnt} cats':
                found = result
                break
        self.assertTrue(found is None)


class TestAdminMessagesHtml(NaayaFunctionalTestCase):

    def afterSetUp(self):
        self.browser_do_login('admin', '')
        self.portal.getPortalI18n().add_language('de')
        import transaction; transaction.commit()

    def get_page(self, query):
        from urllib.parse import quote
        from naaya.i18n.admin_i18n import message_encode
        url = ('http://localhost/portal/portal_i18n/admin_messages_html'
               '?msg=%s%s' % (quote(message_encode('${cnt} cats')), query))
        self.browser.go(url)
        return self.browser.get_html()

    def test_without_trans_lang(self):
        html = self.get_page('')
        self.assertIn('name="translate_en"', html)

    def test_empty_trans_lang(self):
        html = self.get_page('&trans_lang=')
        self.assertIn('name="translate_en"', html)

    def test_with_trans_lang(self):
        html = self.get_page('&trans_lang=de&saved=True')
        self.assertIn('name="translate_de"', html)

