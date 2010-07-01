#Python imports

#Zope imports
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view

#Naaya imports
from Products.NaayaBase.constants import PERMISSION_EDIT_OBJECTS
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile

#naaya.content.meeting imports
from utils import getUserEmail

class EmailSender(SimpleItem):
    security = ClassSecurityInfo()

    title = 'Send Emails'

    def __init__(self, id):
        """ """
        self.id = id

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self, 'meeting': self.aq_parent}, 'meeting_emails')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'send_newsletter')
    def send_email(self, from_email, subject, body_text, REQUEST, to_uids=None):
        """ """
        if to_uids is not None:
            assert isinstance(to_uids, list)
            to_emails = [getUserEmail(self.getSite(), uid) for uid in to_uids]

            email_tool = self.getEmailTool()
            email_tool.sendEmail(p_content=body_text,
                                    p_to=to_emails,
                                    p_from=from_email,
                                    p_subject=subject)

        REQUEST.RESPONSE.redirect(self.aq_parent.absolute_url())


NaayaPageTemplateFile('zpt/email_index', globals(), 'meeting_emails')

