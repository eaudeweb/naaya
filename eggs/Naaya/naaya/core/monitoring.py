import logging
import zExceptions
from AccessControl.unauthorized import Unauthorized
from naaya.core.zope2util import get_zope_env

ignored_types = [
    zExceptions.Redirect,
    zExceptions.Unauthorized,
    Unauthorized,
    zExceptions.Forbidden,
    zExceptions.NotFound,
    zExceptions.MethodNotAllowed,
]

publish_error_log = logging.getLogger(__name__)
publish_error_log.propagate = False


def get_known_headers(request):
    """ ZPublisher's Request is not capable of iterating headers only """
    look_for_headers = ('CONTENT_LENGTH',
                        'CONTENT_TYPE',
                        'HTTP_ACCEPT_ENCODING',
                        'HTTP_ACCEPT_LANGUAGE',
                        'HTTP_HOST',
                        'HTTP_REFERER',
                        'HTTP_USER_AGENT',)
    headers = {}
    for header in look_for_headers:
        headers[header] = request.getHeader(header)
    return headers

def data_for_sentry(request):
    """
    Returns extra information to append to message to be sent to Sentry

    """
    environ = dict(request)
    environ['RESPONSE'] = '-- stripped --'

    return {
            'env': environ,
            'cookies': request.cookies,
            'headers': get_known_headers(request),
            'data': request.form,
           }

def log_pub_failure(event):
    if event.retry:
        return

    if publish_error_log.handlers:
        if event.exc_info[0] not in ignored_types:
            req = event.request
            publish_error_log.error('Exception on %s [%s]', req.URL, req.method,
                                    exc_info=event.exc_info,
                                    extra={
                                        'stack': True,
                                        'data': data_for_sentry(req),
                                    })


def initialize():
    try:
        from raven.contrib.zope import ZopeSentryHandler
    except ImportError:
        return
    else:
        sentry_dsn = get_zope_env('SENTRY_DSN')
        if sentry_dsn:
            sentry_handler = ZopeSentryHandler(sentry_dsn)
            publish_error_log.addHandler(sentry_handler)
