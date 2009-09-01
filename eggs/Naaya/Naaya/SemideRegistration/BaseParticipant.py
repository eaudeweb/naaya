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

    def __init__(self, registration_no, first_name, last_name, email, country, passport_no, \
                passport_expire, phone_number, fax_number, arrival_date, arrival_from, \
                arrival_flight, arrival_time, departure_date, departure_flight, departure_time, is_journalist):
        """ constructor """
        self.id = registration_no
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.country = country
        self.passport_no = passport_no
        self.passport_expire = passport_expire
        self.phone_number = phone_number
        self.fax_number = fax_number
        if arrival_date:
            self.arrival_date = str2date(arrival_date)
        else:
            self.arrival_date = ''
        self.arrival_from = arrival_from
        self.arrival_flight = arrival_flight
        self.arrival_time = arrival_time
        if departure_date:
            self.departure_date = str2date(departure_date)
        else:
            self.departure_date = ''
        self.departure_flight = departure_flight
        self.departure_time = departure_time
        self.is_journalist = is_journalist
        self.registration_date = time.localtime()

    security.declareProtected(constants.VIEW_PERMISSION, 'edit')
    def edit(self, first_name, last_name, email, country, passport_no, passport_expire, phone_number, \
                    fax_number, arrival_date, arrival_from, arrival_flight, arrival_time, departure_date, \
                    departure_flight, departure_time):
        """ edit properties """
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.country = country
        self.passport_no = passport_no
        self.passport_expire = passport_expire
        self.phone_number = phone_number
        self.fax_number = fax_number
        if arrival_date:
            self.arrival_date = str2date(arrival_date)
        else:
            self.arrival_date = ''
        self.arrival_from = arrival_from
        self.arrival_flight = arrival_flight
        self.arrival_time = arrival_time
        if departure_date:
            self.departure_date = str2date(departure_date)
        else:
            self.departure_date = ''
        self.departure_flight = departure_flight
        self.departure_time = departure_time

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
        if REQUEST.form.has_key('authenticate'):
            #The registration number and last name are saved on the session as submitted by the user
            session.set('authentication_id', REQUEST.get('registration_no'))
            session.set('authentication_name', self.unicode2UTF8(REQUEST.get('last_name')))
        if REQUEST.form.has_key('resend_mail'):
            #If the email corresponds with the one used at the registration, the confirmation mail will be resent
            if self.email == REQUEST.form.get('email', ''):
                values = {'registration_edit_link': self.absolute_url(),
                            'registration_event': self.title,
                            'website_team': self.site_title,
                            'registration_number': self.id,
                            'last_name': self.last_name}
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
                self.send_registration_notification(self.email,
                    'Event registration',
                    constants.REGISTRATION_ADD_EDIT_TEMPLATE % values,
                    constants.REGISTRATION_ADD_EDIT_TEMPLATE_TEXT % values)
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
                            'registration_event': self.title,
                            'website_team': self.site_title,
                            'registration_number': self.id}
                self.send_registration_notification(self.administrative_email,
                    'Event registration',
                    constants.NEW_REGISTRATION_ADD_EDIT_TEMPLATE % values,
                    constants.NEW_REGISTRATION_ADD_EDIT_TEMPLATE_TEXT % values)

                return REQUEST.RESPONSE.redirect(self.absolute_url())
        return self._edit_html(REQUEST)

InitializeClass(BaseParticipant)