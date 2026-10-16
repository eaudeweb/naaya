"""Tests for naaya.sentry.handlers; sentry_sdk is always mocked."""

import io
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse
from ZPublisher.pubevents import PubFailure

from naaya.sentry import handlers

SENTRY_VARS = ('SENTRY_DSN', 'SENTRY_ENVIRONMENT', 'SENTRY_RELEASE',
               'SENTRY_SITE', 'EEA_KGS_VERSION', 'SERVER_NAME')


def make_request(user_agent='Mozilla/5.0 Firefox/119.0', **form):
    environ = {
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '8080',
        'REQUEST_METHOD': 'POST',
        'REMOTE_ADDR': '10.0.0.1',
        'QUERY_STRING': 'a=1',
        'HTTP_USER_AGENT': user_agent,
        'SCRIPT_NAME': '',
        'PATH_INFO': '/portal/page',
    }
    request = HTTPRequest(io.BytesIO(), environ, HTTPResponse())
    request.form.update(form)
    request.other['URL'] = 'http://localhost:8080/portal/page'
    return request


class FakeUser:

    def __init__(self, user_id, email=None):
        self._id = user_id
        self._email = email

    def getId(self):
        return self._id

    def getProperty(self, name):
        return self._email if name == 'email' else None


class FakeErrorLog:
    _ignored_exceptions = ('NotFound',)


class FakeSite:
    error_log = FakeErrorLog()

    def getId(self):
        return 'portal'

    def getSite(self):
        return self


def exc_info_for(exc):
    try:
        raise exc
    except Exception:
        return sys.exc_info()


class EnvTestCase(unittest.TestCase):

    def setUp(self):
        patcher = patch.dict(os.environ)
        patcher.start()
        self.addCleanup(patcher.stop)
        for name in SENTRY_VARS:
            os.environ.pop(name, None)


class InitializeTests(EnvTestCase):

    @patch('naaya.sentry.handlers.ignore_logger')
    @patch('naaya.sentry.handlers.sentry_sdk')
    def test_no_dsn(self, sdk, ignore_logger):
        handlers.initialize(None)
        sdk.init.assert_not_called()
        ignore_logger.assert_not_called()

    @patch('naaya.sentry.handlers.ignore_logger')
    @patch('naaya.sentry.handlers.sentry_sdk')
    def test_dsn_defaults(self, sdk, ignore_logger):
        os.environ['SENTRY_DSN'] = 'https://key@sentry.example.org/1'
        handlers.initialize(None)
        kwargs = sdk.init.call_args.kwargs
        self.assertEqual(kwargs['dsn'], 'https://key@sentry.example.org/1')
        self.assertEqual(kwargs['environment'], 'devel')
        self.assertEqual(kwargs['release'], 'dev')
        self.assertIs(kwargs['before_send'], handlers.before_send)
        self.assertNotIn('integrations', kwargs)
        ignore_logger.assert_called_once_with('Zope.SiteErrorLog')

    @patch('naaya.sentry.handlers.ignore_logger')
    @patch('naaya.sentry.handlers.sentry_sdk')
    def test_dsn_from_env(self, sdk, ignore_logger):
        os.environ['SENTRY_DSN'] = 'https://key@sentry.example.org/1'
        os.environ['SENTRY_ENVIRONMENT'] = 'production'
        os.environ['SENTRY_RELEASE'] = '4.4.3'
        handlers.initialize(None)
        kwargs = sdk.init.call_args.kwargs
        self.assertEqual(kwargs['environment'], 'production')
        self.assertEqual(kwargs['release'], '4.4.3')

    @patch('naaya.sentry.handlers.ignore_logger')
    @patch('naaya.sentry.handlers.sentry_sdk')
    def test_release_from_kgs_version(self, sdk, ignore_logger):
        os.environ['SENTRY_DSN'] = 'https://key@sentry.example.org/1'
        os.environ['EEA_KGS_VERSION'] = '1.2'
        handlers.initialize(None)
        self.assertEqual(sdk.init.call_args.kwargs['release'], '1.2')


