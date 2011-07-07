
# Zope imports
from zope.interface import implements
from zope.i18n.interfaces import (ITranslationDomain,
                                  IModifiableUserPreferredLanguages)
from zope.i18n import interpolate
from zope.component import adapts
from Persistence import Persistent

# Naaya imports
try:
    from Products.NaayaCore.constants import ID_TRANSLATIONSTOOL
except ImportError:
    ID_TRANSLATIONSTOOL = 'portal_translations'

# Product imports
from naaya.i18n.interfaces import (INyTranslationCatalog, INyLanguageManagement)

# Localizer imports
from Products.Localizer.patches import get_request
from Products.Localizer.utils import lang_negotiator


class LocalizerWrapper(Persistent):
    implements(INyTranslationCatalog, INyLanguageManagement,
               IModifiableUserPreferredLanguages, ITranslationDomain)

    def __init__(self, portal):
        self.cat = portal._getOb(ID_TRANSLATIONSTOOL)
        self.loc = portal.getLocalizer()

    ### INyTranslationCatalog

    def edit_message(self, msgid, lang, translation):
        """ """
        # language existance test **not present in Localizer**:
        if lang not in self.get_languages():
            return
        # Add-by-edit functionality **not present in Localizer**:
        if not self.cat.message_exists(msgid):
            self.cat.gettext(msgid, lang, add=1)

        self.cat.message_edit(msgid, lang, translation,
                              note="`Note` not present in INyTranslationCatalog")

    def del_message(self, msgid):
        """ """
        self.cat.message_del(msgid)

    def gettext(self, msgid, lang, default=None):
        """Returns the corresponding translation of msgid in Catalog."""
        # language existance test **not present in Localizer**:
        if lang not in self.get_languages():
            add = 0
        else:
            add = 1
        try:
            return self.cat.gettext(msgid, lang, add=add, default=default)
        except KeyError:
            # when add = 0 and msgid not in catalog
            return default or msgid

    def get_languages(self):
        """Get available languages"""
        return self.cat.get_languages() # actually inherited from
        # LanguageManager, where inherited from Multilingual

    def add_language(self, lang):
        """Add language"""
        self.cat.manage_addLanguage(lang) # same comment as in get_languages

    def del_language(self, lang):
        """Delete language with corresponding messages"""
        self.cat.del_language(lang) # inh. from LanguageManager, inh.
        # from Multilingual. LanguageManager only has a manage_ method
        # which requires REQUEST and RESPONSE

        # lang deletion also removes translations **not present in Localizer**
        for msgid in self.cat._messages.keys():
            if self.cat._messages[msgid].has_key(lang):
                del self.cat._messages[msgid][lang]

    def clear(self):
        """Erase all messages"""
        for msgid in self.cat._messages.keys():
            self.del_message(msgid)

    def messages(self):
        """
        Returns a generator used for catalog entries iteration.
        """
        for msgid in self.cat._messages.keys():
            yield msgid

### ILanguageManagement

    def getAvailableLanguages(self):
        """Return a sequence of language tags for available languages
        """
        return tuple(self.loc.get_supported_languages())

    def addAvailableLanguage(self, lang):
        """Adds available language in portal"""
        self.loc.add_language(lang)

    def delAvailableLanguage(self, lang):
        # ValueError if last language **not present in Localizer**
        crt = self.loc.get_supported_languages()
        if len(crt) == 1 and crt[0] == lang:
            raise ValueError
        else:
            self.loc.del_language(lang)

### IModifiableUserPreferredLanguages

    def getPreferredLanguages(self):
        """Return a sequence of user preferred languages.

        The sequence is sorted in order of quality, with the most preferred
        languages first.
        """
        # TODO: localizer only returns one language
        return tuple(self.loc.get_selected_language())

    def setPreferredLanguages(self, languages):
        """Set a sequence of user preferred languages.

        The sequence should be sorted in order of quality, with the most
        preferred languages first.
        """
        # TODO: localizer only sets one language (in cookie)
        self.loc.changeLanguage(languages[0])

    def translate(self, msgid, mapping=None, context=None, target_language=None,
                  default=None):
        """
        * `context` is used in negotiaton - IUserPreferredLanguages(context)
        * `mapping` requires interpolation process
        """
        if target_language is None:
            #target_language = negotiate(self.context.get_languages(), context)
            target_language = lang_negotiator(self.get_languages())
        text = self.gettext(msgid, target_language, default)
        return interpolate(text, mapping)
