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
from Products.NaayaCore.managers.import_export import UnicodeReader
from naaya.i18n.LocalPropertyManager import LocalPropertyManager, LocalProperty
from CHMParticipant import CHMParticipant
from utilities.Slugify import slugify
from utilities.SendMail import send_mail
from utilities.validators import form_validation, registration_validation, str2date
from utilities import tmpfile, checkPermission
import constants


add_chm_registration = PageTemplateFile('zpt/registration/add', globals())
def manage_add_chm_registration(self, id='', title='', conference_details='',\
    conference_description='', conference_period='', conference_place='',
    administrative_email ='', start_date='', end_date='', lang='', REQUEST=None):
    """ Adds a CHM registration instance"""
    if registration_validation(constants.REG_MANDATORY_FIELDS,
                                            constants.REG_DATE_FIELDS,
                                            constants.REG_TIME_FIELDS,
                                            REQUEST):
        id = naaya_utils.make_id(self, id=id, title=title, prefix='registration')
        if lang is None: 
            lang = self.gl_get_selected_language()
        ob = CHMRegistration(id, title, conference_details, conference_description,\
        conference_period, conference_place, administrative_email, start_date, end_date, lang)
        self.gl_add_languages(ob)
        self._setObject(id, ob)
        ob = self._getOb(id)
        ob.loadDefaultContent()
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.absolute_url())
    else:
        return add_chm_registration.__of__(self)(REQUEST)


