# -*- coding: UTF-8 -*-
# Python imports
import unittest

# Zope imports
from zope.i18n.interfaces import IModifiableUserPreferredLanguages

# Project imports
from naaya.i18n.LanguageManagers import NyPortalLanguageManager, normalize_code


class NyPortalLanguageManagerTest(unittest.TestCase):

    def test_normalize_code(self):
        sets = [('pt-br', 'pt-BR'), ('en', 'en'), ('ro_RO', 'ro-RO'),
                ('PT BR', 'pt-BR'), ('pt - br', 'pt-BR'),
                ('sk-Cyrillic', 'sk-CYRILLIC')]
        for (input, expected) in sets:
            self.assertEqual(normalize_code(input), expected)

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
