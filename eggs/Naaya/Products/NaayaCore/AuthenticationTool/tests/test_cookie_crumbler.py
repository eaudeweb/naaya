import unittest
from base64 import encodebytes
from io import BytesIO
from urllib.parse import quote

from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse

from Products.NaayaCore.AuthenticationTool.CookieCrumbler import (
    CookieCrumbler, ATTEMPT_NONE, ATTEMPT_LOGIN, ATTEMPT_RESUME)


def make_request(cookie=''):
    response = HTTPResponse(stdout=BytesIO())
    environ = {'REQUEST_METHOD': 'GET', 'SERVER_NAME': 'localhost',
               'SERVER_PORT': '80', 'HTTP_COOKIE': cookie}
    request = HTTPRequest(BytesIO(), environ, response)
    request.processInputs()
    return request, response


def ac_cookie(raw):
    return '__ac=' + quote(encodebytes(raw).decode().rstrip())


class CookieCrumblerTest(unittest.TestCase):

    def modify(self, cookie):
        request, response = make_request(cookie)
        return CookieCrumbler().modifyRequest(request, response), request

    def test_valid_auth_cookie(self):
        attempt, request = self.modify(ac_cookie(b'bob:secret'))
        self.assertEqual(attempt, ATTEMPT_RESUME)
        self.assertEqual(request._auth, 'Basic %s' %
                         encodebytes(b'bob:secret').decode().rstrip())

    def test_foreign_auth_cookies_ignored(self):
        for raw in [b'no-colon', b'\xff\xfe:x']:
            attempt, request = self.modify(ac_cookie(raw))
            self.assertEqual(attempt, ATTEMPT_NONE, raw)
            self.assertFalse(request._auth)
        attempt, request = self.modify('__ac=not-base64!')
        self.assertEqual(attempt, ATTEMPT_NONE)

    def test_login_sets_auth_cookie(self):
        request, response = make_request(
            '__ac_name=bob; __ac_password=secret')
        attempt = CookieCrumbler().modifyRequest(request, response)
        self.assertEqual(attempt, ATTEMPT_LOGIN)
        ac = encodebytes(b'bob:secret').decode().rstrip()
        self.assertEqual(request._auth, 'Basic %s' % ac)
        self.assertEqual(response.cookies['__ac']['value'], quote(ac))
        self.assertNotIn('__ac_password', request.cookies)
