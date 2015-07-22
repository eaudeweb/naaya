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
from os.path import join
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate import manage_addPageTemplate
from OFS.Folder import Folder
import time

from Products.NaayaCore.managers import utils as naaya_utils
from Products.NaayaBase.NyContainer import NyContainer
from naaya.i18n.LocalPropertyManager import LocalPropertyManager, LocalProperty
from CHMParticipant import CHMParticipant
from utilities.Slugify import slugify
from utilities.SendMail import send_mail
from utilities.validators import form_validation, registration_validation, str2date
from utilities import tmpfile, checkPermission
import constants


add_chm_registration = PageTemplateFile('zpt/registration/add', globals())
def manage_add_chm_registration(self, id='', title='', conference_details='', administrative_email ='', start_date='', end_date='', lang='', REQUEST=None):
    """ Adds a CHM registration instance"""
    if registration_validation(REQUEST):
        if id:
            id = slugify(id)
        else:
            id = slugify(title)
        if lang is None: 
            lang = self.gl_get_selected_language()
        ob = CHMRegistration(id, title, conference_details, administrative_email, start_date, end_date, lang)
        self.gl_add_languages(ob)
        self._setObject(id, ob)
        ob = self._getOb(id)
        ob.loadDefaultContent()
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.absolute_url())
    else:
        return add_chm_registration.__of__(self)(REQUEST)


