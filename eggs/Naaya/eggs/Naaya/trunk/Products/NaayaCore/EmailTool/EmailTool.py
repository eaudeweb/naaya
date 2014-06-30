"""
This tool provides e-mail management in a Naaya Site. Configurable e-mail
templates, e-mail sending and logging of all e-mail traffic.

"""

from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens   # , view
from Globals import InitializeClass
from OFS.Folder import Folder
from Products.NaayaCore.EmailTool.EmailValidator import EmailValidator
from Products.NaayaCore.constants import ID_EMAILTOOL
from Products.NaayaCore.constants import METATYPE_EMAILTEMPLATE
from Products.NaayaCore.constants import METATYPE_EMAILTOOL
from Products.NaayaCore.constants import PERMISSION_ADD_NAAYACORE_TOOL
from Products.NaayaCore.constants import TITLE_EMAILTOOL
from Products.NaayaCore.managers import import_export
from Products.NaayaCore.managers import utils
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from datetime import datetime, timedelta
from email import message_from_file
from email.MIMEText import MIMEText
from email.utils import make_msgid
from naaya.core.permissions import naaya_admin
from naaya.core.site_logging import get_log_dir
from naaya.core.utils import force_to_unicode
from urlparse import urlparse
from zope.component import queryUtility, getGlobalSiteManager
from zope.deprecation import deprecate
from zope.sendmail.interfaces import IMailDelivery
from zope.sendmail.mailer import SMTPMailer
import EmailTemplate
import json
import logging
import os
import random
import re
import time

try:
    import email.utils as email_utils
    import email.charset as email_charset
    import email.header as email_header
    import email.generator as email_generator
except ImportError, e:
    import email.Utils as email_utils
    import email.Charset as email_charset
    import email.Header as email_header
    import email.Generator as email_generator

email_validator = EmailValidator("checked_emails", maxWorkers=10)
g_utils = utils.utils()

DISABLED_EMAILS = ['disabled@eionet.europa.eu']

mail_logger = logging.getLogger('naaya.core.email')

try:
    import email.message
except ImportError:
    def create_plain_message(body_bytes):
        """
        This is just a simple factory for message instance (with payload)
        that works with both email.MIMEText (python 2.4)
        and email.message (python 2.6)

        """
        return MIMEText(body_bytes, 'plain')
else:
    def create_plain_message(body_bytes):
        message = email.message.Message()
        message.set_payload(body_bytes)
        return message


def manage_addEmailTool(self, REQUEST=None):
    """ """
    ob = EmailTool(ID_EMAILTOOL, TITLE_EMAILTOOL)
    self._setObject(ID_EMAILTOOL, ob)
    self._getOb(ID_EMAILTOOL).loadDefaultData()
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)


