from StringIO import StringIO

try: import twill
except: twill = None

try: import wsgiref.validate
except: wsgiref = None

import NaayaTestCase

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

    def browser_get_header(self, header_name):
        return self.browser._browser._response._headers.get(header_name, None)

class NaayaFunctionalTestCase(NaayaTestCase.NaayaTestCase, TwillMixin):
    """
    Functional test case for Naaya - use Twill (http://twill.idyll.org/) for client-side tests
    """

    _naaya_plugin = 'NaayaPortalTestPlugin'

    def setUp(self):
        self.install_twill()
        #This is needed for absolute_url
        self.portal.REQUEST.setServerURL('http', 'localhost')
        super(NaayaFunctionalTestCase, self).setUp()

    def tearDown(self):
        super(NaayaFunctionalTestCase, self).tearDown()
        self.remove_twill()

    def browser_do_login(self, username, password):
        self.browser.go(self.portal.absolute_url() + '/login_html')
        form = self.browser.get_form(2)
        field = self.browser.get_form_field(form, '__ac_name')
        self.browser.clicked(form, field)
        form['__ac_name'] = username
        form['__ac_password'] = password
        self.browser.submit()
        self.failUnless(('You are logged in as: <em>%s</em>' % username)
                        in self.browser.get_html())

    def browser_do_logout(self):
        self.browser.go(self.portal.absolute_url() + '/logout')
        self.failUnless('<h1>Log in</h1>' in self.browser.get_html())

    def assertRedirectLoginPage(self, logic=True):
        url = self.browser.get_url()
        login_prefix = self.portal.absolute_url() + '/login_html?came_from='
        if logic is True:
            self.failUnless(url.startswith(login_prefix))
        else:
            self.failIf(url.startswith(login_prefix))

    def assertRedirectUnauthorizedPage(self, logic=True):
        url = self.browser.get_url()
        login_prefix = self.portal.absolute_url() + \
                                                '/unauthorized_html?came_from='
        if logic is True:
            self.failUnless(url.startswith(login_prefix))
        else:
            self.failIf(url.startswith(login_prefix))

    def assertAccessDenied(self, logic=True, msg=None):
        url = self.browser.get_url()
        login_prefix = self.portal.absolute_url() +  '/login_html?came_from='
        unauthorized_prefix = self.portal.absolute_url() + \
                                            '/unauthorized_html?came_from='
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
