# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency. All
# Rights Reserved.
#
# Authors:
# Cornel Nitu - Finsiel Romania
#
# Thanks to Zope Corporation people for the CookieCrumbler product

""" CookieCrumbler """


from os import path
from urllib import quote, unquote
from base64 import encodestring

from DateTime import DateTime
from ZPublisher.HTTPRequest import HTTPRequest
from AccessControl import ClassSecurityInfo
import Globals

# Constants.
ATTEMPT_DISABLED = -1
ATTEMPT_NONE = 0
ATTEMPT_LOGIN = 1
ATTEMPT_CONT = 2

class CookieCrumbler:
    """ """

    def __init__(self):
        """ """
        pass

    auth_cookie = '__dm'
    name_cookie = '__dm_name'
    pw_cookie = '__dm_password'
    persist_cookie = '__dm_persistent'
    auto_login_page = 'login_html'
    logout_page = 'logout_html'

    security = ClassSecurityInfo()

    #security.declarePrivate('delRequestVar')
    def delRequestVar(self, req, name):
        try: del req.other[name]
        except: pass
        try: del req.form[name]
        except: pass
        try: del req.cookies[name]
        except: pass
        try: del req.environ[name]
        except: pass

    # Allow overridable cookie set/expiration methods.
    #security.declarePrivate('getCookieMethod')
    def getCookieMethod( self, name='setAuthCookie', default=None ):
        return getattr( self.aq_inner.aq_parent, name, default )

    #security.declarePrivate('setDefaultAuthCookie')
    def defaultSetAuthCookie( self, resp, cookie_name, cookie_value ):
        resp.setCookie( cookie_name, cookie_value, path='/')

    #security.declarePrivate('defaultExpireAuthCookie')
    def defaultExpireAuthCookie( self, resp, cookie_name ):
        resp.expireCookie( cookie_name, path='/')

    #security.declarePrivate('modifyRequest')
    def modifyRequest(self, req, resp):
        # Returns flags indicating what the user is trying to do.
        if req.__class__ is not HTTPRequest:
            return ATTEMPT_DISABLED

        if not req[ 'REQUEST_METHOD' ] in ( 'GET', 'PUT', 'POST' ):
            return ATTEMPT_DISABLED

        if not req._auth:
            if (req.has_key(self.pw_cookie) and req.has_key(self.name_cookie)):
                # Attempt to log in and set cookies.
                name = req[self.name_cookie]
                pw = req[self.pw_cookie]
                ac = encodestring('%s:%s' % (name, pw))
                req._auth = 'basic %s' % ac
                resp._auth = 1
                if req.get(self.persist_cookie, 0):
                    # Persist the user name (but not the pw or session)
                    expires = (DateTime() + 365).toZone('GMT').rfc822()
                    resp.setCookie(self.name_cookie, name, path='/', expires=expires)
                else:
                    # Expire the user name
                    resp.expireCookie(self.name_cookie, path='/')
                method = self.getCookieMethod('setAuthCookie', self.defaultSetAuthCookie )
                method( resp, self.auth_cookie, quote( ac ) )
                self.delRequestVar(req, self.name_cookie)
                self.delRequestVar(req, self.pw_cookie)
                return ATTEMPT_LOGIN
            elif req.has_key(self.auth_cookie):
                # Copy __ac to the auth header.
                ac = unquote(req[self.auth_cookie])
                req._auth = 'basic %s' % ac
                resp._auth = 1
                self.delRequestVar(req, self.auth_cookie)
                return ATTEMPT_CONT
        return ATTEMPT_NONE

    def __call__(self, container, req):
        '''The __before_publishing_traverse__ hook.'''
        resp = self.REQUEST['RESPONSE']
        attempt = self.modifyRequest(req, resp)
        if attempt == ATTEMPT_DISABLED:
            return
        if self.auto_login_page:
            if not req.get('disable_cookie_login__', 0):
                if (attempt == ATTEMPT_LOGIN or not getattr(resp, '_auth', 0)):
                    page = getattr(self, self.auto_login_page, None)
                    if page is not None:
                        # Provide a login page.
                        req._hold(ResponseCleanup(resp))
                        resp.unauthorized = self.unauthorized
                        resp._unauthorized = self._unauthorized
        if attempt:
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
        ac = encodestring('%s:%s' % (name, pw))
        method = self.getCookieMethod( 'setAuthCookie'
                                       , self.defaultSetAuthCookie )
        resp = self.REQUEST['RESPONSE']
        method( resp, self.auth_cookie, quote( ac ) )

    def _cleanupResponse(self):
        resp = self.REQUEST['RESPONSE']
        try: del resp.unauthorized
        except: pass
        try: del resp._unauthorized
        except: pass
        return resp

    #security.declarePrivate('unauthorized')
    def unauthorized(self):
        url = self.getLoginURL()
        if url:
            raise 'Redirect', url
        # Use the standard unauthorized() call.
        resp = self._cleanupResponse()
        resp.unauthorized()

    def _unauthorized(self):
        url = self.getLoginURL()
        if url:
            resp = self.REQUEST['RESPONSE']
            resp.redirect(url, lock=1)
            # We don't need to raise an exception.
            return
        # Use the standard _unauthorized() call.
        resp = self._cleanupResponse()
        resp._unauthorized()

    security.declarePublic('getUnauthorizedURL')
    def getUnauthorizedURL(self):
        '''
        Redirects to the login page.
        '''
        req = self.REQUEST
        resp = req['RESPONSE']
        attempt = getattr(req, '_cookie_auth', ATTEMPT_NONE)
        came_from = req.get('came_from', None)
        if came_from is None:
            came_from = req.get('URL', '')
            query = req.get('QUERY_STRING')
        if attempt == ATTEMPT_NONE:
            page_id = ''
            # An anonymous user was denied access to something.
            if came_from.endswith('manage') or came_from.endswith('manage_workspace') or came_from.endswith('manage_main'):
                return
            if came_from.startswith(self.absolute_url()):
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
            page = self.restrictedTraverse(page_id, None)
            if page is not None:
                page_url = self.getDocManagerURL() + '/' + page_id
                #if came_from is None:
                if query:
                    # Include the query string in came_from
                    if not query.startswith('?'):
                        query = '?' + query
                    came_from = came_from + query
                url = '%s?came_from=%s&retry=%s&disable_cookie_login__=1' % (
                    page_url, quote(came_from), retry)
                return url
        return None

    # backward compatible alias
    getLoginURL = getUnauthorizedURL

