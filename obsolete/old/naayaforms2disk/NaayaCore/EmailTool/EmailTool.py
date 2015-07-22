# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

#Python imports
import time
import smtplib
import MimeWriter
import cStringIO

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from Products.NaayaCore.constants import *
import EmailTemplate

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
        {'name': METATYPE_EMAILTEMPLATE, 'action': 'manage_addEmailTemplateForm'},
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
        #load default stuff
        pass

    #core
    def __create_email(self, p_content, p_to, p_from, p_subject):
        if isinstance(p_content, unicode): p_content = p_content.encode('utf-8')        
        if isinstance(p_subject, unicode): p_subject = p_subject.encode('utf-8')
        #creates a mime-message that will render as text
        l_out = cStringIO.StringIO()
        l_writer = MimeWriter.MimeWriter(l_out)
        # set up some basic headers
        l_writer.addheader("From", p_from)
        l_writer.addheader("To", p_to)
        l_writer.addheader("Date", time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()))
        l_writer.addheader("Subject", p_subject)
        l_writer.addheader("MIME-Version", "1.0")
        # start the multipart section of the message
        l_writer.startmultipartbody("alternative")
        l_writer.flushheaders()
        # the plain text section
        l_subpart = l_writer.nextpart()
        l_pout = l_subpart.startbody("text/plain", [("charset", 'utf-8')])
        l_pout.write(p_content)
        #close your writer and return the message body
        l_writer.lastpart()
        l_msg = l_out.getvalue()
        l_out.close()
        return l_msg

    def __build_addresses(self, p_emails):
        #given a list of emails returns a valid string for an email address
        if type(p_emails) == type(''):
            return p_emails
        elif type(p_emails) == type([]):
            return ', '.join(p_emails)

    #api
    security.declareProtected(view, 'sendEmail')
    def sendEmail(self, p_content, p_to, p_from, p_subject):
        #sends a generic email
        if not isinstance(p_to, list):
            p_to = [e.strip() for e in p_to.split(',') if e.strip()!='']
        try:
            if self.mail_server_name and self.mail_server_port and p_to:
                l_message = self.__create_email(p_content, self.__build_addresses(p_to), p_from, p_subject)
                server = smtplib.SMTP(self.mail_server_name, self.mail_server_port)
                server.sendmail(p_from, p_to, l_message)
                server.quit()
                return 1
            return 0
        except:
            return 0

    #zmi actions
    security.declareProtected(view_management_screens, 'manageSettings')
    def manageSettings(self, mail_server_name='', mail_server_port='', administrator_email='', mail_address_from='', notify_on_errors='', REQUEST=None):
        """ """
        site = self.getSite()
        try: mail_server_port = int(mail_server_port)
        except: mail_server_port = site.mail_server_port
        if notify_on_errors: notify_on_errors = 1
        else: notify_on_errors = 0
        site.mail_server_name = mail_server_name
        site.mail_server_port = mail_server_port
        site.mail_address_from = mail_address_from
        site.administrator_email = administrator_email
        site.notify_on_errors = notify_on_errors
        self._p_changed = 1
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_settings_html?save=ok')

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_settings_html')
    manage_settings_html = PageTemplateFile('zpt/email_settings', globals())

InitializeClass(EmailTool)