class EmailTool(Folder):
    """ """

    meta_type = METATYPE_EMAILTOOL
    icon = 'misc_/NaayaCore/EmailTool.gif'

    manage_options = (
        Folder.manage_options[:1]
        +
        (
            {'label': 'Settings', 'action': 'manage_settings_html'},
        )
        +
        Folder.manage_options[3:]
    )

    meta_types = (
        {'name': METATYPE_EMAILTEMPLATE,
         'action': 'manage_addEmailTemplateForm',
         'permission': PERMISSION_ADD_NAAYACORE_TOOL},
    )
    all_meta_types = meta_types

    manage_addEmailTemplateForm = EmailTemplate.manage_addEmailTemplateForm
    manage_addEmailTemplate = EmailTemplate.manage_addEmailTemplate

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        """ """
        self.id = id
        self.title = title

    security.declarePrivate('loadDefaultData')

    def loadDefaultData(self):
        # load default stuff
        pass

    def _guess_from_address(self):
        if self.portal_url != '':
            return 'notifications@%s' % urlparse(
                self.getSite().get_portal_domain())[1]
        else:
            return 'notifications@%s' % urlparse(self.REQUEST.SERVER_URL)[1]

    @deprecate('_get_from_address renamed to get_addr_from')
    def _get_from_address(self):
        return self.get_addr_from()

    security.declarePrivate('get_addr_from')

    def get_addr_from(self):
        """
        Get "From:" address, to use in mails originating from this portal. If
        no such address is configured then we attempt to guess it.
        """
        addr_from = self.getSite().mail_address_from
        return addr_from or self._guess_from_address()

    _errors_report = PageTemplateFile('zpt/configuration_errors_report',
                                      globals())
    security.declareProtected(naaya_admin, 'configuration_errors_report')

    def configuration_errors_report(self):
        errors = []
        delivery = queryUtility(IMailDelivery, 'naaya-mail-delivery')
        if delivery is None:
            if not (self.mail_server_name and self.mail_server_port):
                errors.append('Mail server address/port not configured')
        if not self.get_addr_from():
            errors.append('"From" address not configured')
        return self._errors_report(errors=errors)

    # api
    security.declarePrivate('sendEmail')

    def sendEmail(self, p_content, p_to, p_from, p_subject, _immediately=False,
                  p_cc=[]):
        """
        Send email message on transaction commit. If the transaction fails,
        the message is discarded.
        """
        if not isinstance(p_to, list):
            p_to = [e.strip() for e in p_to.split(',')]

        p_to = filter(None, p_to)  # filter out blank recipients

        if not isinstance(p_cc, list):
            p_cc = [e.strip() for e in p_cc.split(',')]

        p_cc = filter(None, p_cc)  # filter out blank recipients

        try:
            site = self.getSite()
            site_path = '/'.join(site.getPhysicalPath())
        except:
            site = None
            site_path = '[no site]'

        try:
            if diverted_mail is not None:  # we're inside a unit test
                diverted_mail.append([p_content, p_to, p_cc, p_from,
                                      p_subject])
                return 1

            delivery = delivery_for_site(site)
            if delivery is None:
                mail_logger.info('Not sending email from %r because mail '
                                 'server is not configured',
                                 site_path)
                return 0

            if not p_from:
                mail_logger.info('Not sending email from %r - no sender',
                                 site_path)
                return 0

            if not p_to:
                mail_logger.info('Not sending email from %r - no recipients',
                                 site_path)
                return 0

            if _immediately:
                delivery = _ImmediateDelivery(delivery)

            mail_logger.info('Sending email from site: %r '
                             'to: %r, cc: %r, subject: %r',
                             site_path, p_to, p_cc, p_subject)
            l_message = create_message(p_content, p_to, p_from, p_subject,
                                       addr_cc=p_cc)
            # Add CC recp. to the TO recp., this is the only way to send them
            send_by_delivery(delivery, p_from, p_to+p_cc, l_message)
            return 1

        except:
            mail_logger.error('Did not send email from site: %r to: %r '
                              'because an error occurred',
                              site_path, p_to)
            if site is not None:
                self.getSite().log_current_error()
            return 0

    security.declarePrivate('sendEmailImmediately')

    def sendEmailImmediately(self, *args, **kwargs):
        """
        Send email message straight away, without waiting for transaction
        commit. Useful when sending error emails because the transaction
        will probably be aborted.
        """
        kwargs['_immediately'] = True
        self.sendEmail(*args, **kwargs)

    security.declareProtected(view_management_screens, 'manageSettings')

    def manageSettings(self, mail_server_name='', mail_server_port='',
                       administrator_email='', mail_address_from='',
                       notify_on_errors_email='', REQUEST=None):
        """ """
        site = self.getSite()
        try:
            mail_server_port = int(mail_server_port)
        except:
            mail_server_port = site.mail_server_port
        site.mail_server_name = mail_server_name
        site.mail_server_port = mail_server_port
        site.mail_address_from = mail_address_from
        site.administrator_email = administrator_email
        site.notify_on_errors_email = notify_on_errors_email
        self._p_changed = 1
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_settings_html?save=ok')

    # zmi pages
    security.declareProtected(view_management_screens, 'manage_settings_html')
    manage_settings_html = PageTemplateFile('zpt/email_settings', globals())

