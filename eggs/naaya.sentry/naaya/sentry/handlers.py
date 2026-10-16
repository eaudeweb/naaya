"""Sentry initialisation and Zope error reporting."""

import logging
import os
import re

import sentry_sdk
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.users import nobody
from sentry_sdk.integrations.logging import ignore_logger
from zope.component import adapter
from zope.globalrequest import getRequest
from ZPublisher.HTTPRequest import _filterPasswordFields
from ZPublisher.interfaces import IPubFailure

logger = logging.getLogger('naaya.sentry')

BROWSERS = ['Edg', 'Firefox', 'Seamonkey', 'OPR', 'Opera', 'Trident', 'MSIE',
            'Chrome', 'Chromium', 'Safari']
BROWSER_NAMES = {
    'MSIE': 'Internet Explorer',
    'OPR': 'Opera',
    'Trident': 'Internet Explorer',
    'Edg': 'Edge',
}


def get_site(request):
    """Return the Naaya site of the request, or the first object under root."""
    try:
        site = request.PARENTS[0].getSite()
    except (IndexError, AttributeError):
        site = None
    if not site:
        try:
            site = request.PARENTS[-2]
        except (IndexError, AttributeError):
            site = None
    return site


def _get_site_id(site):
    if hasattr(site, 'getId'):
        return site.getId()
    return os.environ.get('SENTRY_SITE', os.environ.get('SERVER_NAME', 'dev'))


def _get_user_from_request(request):
    user = request.get('AUTHENTICATED_USER', None)
    if user is None:
        user = getSecurityManager().getUser()
    if user is None or user == nobody:
        return {'id': 'Anonymous'}
    get_property = getattr(user, 'getProperty', None)
    email = get_property('email') if get_property is not None else ''
    return {'id': user.getId(), 'email': email or ''}


def _get_other_from_request(request):
    return {k: repr(v) for k, v in _filterPasswordFields(request.other.items())
            if k not in ('PARENTS', 'RESPONSE')}


def _get_lazyitems_from_request(request):
    return {k: repr(v)
            for k, v in _filterPasswordFields(request._lazies.items())}


def _get_form_from_request(request):
    return {k: repr(v) for k, v in _filterPasswordFields(request.form.items())}


def _get_request_from_request(request):
    headers = {k: v if isinstance(v, str) else str(v)
               for k, v in request.environ.items()}
    if 'HTTP_USER_AGENT' in headers and 'User-Agent' not in headers:
        headers['User-Agent'] = headers['HTTP_USER_AGENT']
    http = {
        'headers': headers,
        'url': request.getURL(),
        'method': request.method,
        'host': request.environ.get('REMOTE_ADDR', ''),
    }
    if 'QUERY_STRING' in headers:
        http['query_string'] = headers['QUERY_STRING']
    return http


def _get_browser_from_request(request):
    """Return (browser name, version) from the User-Agent, or None."""
    user_agent = request.environ.get('HTTP_USER_AGENT', '')
    for browser in BROWSERS:
        match = re.findall(browser + '[/ ]?([0-9.]+)', user_agent)
        if match:
            return (BROWSER_NAMES.get(browser, browser), match[0])
    return None


def _request_extras(request):
    return {
        'other': _get_other_from_request(request),
        'lazy items': _get_lazyitems_from_request(request),
        'form': _get_form_from_request(request),
        'request': _get_request_from_request(request),
    }


def before_send(event, hint):
    """Add the request data to events sent from the logging integration."""
    request = getRequest()
    if not request:
        return event
    try:
        extra = event.setdefault('extra', {})
        for key, value in _request_extras(request).items():
            extra.setdefault(key, value)
    except Exception:
        logger.warning('Could not extract data from request', exc_info=True)
    return event


def initialize(context):
    """Initialise sentry_sdk when SENTRY_DSN is set."""
    sentry_dsn = os.environ.get('SENTRY_DSN', '')
    if not sentry_dsn:
        return
    sentry_sdk.init(
        dsn=sentry_dsn,
        max_breadcrumbs=50,
        before_send=before_send,
        release=os.environ.get(
            'SENTRY_RELEASE', os.environ.get('EEA_KGS_VERSION', 'dev')),
        environment=os.environ.get('SENTRY_ENVIRONMENT', 'devel'),
        traces_sample_rate=1.0,
    )
    # errorRaisedSubscriber reports these errors with more context
    ignore_logger('Zope.SiteErrorLog')
    logger.info('Sentry integration enabled')


@adapter(IPubFailure)
def errorRaisedSubscriber(event):
    """Send a publishing error to Sentry, unless error_log ignores it."""
    if event.retry:
        return
    exc_info = event.exc_info
    request = event.request
    site = get_site(request)
    error_log = getattr(site, 'error_log', None)
    if error_log is not None and \
            exc_info[0].__name__ in error_log._ignored_exceptions:
        return

    with sentry_sdk.new_scope() as scope:
        for key, value in _request_extras(request).items():
            scope.set_extra(key, value)
        scope.set_user(_get_user_from_request(request))
        scope.set_tag('site', _get_site_id(site))
        browser = _get_browser_from_request(request)
        if browser:
            scope.set_tag('browser', '%s %s' % browser)
            scope.set_tag('browser.name', browser[0])
            scope.set_tag('browser.version', browser[1])
        sentry_sdk.capture_exception(exc_info)
