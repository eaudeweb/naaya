from Products.Naaya.interfaces import INySite
from datetime import datetime, date
from naaya.core.backport import json
from naaya.core.jsonlogger import JSONFormatter
from naaya.core.zope2util import get_zope_env, ofs_path
import codecs
import logging
import os
import re
import time


log = logging.getLogger(__name__)

SITES_LOG_PATH_VAR = 'SITES_LOG_PATH'  # name of config env. var
SUFFIX = '-site-logger'  # for naming loggers

ACCESS = 'ACCESS'
USER_MAN = 'USER_MANAGEMENT'
ALLOWED_SLUGS = {ACCESS: ("VIEW", "DOWNLOAD", ),
                 USER_MAN: ("ASSIGNED", "UNASSIGNED", ),
                 }
#LOG_FILENAME = 'site.log'
LOG_PREFIX = 'splitlog'


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


class MonthBasedFileHandler(logging.StreamHandler):

    """
    A handler class which writes formatted logging records to monthly-separated files.

    Code copied and modified from Standard Library logging.__init__
    """

    _last_recorded_month = None

    def __init__(self, prefix, mode='a', encoding=None, delay=0):
        """
        Open the specified file and use it as the stream for logging.
        """

        # keep the absolute path, otherwise derived classes which use this
        # may come a cropper when the current directory changes
        if codecs is None:
            encoding = None

        self.baseFilename = os.path.abspath(prefix)
        self.mode = mode
        self.encoding = encoding
        if delay:
            # We don't open the stream, but we still need to call the
            # Handler constructor to set level, formatter, lock etc.
            logging.Handler.__init__(self)
            self.stream = None
        else:
            logging.StreamHandler.__init__(self, self._open())

    def close(self):
        """
        Closes the stream.
        """
        if self.stream:
            self.flush()
            if hasattr(self.stream, "close"):
                self.stream.close()
            logging.StreamHandler.close(self)
            self.stream = None

    def _open(self):
        """
        Open the current base file with the (original) mode and encoding.
        Return the resulting stream.
        """
        if self._last_recorded_month == None:
            self._last_recorded_month = date.today().strftime("%y-%m")

        filename = "%s-%s.log" % (self.baseFilename, self._last_recorded_month)

        if self.encoding is None:
            stream = open(filename, self.mode)
        else:
            stream = codecs.open(filename, self.mode, self.encoding)

        return stream

    def emit(self, record):
        """
        Emit a record.

        If the stream was not opened because 'delay' was specified in the
        constructor, open it before calling the superclass's emit.
        """

        if date.today().strftime("%y-%m") != self._last_recorded_month:
            self.close()

        if self.stream is None:
            self.stream = self._open()

        logging.StreamHandler.emit(self, record)


def create_site_logger(site):
    """
    Sets proper file handler to corresponding site logger.
    Called on startup for all existing INySites or after creation of a site.
    Caution: removes previous handlers, if any

    """
    logger = get_site_logger(site)
    logger.propagate = 0
    logger.setLevel(logging.INFO)
    # for testing - i really give up!!
    if hasattr(logger.handlers, '__iter__'):
        existing = list(logger.handlers)
        for handler in existing:
            try:
                logger.removeHandler(handler)
            except Exception:
                log.exception("Could not remove existing site logger handler")
    custom_format = '%(asctime) %(message)'
    abs_path = get_log_dir(site)
    if abs_path:

        # First, we look to see if the site logs have been migrated
        is_migrated = bool([n for n in os.listdir(abs_path) if 'splitlog' in n])
        if not is_migrated:
            rewrite_logs(abs_path)

        try:
            # log_filename = os.path.join(abs_path, LOG_FILENAME)
            # if not os.access(log_filename, os.F_OK):
            #     open(log_filename, 'a').close()
            # if not os.access(log_filename, os.W_OK):
            #     log.warn(("Could not add file handler for site logger %r"
            #                " (log file write permissions)"), site)
            #     return logger
            prefix = os.path.join(abs_path, LOG_PREFIX)
            handler = MonthBasedFileHandler(prefix=prefix)
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

# Views ##


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


LOGGED_MONTH_REGEXP = re.compile("^" + LOG_PREFIX + "-(.*).log$")


