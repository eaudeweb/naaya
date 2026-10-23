from unittest import TestCase

from zope.publisher.http import HTTPRequest
from zope.i18n.interfaces import IUserPreferredCharsets

from naaya.i18n.utilities import NyHTTPCharsets


def create_request(charset_header=None):
    environ = {}
    if charset_header is not None:
        environ['HTTP_ACCEPT_CHARSET'] = charset_header
    return HTTPRequest('', environ)


class HTTPCharsetsTestSuite(TestCase):

    def _validate(self, req, expected):
        naaya_i18n = NyHTTPCharsets(req).getPreferredCharsets()
        self.assertEqual(naaya_i18n, expected)

    def test_missing_header(self):
        """ test defaults on charset header absence """
        req = create_request(None)
        self._validate(req, ['utf-8', 'iso-8859-1', '*'])

    def test_empty_header(self):
        """ test defaults on empty charset header"""
        req = create_request('')
        self._validate(req, ['utf-8', 'iso-8859-1', '*'])

    def test_specific_header(self):
        """ test explicit charset header keeps zope publisher's behaviour """
        req = create_request('ISO-8859-1,utf-8;q=0.7,*;q=0.3')
        self._validate(req, ['utf-8', 'iso-8859-1', '*'])

    def test_star_header(self):
        """ test star charset header keeps zope publisher's behaviour """
        req = create_request('*')
        self._validate(req, ['utf-8', '*'])

    def test_header_without_utf8(self):
        """ an explicit header is not replaced by the defaults """
        req = create_request('iso-8859-2')
        self._validate(req, ['iso-8859-2', 'iso-8859-1'])

    def test_adapter_registered(self):
        """ test naaya.i18n's IPreferredCharset adapter is registered """
        req = create_request()
        adapter = IUserPreferredCharsets(req)
        self.assertTrue(isinstance(adapter, NyHTTPCharsets))
        self.assertEqual(adapter.getPreferredCharsets(),
                         ['utf-8', 'iso-8859-1', '*'])
