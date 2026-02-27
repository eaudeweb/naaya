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

    meta_type = 'Semide Participant'
    product_name = 'SemideRegistration'
    icon = 'misc_/SemideRegistration/SemideParticipant.png'

    security = ClassSecurityInfo()

    def __init__(self, registration_no, delegation_of, participant_type,
                first_name, last_name, position, work_address, city, postal_code,
                country, phone_number, mobile_number, email, fax_number, passport_no,
                languages, hotel, arrival_date, departure_date,
                arrival_flight_number, arrival_flight_company, arrival_time,
                departure_flight_number, departure_flight_company, departure_time,
                special_requests, medical_requirements, special_diet, gender='',
                extra_event_1=None, extra_event_2=None):
        """ constructor """
        self.id = registration_no
        self.delegation_of = delegation_of
        self.participant_type = participant_type
        self.first_name = first_name
        self.last_name = last_name
        self.gender = gender
        self.position = position
        self.work_address = work_address
        self.city = city
        self.postal_code = postal_code
        self.country = country
        self.phone_number = phone_number
        self.mobile_number = mobile_number
        self.email = email
        self.fax_number = fax_number
        self.passport_no = passport_no
        self.languages = languages
        self.hotel = hotel
        self.arrival_date = str2date(arrival_date)
        self.departure_date = str2date(departure_date)
        self.arrival_flight_number = arrival_flight_number
        self.arrival_flight_company = arrival_flight_company
        self.arrival_time = arrival_time
        self.departure_flight_number = departure_flight_number
        self.departure_flight_company = departure_flight_company
        self.departure_time = departure_time
        self.special_requests = special_requests
        self.medical_requirements = medical_requirements
        self.special_diet = special_diet
        self.extra_event_1 = extra_event_1
        self.extra_event_2 = extra_event_2
        self.registration_date = time.localtime()

    security.declareProtected(constants.VIEW_PERMISSION, 'edit')
    def edit(self, delegation_of, participant_type, first_name, last_name,
            position, work_address, city, postal_code, country,
            phone_number, mobile_number, email, fax_number, passport_no,
            languages, hotel, arrival_date, departure_date,
            arrival_flight_number, arrival_flight_company, arrival_time,
            departure_flight_number, departure_flight_company, departure_time,
            special_requests, medical_requirements, special_diet, gender='',
            extra_event_1=None, extra_event_2=None):
        """ edit properties """
        self.delegation_of = delegation_of
        self.participant_type = participant_type
        self.first_name = first_name
        self.last_name = last_name
        self.gender = gender
        self.position = position
        self.work_address = work_address
        self.city = city
        self.postal_code = postal_code
        self.country = country
        self.phone_number = phone_number
        self.mobile_number = mobile_number
        self.email = email
        self.fax_number = fax_number
        self.passport_no = passport_no
        self.languages = languages
        self.hotel = hotel
        self.arrival_date = str2date(arrival_date)
        self.departure_date = str2date(departure_date)
        self.arrival_flight_number = arrival_flight_number
        self.arrival_flight_company = arrival_flight_company
        self.arrival_time = arrival_time
        self.departure_flight_number = departure_flight_number
        self.departure_flight_company = departure_flight_company
        self.departure_time = departure_time
        self.special_requests = special_requests
        self.medical_requirements = medical_requirements
        self.special_diet = special_diet
        self.extra_event_1 = extra_event_1
        self.extra_event_2 = extra_event_2

    def getCountry(self, lang, prop_name='country'):
        """ get country name """
        language, query, results = self.glossary_coverage.searchGlossary(query=getattr(self, prop_name), size=1)
        if results:
            return results[0].get_translation_by_language(lang)
        return ''

    security.declareProtected(constants.VIEW_PERMISSION, 'isEntitled')
    def isEntitled(self, REQUEST):
        """ check if current user has the right to modify this object """
        return ((REQUEST.SESSION.get('authentication_id','') == str(self.id)) and \
            (REQUEST.SESSION.get('authentication_name','') == self.unicode2UTF8(self.last_name))) or \
            self.canManageParticipants()

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
            session.set('authentication_id', REQUEST.get('registration_no'))
            session.set('authentication_name', self.unicode2UTF8(REQUEST.get('last_name')))
        if REQUEST.form.has_key('resend_mail'):
            #If the email corresponds with the one used at the registration, the confirmation mail will be resent
            if self.email == REQUEST.form.get('email', ''):
                values = {'registration_edit_link': self.absolute_url(),
                            'conference_title': self.unicode2UTF8(self.aq_parent.title),
                            'conference_details': self.unicode2UTF8(self.conference_details),
                            'website_team': self.unicode2UTF8(self.site_title),
                            'registration_number': self.id,
                            'last_name': self.unicode2UTF8(self.last_name)}
                self.send_registration_notification(self.email,
                    'Event registration',
                    self.getEmailTemplate('user_registration_html', lang) % values,
                    self.getEmailTemplate('user_registration_text', lang) % values)
                REQUEST.set('email_sent', True)
            else:
                REQUEST.set('wrong_email', True)
        return self._index_html(REQUEST)

    _edit_html = PageTemplateFile('zpt/participant/edit', globals())

    security.declareProtected(constants.VIEW_PERMISSION, 'edit_html')
    def edit_html(self, REQUEST=None):
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
                session.set('authentication_name', self.unicode2UTF8(REQUEST.get('last_name')))
        if REQUEST.form.has_key('resend_mail'):
            #If the email corresponds with the one used at the registration, the confirmation mail will be resent
            if self.email == REQUEST.form.get('email', ''):
                values = {'registration_edit_link': self.absolute_url(),
                            'conference_title': self.unicode2UTF8(self.aq_parent.title),
                            'conference_details': self.unicode2UTF8(self.conference_details),
                            'website_team': self.unicode2UTF8(self.site_title),
                            'registration_number': self.id,
                            'last_name': self.unicode2UTF8(self.last_name)}
                self.send_registration_notification(self.email,
                    'Event registration',
                    self.getEmailTemplate('user_registration_html', lang) % values,
                    self.getEmailTemplate('user_registration_text', lang) % values)
                REQUEST.set('email_sent', True)
            else:
                REQUEST.set('wrong_email', True)
        if submit:
            if form_validation(mandatory_fields=constants.PART_MANDATORY_FIELDS, 
                                date_fields=constants.DATE_FIELDS,
                                time_fields=constants.TIME_FIELDS,
                                REQUEST=REQUEST):
                cleaned_data = REQUEST.form
                del cleaned_data['submit']
                self.edit(**cleaned_data)

                #send notifications
                values = {'registration_edit_link': self.absolute_url(),
                            'conference_title': self.unicode2UTF8(self.title),
                            'conference_details': self.unicode2UTF8(self.conference_details),
                            'website_team': self.unicode2UTF8(self.site_title),
                            'registration_number': self.id}
                self.send_registration_notification(self.administrative_email,
                    'Event registration',
                    self.getEmailTemplate('admin_registration_html', 'en') % values,
                    self.getEmailTemplate('admin_registration_text', 'en') % values)

                return REQUEST.RESPONSE.redirect(self.absolute_url())
        return self._edit_html(REQUEST)

InitializeClass(BaseParticipant)