InitializeClass(EmailTool)

diverted_mail = None


def divert_mail(enabled=True):
    global diverted_mail
    if enabled:
        diverted_mail = []
        return diverted_mail
    else:
        diverted_mail = None


def safe_header(value):
    """ prevent header injection attacks (the email library doesn't) """
    if '\n' in value:
        return email_header.Header(value.encode('utf-8'), 'utf-8')
    else:
        return value


def hack_to_use_quopri(message):
    """
    force message payload to be encoded using quoted-printable
    http://mail.python.org/pipermail/baypiggies/2008-September/003984.html
    """

    charset = email_charset.Charset('utf-8')
    charset.header_encoding = email_charset.QP
    charset.body_encoding = email_charset.QP

    del message['Content-Transfer-Encoding']
    message.set_charset(charset)


def send_by_delivery(delivery, p_from, p_to, message):
    """
    Send `message` email, where `message` is a MIMEText/Message instance
    created by create_message.
    Knows how to handle repoze.sendmail 2.3 differences in `message` arg type.

    """
    if p_to not in DISABLED_EMAILS:
        try:
            delivery.send(p_from, p_to, message.as_string())
        except AssertionError, e:
            if (e.args and e.args[0] ==
                    'Message must be instance of email.message.Message'):
                delivery.send(p_from, p_to, message)
            else:
                raise
        except ValueError, e:
            if (e.args and e.args[0] ==
                    'Message must be email.message.Message'):
                delivery.send(p_from, p_to, message)
            else:
                raise


def create_message(text, addr_to, addr_from, subject, addr_cc=[]):
    if isinstance(addr_to, basestring):
        addr_to = (addr_to,)
    addr_to = ', '.join(addr_to)
    if isinstance(addr_cc, basestring):
        addr_cc = (addr_cc,)
    addr_cc = ', '.join(addr_cc)
    subject = force_to_unicode(subject)
    text = force_to_unicode(text)

    message = create_plain_message(text.encode('utf-8'))
    hack_to_use_quopri(message)
    message['To'] = safe_header(addr_to)
    if addr_cc:
        message['Cc'] = safe_header(addr_cc)
    message['From'] = safe_header(addr_from)
    message['Subject'] = safe_header(subject)
    message['Date'] = email_utils.formatdate()

    return message


def save_bulk_email(site, addr_to, addr_from, subject, content,
                    where_to_save='sent-bulk', addr_cc=[]):
    """
    Save bulk email on disk.
    `addr_to` is a list; if there is more than one recipient,
    adds a 'To' header with each email address.

    """
    save_path = get_log_dir(site)
    join = os.path.join
    filename = None

    if save_path:
        save_path = join(save_path, where_to_save)
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        # Generate email filename according to zope.sendmail.maildir
        # but instead of hostname use site_id
        randmax = 0x7fffffff
        timestamp = int(time.time())
        unique = '%d.%d.%s.%d' % (timestamp, os.getpid(), site.getId(),
                                  random.randrange(randmax))
        filename = join(save_path, unique)
        message_file = os.open(filename,
                               os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                               0600)
        generator = email_generator.Generator(os.fdopen(message_file, 'w'))

        # Add multiple 'To' headers if there is more one receipent
        if len(addr_to) > 1:
            email_message = create_message(content, addr_to[0], addr_from,
                                           subject)
            addr_to.remove(addr_to[0])
            for mail in addr_to:
                email_message['To'] = mail
        else:
            email_message = create_message(content, addr_to, addr_from,
                                           subject)
        for mail in addr_cc:
            email_message['Cc'] = mail
        # Save email in specified file
        generator.flatten(email_message)
    else:
        mail_logger.warning("The bulk email could not be saved on the disk."
                            " Missing configuration for SITES_LOG_PATH?")
    return filename


