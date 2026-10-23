import re
from types import SimpleNamespace
from unittest import mock

from Products.Naaya import views
from Products.Naaya.NySite import NySite
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.NaayaBase import akismet


class AkismetTest(NaayaTestCase):

    def post(self, response, status=200):
        return mock.patch.object(akismet, '__post',
                                 return_value=(response, status))

    def test_verify_key(self):
        with self.post('valid') as post:
            self.assertTrue(akismet.verify_key('k', 'http://site'))
        post.assert_called_once_with('key=k&blog=http://site',
                                     'rest.akismet.com', '/1.1/verify-key',
                                     80)
        with self.post('invalid'):
            self.assertFalse(akismet.verify_key('k', 'http://site'))
        with self.post('error', 500):
            with self.assertRaises(akismet.AkismetError) as cm:
                akismet.verify_key('k', 'http://site')
        self.assertEqual(str(cm.exception), "'error'")
        self.assertEqual(cm.exception.statuscode, 500)

    def test_comment_check(self):
        with self.post('true'):
            self.assertTrue(akismet.comment_check('k', 'b', 'ip', 'ua'))
        with self.post('false'):
            self.assertFalse(akismet.comment_check('k', 'b', 'ip', 'ua'))

    def test_post_decodes_response(self):
        response = mock.Mock(status=200)
        response.read.return_value = b'valid'
        connection = mock.Mock()
        connection.getresponse.return_value = response
        with mock.patch('http.client.HTTPConnection',
                        return_value=connection):
            self.assertTrue(akismet.verify_key('k', 'http://site'))
        args = connection.request.call_args[0]
        self.assertEqual(args[:3], ('POST', '/1.1/verify-key',
                                    'key=k&blog=http://site'))


class APIKeysStatusTest(NaayaTestCase):

    def render(self, environment, provider='google', akismet_response=None):
        conf = SimpleNamespace(environment=environment)
        self.portal.recaptcha_provider = provider
        with mock.patch.object(views, 'getConfiguration',
                               return_value=conf), \
                mock.patch.object(views.akismet, 'verify_key',
                                  return_value=akismet_response) as verify:
            html = views.AdminAPIKeysStatus(self.portal, self.portal.REQUEST)
        return html, verify

    def rows(self, html):
        """Return {title: (row class, key cell)} for the keys table."""
        rows = re.findall(r'<tr align="center" class="(\w+)">\s*'
                          r'<td align="left">(.*?)</td>\s*'
                          r'<td align="left">.*?</td>\s*'
                          r'<td>(.*?)</td>', html, re.S)
        return dict((title, (cls, key.strip()))
                    for cls, title, key in rows)

    def test_no_keys(self):
        self.portal.recaptcha_private_key = ''
        self.portal.recaptcha_public_key = ''
        with mock.patch.object(NySite, 'buildout_recaptcha_private',
                               return_value=''), \
                mock.patch.object(NySite, 'buildout_recaptcha_public',
                                  return_value=''):
            html, verify = self.render({})
        self.assertFalse(verify.called)
        rows = self.rows(html)
        self.assertEqual(rows['Akismet'], ('invalid', ''))
        self.assertEqual(rows['Google Analytics primary tracking code'],
                         ('invalid', ''))
        self.assertEqual(rows['reCaptcha private key'], ('invalid', ''))
        self.assertEqual(len(rows), 8)

    def test_keys(self):
        self.portal.recaptcha_private_key = 'private-key'
        self.portal.recaptcha_public_key = 'public-key'
        self.portal.portal_statistics.ga_id = 'UA-2'
        html, verify = self.render({
            'AKISMET_API_KEY': 'akismet-key',
            'GOOGLE_AUTH_CLIENT_ID': 'client-id',
            'GOOGLE_AUTH_CLIENT_SECRET': 'client-secret',
            'GA_ID': 'UA-1',
            'GA_DOMAIN_NAME': 'example.com',
        }, akismet_response=True)
        verify.assert_called_once_with('akismet-key',
                                       self.portal.getSitePath())
        rows = self.rows(html)
        self.assertEqual(rows['Akismet'], ('valid', 'akismet-key'))
        self.assertEqual(rows['Google Authentication Client ID'],
                         ('valid', ''))
        self.assertEqual(rows['Google Authentication Client Secret Key'],
                         ('valid', ''))
        self.assertEqual(rows['Google Analytics primary tracking code'],
                         ('valid', 'UA-1'))
        self.assertEqual(rows['Google Analytics domain name'],
                         ('valid', 'example.com'))
        self.assertEqual(rows['Google Analytics portal tracking code'],
                         ('valid', 'UA-2'))
        self.assertEqual(rows['reCaptcha private key'],
                         ('valid', 'private-key'))
        self.assertEqual(rows['reCaptcha public key'],
                         ('valid', 'public-key'))
        self.assertIn('href="http://nohost/portal/portal_statistics/'
                      'admin_verify"', html)
        self.assertNotIn('Secret Key</td>\n\n                <td>client',
                         html)

    def test_ec_recaptcha(self):
        html, verify = self.render({}, provider='ec')
        rows = self.rows(html)
        self.assertEqual(rows['reCaptcha provider'],
                         ('valid', 'provider is set to EC, no keys'))
        self.assertNotIn('reCaptcha private key', rows)


class SetBundleViewTest(NaayaTestCase):

    def test_get_and_set_bundle(self):
        view = views.SetBundleView(self.portal, self.portal.REQUEST)
        self.assertEqual(view.get_bundle(),
                         self.portal.get_bundle().__name__)
        view.set_bundle('TestViewsBundle')
        self.assertEqual(view.get_bundle(), 'TestViewsBundle')


class ObPathTest(NaayaTestCase):

    def test_ob_path(self):
        self.assertEqual(views.ob_path(self.portal.info), '/portal/info')
