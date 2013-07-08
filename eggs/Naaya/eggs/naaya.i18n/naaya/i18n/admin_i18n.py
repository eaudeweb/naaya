"""
Provides an interface for administration views in Naaya.

"""
import re
import locale
from urllib import quote
from base64 import encodestring, decodestring

from AccessControl.SecurityInfo import ClassSecurityInfo
from Acquisition import Implicit
try:
    # Zope 2.12
    from App.class_init import InitializeClass
except ImportError:
    # Zope <= 2.11
    from Globals import InitializeClass

from constants import PERMISSION_TRANSLATE_PAGES
from LanguageManagers import get_languages


def message_encode(message):
    """
    Encodes a message to an ASCII string.

    To be used in the user interface, to avoid problems with the
    encodings, HTML entities, etc..

    """
    if isinstance(message, unicode):
        message = message.encode('utf-8')

    return encodestring(message)

def message_decode(message):
    """
    Decodes a message from an ASCII string.

    To be used in the user interface, to avoid problems with the
    encodings, HTML entities, etc..

    """
    message = decodestring(message)
    return unicode(message, 'utf-8')


class AdminI18n(Implicit):

    security = ClassSecurityInfo()

    def __init__(self, portal_i18n):
        self.portal_i18n = portal_i18n
        self.catalog = portal_i18n.get_message_catalog()

    ### helper methods

    security.declarePublic('message_decode')
    def message_decode(self, message):
        """
        Decodes a message from an ASCII string.

        To be used in the user interface, to avoid problems with the
        encodings, HTML entities, etc..

        """
        return message_decode(message)

    security.declarePublic('message_encode_and_quote')
    def message_encode_and_quote(self, message):
        """
        Encodes a message in order to be passed as parameter in
        the query string.
        """
        return quote(message_encode(message))

    security.declarePublic('get_message_translation')
    def get_message_translation(self, message, lang, default=None):
        """
        Returns the translation of the given message in the given language,
        as it is stored in Message Catalog (no interpolation).

        """
        return self.catalog.gettext(message, lang, default)

    security.declareProtected(PERMISSION_TRANSLATE_PAGES, 'get_messages')
    def get_messages(self, query, skey, rkey):
        """
        Returns a list of messages, filtered and sorted according with
        the given parameters.
         * `query` - query against the list of messages
         * `skey` - the sorting key
         * `rkey` - indicates if the list must be reversed
        """
        msgs = []
        langs = self.get_languages_mapping()
        if skey == 'msg': skey = 0
        try: regex = re.compile(query.strip().lower())
        except: regex = re.compile('')
        for m, t in self.catalog.messages():
            default = t.get('en', m).strip()
            # Some old messages saved in catalog do not have their
            # default set on 'en' translation
            if not default:
                default = m
            if regex.search(default.lower()):
                if isinstance(m, unicode):
                    m = m.encode('utf-8')
                e = [m]
                i = 1
                for lang in langs:
                    if skey == lang['code']: skey = i
                    e.append(len(t.get(lang['code'], '').strip())>0)
                    i = i + 1
                msgs.append(tuple(e))
        if not isinstance(skey, int): # lang in skey not found
            skey = 0
        #sort messages
        t = [(x[skey], x) for x in msgs]
        if skey == 0:
            #sort by message
            default_locale = locale.setlocale(locale.LC_ALL)
            try:
                locale.setlocale(locale.LC_ALL, 'en_US.utf-8')
            except locale.Error:
                try:
                    locale.setlocale(locale.LC_ALL, 'en')
                except locale.Error:
                    locale.setlocale(locale.LC_ALL, '')
            t.sort(lambda x, y: locale.strcoll(x[0], y[0]))
            locale.setlocale(locale.LC_ALL, default_locale)
        else:
            #sort by translation status
            t.sort()
        if rkey: t.reverse()
        msgs = [val for (key, val) in t]
        return msgs

    security.declarePublic('get_all_languages')
    def get_all_languages(self):
        """
        Returns a list of mappings
        [ {'code': 'lang-code', 'name': 'Language name'}, .. ]
        containing all existent known language codes in naaya.i18n
        as specified in languages.txt, in ISO639 format.

        """
        return get_languages()

    security.declarePublic('get_languages_mapping')
    def get_languages_mapping(self):
        """
        Returns the languages mapping without the English language.
        Remove the entry for the 'code' = 'en'.
        """
        return [{'code': x,
                 'name': self.portal_i18n.get_language_name(x),
                 'default': False}
                    for x in self.catalog.get_languages() if x != 'en']

    security.declareProtected(PERMISSION_TRANSLATE_PAGES,
                              'get_not_translated_messages_count')
    def get_not_translated_messages_count(self, query):
        """
        Returns the number of not translated messages per language.
        """
        langs = self.get_languages_mapping()
        mesgs = self.get_messages(query, 'msg', False)
        not_translated_messages = {}
        if len(langs) == 0 or len(mesgs) == 0:
            return False
        language = 0
        for lang in langs:
            language += 1
            mesg_count = 0
            for mesg in mesgs:
                if not mesg[language]:
                    mesg_count += 1
            not_translated_messages[lang['code']] = mesg_count
        return not_translated_messages

InitializeClass(AdminI18n)
