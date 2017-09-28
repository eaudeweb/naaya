
import threading
import logging
logger = logging.getLogger(__name__)

from zope.component import adapts
from zope.publisher.interfaces import IRequest
from ZPublisher.BaseRequest import DefaultPublishTraverse

from Products.Naaya.interfaces import INySite


rename_dict = {
 'Products.Localizer.LocalAttributes LocalAttribute': \
     'naaya.i18n.LocalPropertyManager LocalAttribute'
 }


class NySitePublishTraverse(DefaultPublishTraverse):
    adapts(INySite, IRequest)


    def publishTraverse(self, request, name):
        """
        There are 2 patches made on publish:
        * setting Request thread local and adding some i18n-related attributes
        on thread. Useful for i18n operations when OFS context is unavailable.
        * hook for changing language by entering its code in url, after INySite

        """
        portal = self.context
        portal_i18n = portal.getPortalI18n()

        # set Request on thread.local and append i18n info on it
        populate_threading_local(portal, request)

        if portal_i18n is not None:
            lang_manager = portal_i18n.get_lang_manager()
            if name in lang_manager.getAvailableLanguages():
                request[portal_i18n.get_negotiator().cookie_id] = name
                # update selected language, it may be the one found in url
                i18n = get_i18n_context()
                i18n['selected_language'] = portal_i18n.get_selected_language()

                return portal

        return super(NySitePublishTraverse, self).publishTraverse(request, name)


def populate_threading_local(portal, request):
    """
     * Append i18n info on local thread, when OFS context is unavailable
     * Append request on local thread, when request/acquisition is unavailable
    """
    portal_i18n = portal.getPortalI18n()
    if portal_i18n is not None:
        lang_manager = portal_i18n.get_lang_manager()
        i18n = {}
        i18n['default_language'] = lang_manager.get_default_language()
        i18n['languages_mapping'] = portal_i18n.get_languages_mapping()
        i18n['selected_language'] = portal_i18n.get_selected_language()
        set_i18n_context(i18n)

    set_request(request)


thread_data = threading.local()

def set_request(request):
    thread_data.request = request

def get_request():
    return getattr(thread_data, 'request', None)

def set_i18n_context(i18n):
    thread_data.i18n = i18n

def get_i18n_context():
    return getattr(thread_data, 'i18n', None)
