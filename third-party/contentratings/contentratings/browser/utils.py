import random
from zope.interface import implements
from contentratings.browser.interfaces import IAnonymousSession

class AnonSessionUtil(object):
    """A utility to create a unique key for an anonymous browser::

        >>> from contentratings.browser.utils import AnonSessionUtil
        >>> anon_session = AnonSessionUtil()
        >>> from zope.publisher.browser import TestRequest
        >>> req = TestRequest(REMOTE_ADDR='127.0.0.1')

    If it appears cookies are disabled, we should ge the IP::

        >>> anon_session.get_anon_key(req)
        '127.0.0.1'

    Otherwise we get a generated key::

        >>> req = TestRequest(REMOTE_ADDR='127.0.0.1', HTTP_COOKIE='_ZopeId=1;')
        >>> key = anon_session.get_anon_key(req)
        >>> key != '127.0.0.1'
        True
        >>> len(key) == 32
        True

    This should also have set a cookie::

        >>> req.response.getHeaders() # doctest: +ELLIPSIS
        [('X-Powered-By', 'Zope (www.zope.org), Python (www.python.org)'), ('Set-Cookie', 'contentratings=...; expires=Mon, 31 Dec 2035 23:00:01 GMT;')]

    """

    def get_anon_key(self, request):
        """Borrowed from iqpp.plone.rating, this is very Zope2-y
        but it's better than a straight cookie check.
        """
        # If cookies are enabled we assume that some cookie is set
        # (e.g. a session cookie, or _ZopeId).  If disabled use the
        # IP, which will undercount proxies which have multiple users
        # with cookies disabled
        if not request.cookies:
            return request.get("REMOTE_ADDR")

        # First we try to get the session id out of a cookie. If there
        # is none, we get the session id out of the request and create
        # a cookie.
        sid = request.cookies.get("contentratings", None)
        if sid is None:
            # random 256 bit string, because SESSION has unnecessary
            # overhead.  This should be sufficient to differentiate
            # browsers.  Users who delete this cookie can rate again,
            # but the same is true with SESSION if the user removes
            # the cookie and restarts the browser.
            sid =''.join(random.choice('ABCDEF0123456789') for x in xrange(32))
            request.response.setCookie(
                "contentratings",
                sid,
                expires="Mon, 31 Dec 2035 23:00:01 GMT")

        return sid