#    #security.declarePublic('getLoginURL')
#    def getLoginURL(self):
#        ''' Redirects to the login page. '''
#        if self.auto_login_page:
#            req = self.REQUEST
#            resp = req['RESPONSE']
#            iself = getattr(self, 'aq_inner', self)
#            parent = getattr(iself, 'aq_parent', None)
#            page = getattr(parent, self.auto_login_page, None)
#            if page:
#                retry = getattr(resp, '_auth', 0) and '1' or ''
#                url = '%s?came_from=%s&retry=%s' % (page.absolute_url(), quote(req['URL']), retry)
#                return url
#        return None

    security.declarePublic('logged_in')
    def logged_in(self, REQUEST):
        """ """
        came_from = REQUEST.get('came_from', '')
        if REQUEST.AUTHENTICATED_USER.getUserName() == 'Anonymous User':
            if came_from:
                return REQUEST.RESPONSE.redirect(self.auto_login_page + '?came_from=' + quote(came_from) + '&failed=1')
            else:
                return REQUEST.RESPONSE.redirect(self.auto_login_page + '?failed=1')
        else:
            if came_from:
                return REQUEST.RESPONSE.redirect(came_from)
            else:
                #redirect in expert area
                return REQUEST.RESPONSE.redirect(self.absolute_url(0))


    #security.declarePublic('logout')
    def logout(self):
        ''' Logs out the user and redirects to the logout page. '''
        req = self.REQUEST
        resp = req['RESPONSE']
        method = self.getCookieMethod('expireAuthCookie', self.defaultExpireAuthCookie )
        method( resp, cookie_name=self.auth_cookie )
        redir = 0
        if self.logout_page:
            iself = getattr(self, 'aq_inner', self)
            parent = getattr(iself, 'aq_parent', None)
            page = getattr(parent, self.logout_page, None)
            if page is not None:
                redir = 1
                resp.redirect(page.absolute_url())
        if not redir:
            # Should not normally happen.
            return 'Logged out.'

    def is_logged(self, REQUEST):
        """ """
        result = 1
        if REQUEST.AUTHENTICATED_USER.getUserName() == 'Anonymous User':
            result = 0
        return result



Globals.InitializeClass(CookieCrumbler)

class ResponseCleanup:
    def __init__(self, resp):
        self.resp = resp

    def __del__(self):
        # Free the references.
        try: del self.resp.unauthorized
        except: pass
        try: del self.resp._unauthorized
        except: pass
        try: del self.resp
        except: pass