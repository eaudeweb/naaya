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

    def __init__(self, registration_no, first_last_name, position, organisation, address, zip_code,\
                email, phone_number, event_1, event_2, event_3, topic_1, topic_2, topic_3, topic_4, explanation, private_email=False):
        """ constructor """
        self.id = registration_no
        self.first_last_name = first_last_name
        self.position = position
        self.organisation = organisation
        self.address = address
        self.zip_code = zip_code
        self.email = email
        self.private_email = private_email
        self.phone_number = phone_number
        self.event_1 = event_1
        self.event_2 = event_2
        self.event_3 = event_3
        self.topic_1 = topic_1
        self.topic_2 = topic_2
        self.topic_3 = topic_3
        self.topic_4 = topic_4
        self.explanation = explanation
        self.registration_date = time.localtime()

    security.declareProtected(constants.VIEW_PERMISSION, 'edit')
    def edit(self, first_last_name, position, organisation, address, zip_code,\
                email, phone_number, event_1, event_2, event_3, topic_1, topic_2, topic_3, topic_4, explanation, private_email=False):
        """ edit properties """
        self.first_last_name = first_last_name
        self.position = position
        self.organisation = organisation
        self.address = address
        self.zip_code = zip_code
        self.email = email
        self.private_email = private_email
        self.phone_number = phone_number
        self.event_1 = event_1
        self.event_2 = event_2
        self.event_3 = event_3
        self.topic_1 = topic_1
        self.topic_2 = topic_2
        self.topic_3 = topic_3
        self.topic_4 = topic_4
        self.explanation = explanation

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
            (REQUEST.SESSION.get('authentication_name','') == self.unicode2UTF8(self.first_last_name))) or \
            self.canManageParticipants() or self.canViewParticipants()

    security.declareProtected(constants.VIEW_PERMISSION, 'index_html')
    _index_html = PageTemplateFile('zpt/participant/index', globals())
    #@todo: security
    def index_html(self, REQUEST=None):
        """ edit base participant properties """
        session = REQUEST.SESSION
        submit =  REQUEST.form.get('submit', '')
        if REQUEST.form.has_key('authenticate'):
            #The registration number and last name are saved on the session as submitted by the user
            session.set('authentication_id', REQUEST.get('registration_no'))
            session.set('authentication_name', self.unicode2UTF8(REQUEST.get('first_last_name')))
        if REQUEST.form.has_key('resend_mail'):
            #If the email corresponds with the one used at the registration, the confirmation mail will be resent
            if self.email == REQUEST.form.get('email', ''):
                values = {'registration_edit_link': self.absolute_url(),
                            'registration_event': self.title,
                            'website_team': self.site_title,
                            'registration_number': self.id,
                            'name': self.first_last_name}
                self.send_registration_notification(self.email,
                    'Event registration',
                    constants.REGISTRATION_ADD_EDIT_TEMPLATE % values,
                    constants.REGISTRATION_ADD_EDIT_TEMPLATE_TEXT % values)
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
                session.set('authentication_id', REQUEST.get('registration_no'))
                session.set('authentication_name', self.unicode2UTF8(REQUEST.get('first_last_name')))
        if REQUEST.form.has_key('resend_mail'):
            #If the email corresponds with the one used at the registration, the confirmation mail will be resent
            if self.email == REQUEST.form.get('email', ''):
                self.send_registration_notification(self.email,
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
                if not 'event_1' in cleaned_data: cleaned_data['event_1'] = '0'
                if not 'event_2' in cleaned_data: cleaned_data['event_2'] = '0'
                if not 'event_3' in cleaned_data: cleaned_data['event_3'] = '0'
                self.edit(**cleaned_data)

                #send notifications
                values = {'registration_edit_link': self.absolute_url(),
                            'registration_event': self.aq_parent.title,
                            'website_team': self.site_title,
                            'registration_number': self.id}
                self.send_registration_notification(self.administrative_email,
                    'Event registration',
                    self.getEmailTemplate('admin_registration_html', 'en') % values,
                    self.getEmailTemplate('admin_registration_text', 'en') % values)

                return REQUEST.RESPONSE.redirect(self.absolute_url())
        return self._edit_html(REQUEST)

InitializeClass(BaseParticipant)