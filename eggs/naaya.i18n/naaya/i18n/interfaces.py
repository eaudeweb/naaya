# Zope imports
from zope.interface import Interface
from zope.i18n.interfaces import ILanguageAvailability

class INyTranslationCatalog(Interface):


    def edit_message(msgid, lang, translation):
        """ """

    def del_message(msgid):
        """ """

    def gettext(msgid, lang, default=None):
        """Returns the corresponding translation of msgid in Catalog."""

    def get_languages():
        """Get available languages"""

    def add_language(lang):
        """Add language"""

    def del_language(lang):
        """Delete language with corresponding messages"""

    def clear():
        """Erase all messages"""

    def messages():
        """
        Returns a generator used for catalog entries iteration.
        """

class INyLanguageManagement(ILanguageAvailability):

    """ILanguageAvailability only provides method for reading available
    languages. We also need an api to manage them.

    Obs: the order of languages is the adding order, no api for ordering"""

    def addAvailableLanguage(lang):
        """Adds available language in portal"""

    def delAvailableLanguage(lang):
        """Removes a currently available language in portal"""


class IMessageAddEvent(Interface):
    """ New message added to catalog """