class RequestDataTests(unittest.TestCase):

    def test_form_hides_passwords(self):
        request = make_request(title='hello', password='secret')
        form = handlers._get_form_from_request(request)
        self.assertEqual(form['title'], repr('hello'))
        self.assertNotIn('secret', form['password'])

    def test_other_skips_parents_and_response(self):
        request = make_request()
        request.other['PARENTS'] = [object()]
        other = handlers._get_other_from_request(request)
        self.assertNotIn('PARENTS', other)
        self.assertNotIn('RESPONSE', other)
        self.assertIn('URL', other)

    def test_request_headers(self):
        http = handlers._get_request_from_request(make_request())
        self.assertEqual(http['method'], 'POST')
        self.assertEqual(http['host'], '10.0.0.1')
        self.assertEqual(http['query_string'], 'a=1')
        self.assertEqual(http['headers']['User-Agent'],
                         'Mozilla/5.0 Firefox/119.0')
        self.assertTrue(all(isinstance(v, str)
                            for v in http['headers'].values()))

    def test_browser(self):
        cases = [
            ('Mozilla/5.0 Edg/118.0', ('Edge', '118.0')),
            ('Mozilla/5.0 Firefox/119.0', ('Firefox', '119.0')),
            ('Mozilla/5.0 Chrome/118.0.0.0 Safari/537.36',
             ('Chrome', '118.0.0.0')),
            ('Mozilla/5.0 Trident/7.0', ('Internet Explorer', '7.0')),
            ('curl', None),
        ]
        for user_agent, expected in cases:
            request = make_request(user_agent=user_agent)
            self.assertEqual(handlers._get_browser_from_request(request),
                             expected)

    def test_user_anonymous(self):
        self.assertEqual(handlers._get_user_from_request(make_request()),
                         {'id': 'Anonymous'})

    def test_user_with_email(self):
        request = make_request()
        request['AUTHENTICATED_USER'] = FakeUser('john', 'john@example.org')
        self.assertEqual(handlers._get_user_from_request(request),
                         {'id': 'john', 'email': 'john@example.org'})

    def test_user_without_get_property(self):
        request = make_request()
        user = MagicMock(spec=['getId'])
        user.getId.return_value = 'admin'
        request['AUTHENTICATED_USER'] = user
        self.assertEqual(handlers._get_user_from_request(request),
                         {'id': 'admin', 'email': ''})


class BeforeSendTests(unittest.TestCase):

    @patch('naaya.sentry.handlers.getRequest', return_value=None)
    def test_no_request(self, getRequest):
        event = {'extra': {}}
        self.assertEqual(handlers.before_send(event, {}), {'extra': {}})

    @patch('naaya.sentry.handlers.getRequest')
    def test_adds_request_data(self, getRequest):
        getRequest.return_value = make_request(title='hello')
        event = handlers.before_send({}, {})
        self.assertEqual(set(event['extra']),
                         {'other', 'lazy items', 'form', 'request'})
        self.assertEqual(event['extra']['form'], {'title': repr('hello')})

    @patch('naaya.sentry.handlers.getRequest')
    def test_keeps_existing_extra(self, getRequest):
        getRequest.return_value = make_request()
        event = handlers.before_send({'extra': {'form': 'kept'}}, {})
        self.assertEqual(event['extra']['form'], 'kept')

    @patch('naaya.sentry.handlers.getRequest')
    def test_broken_request_keeps_event(self, getRequest):
        getRequest.return_value = MagicMock(spec=[])
        event = handlers.before_send({'message': 'x'}, {})
        self.assertEqual(event['message'], 'x')


@patch('naaya.sentry.handlers.sentry_sdk')
class ErrorRaisedSubscriberTests(EnvTestCase):

    def notify(self, sdk, exc, request, retry=False):
        handlers.errorRaisedSubscriber(
            PubFailure(request, exc_info_for(exc), retry))
        return sdk.new_scope.return_value.__enter__.return_value

    def test_naaya_site(self, sdk):
        request = make_request(title='hello')
        request['PARENTS'] = [FakeSite()]
        request['AUTHENTICATED_USER'] = FakeUser('john', 'john@example.org')
        scope = self.notify(sdk, ValueError('boom'), request)
        sdk.capture_exception.assert_called_once()
        self.assertIs(sdk.capture_exception.call_args.args[0][0], ValueError)
        tags = dict(c.args for c in scope.set_tag.call_args_list)
        self.assertEqual(tags, {
            'site': 'portal',
            'browser': 'Firefox 119.0',
            'browser.name': 'Firefox',
            'browser.version': '119.0',
        })
        extras = dict(c.args for c in scope.set_extra.call_args_list)
        self.assertEqual(set(extras),
                         {'other', 'lazy items', 'form', 'request'})
        self.assertEqual(extras['form'], {'title': repr('hello')})
        scope.set_user.assert_called_once_with(
            {'id': 'john', 'email': 'john@example.org'})

    def test_site_from_env(self, sdk):
        os.environ['SENTRY_SITE'] = 'destinet.eu'
        scope = self.notify(sdk, ValueError('boom'), make_request())
        scope.set_tag.assert_any_call('site', 'destinet.eu')
        sdk.capture_exception.assert_called_once()

    def test_site_default(self, sdk):
        scope = self.notify(sdk, ValueError('boom'), make_request())
        scope.set_tag.assert_any_call('site', 'dev')

    def test_ignored_exception(self, sdk):
        request = make_request()
        request['PARENTS'] = [FakeSite()]

        class NotFound(Exception):
            pass

        self.notify(sdk, NotFound(), request)
        sdk.capture_exception.assert_not_called()

    def test_retry_not_sent(self, sdk):
        self.notify(sdk, ValueError('boom'), make_request(), retry=True)
        sdk.capture_exception.assert_not_called()
