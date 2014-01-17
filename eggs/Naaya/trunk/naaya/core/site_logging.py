from Products.Naaya.interfaces import INySite
from datetime import datetime
from naaya.core.backport import json
from naaya.core.jsonlogger import JSONFormatter
from naaya.core.utils import file_length
from naaya.core.zope2util import get_zope_env, ofs_path
import logging
import os
import time


log = logging.getLogger(__name__)

SITES_LOG_PATH_VAR = 'SITES_LOG_PATH' # name of config env. var
SUFFIX = '-site-logger' # for naming loggers

ACCESS = 'ACCESS'
USER_MAN = 'USER_MANAGEMENT'
ALLOWED_SLUGS = {ACCESS: ("VIEW", "DOWNLOAD", ),
                 USER_MAN: ("ASSIGNED", "UNASSIGNED", ),
                }
LOG_FILENAME = 'site.log'

def get_site_slug(site):
    """ An identifier valid on filesystem """
    return ofs_path(site).strip('/').replace('/', ',')

def get_log_dir(site):
    """
    Each site has its own folder in SITES_LOG_PATH_VAR
    Factory for returning that folder path.

    """
    abs_path = get_zope_env(SITES_LOG_PATH_VAR)
    if not abs_path:
        log.warning("Could not find SITES_LOG_PATH_VAR env variable")
        return None

    abs_path = os.path.join(abs_path, get_site_slug(site))
    if not os.path.exists(abs_path):
        try:
            os.makedirs(abs_path)
        except Exception:
            return None

    return abs_path

def get_site_logger(site):
    """
    Returns a logger based on site ID which will save actions on content types

    """
    site_logger_slug = get_site_slug(site)
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
    if hasattr(logger.handlers, '__iter__'): # for testing - i really give up!!
        existing = list(logger.handlers)
        for handler in existing:
            try:
                logger.removeHandler(handler)
            except Exception:
                log.exception("Could not remove existing site logger handler")
    custom_format = '%(asctime) %(message)'
    abs_path = get_log_dir(site)
    if abs_path:
        try:
            log_filename = os.path.join(abs_path, LOG_FILENAME)
            if not os.access(log_filename, os.F_OK):
                open(log_filename, 'a').close()
            if not os.access(log_filename, os.W_OK):
                log.warn(("Could not add file handler for site logger %r"
                           " (log file write permissions)"), site)
                return logger
            handler = logging.FileHandler(log_filename)
        except Exception:
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
            except Exception:
                log.exception("Exception creating site logger for %r", ob)

## Views ##
def readable_action(line_data):
    """ Returns the human-readable message of the log line """
    if line_data['type'] not in ALLOWED_SLUGS:
        return 'Unknown event type %r' % line_data['action']
    elif line_data['type'] == USER_MAN:
        return ("<strong>%s</strong> was %s the following roles: %s" %
                (line_data['whom'], line_data['action'],
                 ', '.join(line_data['roles'])))
    elif line_data['type'] == ACCESS:
        return ("%sED the content" % line_data['action'])

def get_site_logger_content(site, REQUEST=None, RESPONSE=None):
    """
    Returns plain text and parsed lines of logging files for actions on
    content

    """
    lines = []
    plain_text_lines = []
    show_plain_text = False
    writeable = False
    abs_path = get_log_dir(site)
    if not abs_path:
        return {
            'writeable': writeable,
            'lines': lines,
            'plain_text_lines': plain_text_lines,
        }

    log_filename = os.path.join(abs_path, LOG_FILENAME)
    if os.path.exists(log_filename) and os.access(log_filename, os.W_OK):
        writeable = True
        log_file = open(log_filename)
        file_len = file_length(log_filename)

        if file_len < 200:
            show_plain_text = True

        for line in log_file:
            if show_plain_text:
                plain_text_lines.append(line)

            line = json.loads(line)
            line_data = line['message']
            date_str = line['asctime']
            time_tuple = time.strptime(date_str, "%y-%m-%d %H:%M:%S,%f")
            line_data['date'] = datetime(*(time_tuple[0:6]))
            line_data['readable_message'] = readable_action(line_data)
            lines.append(line_data)

    return {
        'writeable': writeable,
        'lines': lines,
        'plain_text_lines': plain_text_lines,
    }

def admin_download_log_file(site, REQUEST=None, RESPONSE=None):
    """
    Download logging files for actions made on content types

    """
    from Products.NaayaCore.managers.import_export import set_response_attachment
    from StringIO import StringIO
    abs_path = get_log_dir(site)
    log_filepath = os.path.join(abs_path, LOG_FILENAME)
    log_file = open(log_filepath, 'r+')
    data = log_file.read()
    log_file.close()
    output = StringIO()
    output.write(data)
    set_response_attachment(REQUEST.RESPONSE, '%s.log' % get_site_slug(site),
                            'text/html; charset=utf-8', output.len)
    return output.getvalue()

def clear_log_file(site, REQUEST=None, RESPONSE=None):
    """
    Truncate log file
    OBS: Not used

    """
    from naaya.core.utils import is_ajax
    if is_ajax(REQUEST):
        get_log_dir(site)   # TODO: is this needed?
        log_file = open(LOG_FILENAME, 'r+')
        log_file.truncate()
        log_file.close()
        return "SUCCESS"
    else:
        REQUEST.RESPONSE.redirect(site.absolute_url())

def admin_toggle_logger(site, enabled=False, REQUEST=None, RESPONSE=None):
    """
    Enable/Disable site logger
    OBS: Not used

    """
    from naaya.core.utils import str2bool
    site.gl_get_selected_language()     # TODO: is this needed?
    enabled = str2bool(REQUEST.form.get('enabled', False))
    if enabled in [True, False]:
        site.content_action_logging = enabled
    #site.setSessionInfoTrans(MESSAGE_SAVEDCHANGES,
    #                         date=site.utGetTodayDate())
    REQUEST.RESPONSE.redirect('%s/admin_site_logging_html'
                              % (site.absolute_url()))

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
