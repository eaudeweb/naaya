import logging


publish_error_log = logging.getLogger(__name__)
publish_error_log.propagate = False


def log_pub_failure(event):
    if event.retry:
        return

    if publish_error_log.handlers:
        publish_error_log.error('Exception on %s [%s]',
                                event.request.URL,
                                event.request.method,
                                exc_info=event.exc_info)


def initialize():
    try:
        from raven.handlers.logging import SentryHandler
    except ImportError:
        return
    else:
        from App.config import getConfiguration
        env = getattr(getConfiguration(), 'environment', {})
        sentry_dsn = env.get('SENTRY_DSN')
        if sentry_dsn:
            sentry_handler = SentryHandler(sentry_dsn)
            publish_error_log.addHandler(sentry_handler)
