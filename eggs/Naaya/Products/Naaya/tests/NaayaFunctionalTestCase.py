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
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alex Morega, Eau de Web

import sys
from StringIO import StringIO

try: import twill
except: twill = None

try: import wsgiref.validate
except: wsgiref = None

from App.version_txt import getZopeVersion
from ZServer.HTTPResponse import ZServerHTTPResponse
from ZPublisher.Request import Request
from ZPublisher.Publish import publish

import NaayaTestCase

if getZopeVersion() < (2, 10, 9):
    newline = '\n'
else:
    newline = '\r\n'


def test_publish(environ, response, extra):
    """
    copied from publish_module in ZPublisher/Test.py, simplified, and
    modified to accept streaming responses
    """
    must_die=0
    after_list=[None]
    try:
        try:
            stdout=response.stdout
            request=Request(environ['wsgi.input'], environ, response)
            from zope.publisher.browser import setDefaultSkin
            setDefaultSkin(request)

            for k, v in extra.items(): request[k]=v
            response = publish(request, 'Zope2', after_list, debug=0)
        except SystemExit, v:
            must_die=sys.exc_info()
            response.exception(must_die)
        except ImportError, v:
            if isinstance(v, TupleType) and len(v)==3: must_die=v
            else: must_die=sys.exc_info()
            response.exception(1, v)
        except:
            response.exception()

        if response:
            stdout.write(str(response))
            producer = response._bodyproducer
            if producer is not None:
                while True:
                    data = producer.more()
                    if not data:
                        break
                    stdout.write(data)

        # The module defined a post-access function, call it
        if after_list[0] is not None: after_list[0]()

    finally:
        request.close()

    if must_die:
        try: raise must_die[0], must_die[1], must_die[2]
        finally: must_die=None


class TwillMixin(object):
    wsgi_debug = False

    def divert_twill_output(self):
        """ the Twill browser is messy and uses globals; this will divert its output """
        self._twill_original_output = twill.browser.OUT
        self.browser_output = StringIO()
        twill.browser.OUT = self.browser_output

    def restore_twill_output(self):
        twill.browser.OUT = self._twill_original_output

    def install_twill(self):
        wsgi_app = self.wsgi_request
        # TODO: we should run all requests through the validator. For now it's
        # disabled because it mysteriously breaks some tests.
        #if wsgiref:
        #    wsgi_app = wsgiref.validate.validator(wsgi_app)
        twill.add_wsgi_intercept('localhost', 80, lambda: wsgi_app)
        self.browser = twill.browser.TwillBrowser()
        self.divert_twill_output()

    def remove_twill(self):
        self.restore_twill_output()
        twill.remove_wsgi_intercept('localhost', 80)

    def wsgi_request(self, environ, start_response):
        if self.wsgi_debug:
            print 'wsgi_request start'
            print environ
            print '...'

        outstream = StringIO()
        response = ZServerHTTPResponse(stdout=outstream, stderr=sys.stderr)
        extra = {
            'SESSION': self.app.REQUEST.SESSION,
            'AUTHENTICATED_USER': self.app.REQUEST.AUTHENTICATED_USER,
        }

        test_publish(environ, response, extra)

        output = outstream.getvalue()
        headers, body = output.split(newline*2, 1)
        header_lines = headers.split(newline)
        assert header_lines[0].startswith('HTTP/1.0 ')
        status = header_lines[0][len('HTTP/1.0 '):]
        headers = [header.split(': ', 1) for header in header_lines[1:]]

        if self.wsgi_debug:
            print 'wsgi_request done, status="%s"' % status
            print '  ' + '\n'.join([': '.join(header) for header in headers])

        headers = [ (header[0], ', '.join(header[1:])) for header in headers ]
        if 'content-type' not in (header[0].lower() for header in headers):
            headers.append( ('Content-Type', 'text/html; charset=utf-8') )
        start_response(status, headers)
        return [body]

    def serve_http(self, host='', port=8081):
        from wsgiref.simple_server import make_server
        server = make_server(host, port, self.wsgi_request)
        print 'serving pages on "%s" port %d; press ^C to stop' % (host, port)
        server.serve_forever()

    def browser_get_header(self, header_name):
        return self.browser._browser._response._headers.get(header_name, None)

class NaayaFunctionalTestCase(NaayaTestCase.NaayaTestCase, TwillMixin):
    """
    Functional test case for Naaya - use Twill (http://twill.idyll.org/) for client-side tests
    """

    def setUp(self):
        self.install_twill()
        super(NaayaFunctionalTestCase, self).setUp()

    def tearDown(self):
        super(NaayaFunctionalTestCase, self).tearDown()
        self.remove_twill()

    def browser_do_login(self, username, password):
        self.browser.go('http://localhost/portal/login_html')
        form = self.browser.get_form(2)
        field = self.browser.get_form_field(form, '__ac_name')
        self.browser.clicked(form, field)
        form['__ac_name'] = username
        form['__ac_password'] = password
        self.browser.submit()
        self.failUnless('You are logged in as: <em>%s</em>' % username in self.browser.get_html())

    def browser_do_logout(self):
        self.browser.go('http://localhost/portal/logout')
        self.failUnless('<h1>Log in</h1>' in self.browser.get_html())

    def assertRedirectLoginPage(self, logic=True):
        url = self.browser.get_url()
        login_prefix = 'http://localhost/portal/login_html?came_from='
        if logic is True:
            self.failUnless(url.startswith(login_prefix))
        else:
            self.failIf(url.startswith(login_prefix))

    def assertRedirectUnauthorizedPage(self, logic=True):
        url = self.browser.get_url()
        login_prefix = 'http://localhost/portal/unauthorized_html?came_from='
        if logic is True:
            self.failUnless(url.startswith(login_prefix))
        else:
            self.failIf(url.startswith(login_prefix))

    def assertAccessDenied(self, logic=True, msg=None):
        url = self.browser.get_url()
        login_prefix = 'http://localhost/portal/login_html?came_from='
        unauthorized_prefix = 'http://localhost/portal/unauthorized_html?came_from='
        access_denied = (url.startswith(login_prefix) or
                         url.startswith(unauthorized_prefix) or
                         self.browser.result.http_code == 401)
        if logic is True:
            if msg is None:
                msg = "Access should be denied, but is not"
            self.failUnless(access_denied, msg)
        else:
            if msg is None:
                msg = "Access should be allowed, but is denied"
            self.failIf(access_denied, msg)

    def print_last_error(self):
        print self.portal.error_log._getLog()[0]['tb_text']
