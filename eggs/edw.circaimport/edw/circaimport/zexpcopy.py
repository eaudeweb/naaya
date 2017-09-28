"""
This is not exactly a CIRCA related feature, but it is used in EIONET
Forum to move data from Archives instance to Forum/Projects.

"""
import re
import transaction

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.NaayaCore.EmailTool.EmailTool import EmailTool
from naaya.core.zope2util import get_zope_env


NETWORK_NAME = get_zope_env('NETWORK_NAME', 'Eionet')
export_completed_message_zpt = PageTemplateFile('zpt/zexpcopy/mail_export_done.zpt',
                                             globals())


def manage_main_catch_path(self, REQUEST, manage_tabs_message, title):
    """
    Unfortunately ObjectManager.manage_exportObject does not return a value.
    We have to pretend we have request and mock the manage_main call
    to get the path of the zexp on server.

    """
    pattern = r'<em>(.*?)</em> successfully exported to <em>(.*?)</em>'
    path = re.match(pattern, manage_tabs_message)
    if not path:
        raise ValueError("Can not deduct zexp path from ZMI message")
    return path.groups()[1]

def write_zexp(ob):
    """ Generates corresponding zexp file of `ob` and any objects under it """
    sp = transaction.savepoint()
    try:
        ob.manage_main = manage_main_catch_path
        path_on_disk = ob.manage_exportObject(REQUEST=True)
    finally:
        sp.rollback()
    return path_on_disk

def load_zexp(zexp_path, destination):
    """ Given the zexp file, it loads the data in the given OFS destination """
    existing = destination.objectIds()
    destination._importObjectFromFile(zexp_path, verify=0, set_owner=0)
    new_ids = list(set(destination.objectIds()) - set(existing))
    # should I assert len(new_ids) == 1 ?
    return new_ids

def send_action_completed_mail(mail_body, mail_from, mail_to, mail_subject):
    """ Calls an email sender to deliver the info message """
    email_sender = EmailTool('email_sender', 'Zexpcopy email sender')
    mail_body = "%s \n\nHave a great day,\n%s" % (mail_body, NETWORK_NAME)
    email_sender.sendEmail(mail_body, mail_to, mail_from, mail_subject)
