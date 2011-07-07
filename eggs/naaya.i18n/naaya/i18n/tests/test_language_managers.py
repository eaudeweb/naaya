# -*- coding: UTF-8 -*-
# Python imports
import unittest

# Zope imports
from zope.i18n.interfaces import IModifiableUserPreferredLanguages

# Project imports
from naaya.i18n.LanguageManagers import (NyLanguages,
                                         NyPortalLanguageManager,
                                         normalize_code)


class NyLanguageManagerTest(unittest.TestCase):

    def test_normalize_code(self):
        sets = [('pt-br', 'pt-BR'), ('en', 'en'), ('ro_RO', 'ro-RO'),
                ('PT BR', 'pt-BR'), ('pt - br', 'pt-BR'),
                ('sk-Cyrillic', 'sk-CYRILLIC')]
        for (input, expected) in sets:
            self.assertEqual(normalize_code(input), expected)

    def test_language_manager_init(self):
        lang_manager = NyLanguages()
        # test languages.txt was used (we have some langs)
        self.assertTrue(len(lang_manager.langs) > 10)
        self.assertTrue(len(lang_manager.languages) > 10)

    def test_language_manager_add(self):
        lang_manager = NyLanguages()
        count0 = len(lang_manager.langs)
        lang_manager.add_language('en-pt', 'Pirate English')
        self.assertEqual(lang_manager.get_language_name('en-pt'),
                         'Pirate English')
        self.assertEqual(len(lang_manager.langs), count0 + 1)
        # one more time
        self.assertRaises(KeyError, lang_manager.add_language,
                          'en-pt', 'One More')
        self.assertEqual(lang_manager.get_language_name('en-pt'),
                         'Pirate English')

    def test_language_manager_del(self):
        lang_manager = NyLanguages()
        lang_manager.add_language('en-pt', 'Pirate English')
        count0 = len(lang_manager.langs)
        lang_manager.del_language('en-PT')
        # One more time
        self.assertRaises(KeyError, lang_manager.del_language, 'en-PT')
        self.assertEqual(len(lang_manager.langs), count0 - 1)
        self.assertEqual(lang_manager.get_language_name('en-PT'), '???')
    
class NyPortalLanguageManagerTest(unittest.TestCase):

    def test_add_portal_language(self):
        portal_langs = NyPortalLanguageManager()
        portal_langs.addAvailableLanguage('en')
        portal_langs.addAvailableLanguage('fr')
        self.assertEqual(portal_langs.getAvailableLanguages(), ('en', 'fr'))

    def test_del_portal_language(self):
        portal_langs = NyPortalLanguageManager()
        portal_langs.addAvailableLanguage('fr')
        self.assertTrue('fr' in portal_langs.getAvailableLanguages())
        portal_langs.delAvailableLanguage('fr')
        self.assertFalse('fr' in portal_langs.getAvailableLanguages())
        def delete_all():
            for lang in portal_langs.getAvailableLanguages():
                portal_langs.delAvailableLanguage(lang)
        self.assertRaises(ValueError, delete_all)