class CHMRegistration(LocalPropertyManager, Folder):
    """ Main class of the meeting registration"""

    meta_type = 'CHM Registration Dec2009'
    product_name = 'CHMRegistrationDec2009'

    security = ClassSecurityInfo()

    title = LocalProperty('title')
    conference_details = LocalProperty('conference_details')
    conference_description = LocalProperty('conference_description')

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

    def __init__(self, id, title, conference_details, conference_description,\
                    conference_period, conference_place, administrative_email,\
                    start_date, end_date, lang):
        """ constructor """
        self.id = id
        self.save_properties(title, conference_details, conference_description,\
                    conference_period, conference_place, administrative_email,\
                    start_date, end_date, lang)

    security.declareProtected(constants.MANAGE_PERMISSION, 'save_properties')
    def save_properties(self, title, conference_details, conference_description,\
                    conference_period, conference_place, administrative_email,\
                    start_date, end_date, lang):
        """ save properties """
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('conference_details', lang, conference_details)
        self._setLocalPropValue('conference_description', lang, conference_description)
        self._setLocalPropValue('conference_period', lang, conference_period)
        self._setLocalPropValue('conference_place', lang, conference_place)
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
                registration_id = naaya_utils.make_id(self, prefix='p')
                cleaned_data = REQUEST.form
                del cleaned_data['submit']
                ob = CHMParticipant(registration_id, **cleaned_data)
                self._setObject(registration_id, ob)
                participant = self._getOb(registration_id, None)
                if participant:
                    #save the authentication token on session
                    REQUEST.SESSION.set('authentication_id', registration_id)
                    REQUEST.SESSION.set('authentication_name', self.unicode2UTF8(participant.organisation_name))

                    #send notifications
                    email_recipients = [getattr(participant, field) for field in constants.PART_EMAIL_RECIPIENTS]
                    conference_period = self.getPropertyValue('conference_period', lang)
                    conference_place = self.getPropertyValue('conference_place', lang)
                    values = {'registration_edit_link': participant.absolute_url(),
                                'registration_event': self.unicode2UTF8(self.title),
                                'conference_period': conference_period,
                                'conference_place': conference_place,
                                'website_team': self.unicode2UTF8(self.site_title),
                                'registration_id': registration_id,
                                'name': self.unicode2UTF8(participant.organisation_name)}
                    self.send_registration_notification(email_recipients,
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
            if registration_validation(constants.REG_MANDATORY_FIELDS,
                                            constants.REG_DATE_FIELDS,
                                            constants.REG_TIME_FIELDS,
                                            REQUEST):
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

    security.declareProtected(constants.VIEW_EDIT_PERMISSION, 'importParticipants')
    def importParticipants(self, REQUEST=None, RESPONSE=None):
        """ """
        errors = []
        succcess = ''
        data = REQUEST.form.get('data', None)
        if data is None:
            pass
        try:
            reader = UnicodeReader(data)
            header = reader.next()
            record_number = 0
            for row in reader:
                try:
                    record_number += 1
                    participant_data = {}
                    for column, value in zip(header, row):
                        participant_data[str(column)] = value
                    registration_id = naaya_utils.make_id(self, prefix='p')
                    ob = CHMParticipant(registration_id, **participant_data)
                    self._setObject(registration_id, ob)
                except UnicodeDecodeError, e:
                    raise
                except Exception, e:
                    self.log_current_error()
                    msg = 'Error while importing from CSV, row %d: %s' % (record_number, str(e))
                    if REQUEST is None:
                        raise ValueError(msg)
                    else:
                        errors.append(msg)
        except UnicodeDecodeError, e:
            if REQUEST is None:
                raise
            else:
                errors = ['CSV file is not utf-8 encoded']
        if not errors:
            REQUEST.set('success', "%s records were imported successfully." % record_number)
        else:
            REQUEST.set('errors', errors)
        return self.participants(REQUEST)

    security.declareProtected(constants.VIEW_EDIT_PERMISSION, 'exportParticipants')
    def exportParticipants(self, REQUEST=None, RESPONSE=None):
        """ exports the participants list in CSV format """
        data = [('Registration date', 'Registration number',
                'Organisation Name', 'Organisation Address', 'Organisation Website',
                'Media contact name', 'Media contact email',
                'Media contact telephone', 'Media contact details',
                'Program contact name', 'Program contact email', 'Program contact telephone',
                'VIP contact name', 'VIP contact email', 'VIP contact telephone',
                'Activities', 'Disclose permission', 'Comments')]
        data_app = data.append
        for part in self.getParticipants(skey='registration_date', rkey=1):
            """if part.private_email:
                email_type = 'Private'
            else:
                email_type = 'Public'"""
            disclose_permission = part.disclose_permission == '1' and 'Yes' or 'No'
            data_app((self.formatDate(part.registration_date), part.id,
                    self.unicode2UTF8(part.organisation_name), self.unicode2UTF8(part.organisation_address),
                    self.unicode2UTF8(part.organisation_website), self.unicode2UTF8(part.media_contact_name),
                    part.email, self.unicode2UTF8(part.media_contact_telephone), 
                    self.unicode2UTF8(part.media_contact_details.replace('\r\n', ' ').replace('\n', ' ')),
                    self.unicode2UTF8(part.program_contact_name), part.program_contact_email,
                    self.unicode2UTF8(part.program_contact_telephone), self.unicode2UTF8(part.vip_contact_name),
                    part.vip_contact_email, self.unicode2UTF8(part.vip_contact_telephone),
                    self.unicode2UTF8(part.activities.replace('\r\n', ' ').replace('\n', ' ')),
                    disclose_permission, self.unicode2UTF8(part.admin_comment)))

        return self.create_csv(data, filename='participants.csv', RESPONSE=REQUEST.RESPONSE)

    security.declarePrivate('create_csv')
    def create_csv(self, data, filename, RESPONSE):
        tmp_name = tmpfile(data)
        content = open(str(tmp_name)).read()
        RESPONSE.setHeader('Content-Type', 'text/csv')
        RESPONSE.setHeader('Content-Disposition', 'attachment; filename=%s' % filename)
        return content

    _participants = PageTemplateFile('zpt/registration/participants', globals())
    security.declareProtected(constants.VIEW_EDIT_PERMISSION, 'participants')
    def participants(self, ids=[], REQUEST=None):
        """ Loads the participants template.
        Deletes selected participants or saves comments, depending on the pressed button. """
        delete_participants = None
        save_comments = None
        if REQUEST is not None:
            delete_participants = REQUEST.get('delete_selected', None)
            save_comments = REQUEST.get('save_comments', None)
        if delete_participants is not None:
            self.deleteParticipants(ids)
            return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)
        if save_comments is not None:
            comments = [(key.split('_')[-1], value) for key, value in REQUEST.form.items() if key.startswith('admin_comment_') and value]
            for comment in comments:
                self._getOb(comment[0]).admin_comment = comment[1]
            return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)
        return self._participants(REQUEST)

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
    def deleteParticipants(self, ids):
        """ Deletes selected participants """
        ids = self.utConvertToList(ids)
        self.manage_delObjects(ids)

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
