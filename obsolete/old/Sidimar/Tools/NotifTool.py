from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo



class NotifTool:
    """ """

    security = ClassSecurityInfo()

    def sendConfirmationEmail(self, destination, username, password, roles):
        """ sends a confirmation email that contain account credentials """
        email_template = self.getEmailTool()._getOb('email_confirmation')
        sbj = email_template.title
        cnt = email_template.body
        roles = self.utConvertToList(roles)
        cnt = cnt.replace('@@USERNAME@@', username)
        cnt = cnt.replace('@@PASSWORD@@', password)
        cnt = cnt.replace('@@ROLES@@', ','.join(roles))
        cnt = cnt.replace('@@PORTAL_URL@@', self.portal_url)
        cnt = cnt.replace('@@PORTAL_TITLE@@', self.site_title)
        cnt = cnt.replace('@@TIMEOFPOST@@', str(self.utGetTodayDate()))
        self.getEmailTool().sendEmail(cnt, destination, self.mail_address_from, sbj)

    def sendDeactivateEmail(self, destination, firstname, lastname, username):
        """ sends an email to deactivated user """
        email_template = self.getEmailTool()._getOb('email_deactivate')
        sbj = email_template.title
        cnt = email_template.body
        cnt = cnt.replace('@@FIRSTNAME@@', firstname)
        cnt = cnt.replace('@@LASTNAME@@', lastname)
        cnt = cnt.replace('@@USERNAME@@', username)
        cnt = cnt.replace('@@PORTAL_URL@@', self.portal_url)
        cnt = cnt.replace('@@PORTAL_TITLE@@', self.site_title)
        cnt = cnt.replace('@@TIMEOFPOST@@', str(self.utGetTodayDate()))
        self.getEmailTool().sendEmail(cnt, destination, self.mail_address_from, sbj)

    def sendPassword(self, destination, username, password, firstname, lastname):
        """ sends a confirmation email that contain account credentials """
        email_template = self.getEmailTool()._getOb('email_forgotpwd')
        sbj = email_template.title
        cnt = email_template.body
        cnt = cnt.replace('@@FIRSTNAME@@', firstname)
        cnt = cnt.replace('@@LASTNAME@@', lastname)
        cnt = cnt.replace('@@USERNAME@@', username)
        cnt = cnt.replace('@@PASSWORD@@', password)
        cnt = cnt.replace('@@PORTAL_URL@@', self.portal_url)
        cnt = cnt.replace('@@PORTAL_TITLE@@', self.site_title)
        cnt = cnt.replace('@@TIMEOFPOST@@', str(self.utGetTodayDate()))
        self.getEmailTool().sendEmail(cnt, destination, self.mail_address_from, sbj)

    def sendRegistrationEmail(self, destination, id, firstname, lastname, country, street, street_number, zip, 
        city, region, mail, job, organisation, phone):
        """ sends a request role email """
        email_template = self.getEmailTool()._getOb('email_registration')
        sbj = email_template.title
        cnt = email_template.body
        cnt = cnt.replace('@@FIRSTNAME@@', firstname)
        cnt = cnt.replace('@@LASTNAME@@', lastname)
        cnt = cnt.replace('@@COUNTRY@@', country)
        cnt = cnt.replace('@@STREET@@', street)
        cnt = cnt.replace('@@STREETNUMBER@@', street_number)
        cnt = cnt.replace('@@ZIP@@', zip)
        cnt = cnt.replace('@@CITY@@', city)
        cnt = cnt.replace('@@REGION@@', region)
        cnt = cnt.replace('@@JOB@@', job)
        cnt = cnt.replace('@@ORGANISATION@@', organisation)
        cnt = cnt.replace('@@PHONE@@', phone)
        cnt = cnt.replace('@@MAIL@@', mail)
        cnt = cnt.replace('@@PORTAL_URL@@', self.portal_url)
        cnt = cnt.replace('@@PORTAL_TITLE@@', self.site_title)
        cnt = cnt.replace('@@TIMEOFPOST@@', str(self.utGetTodayDate()))
        link = "%s/admin_pending_html" % self.portal_url
        cnt = cnt.replace('@@ACTIVATIONLINK@@', link)
        self.getEmailTool().sendEmail(cnt, destination, self.mail_address_from, sbj)

InitializeClass(NotifTool)