def get_logged_months(site, REQUEST=None, RESPONSE=None):
    """ Returns a list of months that are in the site logged folder
    """
    abs_path = get_log_dir(site)
    if not abs_path:
        return []

    matches = sorted((m.groups()[0] for m in
                      filter(None,
                             [LOGGED_MONTH_REGEXP.match(
                                 n) for n in os.listdir(abs_path)])),
                     reverse=True)
    today = date.today()
    this_month = today.strftime("%y-%m")
    if not this_month in matches:
        matches.insert(0, this_month)
    return matches


def get_site_logger_content(site, REQUEST=None, RESPONSE=None, month=None):
    """
    Returns plain text and parsed lines of logging files for actions on
    content

    month is an optional string in form of "shortyear-month", ex: '13-05'
    """
    lines = []
    plain_text_lines = []
    #show_plain_text = False
    abs_path = get_log_dir(site)

    if not abs_path:
        return {
            'writeable': False,
            'lines': lines,
            'plain_text_lines': plain_text_lines,
        }

    if month:
        if month == 'current':
            today = date.today()
            month = today.strftime("%y-%m")
        log_filenames = [LOG_PREFIX + "-%s.log" % month]
    else:
        log_filenames = [
            n for n in os.listdir(abs_path) if n.startswith(LOG_PREFIX)]

    log_filenames.sort()

    lines = []
    writeables = []

    for logname in log_filenames:
        lfname = os.path.join(abs_path, logname)

        if (not os.path.exists(lfname)) and os.access(lfname, os.W_OK):
            log.error("Could not access log file %s", lfname)
            writeables.append(False)
            continue

        log_file = open(lfname)
        writeables.append(True)

        c = 0
        for line in log_file:
            c += 1
            plain_text_lines.append(line)

            try:
                line = json.loads(line)
            except json.JSONDecodeError:
                log.error("Could not parse line %s from file %s", c, lfname)
                continue

            line_data = line['message']
            date_str = line['asctime']
            time_tuple = time.strptime(date_str, "%y-%m-%d %H:%M:%S,%f")
            line_data['date'] = datetime(*(time_tuple[0:6]))
            line_data['readable_message'] = readable_action(line_data)
            lines.append(line_data)

    return {
        'writeable': all(writeables),
        'lines': lines,
        'plain_text_lines': plain_text_lines,
    }


def admin_download_log_file(site, REQUEST=None, RESPONSE=None):
    """
    Download logging files for actions made on content types

    """
    raise NotImplementedError

    from Products.NaayaCore.managers.import_export import set_response_attachment
    from StringIO import StringIO
    abs_path = get_log_dir(site)
    # TODO: redo this
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
    raise NotImplementedError

    from naaya.core.utils import is_ajax
    if is_ajax(REQUEST):
        get_log_dir(site)   # TODO: is this needed?
        # TODO: redo this
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
    # site.setSessionInfoTrans(MESSAGE_SAVEDCHANGES,
    #                         date=site.utGetTodayDate())
    REQUEST.RESPONSE.redirect('%s/admin_site_logging_html'
                              % (site.absolute_url()))

# Common Site Logging Api ##


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


def rewrite_logs(path):
    """ This is called by the site logger initialization code to migrate
    the logs from being written in site.log to being written in separate files
    """
    log.info("Migrating logs old storage to new storage for %s", path)
    to_process = []
    for name in os.listdir(path):
        if name.startswith('site.log'):
            to_process.append(name)

    entries = {}

    for name in to_process:
        fname = os.path.join(path, name)
        with open(fname) as f:
            counter = 0
            for line in f:
                counter += 1
                try:
                    data = json.loads(line)
                except:
                    log.warning("Line %s could not be parsed in file %s" % (
                        counter, fname))
                    continue
                date = data['asctime']
                ident = date[:5]  # date looks like: "12-09-17 17:02:49,451019"
                if not ident in entries:
                    entries[ident] = []

                entries[ident].append(line)

    for ident in entries.keys():
        flog = os.path.join(path, "splitlog-" + ident + '.log')
        with open(flog, 'w') as _log:
            _log.writelines(entries[ident])
