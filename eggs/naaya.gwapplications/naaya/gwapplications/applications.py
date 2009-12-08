from zope.interface import Interface, implements
from OFS.Folder import Folder
from application_item import IGWApplication, GWApplication
from Products.Five.browser import BrowserView
from Products.NaayaCore.managers.utils import genObjectId, genRandomId
from Products.NaayaCore.EmailTool.EmailTool import EmailTool
from Products.NaayaCore.EmailTool.EmailPageTemplate import EmailPageTemplateFile


new_application_mail = EmailPageTemplateFile('emailpt/new_application.zpt', globals())


class IGWApplications(Interface):
    """Interface for the GWApplications class
    """


class GWApplications(Folder):

    implements(IGWApplications)
    email_sender = EmailTool('email_sender', 'Applications email sender')
    email_sender.mail_server_name = 'localhost'
    email_sender.mail_server_port = '25'

    _properties = (
        {'id':'mail_from', 'mode':'w', 'type': 'string'},
        {'id':'admin_mail', 'mode':'w', 'type': 'string'},
    )

    def __init__(self, appid, title, admin_mail, mail_from):
        self.id = appid
        self.title = title
        self.admin_mail = admin_mail
        self.mail_from = mail_from


    def get_user(self, uid):
        users = self.acl_users.findUser('uid', uid)
        for user in users:
            if user.get('uid') == uid:
                return user

    def get_user_name(self, uid):
        user = self.get_user(uid)
        if user:
            return user.get('cn', '')

    def get_user_email(self, uid):
        user = self.get_user(uid)
        if user:
            return user.get('mail', '')

    def send_new_application_mail(self, app):
        data = {
            'username': app.application_data.get('username', ''),
            'userid': app.userid,
            'appurl': app.absolute_url(),
            'basketurl': self.absolute_url() + '/basket_html',
            }
        mail_data = new_application_mail.render_email(**data)
        self.email_sender.sendEmail(mail_data['body_text'], self.admin_mail, self.mail_from, mail_data['subject'])


class GWApplicationsAddView(BrowserView):
    """Add view for GW applications.
    """

    def __call__(self, add_input_name='', title='', admin_mail='', mail_from='', submit_add=''):
        if not submit_add:
            return self.index()
        obj = GWApplications(add_input_name, title, admin_mail, mail_from)
        self.context.add(obj)
        self.request.response.redirect(self.context.nextURL())
        return ''

class GWApplicationsAddApplicationView(BrowserView):
    """Application submission view
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        if not kwargs.get('submit', ''):
            return self.index()
        title = kwargs.get('site_title', '')
        id = '%s-%s' % (genObjectId(title), genRandomId())
        userid = self.request.AUTHENTICATED_USER.getUserName()
        kwargs['username'] =  self.context.get_user_name(userid)
        kwargs['useremail'] =  self.context.get_user_email(userid)
        obj = GWApplication(id, title, userid, **kwargs)
        self.context._setObject(id, obj)
        self.context.send_new_application_mail(self.context._getOb(id))
        return self.index(**{'done': True})


class GWApplicationsBasketView(BrowserView):
    """Application basket view
    """

    def get_applications(self):
        for doc in self.context.objectValues():
            if not IGWApplication.providedBy(doc):
                continue
            yield doc

    def __call__(self):
        kwargs = {'objects': self.get_applications()}
        return self.index(**kwargs)
