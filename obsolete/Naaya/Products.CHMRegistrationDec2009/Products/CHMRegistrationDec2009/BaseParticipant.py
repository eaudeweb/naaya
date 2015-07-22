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
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Eau de Web
# Valentin Dumitru, Eau de Web

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.SimpleItem import SimpleItem
import time

from utilities.validators import form_validation, str2date
import constants

class BaseParticipant(SimpleItem):
    """ Base class for participants """

    security = ClassSecurityInfo()

    def __init__(self, registration_id, organisation_name, organisation_address,\
                organisation_website, media_contact_name, email,\
                media_contact_telephone, media_contact_details, program_contact_name,\
                program_contact_email, program_contact_telephone, vip_contact_name,\
                vip_contact_email, vip_contact_telephone, activities, disclose_permission,\
                admin_comment=''):
        """ constructor """
        self.id = registration_id
        self.organisation_name = organisation_name
        self.organisation_address = organisation_address
        self.organisation_website = organisation_website
        self.media_contact_name = media_contact_name
        self.email = email
        self.media_contact_telephone = media_contact_telephone
        self.media_contact_details = media_contact_details
        self.program_contact_name = program_contact_name
        self.program_contact_email = program_contact_email
        self.program_contact_telephone = program_contact_telephone
        self.vip_contact_name = vip_contact_name
        self.vip_contact_email = vip_contact_email
        self.vip_contact_telephone = vip_contact_telephone
        self.disclose_permission = disclose_permission
        self.activities = activities
        self.admin_comment = admin_comment
        self.registration_date = time.localtime()

    security.declareProtected(constants.VIEW_PERMISSION, 'edit')
    def edit(self, organisation_name, organisation_address,\
            organisation_website, media_contact_name, email,\
            media_contact_telephone, media_contact_details, program_contact_name,\
            program_contact_email, program_contact_telephone, vip_contact_name,\
            vip_contact_email, vip_contact_telephone, activities, disclose_permission,\
            admin_comment):
        """ edit properties """
        self.organisation_name = organisation_name
        self.organisation_address = organisation_address
        self.organisation_website = organisation_website
        self.media_contact_name = media_contact_name
        self.email = email
        self.media_contact_telephone = media_contact_telephone
        self.media_contact_details = media_contact_details
        self.program_contact_name = program_contact_name
        self.program_contact_email = program_contact_email
        self.program_contact_telephone = program_contact_telephone
        self.vip_contact_name = vip_contact_name
        self.vip_contact_email = vip_contact_email
        self.vip_contact_telephone = vip_contact_telephone
        self.disclose_permission = disclose_permission
        self.activities = activities
        self.admin_comment = admin_comment

    def getCountry(self, lang):
        """ get country name """
        language, query, results = self.glossary_coverage.searchGlossary(query=self.country, size=1)
        if results:
            return results[0].get_translation_by_language(lang)
        return ''

    security.declareProtected(constants.VIEW_PERMISSION, 'isEntitled')
    def isEntitled(self, REQUEST):
        """ check if current user has the right to modify this object """
        return ((REQUEST.SESSION.get('authentication_id','') == str(self.id)) and \
            (REQUEST.SESSION.get('authentication_name','') == self.unicode2UTF8(self.organisation_name))) or \
            self.canManageParticipants() or self.canViewParticipants()

    security.declareProtected(constants.VIEW_PERMISSION, 'index_html')
    _index_html = PageTemplateFile('zpt/participant/index', globals())
    #@todo: security
    def index_html(self, REQUEST=None):
        """ edit base participant properties """
        session = REQUEST.SESSION
        submit =  REQUEST.form.get('submit', '')
        lang = self.gl_get_selected_language()
        if REQUEST.form.has_key('authenticate'):
            #The registration number and last name are saved on the session as submitted by the user
            session.set('authentication_id', REQUEST.get('registration_id'))
            session.set('authentication_name', self.unicode2UTF8(REQUEST.get('authentication_name')))
        if REQUEST.form.has_key('resend_mail'):
            #If the email corresponds with the one used at the registration, the confirmation mail will be resent
            email_recipients = [getattr(self, field) for field in constants.PART_EMAIL_RECIPIENTS]
            user_email = REQUEST.form.get('email', '')
            if user_email in email_recipients:
                conference_period = self.aq_parent.getPropertyValue('conference_period', lang)
                conference_place = self.aq_parent.getPropertyValue('conference_place', lang)
                values = {'registration_edit_link': self.absolute_url(),
                            'registration_event': self.aq_parent.title,
                            'conference_period': conference_period,
                            'conference_place': conference_place,
                            'website_team': self.site_title,
                            'registration_id': self.id,
                            'name': self.organisation_name}
                self.send_registration_notification(user_email,
                    'Event registration',
                    self.getEmailTemplate('user_registration_html', lang) % values,
                    self.getEmailTemplate('user_registration_text', lang) % values)
                REQUEST.set('email_sent', True)
            else:
                REQUEST.set('wrong_email', True)
        return self._index_html(REQUEST)

    _edit_html = PageTemplateFile('zpt/participant/edit', globals())

    security.declareProtected(constants.VIEW_PERMISSION, 'edit_html')
    def edit_html(self, mandatory_fields, REQUEST=None):
        """ edit base participant properties """
        session = REQUEST.SESSION
        submit =  REQUEST.form.get('submit', '')
        lang = self.gl_get_selected_language()
        if REQUEST.form.has_key('authenticate'):
            #The registration number and last name are saved on the session as submitted by the user
            if form_validation(mandatory_fields=constants.AUTH_MANDATORY_FIELDS, 
                                date_fields=constants.DATE_FIELDS,
                                time_fields=constants.TIME_FIELDS,
                                REQUEST=REQUEST):
                session.set('authentication_id', REQUEST.get('registration_id'))
                session.set('authentication_name', self.unicode2UTF8(REQUEST.get('authentication_name')))
        if REQUEST.form.has_key('resend_mail'):
            #If the email corresponds with the one used at the registration, the confirmation mail will be resent
            email_recipients = [getattr(self, field) for field in constants.PART_EMAIL_RECIPIENTS]
            user_email = REQUEST.form.get('email', '')
            if user_email in email_recipients:
                conference_period = self.aq_parent.getPropertyValue('conference_period', lang)
                conference_place = self.aq_parent.getPropertyValue('conference_place', lang)
                values = {'registration_edit_link': self.absolute_url(),
                            'registration_event': self.aq_parent.title,
                            'conference_period': conference_period,
                            'conference_place': conference_place,
                            'website_team': self.site_title,
                            'registration_id': self.id,
                            'name': self.organisation_name}
                self.send_registration_notification(user_email,
                    'Event registration',
                    self.getEmailTemplate('user_registration_html', lang) % values,
                    self.getEmailTemplate('user_registration_text', lang) % values)
                REQUEST.set('email_sent', True)
            else:
                REQUEST.set('wrong_email', True)
        if submit:
            if form_validation(mandatory_fields=mandatory_fields, 
                                date_fields=constants.DATE_FIELDS,
                                time_fields=constants.TIME_FIELDS,
                                REQUEST=REQUEST):
                cleaned_data = REQUEST.form
                del cleaned_data['submit']
                self.edit(**cleaned_data)

                #send notifications
                values = {'registration_edit_link': self.absolute_url(),
                            'registration_event': self.aq_parent.title,
                            'website_team': self.site_title,
                            'registration_id': self.id}
                self.send_registration_notification(self.administrative_email,
                    'Event registration',
                    self.getEmailTemplate('admin_registration_html', 'en') % values,
                    self.getEmailTemplate('admin_registration_text', 'en') % values)

                return REQUEST.RESPONSE.redirect(self.absolute_url())
        return self._edit_html(REQUEST)

InitializeClass(BaseParticipant)