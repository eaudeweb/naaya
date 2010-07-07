#Python imports

#Zope imports
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view

#Naaya imports
from Products.NaayaBase.constants import PERMISSION_EDIT_OBJECTS
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from Products.NaayaCore.EmailTool.EmailPageTemplate import EmailPageTemplateFile

#naaya.content.meeting imports
from utils import getUserEmail

class EmailSender(SimpleItem):
    security = ClassSecurityInfo()

    title = 'Send Emails'

    def __init__(self, id):
        """ """
        self.id = id

    def getMeeting(self):
        return self.aq_parent

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self,
                                                 'meeting': self.getMeeting()},
                        'naaya.content.meeting.email_index')

    def _send_email(self, p_from, p_to, p_subject, p_content):
        """ """
        try:
            email_tool = self.getEmailTool()
            return email_tool.sendEmail(p_content=p_content,
                                p_to=p_to,
                                p_from=p_from,
                                p_subject=p_subject)
        except:
            return 0

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'send_email')
    def send_email(self, from_email, subject, body_text, REQUEST, to_uids=None):
        """ """
        result = 0
        if to_uids is not None:
            assert isinstance(to_uids, list)
            to_emails = [getUserEmail(self.getSite(), uid) for uid in to_uids]

            result = self._send_email(from_email, to_emails, subject, body_text)

        return self.getFormsTool().getContent({'here': self,
                                                'meeting': self.getMeeting(),
                                                'result': result},
                        'naaya.content.meeting.email_sendstatus')

    _signup_email = EmailPageTemplateFile('zpt/email_signup_accepted.zpt', globals())
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'send_signup_accepted_email')
    def send_signup_accepted_email(self, signup):
        """ """
        meeting = self.getMeeting()
        subscriptions = meeting.getParticipants().getSubscriptions()
        from_email = meeting.contact_email
        to_email = signup.email
        login_url = subscriptions.absolute_url() + '/welcome?key=' + signup.key

        mail_opts = {'meeting': meeting,
                     'name': signup.name,
                     'login_url': login_url}
        mail_data = self._signup_email.render_email(**mail_opts)

        subject = mail_data['subject']
        body_text = mail_data['body_text']

        return self._send_email(from_email, to_email, subject, body_text)


NaayaPageTemplateFile('zpt/email_index', globals(),
        'naaya.content.meeting.email_index')
NaayaPageTemplateFile('zpt/email_sendstatus', globals(),
        'naaya.content.meeting.email_sendstatus')

