# python imports
import threading
import traceback
from datetime import datetime

# zope imports
from persistent.list import PersistentList
from ZODB.POSException import POSError
import zLOG

# naaya imports
from naaya.core.utils import ofs_path

def start_sending_emails(site, group, userids, roles, loc, location):
    """
    start the thread to send the emails
    the thread gets the db, the path to the current site and
    all the other arguments required to send each email
    """
    site_path = ofs_path(site)
    db = site._p_jar._db
    t = threading.Thread(target=send_emails,
            args=(db, site_path, group, userids, roles, loc, location))
    t.start()

def send_emails(db, site_path, group, userids, roles, loc, location):
    """
    main function of the thread

    the thread is expected to be able to get the site and auth_tool objects
    if it can't do that we can't save any error information
    """
    #gets the site object and auth_tool object from the database
    conn = db.open()
    app = conn.root()['Application']
    site = app.unrestrictedTraverse(site_path)
    auth_tool = site.getAuthenticationTool()

    errors = []
    start_time = datetime.now()
    # the main try...except if something unexpected happens
    try:
        emails = auth_tool.getUsersEmails(userids)
        for email in emails:
            # if one sending crashes, just get the error and continue
            try:
                site.sendAccountModifiedEmail(email, roles, loc, location)
            except Exception, error:
                errors.append({'email': email,
                               'error': error,
                               'traceback': traceback.format_exc()})
    except Exception, error:
        main_error = error
    else:
        main_error = None
    finish_time = datetime.now()

    # save the error information to auth_tool
    if not hasattr(auth_tool, '_send_emails_log'):
        auth_tool._send_emails_log = PersistentList()
    auth_tool._send_emails_log.append({'start_time': start_time,
                                       'finish_time': finish_time,
                                       'group': group,
                                       'roles': roles,
                                       'loc': loc,
                                       'location': location,
                                       'main_error': main_error,
                                       'errors': errors,
                                       })

    try:
        import transaction; transaction.commit()
    except POSError, e:
        zLOG.LOG('Products.NaayaCore.AuthenticationTool', zLOG.ERROR,
                'Commiting the transaction on send_group_emails_thread - %s'
                    % str(e),
                'Email sending finished with info: %s\n\n Traceback: %s'
                    % (str(errors), traceback.format_exc()))


