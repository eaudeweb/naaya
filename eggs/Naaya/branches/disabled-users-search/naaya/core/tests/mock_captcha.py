import random
from zope.interface import implements, implementer
from zope.component import adapter
from Products.Naaya.tests.NaayaTestCase import ITestSite
from Products.NaayaCore.interfaces import ICaptcha

html_template = """\
    <span id="test-captcha-challenge">%(challenge)s</span>
    <input name="test-captcha-response">
"""

class MockCaptchaProvider(object):
    """
    Mock captcha provider that generates random keys and checks if they
    were submitted back properly.
    """
    implements(ICaptcha)

    def __init__(self, site, mock_data):
        self.site = site
        self.keys = mock_data.setdefault('keys', set())

    is_available = True

    def render_captcha(self):
        key = ''.join(random.choice("abcdefghijklmnop") for c in range(6))
        self.keys.add(key)
        return html_template % {'challenge': 'please enter "%s"' % key}

    def is_valid_captcha(self, request):
        is_valid = request.get('test-captcha-response', None) in self.keys
        if not is_valid:
            self.site.setSession('err_recaptcha',
                'Your previous attempt was incorrect. Please try again')
        return is_valid

    def requested_keys(self):
        return set(self.keys)

def create_mock():
    """
    Create a persistence object (a private dict) and return a factory. The
    factory will give out MockCaptchaProvider objects that use the persistence
    object to store captcha keys. Use like this::
        import unittest
        from zope.component import getGlobalSiteManager
        from naaya.core.tests import mock_captcha
        gsm = getGlobalSiteManager()
        class MyTest(unittest.TestCase):
            def setUp(self):
                self._mock_captcha_factory = mock_captcha.create_mock()
                gsm.registerAdapter(self._mock_captcha_factory)

            def tearDown(self):
                gsm.unregisterAdapter(self._mock_captcha_factory)

            def test_something(self):
                # get contents of span#test-captcha-challenge from the page
                challenge = "..."
                response = mock_captcha.solve(challenge)
                # now, inject "response" as value of
                # input[name=test-captcha-response]
    """

    mock_data = {}

    @implementer(ICaptcha)
    @adapter(ITestSite)
    def captcha_factory(site):
        return MockCaptchaProvider(site, mock_data)

    return captcha_factory

def solve(text):
    start, end = 'please enter "', '"'
    assert text.startswith(start)
    assert text.endswith(end)
    return text[ len(start) : -len(end) ]
