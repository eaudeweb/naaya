"""
Since portal_translations (Products.NaayaCore.TranslationsTool)
was removed from Naaya portal, we needed to build a wrapper
to serve the old API of portal/getPortalTranslations currently in use.
TranslationsToolWrapper is initialized in NySite.getPortalTranslations
within context, with getPortalI18n() as argument (wrapped object).

"""
from zope.i18n.interfaces import ITranslationDomain
from zope.component import queryUtility
from zope.deprecation import deprecate
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Acquisition import Implicit


class TranslationsToolWrapper(Implicit):

    security = ClassSecurityInfo()

    def __init__(self, portal_i18n):
        self.portal_i18n = portal_i18n

    security.declarePublic('trans')
    @deprecate(("Portal Translations/trans is deprecated, use "
                "portal.getPortalI18n().get_translation(msg, **kwargs)"))
    def trans(self, msg, **kwargs):
        """ Translate message and interpolate using kwargs mapping """
        return self.portal_i18n.get_translation(msg, **kwargs)

    security.declarePublic('gettext')
    @deprecate(("Portal Translations/gettext is deprecated, use "
        "portal.getPortalI18n().get_translation(msg, **kwargs)"))
    def gettext(self, message, lang=None, add=1, default=None):
        if not lang:
            lang = self.portal_i18n.get_selected_language()
        message_catalog = self.portal_i18n.get_message_catalog()
        return message_catalog.gettext(message, lang, default)


    security.declarePublic('__call__')
    def __call__(self, message, lang=None, add=1, default=None):
        """ use getPortalTranslations instance as gettext callable """
        return self.portal_i18n.get_translation(message, lang=lang,
                                                add=add, default=default)

    ## used to be in Localizer/MessageCatalog
    # In Naaya: Session messages are translated using this
    security.declarePublic('translate')
    @deprecate(("Translate method shouldn't be called on message catalog;"
                " call the translate of ITranslationDomain utility, or use "
                "portal.getPortalI18n().get_translation(msg, **kwargs)"))
    def translate(self, domain, msgid, *args, **kw):
        """This method is required to get the i18n namespace from ZPT working.
        """

        if domain is None or domain == '':
            domain = 'default'
        ut = queryUtility(ITranslationDomain, domain)
        kw['context'] = self.REQUEST
        return ut.translate(msgid, **kw)

InitializeClass(TranslationsToolWrapper)
