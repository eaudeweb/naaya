# python imports
import threading
import traceback
from datetime import datetime
import Queue
import logging

# zope imports
from persistent.list import PersistentList
from ZODB.POSException import POSError
import transaction

# naaya imports
from naaya.core.zope2util import ofs_path

auth_logger = logging.getLogger('naaya.core.auth')

def start_sending_emails(site, group, userids, roles, loc, location):
    auth_logger.debug('start sending emails for group %s', group)

    def db_callback():
        return site._p_jar._db

    site_path = ofs_path(site)
    add_job(db_callback, site_path, group, userids, roles, loc, location)

    auth_logger.debug('finished sending emails for group %s', group)

# _jobs_queue is None if there is no worker thread started
_jobs_queue = None
# a lock used to check if _jobs_queue is None or an actual queue
_jobs_queue_lock = threading.Lock()
def add_job(db_callback, site_path, group, userids, roles, loc, location):
    global _jobs_queue

    _jobs_queue_lock.acquire()
    try:
        start_thread = _jobs_queue is None

        if _jobs_queue is None:
            _jobs_queue = Queue.Queue()
        _jobs_queue.put({'site_path': site_path,
                         'group': group,
                         'userids': userids,
                         'roles': roles,
                         'loc': loc,
                         'location': location})
    finally:
        _jobs_queue_lock.release()

    auth_logger.debug('added the new email sending job to the queue')

    if start_thread:
        auth_logger.debug('starting new email sending thread')
        db = db_callback()
        t = threading.Thread(target=send_emails_thread, args=(db,))
        t.start()

def send_emails_thread(db):
    """
    main function of the thread
    """
    global _jobs_queue

    conn = db.open()
    try:
        app = conn.root()['Application']

        while True:
            _jobs_queue_lock.acquire()
            try:
                if _jobs_queue.empty():
                    _jobs_queue = None
                    auth_logger.debug('finished the job queue, closing thread')
                    break
            finally:
                _jobs_queue_lock.release()

            auth_logger.debug('start executing new job')
            job_args = _jobs_queue.get()
            try:
                send_emails_job(app, **job_args)
            except Exception, e:
                auth_logger.exception(
                        'Error on send emails job - %s\n\nTraceback: %s',
                        (str(e), traceback.format_exc()))
    finally:
        conn.close()


def send_emails_job(app, site_path, group, userids, roles, loc, location):
    """
    the thread is expected to be able to get the site and auth_tool objects
    if it can't do that we can't save any error information
    """
    site = app.unrestrictedTraverse(site_path)
    auth_tool = site.getAuthenticationTool()

    if not hasattr(auth_tool, '_send_emails_log'):
        auth_logger.debug('Adding the _send_emails_log attribute to auth_tool')
        auth_tool._send_emails_log = PersistentList()
        transaction.commit()

    errors = []
    start_time = datetime.now()
    # the main try...except if something unexpected happens
    try:
        emails = auth_tool.getUsersEmails(userids)
        auth_logger.debug('Finished getting the user emails')

        for email in emails:
            # if one sending crashes, just get the error and continue
            try:
                auth_logger.debug('Sending email to %s', email)
                site.sendAccountModifiedEmail(email, roles, loc, location)
            except Exception, error:
                errors.append({'email': email,
                               'error': error,
                               'traceback': traceback.format_exc()})
                auth_logger.exception('Error sending email to %s', email)
    except Exception, error:
        main_error = error
        auth_logger.exception('Main error sending emails: %s\n\nTraceback: %s',
                str(error), traceback.format_exc())
    else:
        main_error = None
    finish_time = datetime.now()

    info = {'start_time': start_time,
            'finish_time': finish_time,
            'group': group,
            'roles': roles,
            'loc': loc,
            'location': location,
            'main_error': main_error,
            'errors': errors}
    auth_logger.debug('Email sending finished with info: %s', str(errors))

    for i in range(3):
        auth_tool._send_emails_log.append(info)

        try:
            transaction.commit()
        except POSError, e:
            transaction.abort()
            auth_logger.exception(
                    'Commiting the transaction on send_group_emails_thread - %s\n\nTraceback: %s'
                    , str(e), traceback.format_exc())
        else:
            break
    else:
        auth_logger.critical('Could not commit the transaction')