def save_webex_email(site, addr_to, addr_from, subject, content,
                     where_to_save='sent-webex', others=None):
    """
    Save webex email on disk.
    `addr_to` is a list; if there is more than one recipient,
    adds a 'To' header with each email address.

    """
    save_path = get_log_dir(site)
    join = os.path.join
    filename = None

    if save_path:
        save_path = join(save_path, where_to_save)
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        # Generate email filename according to zope.sendmail.maildir
        # but instead of hostname use site_id
        randmax = 0x7fffffff
        timestamp = int(time.time())
        unique = '%d.%d.%s.%d' % (timestamp, os.getpid(), site.getId(),
                                  random.randrange(randmax))
        filename = join(save_path, unique)
        message_file = os.open(filename,
                               os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                               0600)
        generator = email_generator.Generator(os.fdopen(message_file, 'w'))

        # Add multiple 'To' headers if there is more than one recipient
        if len(addr_to) > 1:
            email_message = create_message(content, addr_to[0], addr_from,
                                           subject)
            addr_to.remove(addr_to[0])
            for mail in addr_to:
                email_message['To'] = mail
        else:
            email_message = create_message(content, addr_to, addr_from,
                                           subject)
        # hide meeting info in header field
        email_message['X-Accept-Webex-Data'] = json.dumps(others)

        # Save email in specified file
        generator.flatten(email_message)
    else:
        mail_logger.warning("The webex email could not be saved on the disk."
                            "There is missing configuration(SITES_LOG_PATH)."
                            "Please contact the platform maintainers.")
    return filename


def _get_message_path(site, where_to_read):
    save_path = get_log_dir(site)
    if not save_path:
        return None
    save_path = os.path.join(save_path, where_to_read)
    if not os.path.isdir(save_path):
        return None
    return save_path


def get_bulk_emails(site, where_to_read='sent-bulk'):
    """
    Show all bulk emails saved on the disk
    (Used for webex email too)
    """
    save_path = _get_message_path(site, where_to_read)
    if not save_path:
        return []
    # Get all messages files
    messages = [os.path.join(save_path, filename)
                for filename in os.listdir(save_path)
                if not filename.startswith('.')]

    # Sort them descending by the last modification time
    sorted_messages = [(message, os.path.getmtime(message))
                       for message in messages]
    sorted_messages.sort(key=lambda x: x[1], reverse=True)
    messages = [message[0] for message in sorted_messages]

    emails = []
    for message in messages:
        filename = os.path.split(message)[-1]
        email = get_bulk_email(site, filename, message_file_path=message)
        if email:
            email['filename'] = filename
            emails.append(email)
    return emails


def get_bulk_email(site, filename, where_to_read='sent-bulk',
                   message_file_path=None):
    """ Show a specific bulk email saved on the disk """
    try:
        if not message_file_path:
            save_path = _get_message_path(site, where_to_read)
            message_file_path = os.path.join(save_path, filename)
        message_file = open(message_file_path, 'r+')
    except (IOError, TypeError, AttributeError):
        return None

    mail = message_from_file(message_file)
    message_file.close()

    # Prepare the date to be formatted with utShowFullDateTime
    date = email_utils.parsedate_tz(mail.get('Date', ''))
    date = email_utils.mktime_tz(date)
    date = datetime.fromtimestamp(date)

    r = {
        'subject': mail.get('Subject', '(no-subject)'),
        'content': mail.get_payload(decode=True).replace(
            '\n\n', '</p><p>').replace('\n', '<br/>'),
        'recipients': mail.get_all('To'),
        'cc_recipients': mail.get_all('Cc'),
        'sender': mail.get('From'),
        'date': date,
        'webex': mail.get('X-Accept-Webex-Data', '')
    }
    return r


