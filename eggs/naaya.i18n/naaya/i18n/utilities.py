"""
ITranslationDomain utilities:
 * transitional NyLocalizerTranslator, for old edw-Localizer compliance
 * NyI18nTranslator
"""

from zope.interface import implementer
from zope.i18n.interfaces import ITranslationDomain
from zope.i18n import interpolate
from zope.publisher.http import HTTPCharsets


@implementer(ITranslationDomain)
class NyI18nTranslator(object):


    def translate(self, msgid, mapping=None, context=None,
                  target_language=None, default=None):
        """
            Implementation of ITranslationDomain.translate using portal_i18n
        """
        try:
            site = context['PARENTS'][0].getSite()
        except AttributeError:
            # not in INySite context, fallback to identity translation
            return interpolate(default or msgid, mapping)
        tool = site.getPortalI18n()
        if target_language is None:
            available = tool.get_lang_manager().getAvailableLanguages()
            target_language = tool.get_negotiator().getLanguage(available,
                                                                context)
        if default is not None:
            raw = tool.get_message_catalog().gettext(msgid, target_language,
                                                     default=default)
        else:
            raw = tool.get_message_catalog().gettext(msgid, target_language)
        return interpolate(raw, mapping)


class NyHTTPCharsets(HTTPCharsets):

    def __init__(self, request):
        self.request = request

    def getPreferredCharsets(self):
        """
        If HTTPHeader is missing or empty, default to 'utf-8',
        'iso-8859-1' and then everything that goes.
        Otherwise keep publisher's utility logic.

        """
        header = self.request.get('HTTP_ACCEPT_CHARSET', '')
        if not header:
            return ['utf-8', 'iso-8859-1', '*']
        return super(NyHTTPCharsets, self).getPreferredCharsets()
