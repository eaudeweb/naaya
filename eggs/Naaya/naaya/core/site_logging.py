import os
import logging

from naaya.core.zope2util import get_zope_env, ofs_path
from naaya.core.jsonlogger import JSONFormatter
from Products.Naaya.interfaces import INySite


log = logging.getLogger(__name__)

SITES_LOG_PATH_VAR = 'SITES_LOG_PATH' # name of config env. var

def get_site_logger(site):
    """
    Returns a logger based on site ID which will save actions on content types

    """
    site_logger_slug = ofs_path(site).strip('/').replace('/', ',')
    logger = logging.getLogger('%s-logger' % site_logger_slug)
    return (site_logger_slug, logger)

def create_site_logger(site):
    """
    Appends proper file handler to corresponding site logger.
    Called on startup for all existing INySites or after creation of a site.

    """
    site_logger_slug, logger = get_site_logger(site)
    abs_path = get_zope_env(SITES_LOG_PATH_VAR)
    if abs_path:
        try:
            if not os.path.exists(abs_path):
                os.makedirs(abs_path)
            log_filename = os.path.join(abs_path, '%s.log' % site_logger_slug)
            if not os.access(log_filename, os.F_OK):
                f = open(log_filename, 'a').close()
            if not os.access(log_filename, os.W_OK):
                log.warn(("Could not add file handler for site logger %r"
                           " (log file write permissions)"), site)
                return logger
            logger.propagate = 0

            supported_keys = ('asctime', 'message', )

            log_format = ' '.join(['%%({%d})' % index for index, key in enumerate(supported_keys)])
            custom_format = log_format.format(*supported_keys)

            handler = logging.FileHandler(log_filename)
            handler.setFormatter(JSONFormatter(custom_format))
            logger.setLevel(logging.INFO)
            logger.addHandler(handler)
        except Exception, e:
            log.exception("Could not add file handler for site logger %r", site)

    return logger

def init_site_loggers():
    """ Called once on App startup """
    import Zope2
    for ob in Zope2.app().objectValues():
        if INySite.providedBy(ob):
            create_site_logger(ob)
