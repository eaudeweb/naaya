import transaction
from Products.Naaya.tests.SeleniumTestCase import SeleniumTestCase
from itertools import count
from naaya.content.news.news_item import addNyNews
from naaya.core.zope2util import permission_add_role

news_data = {
    'lang_tag': 'English',
    'news_title': 'Test news',
}


class NaayaBasketsTest(SeleniumTestCase):
    """This test case verifies the following features of Naaya:
    - Basket of Approvals
        Approve
        Unapprove
    - Basket of Translations
    """

    def afterSetUp(self):
        permission_add_role(self.portal, 'Naaya - Skip Captcha', 'contributor')
        addNyNews(self.portal.info, submitted=1, title=news_data['news_title'],
                  contributor='contributor')
        transaction.commit()
        self.login_user('admin', '')
        self.selenium_add_language('fr')

    def test_basket_of_approvals(self):
        "testing the approvals basket's for news items: approve and unnaprove"
        self.selenium_approve_pending(news_data)
        #verifies if the news can be approved
        self.logout_user()
        self.selenium_verify_news_display(news_data)
        #verifies as an anonymous the display of news after approval
        self.login_user('admin', '')
        self.selenium_unapprove_news(news_data)
        #verifies if the news can be unnaproved

    def test_basket_of_translations(self):
        """testing the translations basket"""
        translation_data = {
            'user': 'Contributor',
            'news_title_fr': 'le mot en francaise',
            'lang_tag': 'French',
            'description': '',
            'geo_coverage': '',
            'keywords': '',
            'comments': '',
            'sort_order': '',
            'release_date': '',   #de forma dd/mm/yyyy
            'details': '',
            'expiration_date': '',  #de forma dd/mm/yyyy
            'concerned_url': '',
            'source': '',  #absolute url required (from your computer)
        }

        self.selenium_verify_basket_before(translation_data, news_data)
        self.selenium_add_translation(translation_data, news_data)
        self.selenium_verify_basket_after(translation_data, news_data)

    def selenium_add_language(self, lang):
        """This function works only if you are an administrator"""
        selen = self.selenium
        selen.open("/portal/portal_properties/manage_languages_html", True)
        if lang == 'fr':
            selen.select("language", "label=French [fr]")
            selen.click("//input[@value='Add']")

    def selenium_add_translation(self, translation_data, news_data):
        selen = self.selenium
        selen.open("/portal/info", True)
        selen.click("link=%s" % news_data['news_title'])
        selen.wait_for_page_to_load(self._selenium_page_timeout)
        selen.click("//div[@id='admin_this_folder']/a[2]/span")
        selen.wait_for_page_to_load(self._selenium_page_timeout)

        selen.type("title", translation_data['news_title_fr'])
        selen.type("coverage", translation_data['geo_coverage'])
        selen.type("keywords", translation_data['keywords'])
        if not translation_data['release_date']:
            selen.click("link=Today")
        else:
            selen.type("releasedate", translation_data['release_date'])
        if translation_data['comments']: selen.click("discussion")
        if translation_data['expiration_date']:
            selen.type("expirationdate", translation_data['expiration_date'])
        selen.type("resourceurl", translation_data['concerned_url'])
        selen.type("source", translation_data['source'])
        selen.click("//input[@value='Save changes']")
        selen.wait_for_page_to_load(self._selenium_page_timeout)
        self.assertFalse(selen.is_text_present("Error"),
                         "Translation not added properly")

    def selenium_verify_basket_before(self, translation_data, news_data):
        selen = self.selenium
        selen.open("/portal/admin_centre_html", True)
        selen.click("link=Basket of translations")
        selen.wait_for_page_to_load(self._selenium_page_timeout)
        selen.select("lang", "label=%s" % translation_data['lang_tag'])
        selen.click("//input[@value='Show']")
        selen.wait_for_page_to_load(self._selenium_page_timeout)
        selen.click("link=show items")
        selen.wait_for_page_to_load(self._selenium_page_timeout)
        self.assertTrue(selen.is_element_present("link=%s" % news_data['news_title']),
                        "Althouth unnapproved, news were displayed")

    def selenium_verify_basket_after(self, translation_data, news_data):
        selen = self.selenium
        selen.open("/portal/admin_centre_html", True)
        selen.click("link=Basket of translations")
        selen.wait_for_page_to_load(self._selenium_page_timeout)
        selen.select("lang", "label=%s" % translation_data['lang_tag'])
        selen.click("//input[@value='Show']")
        selen.wait_for_page_to_load(self._selenium_page_timeout)

        #verify if show items still present after approve
        self.assertTrue(selen.is_text_present("show items"),
                        "basket is not clean after approval")

    def selenium_approve_pending(self, news_data):
        selen = self.selenium
        selen.open("/portal/admin_centre_html", True)
        selen.click("link=Basket of approvals")
        selen.wait_for_page_to_load(self._selenium_page_timeout)

        self.assertFalse(selen.is_element_present("a[text()=Information]"),
                         "The basket is empty")
        selen.click("link=Information")
        selen.wait_for_page_to_load(self._selenium_page_timeout)

        if selen.is_text_present("Approvals"):
            selen.click("link=Approvals")
            selen.wait_for_page_to_load(self._selenium_page_timeout)
        if selen.is_text_present(news_data['news_title']):
            selen.check("css=#pndForm>table.datatable>tbody>tr:nth-child(1)>"
                "td:nth-child(6)>input")  #pentru approve news
        else:
            self.fail('news not present in pending table')
        selen.click("//input[@value='Save changes']")
        selen.wait_for_page_to_load(self._selenium_page_timeout)
        self.assertTrue(selen.is_text_present("No pending items to review."),
                         "Approving wrong! element still unapproved")
        self.assertFalse(selen.is_text_present("Error"),
                         "Approving got you an error")

    def selenium_unapprove_news(self, news_data):
        selen = self.selenium
        selen.open("/portal/info", True)
        selen.click("//div[@id='admin_this_folder']/a[3]/span")
        selen.wait_for_page_to_load(self._selenium_page_timeout)

        self.assertTrue(selen.is_text_present(news_data['news_title']))
        for i in count(1):
            try:
                aproved_title = selen.get_text("css=#pblForm>table.datatable"
                    ">tbody>tr:nth-child(%d)>td:nth-child(3)>a" % i)
            except:
                break
            if(aproved_title == news_data['news_title']):
                selen.check("css=#pblForm>table.datatable>tbody>tr:nth-child(%d)"
                      ">td:nth-child(6)>input" % i)
        selen.click("//input[@value='Save changes']")
        selen.wait_for_page_to_load(self._selenium_page_timeout)
        self.assertFalse(selen.is_text_present("No pending items to review."),
                         "Unapproving wrong! element still approved")
        self.assertFalse(selen.is_text_present("Error"),
                         "Unapproving got you an error")

    def selenium_verify_news_display(self, news_data):
        selen = self.selenium
        selen.open("/portal/info", True)
        self.assertTrue(selen.is_element_present("link=%s"
                                                 % news_data['news_title']),
                        "The news can't be viewed by anonimous after approval")
