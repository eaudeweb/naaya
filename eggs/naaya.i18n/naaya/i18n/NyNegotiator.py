"""
NyNegotiator handles negotiation using available languages and
request passed to getLanguage.
It is initialized in portal_tool and in LocalPropertyManager, when
selecting language for a localized property.

* `cookie_id` is used from constants.COOKIE_ID
* `policy` is a hardcoded list/tuple of priorities

"""

from zope.i18n.interfaces import INegotiator
from zope.interface import implements
from ZPublisher.Request import Request

from LanguageManagers import normalize_code
from constants import COOKIE_ID

class NyNegotiator(object):
    """
    Implementation of i18n negotiator, using cache on Request,
    with available policies:

    * `path` - language code present in url, after portal
    * `url` - language code in querystring
    * `cookie` - language setting saved in cookie
    * `browser` - HTTP_ACCEPT_LANGUAGE header

    Performs negotiation and sets preferred language in cookie.

    """

    implements(INegotiator)

    def __init__(self):
        """
        Loading default configuration
        """
        self.cookie_id = COOKIE_ID
        self.set_policy(('path', 'url', 'cookie', 'browser'))

    def set_policy(self, policy):
        if isinstance(policy, str):
            policy = (policy, )
        else:
            policy = tuple(policy)
        for opt in policy:
            if opt not in ('browser', 'url', 'path', 'cookie'):
                raise ValueError('Invalid component for policy: "%s"' % opt)
        self.policy = policy

    def _get_cache_key(self, available, client_langs):
        return (','.join(self.policy) + '/' + ','.join(available) +
                '/' + repr(client_langs))

    def _update_cache(self, cache_key, lang, request):
        if not request.has_key(self.cookie_id + '_cache'):
            request[self.cookie_id + '_cache'] = {}
        request[self.cookie_id + '_cache'][cache_key] = lang

    def _query_cache(self, cache_key, request):
        if (request.has_key(self.cookie_id + '_cache') and
            request[self.cookie_id + '_cache'].has_key(cache_key) and
            request[self.cookie_id + '_cache'][cache_key]):
            return request[self.cookie_id + '_cache'][cache_key]
        else:
            return None

    # INegotiator interface:
    def getLanguage(self, available, request, fallback=True):
        """
        Returns the best matching language based on `available` languages,
        preferred languages in `request` and negotiation policies.

        If `fallback` is True (default), return first available
        language on failure.
        If `fallback` is False, return None on failure, let third party app
        choose an app-dependant default (e.g. get_default_language() in portal)

        """
        available = map(normalize_code, available)
        # here we keep {'xx': 'xx-zz'} for xx-zz, for fallback cases
        secondary = {}
        for x in [av for av in available if av.find("-") > -1]:
            secondary[x.split("-", 1)[0]] = x

        accept_langs = request.get('HTTP_ACCEPT_LANGUAGE', '')
        if accept_langs in (None, ''):
            accept_langs = []
        else:
            accept_langs = accept_langs.split(';', 1)[0].split(',')

        cookie = request.cookies.get(self.cookie_id, '')
        url = request.form.get(self.cookie_id, '')
        path = request.get(self.cookie_id, '')

        client_langs = {'browser': map(normalize_code, accept_langs),
                        'url': normalize_code(url),
                        'path': normalize_code(path),
                        'cookie': normalize_code(cookie)}

        # compute place in cache and check cache
        key = self._get_cache_key(available, client_langs)
        cached_value = self._query_cache(key, request)
        # 2nd assertion: one last check, just to make sure it's valid
        if cached_value is not None and cached_value in available:
            return cached_value

        for policy in self.policy:
            langs = client_langs[policy]
            if not isinstance(langs, list):
                langs = [langs, ]
            for lang in langs:
                if lang in available:
                    self._update_cache(key, lang, request)
                    return lang
                elif lang.find("-") > -1:
                    first_code = lang.split("-", 1)[0]
                    # if xx-yy not found, but xx is available, return xx
                    if first_code in available:
                        return first_code
                    # if xx-yy not found, but xx-zz is available, return xx-zz
                    elif first_code in secondary.keys():
                        return secondary[first_code]
        if fallback and available:
            return available[0]
        else:
            return None

    def change_language(self, lang, context, request):
        """ Changes the cookie value for COOKIE_ID to specified language """
        response = request.RESPONSE
        parent = context.aq_parent
        path = parent.absolute_url()[len(request['SERVER_URL']):] or '/'
        response.setCookie(self.cookie_id, lang, path=path)
