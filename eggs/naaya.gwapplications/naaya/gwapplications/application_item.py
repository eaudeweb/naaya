from datetime import datetime

from zope.interface import Interface, implements
from zope.event import notify
from OFS.SimpleItem import SimpleItem
from Products.Five.browser import BrowserView

from Products.NaayaCore.managers.utils import genObjectId
from naaya.groupware.groupware_site import manage_addGroupwareSite
from Products.NaayaCore.EmailTool.EmailPageTemplate import EmailPageTemplateFile
from naaya.core.zope2util import get_zope_env


NETWORK_NAME = get_zope_env('NETWORK_NAME', 'Eionet')
approved_mail = EmailPageTemplateFile('emailpt/approved_application.zpt', globals())
rejected_mail = EmailPageTemplateFile('emailpt/rejected_application.zpt', globals())

def make_unicode(s):
    if isinstance(s, unicode):
        return s
    try:
        return s.decode('utf-8')
    except:
        return s.decode('latin-1')

class IGWApplication(Interface):
    """Interface for the GWApplication class
    """

    def approve(self):
        """Approve the application.
            - mark application as accepted
            - create portal
            - customize portal according to application_data
            - send notification mail
        """

    def reject(self):
        """Reject the application.
            - mark application as rejected
            - send notification mail
        """

class GWApplication(SimpleItem):

    implements(IGWApplication)

    approved_on = []
    rejected_on = None
    created_path = ""

    def __init__(self, id, title, userid, **kwargs):
        self.id = id
        self.title = title
        self.userid = userid
        self.application_data = kwargs
        self.approved = False
        self.rejected = False
        self.created_path = ""
        self.date_created = datetime.utcnow()
        self.approved_on = []
        self.rejected_on = None

    def approve(self, **kwargs):
        self.approved = True
        self.rejected = False
        self.approved_on.append(datetime.utcnow())
        portal = self.create_portal(**kwargs)
        self.customize_portal(portal, **kwargs)
        self.created_path = portal.absolute_url(1)
        self.send_approved_email(kwargs['admin_comments'])
        notify(ApplicationApproved(self))

    def reject(self, **kwargs):
        self.rejected = True
        self.approved = False
        self.rejected_on = datetime.utcnow()
        self.send_rejected_email(kwargs['admin_comments'])

    def created_url(self):
        portal = self.unrestrictedTraverse(self.created_path, None)
        if portal:
            return portal.absolute_url()

    def create_portal(self, **kwargs):
        gw_root = self.get_gw_root(ob=True)
        pid = kwargs.get('id', '')
        ptitle = kwargs.get('title', '')
        return manage_addGroupwareSite(gw_root, pid, ptitle)

    def customize_portal(self, portal, **kwargs):
        portal.admin_metadata(kwargs.get('title', ''),
                              kwargs.get('subtitle', ''),
                              kwargs.get('description', ''))

        portal.administrator_email = self.application_data.get('useremail', '')
        portal.mail_address_from = 'no-reply@eionet.europa.eu'

        acl_path = self.acl_users.absolute_url(1)
        ac_tool = portal.getAuthenticationTool()
        ac_tool.manageAddSource(acl_path, NETWORK_NAME)
        ac_tool.getSources()[0].addUserRoles(name=self.userid, roles=['Administrator'], user_location='Users')

    def send_approved_email(self, admin_comments):
        data = {'igurl': self.created_url(), 'admin_comments': admin_comments}
        mail_data = approved_mail.render_email(**data)
        mail_to = self.application_data.get('useremail', '')
        mail_from = self.mail_from
        mail_subject = mail_data['subject']
        mail_body = mail_data['body_text']
        self.email_sender.sendEmail(mail_body, mail_to, mail_from, mail_subject)

    def send_rejected_email(self, admin_comments):
        data = {'igtitle': self.title, 'admin_comments': admin_comments}
        mail_data = rejected_mail.render_email(**data)
        mail_to = self.application_data.get('useremail', '')
        mail_from = self.mail_from
        mail_subject = mail_data['subject']
        mail_body = mail_data['body_text']
        self.email_sender.sendEmail(mail_body, mail_to, mail_from, mail_subject)

    def gen_id(self):
        return genObjectId(self.application_data.get('site_title', ''))

    def get_pretty_date(self, date):
        return date.strftime("%d %b %Y")

    def get_latest_approval_date(self):
        try:
            return self.approved_on[-1]
        except IndexError:
            return

    def get_application_data(self):
        for key, value in self.application_data.items():
            self.application_data[key] = make_unicode(value)
        return self.application_data

    @property
    def pretty_date(self):
        return self.get_pretty_date(self.date_created)

    @property
    def pretty_approved_date(self):
        try:
            return self.get_pretty_date(self.get_latest_approval_date())
        except:
            return

    @property
    def pretty_rejected_date(self):
        return self.get_pretty_date(self.rejected_on)

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
            self.context.reject(**kwargs)

        return self.request.response.redirect('../basket_html')


class IApplicationApproved(Interface):
    """ Event - application has been approved """


class ApplicationApproved(object):
    implements(IApplicationApproved)

    def __init__(self, application):
        self.application = application
