import os
import re
import logging

from naaya.core.zope2util import get_zope_env, ofs_path
from naaya.core.jsonlogger import JSONFormatter
from Products.Naaya.interfaces import INySite


log = logging.getLogger(__name__)

SITES_LOG_PATH_VAR = 'SITES_LOG_PATH' # name of config env. var
SUFFIX = '-site-logger' # for naming loggers

ACCESS = 'ACCESS'
USER_MAN = 'USER_MANAGEMENT'
ALLOWED_SLUGS = {ACCESS: ("VIEW", "DOWNLOAD", ),
                 USER_MAN: ("ASSIGNED", "UNASSIGNED", ),
                }

def get_site_logger(site):
    """
    Returns a logger based on site ID which will save actions on content types

    """
    site_logger_slug = ofs_path(site).strip('/').replace('/', ',')
    logger = logging.getLogger('%s%s' % (site_logger_slug, SUFFIX))
    return logger

def create_site_logger(site):
    """
    Sets proper file handler to corresponding site logger.
    Called on startup for all existing INySites or after creation of a site.
    Caution: removes previous handlers, if any

    """
    logger = get_site_logger(site)
    logger.propagate = 0
    logger.setLevel(logging.INFO)
    existing = list(logger.handlers) # we don't iterate what we modify
    for handler in existing:
        try:
            logger.removeHandler(handler)
        except Exception, e:
            log.exception("Could not remove existing site logger handler")
    custom_format = '%(asctime) %(message)'
    abs_path = get_zope_env(SITES_LOG_PATH_VAR)
    if abs_path:
        try:
            if not os.path.exists(abs_path):
                os.makedirs(abs_path)
            log_filename = os.path.join(abs_path, '%s.log' % logger.name)
            if not os.access(log_filename, os.F_OK):
                f = open(log_filename, 'a').close()
            if not os.access(log_filename, os.W_OK):
                log.warn(("Could not add file handler for site logger %r"
                           " (log file write permissions)"), site)
                return logger
            handler = logging.FileHandler(log_filename)
        except Exception, e:
            handler = logging.StreamHandler()
            log.exception("Could not create file handler for site logger %r",
                          site)
        else:
            handler.setFormatter(JSONFormatter(custom_format))
            logger.addHandler(handler)
    return logger

def init_site_loggers():
    """ Called once on App startup """
    import Zope2
    for ob in Zope2.app().objectValues():
        if INySite.providedBy(ob):
            try:
                create_site_logger(ob)
            except Exception, e:
                log.exception("Exception creating site logger for %r", ob)


## Common Site Logging Api ##

def log_user_access(context, who, how):
    """ On open/download of a content type """
    if how not in ALLOWED_SLUGS[ACCESS]:
        log.info("Invalid value for `how`: %r in logging access", how)
        return
    data = {
        'type': ACCESS,
        'action': how,
        'who': who,
        'content_path': ofs_path(context),
    }
    site_logger = get_site_logger(context.getSite())
    site_logger.info(data)

def log_user_management_action(context, who, whom, assigned, unassigned):
    """
    It is called where user management logging is required, guarantees
    consistency in log messages.

    * `who` and `whom` are user ids
    * `assigned` and `unnasigned` are lists of roles, both can not be empty

    """
    site_logger = get_site_logger(context.getSite())
    data = {
        'type': USER_MAN,
        'who': who,
        'whom': whom,
        'content_path': ofs_path(context),
    }

    if unassigned:
        site_logger.info(dict(data, action='UNASSIGNED', roles=unassigned))
    if assigned:
        site_logger.info(dict(data, action='ASSIGNED', roles=assigned))
