"""
This modules provides procedures for obtaining all available languages
in different formats and a class to store available languages in a portal.

"""

import os.path
import re

from zope.interface import implements
from Persistence import Persistent
from persistent.list import PersistentList

from interfaces import INyLanguageManagement


def normalize_code(code):
    not_letter = re.compile(r'[^a-z]+', re.IGNORECASE)
    parts = re.sub(not_letter, '-', code).split('-', 1)
    parts[0] = parts[0].lower()
    if len(parts) > 1:
        return parts[0] + '-' + parts[1].upper()
    else:
        return parts[0]

def get_languages_list():
    languages = {}
    cwd = __file__.rsplit(os.path.sep, 1)[0]
    filename = os.path.join(cwd, 'languages.txt')
    for line in open(filename).readlines():
        line = line.strip()
        if line and line[0] != '#':
            code, name = line.split(' ', 1)
            languages[normalize_code(code)] = name

    return languages

def get_languages():
    languages = get_languages_list()
    language_codes = languages.keys()
    language_codes.sort()
    return[ {'code': x, 'name': languages[x]} for x in language_codes ]

def get_language_name(code):
    """
    Returns the name of a language. In order to return the name of a custom
    language added in portal, use get_language_name on portal_i18n portal tool

    """
    code = normalize_code(code)
    return get_languages_list().get(code, '???')


class NyPortalLanguageManager(Persistent):
    """
    Portal_i18n has an instance of this type, accessible by *get_lang_manager()*
    method. It supplies add/edit/remove/set_default operations with languages
    available in portal and it is also used to get current available
    languages and default language.

    """
    implements(INyLanguageManagement)


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
            lang_name = get_language_name(lang_code)
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
