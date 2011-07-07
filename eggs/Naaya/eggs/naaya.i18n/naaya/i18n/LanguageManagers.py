# Python imports
import os.path
import re

# Zope imports
from zope.interface import implements
from zope.i18n.interfaces import (IModifiableUserPreferredLanguages,
                                  ILanguageAvailability)
from Persistence import Persistent
from persistent.list import PersistentList

# Project imports
from interfaces import INyLanguageManagement


def normalize_code(code):
    not_letter = re.compile(r'[^a-z]+', re.IGNORECASE)
    parts = re.sub(not_letter, '-', code).split('-', 1)
    parts[0] = parts[0].lower()
    if len(parts) > 1:
        return parts[0] + '-' + parts[1].upper()
    else:
        return parts[0]

class NyLanguages(object):

    def __init__(self):
        self.reset()

    def reset(self):
        self.languages = {}
        cwd = __file__.rsplit(os.path.sep, 1)[0]
        filename = os.path.join(cwd, 'languages.txt')
        for line in open(filename).readlines():
            line = line.strip()
            if line and line[0] != '#':
                code, name = line.split(' ', 1)
                self.languages[normalize_code(code)] = name

        # Builds a sorted list with the languages code and name
        language_codes = self.languages.keys()
        language_codes.sort()
        self.langs = [ {'code': x,
                        'name': self.languages[x]} for x in language_codes ]

    def add_language(self, code, name):
        """
        Returns code of added language, None if code already exists
        """
        code = normalize_code(code)
        if self.languages.has_key(code):
            raise KeyError("`%s` language code already exists" % code)
        self.languages[code] = name
        language_codes = self.languages.keys()
        language_codes.sort()
        self.langs = [ {'code': x,
                        'name': self.languages[x]} for x in language_codes ]

    def del_language(self, code):
        """
        Returns deleted language code, None if language code not found
        """
        code = normalize_code(code)
        if code not in self.languages.keys():
            raise KeyError("`%s` language code doesn't exist" % code)
        name = self.languages[code]
        del self.languages[code]
        self.langs.pop(self.langs.index({'code': code, 'name': name}))

    def get_language_name(self, code):
        """
        Returns the name of a language.
        """
        code = normalize_code(code)
        return self.languages.get(code, '???')

    def get_all_languages(self):
        return self.langs

class NyPortalLanguageManager(Persistent):

    implements(ILanguageAvailability)

    def __init__(self, default_langs=[('en', 'English')]):
        if not isinstance(default_langs, list):
            raise ValueError("Default languages must be a list of touples"
                             " (code, name)")
        self.portal_languages = PersistentList(default_langs)

    def getAvailableLanguages(self):
        """Return a sequence of language tags for available languages
        """
        return tuple([ x[0] for x in self.portal_languages ])

    def addAvailableLanguage(self, lang_code, lang_name=None):
        """Adds available language in portal"""
        lang_code = normalize_code(lang_code)
        if not lang_name:
            n = NyLanguages()
            lang_name = n.get_language_name(lang_code)
        if lang_code not in self.getAvailableLanguages():
            self.portal_languages.append((lang_code, lang_name))

    def delAvailableLanguage(self, lang):
        lang = normalize_code(lang)
        pos = list(self.getAvailableLanguages()).index(lang)
        if pos > -1:
            if len(self.getAvailableLanguages()) == 1:
                raise ValueError("Can not delete the only available language")
            else:
                self.portal_languages.pop(pos)

    # MORE:
    def set_default_language(self, lang):
        lang = normalize_code(lang)
        if lang not in self.getAvailableLanguages():
            raise ValueError("Language %s is not provided by portal" % lang)
        available = list(self.getAvailableLanguages())
        if len(available)==1:
            return
        pos = available.index(lang)
        new_default = self.portal_languages.pop(pos)
        self.portal_languages.insert(0, new_default)

    def get_default_language(self):
        return self.portal_languages[0][0]

    def get_language_name(self, code):
        pos = list(self.getAvailableLanguages()).index(code)
        if pos > -1:
            return self.portal_languages[pos][1]
        else:
            return "???"
