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
#
#
#
#$Id: EWApplication.py 2705 2004-11-26 14:30:23Z finrocvs $

#Python imports

#Zope imports
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view

#Product imports
from constants import *
from Products.NaayaBase.constants import *


def manage_addEWApplication_html(self):
    """ """
    raise 'Cannot add an application form this way! Use website wizzard.'

class EWApplication(SimpleItem):
    """ EWApplication class """

    meta_type = METATYPE_EWAPPLICATION
    icon = 'misc_/EnviroWindowsApplications/application.gif'
    icon_accepted = 'misc_/EnviroWindowsApplications/icon_accepted.gif'
    icon_rejected = 'misc_/EnviroWindowsApplications/icon_rejected.gif'
    icon_pending = 'misc_/EnviroWindowsApplications/icon_pending.gif'

    manage_options = (
        (
            {'label' : 'Application view', 'action' : 'manage_view_html'},
        )
        +
        SimpleItem.manage_options
    )

    security = ClassSecurityInfo()

    def __init__(self, id, title, site_logo, application_data, ewsite_id, request_date):
        """ """
        self.id = id
        self.title = title
        self.application_data = application_data
        self.request_date = request_date
        self.status = 0    # -1 rejected, 0 pending, 1 approved
        self.site_logo = site_logo
        self.ewsite_id = ewsite_id
        self.status_message = ''    # action that has been executed after approving this

    def __setstate__(self, state):
        """ """
        EWApplication.inheritedAttribute('__setstate__')(self, state)

    def setMyPicture(self, p_picture):
        """ """
        self.logo_icon = None
        if p_picture:
            if hasattr(p_picture, 'filename'):
                if p_picture.filename != '':
                    l_read = p_picture.read()
                    if l_read != '':
                        self.logo_icon = l_read
                        self._p_changed = 1
            else:
                self.logo_icon = p_picture
                if self.logo_icon is not None:
                    print 'is not none'
                self._p_changed = 1

    def getMyPicture(self):
        """ """
        return self.logo_icon

    def hasLogo(self):
        """ """
        return self.logo_icon is not None

    def get_selected_logo(self, REQUEST=None):
        """ """
        try:
            REQUEST.RESPONSE.setHeader('Content-Type', 'image/jpeg')
            REQUEST.RESPONSE.setHeader('Content-Disposition', 'inline; filename="logo.jpg"')
            return self.site_logo
        except: return None

    # API
    def getStatusLabel(self):
        #returns the label for current status
        if self.status == -1: return APPLICATION_STATUS_REJECTED
        elif self.status == 0:
            self.status_message = APPLICATION_STATUS_MESSAGE_PENDING
            return APPLICATION_STATUS_PENDING
        elif self.status == 1: return APPLICATION_STATUS_APPROVED
        else: return '-'

    def getstatus(self):
        #  if approved and not yet finished, the font is red
        if (self.status == 1 and self.status_message !=  APPLICATION_STATUS_MESSAGE_FINISHED): return 1
        else: return 0

    def canApproveApplication(self):
        #returns 1 if the application can be approved and processed
        return self.status == 0 or (self.status == 1 and self.status_message != APPLICATION_STATUS_MESSAGE_FINISHED)

    def canRejectApplication(self):
        #returns 1 if the application can be rejected
        return self.status == 0 or (self.status == 1 and self.status_message != APPLICATION_STATUS_MESSAGE_FINISHED)

    # ACTIONS
    def approveApplication(self, REQUEST=None):
        """ """
        if self.canApproveApplication():
            self.status = 1
            self.status_message = APPLICATION_STATUS_MESSAGE_WORKING
            self._p_changed = 1
            #go to EWInstaller wizzard
            if REQUEST:
                ewinstaller = self.getEWInstaller()
                if ewinstaller:
                    ewinstaller.install_init(
                        site_title=self.application_data['site_title'],
                        subtitle=self.application_data['subtitle'],
                        description=self.application_data['description'],
                        publisher=self.application_data['publisher'],
                        contributor=self.application_data['contributor'],
                        languages=self.application_data['languages'],
                        creator=self.application_data['creator'],
                        rights=self.application_data['rights'],
                        administrator_email=self.application_data['administrator_email'],
                        administrator_name=self.application_data['administrator_name'],
                        portal_url=self.application_data['portal_url'],
                        contact_email=self.application_data['contact_email'],
                        products=ewinstaller.getProductsEmptyStruct(self.application_data['products']),
                        skin=self.application_data['skin'],
                        skin_style=self.application_data['skin_style'],
                        DestinationURL='%s/finishApplication' % self.absolute_url(),
                        status = self.status,
                        status_message_mail = APPLICATION_STATUS_MESSAGE_FINISHED,
                        ewindows_portal_url = self.getSite().absolute_url(1),
                        applications_url = self.getApplicationsContainer().absolute_url(1),
                        username=self.application_data['username'],
                        password=self.application_data['password'],
                        site_logo = self.application_data['site_logo'],
                        application_url=self.absolute_url(1)
                    )
                    REQUEST.RESPONSE.redirect('%s/install_welcome_html' % ewinstaller.absolute_url())
                else:
                    raise "No EWInstaller found in your Zope's Root Folder", None
        elif self.status == -1:
            raise "This application form was rejected once.", '%s (%s)' % (self.getStatusLabel(), self.status_message)
        else:
            raise "This application form was proccesed once.", '%s (%s)' % (self.getStatusLabel(), self.status_message)

    def rejectApplication(self, REQUEST=None):
        """ """
        if self.canRejectApplication():
            self.status = -1
            self.status_message = APPLICATION_STATUS_MESSAGE_REJECTED
            self._p_changed = 1
            # send emails to appliants: administrator and contact
            p_to = [self.application_data['administrator_email'], self.application_data['contact_email']]
            p_from = self.email_from
            p_subject = 'Your portal application on EnviroWindows has been rejected'
            p_content = """
You have applied for an EnviroWindows-compliant portal hosted on the EnviroWindows servers.
The application has been rejected by the EnviroWindows managers and no portal has been created.

Regards,
EnviroWindows Team

****************************************************
IMPORTANT NOTICE: This is an automatic service.
Please do not reply to this message.
****************************************************
            """
            self.getEmailTool().sendEmail(p_content, p_to, p_from, p_subject)

            if REQUEST: REQUEST.RESPONSE.redirect('%s/basket_html' % self.getApplicationsContainer().absolute_url())
        elif self.status == -1:
            raise "This application form was rejected once.", '%s (%s)' % (self.getStatusLabel(), self.status_message)
        else:
            raise "This application form was proccesed once.", '%s (%s)' % (self.getStatusLabel(), self.status_message)

    def finishApplication(self, action='finish', REQUEST=None):
        """ """
        if self.status == 1 and self.status_message == APPLICATION_STATUS_MESSAGE_WORKING:
            if action == 'finish':
                self.status_message = APPLICATION_STATUS_MESSAGE_FINISHED
            else:
                self.status_message = APPLICATION_STATUS_MESSAGE_ABORTED
            self._p_changed = 1
            if REQUEST: REQUEST.RESPONSE.redirect('%s/basket_html' % self.getApplicationsContainer().absolute_url())
        else:
            raise "This application form was processed and approved.", '%s (%s)' % (self.getStatusLabel(), self.status_message)

    # SITE FORMS
    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'index_html')
    index_html = PageTemplateFile('zpt/application_index', globals())

    # ZMI FORMS
    security.declareProtected(view_management_screens, 'manage_view_html')
    manage_view_html = PageTemplateFile('zpt/application_manage_view', globals())

InitializeClass(EWApplication)
