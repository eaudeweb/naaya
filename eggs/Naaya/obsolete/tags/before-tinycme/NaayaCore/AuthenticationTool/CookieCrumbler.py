#
# Thanks to Zope Corporation people for the CookieCrumbler product

""" CookieCrumbler """

from base64 import encodestring, decodestring
from urllib import quote, unquote
import sys

from Acquisition import aq_inner, aq_parent
from DateTime import DateTime
from AccessControl import ClassSecurityInfo, getSecurityManager
from ZPublisher import BeforeTraverse
from zLOG import LOG, ERROR
from ZPublisher.HTTPRequest import HTTPRequest
from Globals import InitializeClass

try:
    from zExceptions import Redirect
except ImportError:
    # Pre Zope 2.7
    Redirect = 'Redirect'

# Constants.
ATTEMPT_NONE = 0       # No attempt at authentication
ATTEMPT_LOGIN = 1      # Attempt to log in
ATTEMPT_RESUME = 2     # Attempt to resume session


class CookieCrumblerDisabled (Exception):
    """Cookie crumbler should not be used for a certain request"""


class CookieCrumbler:
    """ Reads cookies during traversal and simulates the HTTP  authentication headers."""

    auth_cookie = '__ac'
    name_cookie = '__ac_name'
    pw_cookie = '__ac_password'
    persist_cookie = '__ac_persistent'
    auto_login_page = 'login_html'
    unauth_page = 'unauthorized_html'
    logout_page = 'logout_html'
    local_cookie_path = 0
    cache_header_value = 'no-cache'

    security = ClassSecurityInfo()

    def __init__(self):
        pass
    
    security.declarePrivate('delRequestVar')
    def delRequestVar(self, req, name):
        # No errors of any sort may propagate, and we don't care *what*
        # they are, even to log them.
        try: del req.other[name]
        except: pass
        try: del req.form[name]
        except: pass
        try: del req.cookies[name]
        except: pass
        try: del req.environ[name]
        except: pass

    security.declarePublic('getCookiePath')
    def getCookiePath(self):
        if not self.local_cookie_path:
            return '/'
        parent = aq_parent(aq_inner(self))
        if parent is not None:
            return '/' + parent.absolute_url(1)
        else:
            return '/'

    # Allow overridable cookie set/expiration methods.
    security.declarePrivate('getCookieMethod')
    def getCookieMethod(self, name, default=None):
        return getattr(self, name, default)

    security.declarePrivate('defaultExpireAuthCookie')
    def defaultExpireAuthCookie(self, resp, cookie_name):
        resp.expireCookie(cookie_name, path=self.getCookiePath())

    security.declarePrivate('defaultSetAuthCookie')
    def defaultSetAuthCookie(self, resp, cookie_name, cookie_value):
        kw = {}
        req = getattr(self, 'REQUEST', None)
        if req is not None and req.get('SERVER_URL', '').startswith('https:'):
            # Ask the client to send back the cookie only in SSL mode
            kw['secure'] = 'y'
        resp.setCookie(cookie_name, cookie_value,
                       path=self.getCookiePath(), **kw)

    security.declarePrivate('modifyRequest')
    def modifyRequest(self, req, resp):
        """ Copies cookie-supplied credentials to the basic auth fields.

        Returns a flag indicating what the user is trying to do with
        cookies: ATTEMPT_NONE, ATTEMPT_LOGIN, or ATTEMPT_RESUME.  If
        cookie login is disabled for this request, raises
        CookieCrumblerDisabled.
        """
        if (req.__class__ is not HTTPRequest
            or not req['REQUEST_METHOD'] in ('HEAD', 'GET', 'PUT', 'POST')
            or req.environ.has_key('WEBDAV_SOURCE_PORT')):
            raise CookieCrumblerDisabled

        # attempt may contain information about an earlier attempt to
        # authenticate using a higher-up cookie crumbler within the
        # same request.
        attempt = getattr(req, '_cookie_auth', ATTEMPT_NONE)

        if attempt == ATTEMPT_NONE:
            if req._auth:
                # An auth header was provided and no cookie crumbler
                # created it.  The user must be using basic auth.
                raise CookieCrumblerDisabled

            if req.has_key(self.pw_cookie) and req.has_key(self.name_cookie):
                # Attempt to log in and set cookies.
                attempt = ATTEMPT_LOGIN
                name = req[self.name_cookie]
                pw = req[self.pw_cookie]
                ac = encodestring('%s:%s' % (name, pw)).rstrip()
                req._auth = 'Basic %s' % ac
                resp._auth = 1
                if req.get(self.persist_cookie, 0):
                    # Persist the user name (but not the pw or session)
                    expires = (DateTime() + 365).toZone('GMT').rfc822()
                    resp.setCookie(self.name_cookie, name,
                                   path=self.getCookiePath(),
                                   expires=expires)
                else:
                    # Expire the user name
                    resp.expireCookie(self.name_cookie,
                                      path=self.getCookiePath())
                method = self.getCookieMethod( 'setAuthCookie'
                                             , self.defaultSetAuthCookie )
                method( resp, self.auth_cookie, quote( ac ) )
                self.delRequestVar(req, self.name_cookie)
                self.delRequestVar(req, self.pw_cookie)

            elif req.has_key(self.auth_cookie):
                # Attempt to resume a session if the cookie is valid.
                # Copy __ac to the auth header.
                ac = unquote(req[self.auth_cookie])
                if ac and ac != 'deleted':
                    try:
                        decodestring(ac)
                    except:
                        # Not a valid auth header.
                        pass
                    else:
                        attempt = ATTEMPT_RESUME
                        req._auth = 'Basic %s' % ac
                        resp._auth = 1
                        self.delRequestVar(req, self.auth_cookie)
                        method = self.getCookieMethod(
                            'twiddleAuthCookie', None)
                        if method is not None:
                            method(resp, self.auth_cookie, quote(ac))

        req._cookie_auth = attempt
        return attempt

    def __call__(self, container, req):
        """ The __before_publishing_traverse__ hook. """
        resp = self.REQUEST['RESPONSE']
        try:
            attempt = self.modifyRequest(req, resp)
        except CookieCrumblerDisabled:
            return
        if req.get('disable_cookie_login__', 0):
            return

        if (self.unauth_page or
            attempt == ATTEMPT_LOGIN or attempt == ATTEMPT_NONE):
            # Modify the "unauthorized" response.
            req._hold(ResponseCleanup(resp))
            resp.unauthorized = self.unauthorized
            resp._unauthorized = self._unauthorized
        if attempt != ATTEMPT_NONE:
            # Trying to log in or resume a session
            if self.cache_header_value:
                # we don't want caches to cache the resulting page
                resp.setHeader('Cache-Control', self.cache_header_value)
                # demystify this in the response.
                resp.setHeader('X-Cache-Control-Hdr-Modified-By',
                               'CookieCrumbler')
            phys_path = self.getPhysicalPath()
            if self.logout_page:
                # Cookies are in use.
                page = getattr(container, self.logout_page, None)
                if page is not None:
                    # Provide a logout page.
                    req._logout_path = phys_path + ('logout',)
            req._credentials_changed_path = (
                phys_path + ('credentialsChanged',))

    security.declarePublic('credentialsChanged')
    def credentialsChanged(self, name, pw):
        ac = encodestring('%s:%s' % (name, pw)).rstrip()
        method = self.getCookieMethod( 'setAuthCookie'
                                       , self.defaultSetAuthCookie )
        resp = self.REQUEST['RESPONSE']
        method( resp, self.auth_cookie, quote( ac ) )

    def _cleanupResponse(self):
        resp = self.REQUEST['RESPONSE']
        # No errors of any sort may propagate, and we don't care *what*
        # they are, even to log them.
        try: del resp.unauthorized
        except: pass
        try: del resp._unauthorized
        except: pass
        return resp

    security.declarePrivate('unauthorized')
    def unauthorized(self):
        resp = self._cleanupResponse()
        # If we set the auth cookie before, delete it now.
        if resp.cookies.has_key(self.auth_cookie):
            del resp.cookies[self.auth_cookie]
        # Redirect if desired.
        url = self.getUnauthorizedURL()
        if url is not None:
            raise Redirect, url
        # Fall through to the standard unauthorized() call.
        resp.unauthorized()

    def _unauthorized(self):
        resp = self._cleanupResponse()
        # If we set the auth cookie before, delete it now.
        if resp.cookies.has_key(self.auth_cookie):
            del resp.cookies[self.auth_cookie]
        # Redirect if desired.
        url = self.getUnauthorizedURL()
        if url is not None:
            resp.redirect(url, lock=1)
            # We don't need to raise an exception.
            return
        # Fall through to the standard _unauthorized() call.
        resp._unauthorized()

    security.declarePublic('getUnauthorizedURL')
    def getUnauthorizedURL(self):
        """ Redirects to the login page. """
        req = self.REQUEST
        url = req.URL
        resp = req['RESPONSE']
        attempt = getattr(req, '_cookie_auth', ATTEMPT_NONE)
        if url.endswith('manage') or url.endswith('manage_workspace') or url.endswith('manage_main'):
            return None
        if attempt == ATTEMPT_NONE:
            # An anonymous user was denied access to something.
            page_id = self.auto_login_page
            retry = ''
        elif attempt == ATTEMPT_LOGIN:
            # The login attempt failed.  Try again.
            page_id = self.auto_login_page
            retry = '1'
        else:
            # An authenticated user was denied access to something.
            page_id = self.unauth_page
            retry = ''
        if page_id:
            #page = self.restrictedTraverse(page_id, None)
            page = "%s/%s" % (self.absolute_url(), page_id)
            came_from = req.get('came_from', None)
            if came_from is None:
                came_from = req.get('URL', '')
                query = req.get('QUERY_STRING')
                if query:
                    # Include the query string in came_from
                    if not query.startswith('?'):
                        query = '?' + query
                    came_from = came_from + query
            url = '%s?came_from=%s&retry=%s&disable_cookie_login__=1' % (
                page, quote(came_from), retry)
            return url
        return None

    # backward compatible alias
    getLoginURL = getUnauthorizedURL

    security.declarePublic('logged_in')
    def logged_in(self, REQUEST, RESPONSE):
        """ """
        isAnonymous = self.isAnonymousUser()
        came_from = REQUEST.get('came_from', '')
        
        if isAnonymous:
            url = self.unauthorized()
            return RESPONSE.redirect("%s%s" % (self.auto_login_page,url))
        else:
            if came_from:
                return RESPONSE.redirect(came_from)
            else:
                #redirect in expert area
                #return RESPONSE.redirect(self.absolute_url(0))
                #redirect to welcome page
                return self.admin_welcome_page(REQUEST=REQUEST)

    security.declarePublic('logout')
    def logout(self):
        """  Logs out the user and redirects to the logout page. """
        req = self.REQUEST
        resp = req['RESPONSE']
        method = self.getCookieMethod( 'expireAuthCookie'
                                     , self.defaultExpireAuthCookie )
        method( resp, cookie_name=self.auth_cookie )
        if self.logout_page:
            page = "%s/%s" % (self.absolute_url(), self.auto_login_page)
            resp.redirect('%s?disable_cookie_login__=1' % page)
            return ''
        # We should not normally get here.
        return 'Logged out.'

    security.declarePrivate('_getAuthenticatedUser')
    def _getAuthenticatedUser(self):
        return getSecurityManager().getUser()

    security.declarePublic('isAnonymousUser')
    def isAnonymousUser(self):
        ''' Returns 1 if the user is not logged in.  '''
        u = self._getAuthenticatedUser()
        if u is None or u.getUserName() == 'Anonymous User':
            return 1
        return 0

InitializeClass(CookieCrumbler)


class ResponseCleanup:
    def __init__(self, resp):
        self.resp = resp

    def __del__(self):
        # Free the references.
        #
        # No errors of any sort may propagate, and we don't care *what*
        # they are, even to log them.
        try: del self.resp.unauthorized
        except: pass
        try: del self.resp._unauthorized
        except: pass
        try: del self.resp
        except: pass