class CHMRegistration(LocalPropertyManager, Folder, NyContainer):
    """ Main class of the meeting registration"""

    meta_type = 'CHM Registration'
    product_name = 'CHMRegistration'

    security = ClassSecurityInfo()

    title = LocalProperty('title')
    conference_details = LocalProperty('conference_details')

    manage_options = (
        Folder.manage_options[:1]
        +
        (
            {'label': 'Reload registration forms', 'action': 'reloadRegistrationForms'},
        )
        +
        Folder.manage_options[2:]
    )

    security.declareProtected(constants.MANAGE_PERMISSION, 'loadDefaultContent')
    def loadDefaultContent(self):
        """ load default content such as: email templates """
        from TemplatesManager import manage_addTemplatesManager
        manage_addTemplatesManager(self)
        self._loadRegistrationForms()

    def __init__(self, id, title, conference_details, administrative_email, start_date, end_date, lang):
        """ constructor """
        self.id = id
        self.save_properties(title, conference_details, administrative_email, start_date, end_date, lang)

    security.declareProtected(constants.MANAGE_PERMISSION, 'save_properties')
    def save_properties(self, title, conference_details, administrative_email, start_date, end_date, lang):
        """ save properties """
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('conference_details', lang, conference_details)
        self.administrative_email = administrative_email
        self.start_date = str2date(start_date)
        self.end_date = str2date(end_date)

    security.declarePrivate('loadDefaultContent')
    def _loadRegistrationForms(self):
        """ load registration forms """
        registration_form = file(join(constants.PRODUCT_PATH, 'zpt', 'registration', 'registration.zpt')).read()
        manage_addPageTemplate(self, 'registration_form', title='', text=registration_form)
        view_participant = file(join(constants.PRODUCT_PATH, 'zpt', 'participant', 'view_participant.zpt')).read()
        edit_participant = file(join(constants.PRODUCT_PATH, 'zpt', 'participant', 'edit_participant.zpt')).read()
        menu_buttons = file(join(constants.PRODUCT_PATH, 'zpt', 'menu_buttons.zpt')).read()
        manage_addPageTemplate(self, 'menu_buttons', title='', text=menu_buttons)
        manage_addPageTemplate(self, 'view_participant', title='', text=view_participant)
        manage_addPageTemplate(self, 'edit_participant', title='', text=edit_participant)

    def _deleteRegistrationForms(self):
        try:
            self.manage_delObjects(['registration_form', 'menu_buttons', 'view_participant', 'edit_participant'])
        except:
            pass

    security.declareProtected(constants.MANAGE_PERMISSION, 'reloadRegistrationForms')
    def reloadRegistrationForms(self, REQUEST=None):
        """ reload registration forms """
        self._deleteRegistrationForms()
        self._loadRegistrationForms()
        if REQUEST:
            return self.manage_main(self, REQUEST, update_menu=1)

    def registration_html(self, REQUEST):
        """ registration form """
        submit =  REQUEST.form.get('submit', '')
        if submit:
            form_valid = form_validation(constants.PART_MANDATORY_FIELDS,
                                            constants.DATE_FIELDS,
                                            constants.TIME_FIELDS,
                                            REQUEST)
            if form_valid:
                lang = self.gl_get_selected_language()
                registration_no = naaya_utils.genRandomId(10)
                cleaned_data = REQUEST.form
                del cleaned_data['submit']
                if not 'event_1' in cleaned_data: cleaned_data['event_1'] = '0'
                if not 'event_2' in cleaned_data: cleaned_data['event_2'] = '0'
                if not 'event_3' in cleaned_data: cleaned_data['event_3'] = '0'
                ob = CHMParticipant(registration_no, **cleaned_data)
                self._setObject(registration_no, ob)
                participant = self._getOb(registration_no, None)
                if participant:
                    #save the authentication token on session
                    REQUEST.SESSION.set('authentication_id', registration_no)
                    REQUEST.SESSION.set('authentication_name', self.unicode2UTF8(participant.first_last_name))

                    #send notifications
                    values = {'registration_edit_link': participant.absolute_url(),
                                'registration_event': self.unicode2UTF8(self.title),
                                'website_team': self.unicode2UTF8(self.site_title),
                                'registration_number': registration_no,
                                'name': self.unicode2UTF8(participant.first_last_name)}
                    self.send_registration_notification(participant.email,
                        'Event registration',
                        self.getEmailTemplate('user_registration_html', lang) % values,
                        self.getEmailTemplate('user_registration_text', lang) % values)
                    self.send_registration_notification(self.administrative_email,
                        'Event registration',
                        self.getEmailTemplate('admin_registration_html', 'en') % values,
                        self.getEmailTemplate('admin_registration_text', 'en') % values)

                    #redirect to profile page
                    return REQUEST.RESPONSE.redirect(participant.absolute_url())
        return self.registration_form(REQUEST)

    security.declareProtected(constants.VIEW_PERMISSION, 'index_html')
    index_html = PageTemplateFile('zpt/registration/index', globals())

    security.declareProtected(constants.MANAGE_PERMISSION, '_edit_html')
    _edit_html = PageTemplateFile('zpt/registration/edit', globals())

    security.declarePrivate('getEmailTemplate')
    def getEmailTemplate(self, id, lang='en'):
        """ get email template """
        lang_dir = self.email_templates._getOb(lang, None)
        if lang_dir is None:    #maybe arabic?
            lang_dir = self.email_templates._getOb('en', None)
        email_template = lang_dir._getOb(id)
        return self.unicode2UTF8(email_template.document_src())

    def registrationOpened(self):
        """ check if the registration is opend to the public """
        now = time.localtime()
        if now >= self.start_date:
            return True
        return False

    def registrationNotClosed(self):
        """ check if the registration is opend to the public """
        now = time.localtime()
        from datetime import date, timedelta
        end_date = date(*self.end_date[0:3]) + timedelta(days=1)
        end_date = end_date.timetuple()[0:3] + self.end_date[3:]
        if now < end_date:
            return True
        return False

    security.declareProtected(constants.MANAGE_PERMISSION, 'edit_html')
    def edit_html(self, REQUEST):
        """ edit properties """
        submit =  REQUEST.form.get('edit-submit', '')
        if submit:
            if registration_validation(REQUEST):
                cleaned_data = REQUEST.form
                del cleaned_data['edit-submit']
                self.save_properties(**cleaned_data)
        return self._edit_html(REQUEST)

    security.declarePrivate('send_registration_notification')
    def send_registration_notification(self, email, title, email_html, email_txt):
        """ send a notification when a folder is added / edited / commented"""
        send_mail(msg_from=constants.NO_REPLY_MAIL,
                    msg_to=self.utConvertToList(email),
                    msg_subject='%s - Registration added / edited' % title,
                    msg_body=self.unicode2UTF8(email_html),
                    msg_body_text=self.unicode2UTF8(email_txt),
                    smtp_host = constants.SMTP_HOST,
                    smtp_port = constants.SMTP_PORT
                    )

    security.declareProtected(constants.VIEW_EDIT_PERMISSION, 'exportParticipants')
    def exportParticipants(self, REQUEST=None, RESPONSE=None):
        """ exports the participants list in CSV format """
        data = [('Registration date', 'Registration number', 'Name', 'Position', 'Organisation',
                    'Address', 'Postal code', 'eMail', 'eMail type', 'Phone number', 'Event #1', 'Event #2', 'Event #3', 
                    'Topic #1', 'Topic #2', 'Topic #3', 'Topic #4', 'Explanation')]
        data_app = data.append
        for part in self.getParticipants(skey='registration_date', rkey=1):
            if part.private_email:
                email_type = 'Private'
            else:
                email_type = 'Public'
            data_app((self.formatDate(part.registration_date), part.id,
                    self.unicode2UTF8(part.first_last_name), self.unicode2UTF8(part.position), 
                    self.unicode2UTF8(part.organisation), self.unicode2UTF8(part.address),
                    self.unicode2UTF8(part.zip_code), part.email, email_type, self.unicode2UTF8(part.phone_number),
                    self.unicode2UTF8(part.event_1), self.unicode2UTF8(part.event_2),
                    self.unicode2UTF8(part.event_3), self.unicode2UTF8(part.topic_1),
                     self.unicode2UTF8(part.topic_2), self.unicode2UTF8(part.topic_3),
                     self.unicode2UTF8(part.topic_4),
                     self.unicode2UTF8(part.explanation.replace('\r\n', ' ').replace('\n', ' '))))

        return self.create_csv(data, filename='participants.csv', RESPONSE=REQUEST.RESPONSE)

    security.declarePrivate('create_csv')
    def create_csv(self, data, filename, RESPONSE):
        tmp_name = tmpfile(data)
        content = open(str(tmp_name)).read()
        RESPONSE.setHeader('Content-Type', 'text/csv')
        RESPONSE.setHeader('Content-Disposition', 'attachment; filename=%s' % filename)
        return content

    security.declareProtected(constants.VIEW_EDIT_PERMISSION, 'participants')
    participants = PageTemplateFile('zpt/registration/participants', globals())

    security.declareProtected(constants.VIEW_EDIT_PERMISSION, 'getParticipants')
    def getParticipants(self, skey, rkey):
        """ Returns the list of participants """
        meta_type = 'CHM Participant'
        participants = [ ( self.unicode2UTF8(getattr(p, skey)), p ) for p in self.objectValues(meta_type) ]
        participants.sort()
        if rkey:
            participants.reverse()
        return [p for (key, p) in participants]

    security.declareProtected(constants.VIEW_EDIT_PERMISSION, 'deleteParticipants')
    def deleteParticipants(self, ids=[], REQUEST=None):
        """ Deletes selected participants """
        ids = self.utConvertToList(ids)
        self.manage_delObjects(ids)
        return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

    security.declarePublic('canManageParticipants')
    def canManageParticipants(self):
        """ Check the permissions to edit/delete meeting settgins and participants """
        return checkPermission(constants.MANAGE_PERMISSION, self)

    security.declarePublic('canViewParticipants')
    def canViewParticipants(self):
        """ Check the permissions to edit/delete participants """
        return checkPermission(constants.VIEW_EDIT_PERMISSION, self)

    security.declarePublic('getRegistrationTitle')
    def getRegistrationTitle(self):
        """ """
        return self.title

    security.declarePublic('getConferenceDetails')
    def getConferenceDetails(self):
        """ """
        return self.conference_details

    #internal
    def formatDate(self, sdate, format='%d/%m/%Y'):
        if sdate:
            return time.strftime(format, sdate)
        return None

    def unicode2UTF8(self, s):
        if isinstance(s, unicode):
            return s.encode('utf-8')
        return s

    def getPropertyValue(self, id, lang=None):
        """ Returns a property value in the specified language. """
        if lang is None: lang = self.gl_get_selected_language()
        return self.getLocalProperty(id, lang)

    security.declareProtected(constants.VIEW_PERMISSION, 'getCountryList')
    def getCountryList(self):
        """ """
        catalog = self.glossary_coverage.getGlossaryCatalog()
        brains = catalog(meta_type='Naaya Glossary Element', sort_on='id', sort_order='ascending')
        return self.__getObjects(catalog, brains)

    def __getObjects(self, catalog, p_brains):
        """ """
        try:
            return map(catalog.getobject, map(getattr, p_brains, ('data_record_id_',)*len(p_brains)))
        except:
            return []

    def hasVersion(self):
        """ """
        return None

InitializeClass(CHMRegistration)
