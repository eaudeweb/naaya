import transaction

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from naaya.content.news.news_item import addNyNews

BASKET_URL = 'http://localhost/portal/portal_i18n/admin_basket_translations_html'


class BasketOfTranslationsTest(NaayaFunctionalTestCase):

    def afterSetUp(self):
        self.portal.gl_add_site_language('fr')
        addNyNews(self.portal.info, id='basketnews', title='Basket news',
                  submitted=1, contributor='admin', lang='en')
        transaction.commit()

    def beforeTearDown(self):
        self.portal.info.manage_delObjects(['basketnews'])
        self.portal.gl_del_site_languages(['fr'])
        transaction.commit()

    def test_untranslated_item_listed_until_translated(self):
        self.browser_do_login('admin', '')
        self.browser.go(BASKET_URL + '?lang=fr&show=portal/info')
        html = self.browser.get_html()
        self.assertTrue('/portal/info/basketnews/edit_html?lang=fr' in html,
                        'untranslated news not listed')

        self.browser.go('http://localhost/portal/info/basketnews/edit_html?lang=fr')
        form = self.browser.get_form('frmEdit')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:string'))
        form['title:utf8:string'] = 'Nouvelle du panier'
        self.browser.submit()
        self.assertEqual(self.portal.info.basketnews.getLocalProperty('title', 'fr'),
                         'Nouvelle du panier')

        self.browser.go(BASKET_URL + '?lang=fr&show=portal/info')
        self.assertFalse('/portal/info/basketnews/edit_html?lang=fr' in self.browser.get_html(),
                         'translated news still listed')
