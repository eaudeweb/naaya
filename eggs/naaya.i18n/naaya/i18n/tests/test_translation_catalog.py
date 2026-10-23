# -*- coding: UTF-8 -*-
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase


class _TranslationCatalog(object):
    """ Catalog tests; mix into a TestCase that defines catalog_factory """

    def test_clean_catalog_from_setup(self):
        catalog = self.catalog_factory(languages=('en', 'de'))
        self.assertRaises(StopIteration, lambda: next(catalog.messages()))


    def test_clean_translation(self):
        catalog = self.catalog_factory(languages=('en', 'de'))
        catalog.edit_message('water', 'en',
                             '  water	 is  \r\n\n  healthy	\n	')
        self.assertEqual(catalog.gettext('water', 'en'),
                         'water is healthy')

    def test_get_unexistent_message(self):
        catalog = self.catalog_factory(languages=('en', 'de'))
        cat_en = catalog.gettext('cat', 'en')
        cat_de = catalog.gettext('cat', 'de')
        self.assertEqual((cat_en, cat_de), ('cat', 'cat'))

    def test_edit_and_get_message(self):
        catalog = self.catalog_factory(languages=('en', 'de'))
        catalog.edit_message('cat', 'de', 'Katze')
        cat_de = catalog.gettext('cat', 'de')
        self.assertEqual(catalog.gettext('cat', 'de'), 'Katze')

    def test_del_message(self):
        catalog = self.catalog_factory(languages=('en', 'de'))
        catalog.edit_message('water', 'en', 'water')
        catalog.edit_message('water', 'de', 'Wasser')
        catalog.del_message('water')
        self.assertEqual(catalog.gettext('water', 'en'), 'water')
        self.assertEqual(catalog.gettext('water', 'de'), 'water')

    def test_default_behaviour_specified(self):
        catalog = self.catalog_factory(languages=('en', 'de'))
        # return and set default as 'en' Translation
        self.assertEqual(catalog.gettext('cat', 'en', 'Default cat'),
                         'Default cat')
        self.assertEqual(catalog.gettext('cat', 'en'), 'Default cat')
        # return default, but do not set it, since this is not 'en' lang
        self.assertEqual(catalog.gettext('water', 'de', 'Wasser'),'Wasser')
        self.assertEqual(catalog.gettext('water', 'de'), 'water')

    def test_message_iteration(self):
        catalog = self.catalog_factory(languages=('en', 'de'))
        catalog.gettext('cat', 'en')
        catalog.gettext('water', 'de')
        # test iteration, 'water' and 'cat' in catalog
        i = 0
        all_msgs = catalog.messages()
        try:
            while True:
                next(all_msgs)
                i += 1
        except StopIteration:
            pass
        self.assertEqual(i, 2)

    def test_language_inexistent(self):
        catalog = self.catalog_factory(languages=('en', 'de'))
        catalog.gettext('cat', 'fr')
        # fr doesn't exist, don't add msgid 'cat'
        self.assertRaises(StopIteration, lambda: next(catalog.messages()))

    def test_language_get(self):
        catalog = self.catalog_factory(languages=('en', 'de'))
        self.assertEqual(('en', 'de'), tuple(catalog.get_languages()))

    def test_language_add(self):
        catalog = self.catalog_factory(languages=('en', 'de'))
        catalog.add_language('fr')
        catalog.edit_message('cat', 'fr', 'chat')
        self.assertEqual(catalog.gettext('cat', 'fr'), 'chat')
        self.assertTrue('fr' in catalog.get_languages())

    def test_language_del(self):
        catalog = self.catalog_factory(languages=('en', 'de'))
        catalog.edit_message('dog', 'de', 'Hund')
        catalog.del_language('de')
        self.assertFalse('de' in catalog.get_languages())
        # since lang not in catalog, return en translation
        self.assertEqual(catalog.gettext('dog', 'de'), 'dog')
        # lang deletion must not removes translations
        for (m, tr) in catalog.messages():
            if m=='dog':
                self.assertEqual(tr.get('de', None), 'Hund')

class NyMessageCatalogTest(NaayaTestCase, _TranslationCatalog):
    def catalog_factory(self, **kw):
        """ clean, add extra langs and return catalog from portal_i18n """
        catalog = self.portal.getPortalI18n().get_message_catalog()
        # erase catalog
        catalog.clear()
        for lang in catalog.get_languages():
            catalog.del_language(lang)
        if 'languages' in kw:
            for lang in kw['languages']:
                catalog.add_language(lang)
        return catalog
