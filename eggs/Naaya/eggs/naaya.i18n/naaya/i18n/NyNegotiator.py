
# Zope imports
from zope.i18n.interfaces import INegotiator
from zope.interface import implements
from ZPublisher.Request import Request
from patches import get_request

# Product imports
from LanguageManagers import normalize_code

class NyNegotiator(object):
    implements(INegotiator)

    def __init__(self, cookie_id='LOCALIZER_LANGUAGE',
                 policy=('path', 'url', 'cookie', 'browser'),
                 request=None):
        """
            * `cookie_id` is a key looked up in cookies/querystrings
            * `policy` can be 'browser', 'url', 'path', 'cookie',
            or any combination as a list of priorities
        """
        self.cookie_id = cookie_id
        self.request = request
        if not isinstance(self.request, Request):
            self.request = get_request()
        self.set_policy(policy)

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
    def getLanguage(self, available, request=None, fallback=True):
        """
        Returns the language dependent on the policy.

        If `fallback` is True (default), return first av. language on failure.
        If `fallback` is False, return None on failure, let third party app
        choose an app-dependant default (eg get_default_language() in portal)
        """
        if request is None:
            if self.request is not None:
                request = self.request
            else:
                raise ValueError("No request to manage negotiation")
        available = map(normalize_code, available)
        # here we keep {'xx': 'xx-zz'} for xx-zz, for fallback cases
        secondary = {}
        for x in [av for av in available if av.find("-") > -1]:
            secondary[x.split("-", 1)[0]] = x

        AcceptLanguage = request.get('HTTP_ACCEPT_LANGUAGE', '')
        if AcceptLanguage is None:
            AcceptLanguage = ''

        cookie = request.cookies.get(self.cookie_id, '')
        url = request.form.get(self.cookie_id, '')
        path = request.get(self.cookie_id, '')

        client_langs = {'browser': normalize_code(AcceptLanguage),
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
            lang = client_langs[policy]
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
        if fallback:
            return available[0]
        else:
            return None
