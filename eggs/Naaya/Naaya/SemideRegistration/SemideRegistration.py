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
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.Folder import Folder

from Products.NaayaCore.managers import utils as naaya_utils
from SemideParticipant import SemideParticipant
from SemidePress import SemidePress
from utilities.Slugify import slugify
from utilities.SendMail import send_mail
from utilities.validators import form_validation, registration_validation
from utilities import tmpfile
import constants


add_registration = PageTemplateFile('zpt/registration/add', globals())
def manage_add_registration(self, id='', title='', administrative_email ='', start_date='', end_date='', introduction='', registration_event='', email_sender='', REQUEST=None):
    """ Adds a Semide registration instance"""
    if registration_validation(REQUEST):
        if not id:
            id = slugify(title)
        ob = SemideRegistration(id, title, administrative_email, start_date, end_date, introduction, registration_event, email_sender)
        self._setObject(id, ob)
        ob = self._getOb(id)
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.absolute_url())
    else:
        return add_registration.__of__(self)(REQUEST)


class SemideRegistration(Folder):
    """ Main class of the meeting registration"""

    meta_type = 'Semide Registration'
    product_name = 'SemideRegistration'

    security = ClassSecurityInfo()

    def __init__(self, id, title, administrative_email, start_date, end_date, introduction, registration_event, email_sender):
        """ constructor """
        self.id = id
        self.title = title
        self.administrative_email = administrative_email
        self.start_date = start_date
        self.end_date = end_date
        self.introduction = introduction
        self.registration_event = registration_event 
        self.email_sender = email_sender

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
                    self.send_registration_notification(self.administrative_email, participant.email, 'Event registration', participant.absolute_url())
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

    #security.declarePrivate('send_registration_notification')
    def send_registration_notification(self, sender_email, email, title, url):
        """ send a notification when a folder is added / edited / commented"""
        values = {'registration_edit_link': url,
                    'registration_event': self.registration_event,
                    'email_sender': self.email_sender}
        send_mail(msg_from=sender_email,
                    msg_to=email,
                    msg_subject='%s - Registration added / edited' % title,
                    msg_body=constants.REGISTRATION_ADD_EDIT_TEMPLATE % values,
                    msg_body_text=constants.REGISTRATION_ADD_EDIT_TEMPLATE_TEXT % values,
                    smtp_host = constants.SMTP_HOST,
                    smtp_port = constants.SMTP_PORT
                    )

    def formatDate(self, sdate):
        return sdate.strftime('%d %b %Y')

    #@todo: security
    def exportParticipants(self, REQUEST=None, RESPONSE=None):
        """ exports the participants list in CSV format """
        data = [('Registration date', 'First name', 'Name', 'Country', 'Organisation', 'Arriving date', 'Registration number')]
        data_app = data.append
        for part in self.getParticipants(skey='registration_date', rkey=1):
            data_app((part.registration_date, part.first_name, part.last_name, part.country, part.organisation, part.arrival_date, part.id))
        return self.create_csv(data, filename='participants.csv', RESPONSE=REQUEST.RESPONSE)

    #@todo: security
    def exportPress(self, REQUEST=None, RESPONSE=None):
        """ exports the press participants list in CSV format """
        data = [('Registration date', 'First name', 'Name', 'Country', 'Media name', 'Arriving date', 'Registration number')]
        data_app = data.append
        for part in self.getParticipants(skey='registration_date', rkey=1):
            data_app((part.registration_date, part.first_name, part.last_name, part.country, part.media_name, part.arrival_date, part.id))
        return self.create_csv(data, filename='press.csv', RESPONSE=REQUEST.RESPONSE)

    security.declarePrivate('create_csv')
    def create_csv(self, data, filename, RESPONSE):
        tmp_name = tmpfile(data)
        content = open(str(tmp_name)).read()
        RESPONSE.setHeader('Content-Type', 'text/csv')
        RESPONSE.setHeader('Content-Disposition', 'attachment; filename=participants.csv')
        return content

    #@todo: security
    participants = PageTemplateFile('zpt/registration/participants', globals())

    #@todo: security
    def getParticipants(self, skey, rkey):
        """ Returns the list of participants """
        participants = [ (getattr(p, skey), p) for p in self.objectValues('Semide Participant') if p.is_journalist is False ]
        participants.sort()
        if rkey:
            participants.reverse()
        return [p for (key, p) in participants]

InitializeClass(SemideRegistration)