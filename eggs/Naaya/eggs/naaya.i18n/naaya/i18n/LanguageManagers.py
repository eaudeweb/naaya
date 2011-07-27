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
    """
    Normalizes language code case to ISO639 format, eg. 'en_us' becomes 'en-US'

    """
    not_letter = re.compile(r'[^a-z]+', re.IGNORECASE)
    parts = re.sub(not_letter, '-', code).split('-', 1)
    parts[0] = parts[0].lower()
    if len(parts) > 1:
        return parts[0] + '-' + parts[1].upper()
    else:
        return parts[0]

def get_languages_list():
    """
    Returns a mapping {'lang-code': 'Lang-name', ..} with all languages
    specified in ISO639 format in languages.txt

    """
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
    """
    Returns a list of mappings
    [ {'code': 'lang-code', 'name': 'Language name'}, .. ]
    with all languages specified in ISO639 format in languages.txt

    """
    languages = get_languages_list()
    language_codes = languages.keys()
    language_codes.sort()
    return[ {'code': x, 'name': languages[x]} for x in language_codes ]

def get_iso639_name(code):
    """
    Returns the name of a language.
    Used by get_language_name in portal_i18n tool, in order to
    return the name of a language which is not a custom language
    added in portal (used as fallback or default language name for a code)

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
        """Return a sequence of language tags/codes for available languages
        """
        return tuple([ x[0] for x in self.portal_languages ])

    def addAvailableLanguage(self, lang_code, lang_name=None):
        """Adds available language in portal"""
        lang_code = normalize_code(lang_code)
        if not lang_name:
            lang_name = get_iso639_name(lang_code)
        if lang_code not in self.getAvailableLanguages():
            self.portal_languages.append((lang_code, lang_name))

    def delAvailableLanguage(self, lang):
        """
        Deletes specified language from available languages list in portal

        """
        lang = normalize_code(lang)
        available = list(self.getAvailableLanguages())
        if lang in available:
            if len(self.getAvailableLanguages()) == 1:
                raise ValueError("Can not delete the only available language")
            else:
                pos = available.index(lang)
                self.portal_languages.pop(pos)

    # MORE:
    def set_default_language(self, lang):
        """
        Sets default language in language manager. Default language
        is mainly used in negotiation.

        """
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
        """ Returns default language """
        return self.portal_languages[0][0]

    def get_language_name(self, code):
        """
        Returns the name of a language available in portal, '???' otherwise.

        """
        available = list(self.getAvailableLanguages())
        if code in available:
            pos = available.index(code)
            return self.portal_languages[pos][1]
        else:
            return "???"
