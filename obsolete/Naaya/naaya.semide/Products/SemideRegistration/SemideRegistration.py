import re
import time
import simplejson as json
from os.path import join

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view, view_management_screens
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.Folder import Folder

from Products.NaayaCore.managers import utils as naaya_utils
from naaya.i18n.LocalPropertyManager import LocalPropertyManager, LocalProperty
from BaseParticipant import BaseParticipant
from SemidePress import SemidePress
from utilities.Slugify import slugify
from utilities.SendMail import send_mail
from utilities.validators import form_validation, registration_validation, str2date
from utilities import tmpfile, checkPermission
import constants


add_registration = PageTemplateFile('zpt/registration/add', globals())
def manage_add_registration(self, id='', title='', conference_details='', administrative_email ='', start_date='', end_date='', introduction='', lang='', REQUEST=None):
    """ Adds a Semide registration instance"""
    if registration_validation(REQUEST):

        ptool = self.getPortletsTool()
        list_id = 'conference_participant_types'
        itopics = getattr(ptool, list_id, None)
        if not itopics:
            ptool.manage_addRefTree(list_id, 'Participant types')
            itopics = getattr(ptool, list_id, None)
            item_no = 0
            for list_item in constants.PARTICIPANT_TYPES:
                itopics.manage_addRefTreeNode(str(item_no), list_item)
                item_no += 1

        if id:
            id = slugify(id)
        else:
            id = slugify(title)
        if lang is None:
            lang = self.gl_get_selected_language()
        ob = SemideRegistration(id, title, conference_details, administrative_email, start_date, end_date, introduction, lang)
        self.gl_add_languages(ob)
        self._setObject(id, ob)
        ob = self._getOb(id)
        ob.loadDefaultContent()
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

    manage_options = (
        Folder.manage_options[:1]
        +
        (
            {'label': 'Reload registration forms', 'action': 'reloadRegistrationForms'},
        )
        +
        Folder.manage_options[2:]
    )
    security.declareProtected(view, 'index_html')
    index_html = PageTemplateFile('zpt/registration/index', globals())

    security.declareProtected(view_management_screens, '_edit_html')
    _edit_html = PageTemplateFile('zpt/registration/edit', globals())

    security.declarePublic('registration_form')
    registration_form = PageTemplateFile('zpt/registration/registration',
                                         globals())

    security.declarePublic('registration_press_form')
    registration_press_form = PageTemplateFile(
        'zpt/registration/registration_press', globals())

    security.declarePublic('view_participant')
    view_participant = PageTemplateFile('zpt/participant/view_participant',
                                        globals())

    security.declarePublic('edit_participant')
    edit_participant = PageTemplateFile('zpt/participant/edit_participant',
                                        globals())

    security.declarePublic('menu_buttons')
    menu_buttons = PageTemplateFile('zpt/menu_buttons',
                                        globals())

    security.declareProtected(view_management_screens, 'participants')
    participants = PageTemplateFile('zpt/registration/participants', globals())

    security.declareProtected(view_management_screens, 'participants_press')
    participants_press = PageTemplateFile(
        'zpt/registration/participants_press', globals())

    def __init__(self, id, title, conference_details, administrative_email, start_date, end_date, introduction, lang):
        """ constructor """
        self.id = id
        self.save_properties(title, conference_details, administrative_email, start_date, end_date, introduction, lang)

    security.declareProtected(view_management_screens, 'loadDefaultContent')
    def loadDefaultContent(self):
        """ load default content such as: email templates """
        from TemplatesManager import manage_addTemplatesManager
        manage_addTemplatesManager(self)
        self._loadRegistrationForms()

    security.declarePrivate('_loadRegistrationForms')
    def _loadRegistrationForms(self):
        """ load registration forms """

    security.declarePrivate('_deleteRegistrationForms')
    def _deleteRegistrationForms(self):
        try:
            self.manage_delObjects(['registration_form', 'registration_press_form', 'menu_buttons', 'view_participant', 'edit_participant'])
        except:
            pass

    security.declareProtected(view_management_screens, 'save_properties')
    def save_properties(self, title, conference_details, administrative_email, start_date, end_date, introduction, lang):
        """ save properties """
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('conference_details', lang, conference_details)
        self._setLocalPropValue('introduction', lang, introduction)
        self.administrative_email = administrative_email
        self.start_date = str2date(start_date)
        self.end_date = str2date(end_date)


    security.declareProtected(view_management_screens, 'reloadRegistrationForms')
    def reloadRegistrationForms(self, REQUEST=None):
        """ reload registration forms """
        self._deleteRegistrationForms()
        self._loadRegistrationForms()
        if REQUEST:
            return self.manage_main(self, REQUEST, update_menu=1)

    security.declareProtected(view, 'registration_html')
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
                ob = BaseParticipant(registration_no, **cleaned_data)
                self._setObject(registration_no, ob)
                participant = self._getOb(registration_no, None)
                if participant:
                    #save the authentication token on session
                    REQUEST.SESSION.set('authentication_id', registration_no)
                    REQUEST.SESSION.set('authentication_name', self.unicode2UTF8(participant.last_name))

                    #send notifications
                    values = {'registration_edit_link': participant.absolute_url(),
                                'conference_title': self.unicode2UTF8(self.title),
                                'conference_details': self.unicode2UTF8(self.conference_details),
                                'website_team': self.unicode2UTF8(self.site_title),
                                'registration_number': registration_no,
                                'last_name': self.unicode2UTF8(participant.last_name)}
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

    security.declareProtected(view, 'registration_press_html')
    def registration_press_html(self, REQUEST):
        """ registration form """
        submit =  REQUEST.form.get('submit', '')
        if submit:
            form_valid = form_validation(constants.PRESS_MANDATORY_FIELDS,
                                            constants.DATE_FIELDS,
                                            constants.TIME_FIELDS,
                                            REQUEST)
            if form_valid:
                lang = self.gl_get_selected_language()
                registration_no = naaya_utils.genRandomId(10)
                cleaned_data = REQUEST.form
                del cleaned_data['submit']
                ob = SemidePress(registration_no, **cleaned_data)
                self._setObject(registration_no, ob)
                press = self._getOb(registration_no, None)
                if press:
                    #save the authentication token on session
                    REQUEST.SESSION.set('authentication_id', registration_no)
                    REQUEST.SESSION.set('authentication_name', self.unicode2UTF8(press.last_name))

                    #send notifications
                    values = {'registration_edit_link': press.absolute_url(),
                                'conference_title': self.unicode2UTF8(self.title),
                                'conference_details': self.unicode2UTF8(self.conference_details),
                                'website_team': self.unicode2UTF8(self.site_title),
                                'registration_number': registration_no,
                                'last_name': self.unicode2UTF8(press.last_name)}
                    self.send_registration_notification(press.email,
                        'Event registration',
                        self.getEmailTemplate('user_registration_html', lang) % values,
                        self.getEmailTemplate('user_registration_text', lang) % values)
                    self.send_registration_notification(self.administrative_email,
                        'Event registration',
                        self.getEmailTemplate('admin_registration_html', 'en') % values,
                        self.getEmailTemplate('admin_registration_text', 'en') % values)

                    return REQUEST.RESPONSE.redirect(press.absolute_url())
        return self.registration_press_form(REQUEST)

    security.declarePrivate('getEmailTemplate')
    def getEmailTemplate(self, id, lang='en'):
        """ get email template """
        lang_dir = self.email_templates._getOb(lang, None)
        if lang_dir is None:    #maybe arabic?
            lang_dir = self.email_templates._getOb('en', None)
        email_template = lang_dir._getOb(id)
        return self.unicode2UTF8(email_template.document_src())

    #XXX: security?
    def registrationOpened(self):
        """ check if the registration is opend to the public """
        now = time.localtime()
        if now >= self.start_date:
            return True
        return False

    #XXX: security?
    def registrationNotClosed(self):
        """ check if the registration is opend to the public """
        now = time.localtime()
        from datetime import date, timedelta
        end_date = date(*self.end_date[0:3]) + timedelta(days=1)
        end_date = end_date.timetuple()[0:3] + self.end_date[3:]
        if now < end_date:
            return True
        return False

    security.declareProtected(view_management_screens, 'edit_html')
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

    security.declareProtected(view_management_screens, 'exportParticipants')
    def exportParticipants(self, REQUEST=None, RESPONSE=None):
        """ exports the participants list in CSV format """
        data = [('Registration date', 'Registration number', 'Official delegation of',
                    'Participant type', 'First name', 'Name', 'Gender', 'Position',
                    'Work address', 'City', 'Postal code', 'Country', 'Phone number',
                    'Mobile number', 'Email', 'Fax number', 'Passport number', 'Language(s) spoken',
                    'Date of arrival', 'Time of arrival',
                    'Arrival flight number', 'Arrival flight company',
                    'Date of departure', 'Time of departure',
                    'Departure flight number', 'Departure flight company',
                    'Special requests', 'Medical requirements', 'Special diet',
                    'Participation in the 12/04 event', 'Participation in the 14/04 activity')]
        data_app = data.append
        for part in self.getParticipants(skey='registration_date', rkey=1, is_journalist=False):
            if part.arrival_date:
                arrival_date = self.formatDate(part.arrival_date)
            else:
                arrival_date = 'n/a'
            if part.departure_date:
                departure_date = self.formatDate(part.departure_date)
            else:
                departure_date = 'n/a'
            if part.extra_event_1:
                extra_event_1 = 'Yes'
            else:
                extra_event_1 = 'No'
            if part.extra_event_2:
                extra_event_2 = 'Yes'
            else:
                extra_event_2 = 'No'
            data_app((self.formatDate(part.registration_date), part.id, self.unicode2UTF8(part.delegation_of),
            self.getRefTreeTitle(part.participant_type), self.unicode2UTF8(part.first_name),
            self.unicode2UTF8(part.last_name), self.unicode2UTF8(part.gender),
            self.unicode2UTF8(part.position),
            self.unicode2UTF8(part.work_address).replace('\r\n', ' ').replace('\n', ' '),
            self.unicode2UTF8(part.city), self.unicode2UTF8(part.postal_code), self.unicode2UTF8(part.country),
            self.unicode2UTF8(part.phone_number), self.unicode2UTF8(part.mobile_number),
            part.email, self.unicode2UTF8(part.fax_number), self.unicode2UTF8(part.passport_no),
            self.unicode2UTF8(part.languages),
            arrival_date, part.arrival_time,
            self.unicode2UTF8(part.arrival_flight_number), self.unicode2UTF8(part.arrival_flight_company),
            departure_date, part.departure_time,
            self.unicode2UTF8(part.departure_flight_number), self.unicode2UTF8(part.departure_flight_company),
            self.unicode2UTF8(part.special_requests), self.unicode2UTF8(part.medical_requirements),
            self.unicode2UTF8(part.special_diet), extra_event_1, extra_event_2))

        return self.create_csv(data, filename='participants.csv', RESPONSE=REQUEST.RESPONSE)

    security.declareProtected(view_management_screens, 'exportPress')
    def exportPress(self, REQUEST=None, RESPONSE=None):
        """ exports the press participants list in CSV format """
        data = [('Registration date', 'Registration number', 'First name', 'Name', 'Country', 'Media name',
                    'Type of media', 'Description of equipment used', 'Your position', 'Passport number',
                    'Expiry date of the passport', 'Email address', 'Phone number', 'Fax number', 'Mobile phone', 'Date of arrival', 'Arriving from', 'Flight number', 'Time of arrival',
                    'Date of departure', 'Flight number', 'Time of departure')]
        data_app = data.append
        for part in self.getParticipants(skey='registration_date', rkey=1, is_journalist=True):
            if part.arrival_date:
                arrival_date = self.formatDate(part.arrival_date)
            else:
                arrival_date = 'n/a'
            if part.departure_date:
                departure_date = self.formatDate(part.departure_date)
            else:
                departure_date = 'n/a'
            data_app((self.formatDate(part.registration_date), part.id, self.unicode2UTF8(part.first_name), self.unicode2UTF8(part.last_name),
                        self.unicode2UTF8(part.country), self.unicode2UTF8(part.media_name), self.unicode2UTF8(part.media_type), self.unicode2UTF8(part.media_description).replace('\r\n', ' ').replace('\n', ' '),
                        self.unicode2UTF8(part.media_position), self.unicode2UTF8(part.passport_no), self.unicode2UTF8(part.passport_expire), part.email,
                        self.unicode2UTF8(part.phone_number), self.unicode2UTF8(part.fax_number), self.unicode2UTF8(part.mobile_number), arrival_date,
                        self.unicode2UTF8(part.arrival_from), self.unicode2UTF8(part.arrival_flight), part.arrival_time, departure_date, self.unicode2UTF8(part.departure_flight),
                        part.departure_time))
        return self.create_csv(data, filename='press_participants.csv', RESPONSE=REQUEST.RESPONSE)

    security.declarePrivate('create_csv')
    def create_csv(self, data, filename, RESPONSE):
        tmp_name = tmpfile(data)
        content = open(str(tmp_name)).read()
        RESPONSE.setHeader('Content-Type', 'text/csv')
        RESPONSE.setHeader('Content-Disposition', 'attachment; filename=%s' % filename)
        return content

    security.declareProtected(view_management_screens, 'getParticipants')
    def getParticipants(self, skey, rkey, is_journalist):
        """ Returns the list of participants """
        if is_journalist:
            meta_type = 'Semide Press Participant'
        else:
            meta_type = 'Semide Participant'
        participants = [ ( self.unicode2UTF8(getattr(p, skey)), p ) for p in self.objectValues(meta_type) ]
        participants.sort()
        if rkey:
            participants.reverse()
        return [p for (key, p) in participants]

    security.declareProtected(view_management_screens, 'deleteParticipants')
    def deleteParticipants(self, ids=[], REQUEST=None):
        """ Deletes selected participants """
        ids = self.utConvertToList(ids)
        self.manage_delObjects(ids)
        return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

    security.declarePublic('canManageParticipants')
    def canManageParticipants(self):
        """ Check the permissions to edit/delete participants """
        return checkPermission(view_management_screens, self)

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

    security.declareProtected(view, 'getCountryList')
    def getCountryList(self):
        """ """
        catalog = self.glossary_coverage.getGlossaryCatalog()
        brains = catalog(meta_type='Naaya Glossary Element', sort_on='id', sort_order='ascending')
        #if there are several glossaries, countries can get duplicated, so remove duplicates:
        all_countries_list = self.__getObjects(catalog, brains)
        country_list = {}
        for country in all_countries_list:
            country_list[country.id] = country
        return self.utSortObjsListByAttr(country_list.values(), 'id', False)

    def __getObjects(self, catalog, p_brains):
        """ """
        try:
            return map(catalog.getobject, map(getattr, p_brains, ('data_record_id_',)*len(p_brains)))
        except:
            return []

    def hasVersion(self):
        """ """
        return None

    def getRefTree(self, ref_tree_id):
        """ """
        return self.getPortletsTool().getRefTreeById(ref_tree_id)

    def getRefTreeNodes(self, ref_tree_id='conference_participant_types'):
        """ """
        ref_tree = self.getRefTree(ref_tree_id)
        nodes = ref_tree.get_tree_nodes()
        return [(node.id, node.title) for node in nodes]

    def getRefTreeTitle(self, node_id, ref_tree_id='conference_participant_types'):
        """ """
        ref_tree = self.getRefTree(ref_tree_id)
        for node in ref_tree.get_tree_nodes():
            if node.id == node_id:
                return node.title
        return None

    security.declareProtected(view, 'getDelegations')
    def getDelegations(self, meta_type='Semide Participant'):
        """ """
        return json.dumps([ob.delegation_of for ob in self.objectValues(meta_type)])

InitializeClass(SemideRegistration)