# alter mutable email to fit xcel row
def _prepare_xcel_data(email, site, check_status):
    _separator = ', '
    _max_cell = 32767
    if check_status:
        # no dict comprehension in python 2.6 :((
        # beautify this when we get to 2.7
        check_values = {}
        for k in ['sender', 'recipients', 'subject', 'content', 'date']:
            check_values[k] = email.get(k, '')
        email['status'] = _mail_in_queue(site, email['filename'], check_values)
    for k, v in email.items():
        if v is None:
            email[k] = ''
        elif isinstance(v, tuple) or isinstance(v, list):
            # FIXME: elements inside iteratable must be strings...
            email[k] = _separator.join(v)
        elif isinstance(v, datetime):
            email[k] = g_utils.utShowFullDateTime(v)
        else:
            email[k] = unicode(v)
        # xcel limit for cell content
        if len(email[k]) > _max_cell:
            email[k] = email[k][:_max_cell]
    return email


def export_email_list_xcel(site, cols, filenames=None,
                           where_to_read='sent-bulk'):
    """Generate excel file with columns named after first value of
    tuples in cols, and the contets of the cells set by the key in
    the second value of the tuple in cols

    If key named exactly 'status' is present make a status check
    and include it in the resulting excel.
    """
    emails = get_bulk_emails(site, where_to_read=where_to_read)
    header = [v[0] for v in cols]
    rows = []
    check_status = True if 'status' in [v[1] for v in cols] else False
    for eml in emails:
        if not filenames or eml['filename'] in filenames:
            _prepare_xcel_data(eml, site, check_status)
            r = []
            for _, key in cols:
                r.append(eml.get(key, ''))
            rows.append(r)
    r = import_export.generate_excel(header, rows)
    return r


def check_cached_valid_emails(obj, emails):
    """Instance calling this (obj) must have a dict like member checked_emails
    on it.
    This breaks encapsulation and should be done better, probably in NySite"""
    invalid_emails = []
    not_resolved_emails = []
    if type(emails) == str:
        emails = [emails]
    email_validator.bind(obj)
    for eml in emails:
        check_value = email_validator.validate_from_cache(eml)
        if check_value is False:
            invalid_emails.append(eml)
        elif check_value is None:
            not_resolved_emails.append(eml)
    if not_resolved_emails:
        _defer_check_valid_emails(obj, not_resolved_emails)
    return invalid_emails, not_resolved_emails


def _defer_check_valid_emails(obj, emails):
    emails = set(emails)
    email_validator.bind(obj)
    for eml in emails:
        email_validator.enqueue(eml)


def get_mail_queue(site):
    """ Get a list of files that are still in the NEW mail_queue folder """
    join = os.path.join

    queue_path = os.environ.get('NAAYA_MAIL_QUEUE', None)
    if queue_path is None:
        return []

    mail_queue = []
    new_queue_path = join(queue_path, 'new')
    if os.path.isdir(new_queue_path):
        # Get all messages files
        messages = [join(new_queue_path, filename)
                    for filename in sorted(os.listdir(new_queue_path))]

        for message in messages:
            message_file = open(message, 'r+')
            mail = message_from_file(message_file)
            message_file.close()

            # Prepare the date to be formatted with utShowFullDateTime
            date = email_utils.parsedate_tz(mail.get('Date', ''))
            date = email_utils.mktime_tz(date)
            date = datetime.fromtimestamp(date)

            mail_queue.append({
                'subject': mail.get('Subject', '(no-subject)'),
                'content': mail.get_payload(decode=True),
                'recipients': mail.get_all('To'),
                'sender': mail.get('From'),
                'date': date,
                'filename': os.path.split(message)[-1]
            })

    return mail_queue


def get_webex_email(site, filename, where_to_read='sent-webex'):
    """ Show a specific webex email saved on the disk """
    save_path = get_log_dir(site)
    join = os.path.join

    if save_path:
        save_path = join(save_path, where_to_read)
        if os.path.isdir(save_path):
            message_path = join(save_path, filename)

            try:
                message_file = open(message_path, 'r+')
            except IOError:
                return None
            mail = message_from_file(message_file)
            message_file.close()

            # Prepare the date to be formatted with utShowFullDateTime
            date = email_utils.parsedate_tz(mail.get('Date', ''))
            date = email_utils.mktime_tz(date)
            date = datetime.fromtimestamp(date)

            return {
                'subject': mail.get('Subject', '(no-subject)'),
                'content': mail.get_payload(decode=True).replace(
                    '\n\n', '</p><p>').replace('\n', '<br/>'),
                'recipients': mail.get_all('To'),
                'sender': mail.get('From'),
                'date': date,
                'webex': mail.get('X-Accept-Webex-Data', '')
            }


