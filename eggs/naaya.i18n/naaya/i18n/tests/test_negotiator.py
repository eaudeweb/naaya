
# Python imports
from lxml.html.soupparser import fromstring
import re

# Zope imports
from zope.i18n.interfaces import INegotiator
from zope.component import queryUtility

# Naaya imports
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

# Product imports
from naaya.i18n.NyNegotiator import NyNegotiator
from naaya.i18n.constants import COOKIE_ID

class NegotiatorTestSuite(NaayaTestCase):


    def setUp(self):
        self.negotiator = NyNegotiator()
        self.req = self.portal.REQUEST
        self.req['HTTP_ACCEPT_LANGUAGE'] = 'pt-br'
        self.req.cookies[COOKIE_ID] = 'es'
        self.req[self.negotiator.cookie_id] = 'de'
        self.req.form[COOKIE_ID] = 'fr'

    def test_negotiation_cache(self):
        client_langs = {'browser': ['pt-BR'],
                        'path': 'de',
                        'cookie': 'es',
                        'url': 'fr'}
        self.negotiator.set_policy(['browser', 'path', 'cookie', 'url'])

        key = self.negotiator._get_cache_key(('bg', 'fr'), client_langs)
        miss = self.negotiator._query_cache(key, self.req)
        self.assertEqual(miss, None)
        result = self.negotiator.getLanguage(('bg', 'fr'), self.req)
        self.assertEqual(result, 'fr')
        hit = self.negotiator._query_cache(key, self.req)
        self.assertEqual(hit, 'fr')

    def test_negotiate_url(self):
        self.negotiator.set_policy('url')
        result = self.negotiator.getLanguage(('en', 'de', 'fr'), self.req)
        self.assertEqual(result, 'fr')

    def test_negotiate_path(self):
        self.negotiator.set_policy('path')
        result = self.negotiator.getLanguage(('en', 'de', 'fr'), self.req)
        self.assertEqual(result, 'de')

    def test_negotiate_cookie(self):
        self.negotiator.set_policy('cookie')
        result = self.negotiator.getLanguage(('en', 'es', 'fr'), self.req)
        self.assertEqual(result, 'es')

    def test_negotiate_browser(self):
        self.negotiator.set_policy('browser')
        result = self.negotiator.getLanguage(('en', 'pt_BR', 'fr'), self.req)
        self.assertEqual(result, 'pt-BR')

    def test_negotiate_partial(self):
        self.negotiator.set_policy('cookie')
        self.req.cookies[COOKIE_ID] = 'pt-un'
        result = self.negotiator.getLanguage(('en', 'pt-br', 'pt-un', 'fr'), self.req)
        self.assertEqual(result, 'pt-UN')
        result = self.negotiator.getLanguage(('en', 'pt-br', 'fr'), self.req)
        self.assertEqual(result, 'pt-BR')
        result = self.negotiator.getLanguage(('en', 'pt', 'fr'), self.req)
        self.assertEqual(result, 'pt')

    def test_negotiate_priorities(self):
        self.negotiator.set_policy(('cookie', 'browser', 'url'))
        self.req.cookies[COOKIE_ID] = 'bg' # fails
        self.req['HTTP_ACCEPT_LANGUAGE'] = 'es' # fails
        self.req.form[COOKIE_ID] = 'de' # hits
        result = self.negotiator.getLanguage(('en', 'de', 'fr'), self.req)
        self.assertEqual(result, 'de')

    def test_default_fallback(self):
        self.req.cookies[COOKIE_ID] = 'fr' # fails
        result = self.negotiator.getLanguage(('de', 'en', 'es'), self.req)
        self.assertEqual(result, 'de')

class NegotiatorFunctionalTestSuite(NaayaFunctionalTestCase):

    def test_lang_in_path(self):
        self.browser_do_login('admin', '')
        self.portal.gl_add_site_language('es', 'Spanish')
        import transaction; transaction.commit()

        self.browser.go('http://localhost/portal/de')
        doc = fromstring(re.sub(r'\s+', ' ', self.browser.get_html()))
        self.assertEqual(doc.xpath('//div[@id="middle_port"]/h1')[0].text,
                         'Error page')

        self.browser.go('http://localhost/portal/es')
        doc = fromstring(re.sub(r'\s+', ' ', self.browser.get_html()))
        self.assertTrue(doc.attrib.has_key('lang'))
        self.assertEqual(doc.attrib['lang'], 'es')
