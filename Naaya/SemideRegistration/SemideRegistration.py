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

import re
from DateTime import DateTime
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.Folder import Folder

from Products.NaayaCore.managers import utils as naaya_utils

from Products.Localizer.LocalPropertyManager import LocalPropertyManager, LocalProperty
from SemideParticipant import SemideParticipant
from SemidePress import SemidePress
from utilities.Slugify import slugify
from utilities.SendMail import send_mail
from utilities.validators import form_validation, registration_validation
from utilities.countries import countries
from utilities import tmpfile, checkPermission
import constants


add_registration = PageTemplateFile('zpt/registration/add', globals())
def manage_add_registration(self, id='', title='', conference_details='', administrative_email ='', start_date='', end_date='', introduction='', lang='', REQUEST=None):
    """ Adds a Semide registration instance"""
    if registration_validation(REQUEST):
        if not id:
            id = slugify(title)
        if lang is None: 
            lang = self.gl_get_selected_language()
        ob = SemideRegistration(id, title, conference_details, administrative_email, start_date, end_date, introduction, lang)
        self.gl_add_languages(ob)
        self._setObject(id, ob)
        ob = self._getOb(id)
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.absolute_url())
    else:
        return add_registration.__of__(self)(REQUEST)


class SemideRegistration(LocalPropertyManager, Folder):
    """ Main class of the meeting registration"""

    meta_type = 'Semide Registration'
    product_name = 'SemideRegistration'

    security = ClassSecurityInfo()

    title = LocalProperty('title')
    conference_details = LocalProperty('conference_details')
    introduction = LocalProperty('introduction')

    manage_options = Folder.manage_options

    def __init__(self, id, title, conference_details, administrative_email, start_date, end_date, introduction, lang):
        """ constructor """
        self.id = id
        self.save_properties(title, conference_details, administrative_email, start_date, end_date, introduction, lang)

    security.declareProtected(constants.MANAGE_PERMISSION, 'save_properties')
    def save_properties(self, title, conference_details, administrative_email, start_date, end_date, introduction, lang):
        """ save properties """
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('conference_details', lang, conference_details)
        self._setLocalPropValue('introduction', lang, introduction)
        self.administrative_email = administrative_email
        self.start_date = DateTime(start_date)
        self.end_date = DateTime(end_date)

    _registration_html = PageTemplateFile('zpt/registration/registration', globals())
    def registration_html(self, REQUEST):
        """ registration form """
        submit =  REQUEST.form.get('submit', '')
        if submit:
            form_valid = form_validation(constants.PART_MANDATORY_FIELDS,
                                            constants.DATE_FIELDS,
                                            constants.TIME_FIELDS,
                                            REQUEST)
            if form_valid:
                registration_no = naaya_utils.genRandomId(10)
                cleaned_data = REQUEST.form
                del cleaned_data['submit']
                ob = SemideParticipant(registration_no, **cleaned_data)
                self._setObject(registration_no, ob)
                participant = self._getOb(registration_no, None)
                if participant:
                    lang = self.gl_get_selected_language()
                    REQUEST.SESSION.set('authentication_id', registration_no)
                    REQUEST.SESSION.set('authentication_name', participant.last_name)
                    values = {'registration_edit_link': participant.absolute_url(),
                                'registration_event': self.title,
                                'website_team': self.site_title,
                                'registration_number': registration_no,
                                'last_name': participant.last_name}
                    self.send_registration_notification(participant.email,
                        'Event registration',
                        constants.REGISTRATION_ADD_EDIT_TEMPLATE % values,
                        constants.REGISTRATION_ADD_EDIT_TEMPLATE_TEXT % values)
                    self.send_registration_notification(self.administrative_email,
                        'Event registration',
                        constants.NEW_REGISTRATION_ADD_EDIT_TEMPLATE % values,
                        constants.NEW_REGISTRATION_ADD_EDIT_TEMPLATE_TEXT % values)
                    return REQUEST.RESPONSE.redirect(participant.absolute_url())
        return self._registration_html(REQUEST)

    _registration_press_html = PageTemplateFile('zpt/registration/registration_press', globals())
    def registration_press_html(self, REQUEST):
        """ registration form """
        submit =  REQUEST.form.get('submit', '')
        if submit:
            form_valid = form_validation(constants.PRESS_MANDATORY_FIELDS,
                                            constants.DATE_FIELDS,
                                            constants.TIME_FIELDS,
                                            REQUEST)
            if form_valid:
                registration_no = naaya_utils.genRandomId(10)
                cleaned_data = REQUEST.form
                del cleaned_data['submit']
                ob = SemidePress(registration_no, **cleaned_data)
                self._setObject(registration_no, ob)
                press = self._getOb(registration_no, None)
                if press:
                    return REQUEST.RESPONSE.redirect(press.absolute_url())
        return self._registration_press_html(REQUEST)

    security.declareProtected(constants.VIEW_PERMISSION, 'index_html')
    index_html = PageTemplateFile('zpt/registration/index', globals())

    security.declareProtected(constants.MANAGE_PERMISSION, '_edit_html')
    _edit_html = PageTemplateFile('zpt/registration/edit', globals())

    def registrationIsOpen(self):
        """ check if the registration is opend to the public """
        now = DateTime(DateTime().strftime('%d/%m/%Y'))
        if now >= self.start_date and now <= self.end_date:
            return True
        return False

    security.declareProtected(constants.MANAGE_PERMISSION, 'edit_html')
    def edit_html(self, REQUEST):
        """ edit properties """
        submit =  REQUEST.form.get('edit-submit', '')
        if submit:
            cleaned_data = REQUEST.form
            del cleaned_data['edit-submit']
            self.save_properties(**cleaned_data)
        return self._edit_html(REQUEST)

    security.declarePrivate('send_registration_notification')
    def send_registration_notification(self, email, title, email_html, email_txt):
        """ send a notification when a folder is added / edited / commented"""
        send_mail(msg_from=constants.NO_REPLY_MAIL,
                    msg_to=email,
                    msg_subject='%s - Registration added / edited' % title,
                    msg_body=email_html,
                    msg_body_text=email_txt,
                    smtp_host = constants.SMTP_HOST,
                    smtp_port = constants.SMTP_PORT
                    )

    security.declareProtected(constants.MANAGE_PERMISSION, 'exportParticipants')
    def exportParticipants(self, REQUEST=None, RESPONSE=None):
        """ exports the participants list in CSV format """
        data = [('Registration date', 'First name', 'Name', 'Country', 'Organisation', 'Arriving date', 'Registration number')]
        data_app = data.append
        for part in self.getParticipants(skey='registration_date', rkey=1, is_journalist=False):
            if part.arrival_date:
                arrival_date = self.formatDate(part.arrival_date)
            else:
                arrival_date = 'n/a'
            data_app((self.formatDate(part.registration_date), part.first_name, part.last_name, part.country, part.organisation, arrival_date, part.id))
        return self.create_csv(data, filename='participants.csv', RESPONSE=REQUEST.RESPONSE)

    security.declareProtected(constants.MANAGE_PERMISSION, 'exportPress')
    def exportPress(self, REQUEST=None, RESPONSE=None):
        """ exports the press participants list in CSV format """
        data = [('Registration date', 'First name', 'Name', 'Country', 'Media name', 'Arriving date', 'Registration number')]
        data_app = data.append
        for part in self.getParticipants(skey='registration_date', rkey=1, is_journalist=True):
            if part.arrival_date:
                arrival_date = self.formatDate(part.arrival_date)
            else:
                arrival_date = 'n/a'
            data_app((self.formatDate(part.registration_date), part.first_name, part.last_name, part.country, part.media_name, arrival_date, part.id))
        return self.create_csv(data, filename='press.csv', RESPONSE=REQUEST.RESPONSE)

    security.declarePrivate('create_csv')
    def create_csv(self, data, filename, RESPONSE):
        tmp_name = tmpfile(data)
        content = open(str(tmp_name)).read()
        RESPONSE.setHeader('Content-Type', 'text/csv')
        RESPONSE.setHeader('Content-Disposition', 'attachment; filename=participants.csv')
        return content

    security.declareProtected(constants.MANAGE_PERMISSION, 'participants')
    participants = PageTemplateFile('zpt/registration/participants', globals())

    security.declareProtected(constants.MANAGE_PERMISSION, 'participants_press')
    participants_press = PageTemplateFile('zpt/registration/participants_press', globals())

    security.declareProtected(constants.MANAGE_PERMISSION, 'getParticipants')
    def getParticipants(self, skey, rkey, is_journalist):
        """ Returns the list of participants """
        if is_journalist:
            meta_type = 'Semide Press Participant'
        else:
            meta_type = 'Semide Participant'
        participants = [ (getattr(p, skey), p) for p in self.objectValues(meta_type) ]
        participants.sort()
        if rkey:
            participants.reverse()
        return [p for (key, p) in participants]

    security.declarePublic('canManageParticipants')
    def canManageParticipants(self):
        """ Check the permissions to edit/delete participants """
        return checkPermission(constants.MANAGE_PERMISSION, self)

    security.declarePublic('getRegistrationTitle')
    def getRegistrationTitle(self):
        """ """
        return self.title

    security.declarePublic('getConferenceDetails')
    def getConferenceDetails(self):
        """ """
        return self.conference_details

    #internal
    def formatDate(self, sdate):
        return sdate.strftime('%d %b %Y')

    def getPropertyValue(self, id, lang=None):
        """ Returns a property value in the specified language. """
        if lang is None: lang = self.gl_get_selected_language()
        return self.getLocalProperty(id, lang)

    security.declareProtected(constants.VIEW_PERMISSION, 'getCountryList')
    def getCountryList(self):
        return countries

    def hasVersion(self):
        """ """
        return None

InitializeClass(SemideRegistration)