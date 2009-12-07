from zope.interface import Interface, implements
from OFS.SimpleItem import SimpleItem
from Products.Five.browser import BrowserView
from Products.NaayaCore.managers.utils import genObjectId
from naaya.groupware.groupware_site import manage_addGroupwareSite
from Products.NaayaCore.EmailTool.EmailPageTemplate import EmailPageTemplateFile
from datetime import datetime


approved_mail = EmailPageTemplateFile('emailpt/approved_application.zpt', globals())
rejected_mail = EmailPageTemplateFile('emailpt/rejected_application.zpt', globals())

class IGWApplication(Interface):
    """
    """

    def approve(self):
        """
        """

    def reject(self):
        """
        """

class GWApplication(SimpleItem):

    implements(IGWApplication)

    def __init__(self, id, title, userid, **kwargs):
        self.id = id
        self.title = title
        self.userid = userid
        self.application_data = kwargs
        self.approved = False
        self.rejected = False
        self.created_url = ""
        #TODO: add date created
        self.date_created = datetime.now()

    def approve(self, **kwargs):
        self.approved = True
        self.rejected = False
        portal = self.create_portal(**kwargs)
        self.customize_portal(portal, **kwargs)
        self.created_url = portal.absolute_url()
        self.send_approved_email()

    def reject(self):
        self.rejected = True
        self.approved = False
        self.send_rejected_email()

    def create_portal(self, **kwargs):
        # TODO: properly get gw root
        gw_root = self.aq_parent.aq_parent.aq_parent.aq_parent
        pid = kwargs.get('id', '')
        ptitle = kwargs.get('title', '')
        return manage_addGroupwareSite(gw_root, pid, ptitle)

    def customize_portal(self, portal, **kwargs):
        portal.admin_metadata(kwargs.get('title', ''),
                              kwargs.get('subtitle', ''),
                              kwargs.get('description', ''))

        portal.admin_email(administrator_email=self.application_data.get('useremail', ''))

        acl_path = self.acl_users.absolute_url(1)
        ac_tool = portal.getAuthenticationTool()
        ac_tool.manageAddSource(acl_path, 'LDAP')
        ac_tool.getSources()[0].addUserRoles(name=self.userid, roles=['Administrator'], user_location='Users')

    def send_approved_email(self):
        data = {'igurl': self.created_url}
        mail_data = rejected_mail.render_email(**data)
        mail_to = self.application_data.get('useremail', '')
        mail_from = self.mail_from
        mail_subject = mail_data['subject']
        mail_body = mail_data['body_text']
        self.email_sender.sendEmail(mail_body, mail_to, mail_from, mail_subject)

    def send_rejected_email(self):
        mail_data = approved_mail.render_email()
        mail_to = self.application_data.get('useremail', '')
        mail_from = self.mail_from
        mail_subject = mail_data['subject']
        mail_body = mail_data['body_text']
        self.email_sender.sendEmail(mail_body, mail_to, mail_from, mail_subject)

    def gen_id(self):
        return genObjectId(self.application_data.get('site_title', ''))

    @property
    def pretty_date(self):
        return self.date_created.strftime('%d %b %Y')

class GWApplicationIndexView(BrowserView):
    """
    """

    def __call__(self, submitted='', **kwargs):
        if not submitted:
            return self.index()

        kwargs.update(self.request.form)

        if submitted == 'Approve':
            self.context.approve(**kwargs)

        elif submitted == 'Reject':
            self.context.reject()

        return self.request.response.redirect('../basket_html')

