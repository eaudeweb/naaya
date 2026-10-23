from zope.i18n.interfaces import ITranslationDomain
from zope.component import queryUtility

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase

from naaya.i18n.utilities import NyI18nTranslator


class TestTranslationUtility(NaayaTestCase):


    def test_utility_existence(self):
        utility = queryUtility(ITranslationDomain, 'default')
        self.assertTrue(isinstance(utility, NyI18nTranslator))

    def test_utility_translation(self):
        utility = queryUtility(ITranslationDomain, 'default')
        self.assertEqual(utility.translate('${cnt} puppies', {'cnt': 2},
                                           self.portal.REQUEST),
                         '2 puppies')

    def test_utility_translates_with_portal_catalog(self):
        self.portal.gl_add_site_language('de')
        self.portal.getPortalI18n().get_message_catalog().edit_message(
            '${cnt} puppies', 'de', '${cnt} Welpen')
        utility = queryUtility(ITranslationDomain, 'default')
        self.assertEqual(utility.translate('${cnt} puppies', {'cnt': 2},
                                           self.portal.REQUEST,
                                           target_language='de'),
                         '2 Welpen')
        self.assertEqual(utility.translate('${cnt} puppies', {'cnt': 2},
                                           self.portal.REQUEST,
                                           target_language='en'),
                         '2 puppies')

    def test_utility_negotiates_language(self):
        self.portal.gl_add_site_language('de')
        i18n = self.portal.getPortalI18n()
        i18n.get_message_catalog().edit_message('Hello', 'de', 'Hallo')
        self.portal.REQUEST[i18n.get_negotiator().cookie_id] = 'de'
        utility = queryUtility(ITranslationDomain, 'default')
        self.assertEqual(utility.translate('Hello', None,
                                           self.portal.REQUEST), 'Hallo')

    def test_utility_outside_site(self):
        utility = queryUtility(ITranslationDomain, 'default')
        self.assertEqual(utility.translate('${x} cats', {'x': 3},
                                           {'PARENTS': [object()]}),
                         '3 cats')