class BestEffortSMTPMailer(SMTPMailer):
    """
    Try to send the message; if we fail, just log the error, and don't abort
    the transaction.
    """
    def send(self, fromaddr, toaddrs, message):
        try:
            super(BestEffortSMTPMailer, self).send(fromaddr, toaddrs, message)
        except:
            mail_logger.exception("Failed to send email message.")
            # TODO write message to the portal's `error_log`


def delivery_for_site(site=None):
    delivery = queryUtility(IMailDelivery, 'naaya-mail-delivery')
    if delivery is not None:
        return delivery

    elif site and site.mail_server_name and site.mail_server_port:
        from zope.sendmail.delivery import DirectMailDelivery
        site_mailer = BestEffortSMTPMailer(site.mail_server_name,
                                           site.mail_server_port)
        return DirectMailDelivery(site_mailer)

    else:
        return None


class _ImmediateDelivery(object):
    """
    Hack a queued message delivery to send the message immediately, and not
    wait for transaction finish; useful when sending error messages.
    """
    def __init__(self, delivery):
        self._d = delivery

    def send(self, fromaddr, toaddrs, message):
        try:
            message_id = self._d.newMessageId()
        except AttributeError:      # repose.sendmail compatibility
            message_id = make_msgid('repoze.sendmail')
        email_message = create_plain_message(message)
        email_message['Message-Id'] = '<%s>' % message_id
        # make data_manager think it's being called by a transaction
        try:
            data_manager = self._d.createDataManager(fromaddr, toaddrs,
                                                     email_message)
        except TypeError:
            # backwards compat with zope.sendmail and repoze.sendmail < 2.0
            message_bytes = 'Message-Id: <%s>\n%s' % (message_id, message)
            data_manager = self._d.createDataManager(fromaddr, toaddrs,
                                                     message_bytes)
        data_manager.tpc_finish(None)


def configure_mail_queue():
    """
    Check if a mail queue path is configured; register a QueuedMailDelivery.
    """
    queue_path = os.environ.get('NAAYA_MAIL_QUEUE', None)
    if queue_path is None:
        return

    from zope.sendmail.interfaces import IMailDelivery
    try:
        from repoze.sendmail.delivery import QueuedMailDelivery
    except ImportError:
        from zope.sendmail.delivery import QueuedMailDelivery
    gsm = getGlobalSiteManager()
    gsm.registerUtility(QueuedMailDelivery(queue_path),
                        IMailDelivery, "naaya-mail-delivery")

    mail_logger.info("Mail queue: %r", queue_path)


def _mail_in_queue(site, filename, check_values):
    """ Check if a specific message is still in queue """
    mail_queue = get_mail_queue(site)
    filename_split = filename.split('.')
    for queued_email in mail_queue:
        sending = False
        if queued_email['filename'].startswith('.sending-'):
            sending = True
            queued_email['filename'] = queued_email['filename'].replace(
                '.sending-', '')
        email_split = queued_email['filename'].split('.')
        if (filename_split[0] == email_split[0] and
                filename_split[1] == email_split[1]):
            for k, v in check_values.items():
                if k in ['recipients', 'cc_recipients']:
                    queued_recipients = set(
                        re.split(", |,\n\t|,\n", queued_email[k][0]))
                    if queued_recipients != set(v):
                        break
                elif isinstance(v, basestring):
                    if _strip_code(queued_email.get(k)) != _strip_code(v):
                        break
            else:
                if sending:
                    if datetime.now() > queued_email['date'] + timedelta(
                            minutes=5):
                        return 'Send error'
                return 'In sending queue'
    return 'Sent'


def _strip_code(text_str):
    return text_str.replace('\n', '').replace('</p><p>', '')
