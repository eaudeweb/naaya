"""
This is the main data type for translation storage. NyMessageCatalog implements
:py:class:`~naaya.i18n.interfaces.INyTranslationCatalog`
Its implementation is based on indexing msgid-s and their translations
in a PersistentMapping.

"""
import logging
import re

try:
    # zope 2.12
    from Persistence import PersistentMapping
except ImportError:
    # zope <= 2.11
    from Globals import PersistentMapping
from Persistence import Persistent
from zope.interface import implements
from zope.event import notify

from naaya.core.utils import force_to_unicode

from interfaces import INyTranslationCatalog
from events import MessageAddEvent


def collapse_whitespace(text):
    """
    Strips, replaces new line with spaces and collapses multiple spaces

    """
    text = text.strip()
    return re.sub(r'\s+', ' ', text)


class NyMessageCatalog(Persistent):
    """Stores messages and their translations"""

    implements(INyTranslationCatalog)


    def __init__(self, id, title, languages=('en', )):

        self.id = id
        self.title = title

        # Language Manager data
        self._languages = tuple(languages)

        # We suppose all zope/portal products are written in English
        # therefore we consider all new messages in English
        # Default language in Catalog is always 'en', thus it can be different
        # from the default language of the portal
        self._default_language = 'en' # self._languages[0]

        # Here the message translations are stored
        self._messages = PersistentMapping()
        self._po_headers = PersistentMapping()

    ### INyTranslationCatalog

    def edit_message(self, msgid, lang, translation):
        """Edits or adds message with `translation` in `lang` language"""
        # input type sanitize
        logger = logging.getLogger(__name__)
        if isinstance(msgid, str):
            msgid = force_to_unicode(msgid)
        if isinstance(translation, str):
            translation = force_to_unicode(translation)
        # language existance test
        if lang not in self.get_languages():
            return
        # Add-by-edit functionality
        if not self._messages.has_key(msgid):
            self.gettext(msgid, lang)
        self._messages[msgid][lang] = collapse_whitespace(translation)

    def del_message(self, msgid):
        """Deletes message and its translations from catalog"""
        if self._messages.has_key(msgid):
            del self._messages[msgid]

    def gettext(self, msgid, lang=None, default=None):
        """Returns the corresponding translation of msgid in Catalog."""
        if not isinstance(msgid, basestring):
            raise TypeError('Only strings can be translated.')
        # saving everything unicode, utf-8
        elif isinstance(msgid, str):
            msgid = force_to_unicode(msgid)
        if not lang:
            raise ValueError("No language provided for gettext")
        msgid = msgid.strip()
        # empty message is translated as empty message, regardless of lang
        if not msgid:
            return msgid
        # default `default translation` is the msgid itself
        if default is None:
            default = msgid

        if lang not in self.get_languages():
            # we don't have that lang, thus we can't translate and won't add msg
            return default

        # Add it if it's not in the dictionary
        if not self._messages.has_key(msgid):
            self._messages[msgid] = PersistentMapping()
            notify(MessageAddEvent(self, msgid, lang, default))

        if not self._messages[msgid].has_key(self._default_language):
            default_translation = collapse_whitespace(default)
            self._messages[msgid][self._default_language] = default_translation

        # translation may be blank (supposition), then-> default (usually msgid)
        in_catalog = self._messages[msgid].get(lang, '')
        return in_catalog or default

    def get_languages(self):
        """Get available languages"""
        return self._languages

    def add_language(self, lang):
        """Add language"""
        if lang not in self._languages:
            self._languages = self._languages + (lang, )

    def del_language(self, lang):
        """Delete language with corresponding messages"""
        if lang not in self.get_languages():
            return
        langlist = list(self._languages)
        langlist.pop(langlist.index(lang))
        self._languages = tuple(langlist)

    def clear(self):
        """Erase all messages"""
        self._messages.clear()

    def messages(self):
        """
        Returns a generator used for catalog entries iteration.
        """
        for (msgid, translations_dict) in self._messages.items():
            yield (msgid, translations_dict)

    ### Dictionary-like API

    def __getitem__(self, key):
        return self._messages[key]

    def __delitem__(self, key):
        del self._messages[key]
