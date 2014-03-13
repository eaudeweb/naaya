#Python impors
from copy import deepcopy
import os
import sys
import datetime
import vobject
import logging
from html2text import html2text

#Zope imports
from AccessControl import ClassSecurityInfo
from AccessControl import SpecialUsers
from AccessControl import getSecurityManager
from AccessControl.Permission import Permission
from AccessControl.Permissions import view_management_screens, view, change_permissions
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from App.ImageFile import ImageFile
from DateTime import DateTime
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate import manage_addPageTemplate
from Products.PythonScripts.PythonScript import manage_addPythonScript
from ZPublisher.BaseRequest import DefaultPublishTraverse
from naaya.content.base.events import NyContentObjectAddEvent
from naaya.content.base.events import NyContentObjectEditEvent
from zope.event import notify
from zope.interface import implements

#Naaya imports
from Products.Naaya.NyFolder import NyFolder
from Products.NaayaBase.NyContentType import NyContentData, NY_CONTENT_BASE_SCHEMA
from Products.NaayaBase.constants import EXCEPTION_NOTAUTHORIZED
from Products.NaayaBase.constants import EXCEPTION_NOTAUTHORIZED_MSG
from Products.NaayaBase.constants import PERMISSION_EDIT_OBJECTS
from Products.NaayaBase.constants import MESSAGE_SAVEDCHANGES
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyBase import rss_item_for_object
from Products.NaayaCore.managers.utils import make_id, get_nsmap
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from Products.NaayaCore.LayoutTool.LayoutTool import AdditionalStyle
from naaya.core.zope2util import DT2dt
from naaya.core.zope2util import relative_object_path
from naaya.core.zope2util import get_zope_env
from interfaces import INyMeeting
from Products.Naaya.NySite import NySite
from Products.NaayaSurvey.MegaSurvey import manage_addMegaSurvey

#Meeting imports
from naaya.content.meeting import (OBSERVER_ROLE, WAITING_ROLE, PARTICIPANT_ROLE,
        ADMINISTRATOR_ROLE, MANAGER_ROLE, OWNER_ROLE)
from permissions import (PERMISSION_ADD_MEETING,
                         PERMISSION_PARTICIPATE_IN_MEETING,
                         PERMISSION_ADMIN_MEETING)
from participants import Participants
from email import EmailSender, configureEmailNotifications
from reports import MeetingReports
from subscriptions import SignupUsersTool

from lxml import etree
from lxml.builder import ElementMaker

from countries import country_from_country_code

#module constants
NETWORK_NAME = get_zope_env('NETWORK_NAME', '')
DEFAULT_SCHEMA = {
    'interval':             dict(sortorder=140, widget_type='Interval',
                                label='Meeting Interval', data_type='interval',
                                required=True),
    'location':             dict(sortorder=143, widget_type='String',
                                label='Organization/Building/Room'),
    'allow_register':       dict(sortorder=147, widget_type='Checkbox',
                                label='Allow people to register to participate',
                                data_type='bool'),
    'auto_register':        dict(sortorder=148, widget_type='Checkbox',
                                label=('Automatically approve participants '
                                'when they register'),
                                data_type='bool'),
    'restrict_items':       dict(sortorder=149, widget_type='Checkbox',
                                label=('Restrict user access to the contents '
                                'in the meeting'), default=True,
                                data_type='bool'),
    'max_participants':     dict(sortorder=150, widget_type='String',
                                label='Maximum number of participants',
                                data_type='int'),
    'contact_person':       dict(sortorder=150, widget_type='String',
                                label='Contact person'),
    'contact_email':        dict(sortorder=160, widget_type='String',
                                label='Contact email', required=True),
    'is_eionet_meeting':    dict(sortorder=220, widget_type='Checkbox',
                                label='This is an EIONET meeting',
                                data_type='bool',
                                visible=NETWORK_NAME.lower()=='eionet'),
    'survey_pointer':       dict(sortorder=230, widget_type='Pointer',
                                label='Link to the Meeting Survey',
                                relative=True),
    'survey_required':      dict(sortorder=240, widget_type='Checkbox',
                                label='Survey Required', data_type='bool'),
    'agenda_pointer':       dict(sortorder=310, widget_type='Pointer',
                                label='Link to the Meeting Agenda',
                                relative=True),
    'minutes_pointer':      dict(sortorder=320, widget_type='Pointer',
                                label='Link to the Meeting Minutes',
                                relative=True),
}
DEFAULT_SCHEMA.update(deepcopy(NY_CONTENT_BASE_SCHEMA))
DEFAULT_SCHEMA['geo_location'].update(visible=True, required=True)
DEFAULT_SCHEMA['geo_type'].update(visible=True, label="Meeting type")
DEFAULT_SCHEMA['coverage'].update(visible=False)
DEFAULT_SCHEMA['releasedate'].update(visible=True)

# this dictionary is updated at the end of the module
config = {
        'product': 'NaayaContent',
        'module': 'meeting',
        'package_path': os.path.abspath(os.path.dirname(__file__)),
        'meta_type': 'Naaya Meeting',
        'label': 'Meeting',
        'permission': PERMISSION_ADD_MEETING,
        'forms': ['meeting_add', 'meeting_edit', 'meeting_index'],
        'add_form': 'meeting_add_html',
        'description': 'This is Naaya Meeting type.',
        'default_schema': DEFAULT_SCHEMA,
        'schema_name': 'NyMeeting',
        '_module': sys.modules[__name__],
        'additional_style': AdditionalStyle('www/style.css', globals()),
        'icon': os.path.join(os.path.dirname(__file__), 'www', 'meeting.gif'),
        '_misc': {
                'NyMeeting.gif': ImageFile('www/meeting.gif', globals()),
                'NyMeeting_marked.gif': ImageFile('www/meeting_marked.gif', globals()),
                'Attendees.jpg': ImageFile('www/Attendees.jpg', globals()),
                'Email.jpg': ImageFile('www/Email.jpg', globals()),
                'iCalendar.jpg': ImageFile('www/iCalendar.jpg', globals()),
                'participant.gif': ImageFile('www/participant.gif', globals()),
                'organization.gif': ImageFile('www/organization.gif', globals()),
                'Agenda.png': ImageFile('www/Agenda.png', globals()),
                'Minutes.png': ImageFile('www/Minutes.png', globals()),
                'survey.gif': ImageFile('www/survey.gif', globals()),
                'RegisterExistingUser.jpg': ImageFile('www/RegisterExistingUser.jpg', globals()),
                'RegisterNewAccount.jpg': ImageFile('www/RegisterNewAccount.jpg', globals()),
            },
    }

#add meeting reports to NySite
NySite.meeting_reports = MeetingReports('meeting_reports')

# Meeting Logger
log = logging.getLogger('naaya.content.meeting')

def add_observer_role(site):
    """
    !!! Adding OBSERVER_ROLE on meeting installation.
    This is given to the non participants users of the meetings.
    Permissions are set similar to the Authenticated role.
    The role will also get permission to view the meeting as a participant.
    """
    permissions = ['Naaya - Skip Captcha',
                   'Naaya - View Naaya Survey Answers',
                   'Naaya - View Naaya Survey Reports']

    auth_tool = site.getAuthenticationTool()

    if OBSERVER_ROLE not in auth_tool.list_all_roles():
        auth_tool.addRole(OBSERVER_ROLE)

    b = [x['name'] for x in site.permissionsOfRole(OBSERVER_ROLE)
                        if x['selected']=='SELECTED']
    b.extend(permissions)
    site.manage_role(OBSERVER_ROLE, b)

def meeting_on_install(site):
    """ """
    add_observer_role(site)

    # add new map symbols for the meeting
    portal_map = site.getGeoMapTool()
    if portal_map is not None:
        new_map_symbols = [('meeting.png', 'Meeting'),
                        ('conference.png', 'Conference'),
                        ('workshop.png', 'Workshop')]
        for i in range(len(new_map_symbols)):
            new_map_symbols[i] = (os.path.join(
                                    os.path.dirname(__file__),
                                    'www',
                                    'map_symbols',
                                    new_map_symbols[i][0]),
                             new_map_symbols[i][1])

        map_symbols = portal_map.getSymbolsListOrdered()
        map_symbols_titles = [s.title for s in map_symbols]
        new_map_symbols = [nms for nms in new_map_symbols
                                    if nms[1] not in map_symbols_titles]

        for filename, symbol_name in new_map_symbols:
            file = open(filename, 'r')
            symbol = file.read()
            file.close()

            portal_map.adminAddSymbol(title=symbol_name, picture=symbol)

    configureEmailNotifications(site)

def meeting_add_html(self):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, config['meta_type'])
    return self.getFormsTool().getContent({'here': self, 'kind': config['meta_type'], 'action': 'addNyMeeting', 'form_helper': form_helper}, 'meeting_add')

def _create_NyMeeting_object(parent, id, contributor):
    id = make_id(parent, id=id, prefix='meeting')
    ob = NyMeeting(id, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def addNyMeeting(self, id='', REQUEST=None, contributor=None, **kwargs):
    """
    Create an Meeting type of object.
    """
    if REQUEST is not None:
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs
    _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
    _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''))
    schema_raw_data.setdefault('resourceurl', '')
    schema_raw_data.setdefault('source', '')
    _contact_word = schema_raw_data.get('contact_word', '')

    id = make_id(self, id=id, title=schema_raw_data.get('title', ''), prefix='meeting')
    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_NyMeeting_object(self, id, contributor)

    form_errors = ob.meeting_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

    #check Captcha/reCaptcha
    if REQUEST:
        if not self.checkPermissionSkipCaptcha():
            captcha_validator = self.validateCaptcha(_contact_word, REQUEST)
            if captcha_validator:
                form_errors['captcha'] = captcha_validator

    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1]) # pick a random error
        else:
            import transaction; transaction.abort() # because we already called _crete_NyZzz_object
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            REQUEST.RESPONSE.redirect('%s/meeting_add_html' % self.absolute_url())
            return

    if self.checkPermissionSkipApproval():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    ob.approveThis(approved, approved_by)
    ob.submitThis()

    # add change permission to administrator and owner
    permission = Permission(change_permissions, (), ob)
    permission.setRoles([ADMINISTRATOR_ROLE, OWNER_ROLE])
    permission = Permission(PERMISSION_PARTICIPATE_IN_MEETING, (), ob)
    permission.setRoles([OBSERVER_ROLE, WAITING_ROLE, PARTICIPANT_ROLE,
                         ADMINISTRATOR_ROLE, OWNER_ROLE])
    permission = Permission(PERMISSION_ADMIN_MEETING, (), ob)
    permission.setRoles([ADMINISTRATOR_ROLE, OWNER_ROLE])
    #add view permission for signups - useful in restricted portals
    permission = Permission('View', (), ob)
    permission.setRoles([OBSERVER_ROLE, WAITING_ROLE, PARTICIPANT_ROLE,])

    if ob.discussion: ob.open_for_comments()
    self.recatalogNyObject(ob)
    notify(NyContentObjectAddEvent(ob, contributor, schema_raw_data))
    #log post date
    auth_tool = self.getAuthenticationTool()
    auth_tool.changeLastPost(contributor)

    # load default meta_types on meetings (the `use default` logic)
    ob.manageSubobjects(default='default')

    #redirect if case
    if REQUEST is not None:
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'meeting_manage_add' or l_referer.find('meeting_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'meeting_add_html':
            self.setSession('referer', self.absolute_url())
            return ob.object_submitted_message(REQUEST)
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())

    return ob.getId()

def _restrict_meeting_item_view(item):
    permission = Permission(view, (), item)
    # tuple means no inheritance for permission
    permission.setRoles((OBSERVER_ROLE, WAITING_ROLE, PARTICIPANT_ROLE,
                         ADMINISTRATOR_ROLE, MANAGER_ROLE, OWNER_ROLE))

def _unrestrict_meeting_item_view(item):
    permission = Permission(view, (), item)
    permission.setRoles([])

def on_added_meeting_item(ob, event):
    """ Catch event to restrict view permission for meeting items """
    parent = ob.aq_inner.aq_parent
    if parent.meta_type == NyMeeting.meta_type:
        if getattr(parent, 'restrict_items', True):
            _restrict_meeting_item_view(ob)

class NyMeeting(NyContentData, NyFolder):
    """ """

    implements(INyMeeting)

    meta_type = config['meta_type']
    meta_label = config['label']
    icon = 'misc_/NaayaContent/NyMeeting.gif'
    icon_marked = 'misc_/NaayaContent/NyMeeting_marked.gif'

    attendees_icon = 'misc_/NaayaContent/Attendees.jpg'
    email_icon = 'misc_/NaayaContent/Email.jpg'
    icalendar_icon = 'misc_/NaayaContent/iCalendar.jpg'

    agenda_icon = 'misc_/NaayaContent/Agenda.png'
    minutes_icon = 'misc_/NaayaContent/Minutes.png'
    survey_icon = 'misc_/NaayaContent/survey.gif'

    default_form_id = 'meeting_index'
    is_eionet_meeting = False

    manage_options = NyFolder.manage_options

    security = ClassSecurityInfo()

    __allow_groups__ = SignupUsersTool()
    __ac_roles__ = (PARTICIPANT_ROLE, WAITING_ROLE)

    def __init__(self, id, contributor):
        """ """
        NyFolder.__dict__['__init__'](self, id, contributor)
        self.participants = Participants('participants')
        self.email_sender = EmailSender('email_sender')
        self.survey_required = False
        self.allow_register = True
        self.restrict_items = True
        self.is_eionet_meeting = False

    security.declareProtected(view, 'getParticipants')
    def getParticipants(self):
        return self.participants

    security.declareProtected(PERMISSION_ADMIN_MEETING, 'getEmailSender')
    def getEmailSender(self):
        return self.email_sender

    security.declarePrivate('objectkeywords')
    def objectkeywords(self, lang):
        return u' '.join([self._objectkeywords(lang), self.geo_address()])

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        return 'location="%s" start_date="%s" end_date="%s" max_participants="%s" agenda_pointer="%s" minutes_pointer="%s" survey_pointer="%s" contact_person="%s" contact_email="%s"' % \
            (
                self.utXmlEncode(self.geo_address()),
                self.utXmlEncode(self.utNoneToEmpty(self.interval.start_date)),
                self.utXmlEncode(self.utNoneToEmpty(self.interval.end_date)),
                self.utXmlEncode(self.max_participants),
                self.utXmlEncode(self.agenda_pointer),
                self.utXmlEncode(self.minutes_pointer),
                self.utXmlEncode(self.survey_pointer),
                self.utXmlEncode(self.contact_person),
                self.utXmlEncode(self.contact_email),
            )

    security.declarePrivate('export_this_body_custom')
    def export_this_body_custom(self):
        r = []
        return ''.join(r)

    security.declarePrivate('syndicateThis')
    def syndicateThis(self, lang=None):
        l_site = self.getSite()
        if lang is None: lang = self.gl_get_selected_language()
        item = rss_item_for_object(self, lang)
        syndication_tool = self.getSyndicationTool()
        namespaces = syndication_tool.getNamespaceItemsList()
        nsmap = get_nsmap(namespaces)
        dc_namespace = nsmap['dc']
        ev_namespace = nsmap['ev']
        Dc = ElementMaker(namespace=dc_namespace, nsmap=nsmap)
        Ev = ElementMaker(namespace=ev_namespace, nsmap=nsmap)
        the_rest = Dc.root(
            Dc.type('Meeting'),
            Dc.format('text'),
            Dc.source(l_site.getLocalProperty('publisher', lang)),
            Dc.creator(l_site.getLocalProperty('creator', lang)),
            Dc.publisher(l_site.getLocalProperty('publisher', lang)),
            Ev.startdate(self.utShowFullDateTimeHTML(self.interval.start_date)),
            Ev.enddate(self.utShowFullDateTimeHTML(self.interval.end_date)),
            Ev.location(self.geo_address()),
            Ev.organizer(self.contact_person),
            Ev.type('Meeting')
            )
        item.extend(the_rest)
        return etree.tostring(item, xml_declaration=False, encoding="utf-8")

    def _check_meeting_dates(self, form_errors):
        _startdate = getattr(self, 'interval.start_date', '')
        _enddate = getattr(self, 'interval.end_date', '')
        if _startdate and _enddate:
            if _startdate > _enddate:
                form_errors.setdefault('interval.start_date', [])
                form_errors['interval.start_date'].append('The start date should be before the end date')
                form_errors.setdefault('interval.end_date', [])
                form_errors['interval.end_date'].append('The start date should be before the end date')

    def _check_meeting_pointers(self, form_errors):
        if getattr(self, 'agenda_pointer', ''):
            try:
                self.unrestrictedTraverse(str(self.agenda_pointer))
            except KeyError:
                form_errors.setdefault('agenda_pointer', [])
                form_errors['agenda_pointer'].append(
                        'No object at the selected path')
        if getattr(self, 'survey_pointer', ''):
            try:
                self.unrestrictedTraverse(str(self.survey_pointer))
            except KeyError:
                form_errors.setdefault('survey_pointer', [])
                form_errors['survey_pointer'].append(
                        'No object at the selected path')
        if getattr(self, 'minutes_pointer', ''):
            try:
                self.unrestrictedTraverse(str(self.minutes_pointer))
            except KeyError:
                form_errors.setdefault('minutes_pointer', [])
                form_errors['minutes_pointer'].append(
                        'No object at the selected path')

    security.declarePrivate('meeting_submitted_form')
    def meeting_submitted_form(self, REQUEST_form, _lang=None, _all_values=True,
            _override_releasedate=None):
        """
        this shoule be used for the meeting instead of process_submitted_form
        """
        form_errors = super(NyMeeting, self).process_submitted_form(REQUEST_form,
                _lang, _all_values, _override_releasedate)
        self._check_meeting_dates(form_errors) # can modify form_errors
        self._check_meeting_pointers(form_errors) # can modify form_errors

        self._set_items_view_permissions()

        return form_errors

    def _set_items_view_permissions(self):
        if getattr(self, 'restrict_items', True):
            agenda_pointer = str(getattr(self, 'agenda_pointer', ''))
            site = self.getSite()
            for item in self.objectValues():
                if relative_object_path(item, site) == agenda_pointer:
                    _unrestrict_meeting_item_view(item)
                else:
                    _restrict_meeting_item_view(item)
        else:
            for item in self.objectValues():
                _unrestrict_meeting_item_view(item)

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG

        if REQUEST is not None:
            schema_raw_data = dict(REQUEST.form)
        else:
            schema_raw_data = kwargs
        _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
        _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''), self.releasedate)
        _approved = int(bool(schema_raw_data.pop('approved', False)))

        form_errors = self.meeting_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)
        if form_errors:
            raise ValueError(form_errors.popitem()[1]) # pick a random error

        self.custom_index = schema_raw_data.pop('custom_index', '')

        if _approved != self.approved:
            if _approved == 0: _approved_by = None
            else: _approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
            self.approveThis(_approved, _approved_by)

        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    #site actions
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG

        obj = self

        if REQUEST is not None:
            schema_raw_data = dict(REQUEST.form)
        else:
            schema_raw_data = kwargs
        _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
        _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''), obj.releasedate)

        form_errors = self.meeting_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

        if not form_errors:
            self._p_changed = 1
            self.recatalogNyObject(self)
            #log date
            if schema_raw_data.get('is_eionet_meeting'):
                survey_ids = [survey.getId() for survey in
                                        self.objectValues('Naaya Mega Survey')]
                if EIONET_SURVEY_ID not in survey_ids:
                    _create_eionet_survey(self)
            contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
            auth_tool = self.getAuthenticationTool()
            auth_tool.changeLastPost(contributor)
            notify(NyContentObjectEditEvent(self, contributor))
            if REQUEST:
                self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))
        else:
            if REQUEST is not None:
                self._prepare_error_response(REQUEST, form_errors, schema_raw_data)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))
            else:
                raise ValueError(form_errors.popitem()[1]) # pick a random error

    def checkPermissionParticipateInMeeting(self):
        """ """
        return (self.checkPermission(PERMISSION_PARTICIPATE_IN_MEETING) or
                self.checkPermissionAdminMeeting() or
                self.nfp_for_country())

    def checkPermissionAdminMeeting(self):
        """ """
        return self.checkPermission(PERMISSION_ADMIN_MEETING)

    def checkPermissionChangePermissions(self):
        """ """
        return self.nfp_for_country() or self.checkPermission(change_permissions)

    def isParticipant(self, userid=None):
        """ """
        participants = self.getParticipants()
        return participants.isParticipant(userid)

    def registration_status(self, username=None):
        """ """
        username = username or self.REQUEST.AUTHENTICATED_USER.getUserName()
        participants = self.getParticipants()
        subscriptions = participants.subscriptions._account_subscriptions.itervalues()
        for subscriber in subscriptions:
            if username == subscriber.uid:
                return subscriber.accepted
        attendees = participants._get_attendees()
        attendee_data = attendees.get(username)
        if attendee_data:
            attendee_role = attendee_data['role']
            if attendee_role == 'Meeting Participant':
                return 'accepted'
            elif attendee_role == 'Meeting Waiting List':
                return 'new'
        return None

    security.declareProtected(view, 'get_survey')
    def get_survey(self):
        site = self.getSite()
        path = str(self.survey_pointer)
        return site.unrestrictedTraverse(path, None)

    security.declareProtected(view, 'get_survey_questions')
    def get_survey_questions(self):
        survey = self.get_survey()
        if survey is not None and survey.meta_type == 'Naaya Mega Survey':
            questions = []
            for question in survey.getSortedWidgets():
                questions.append((question.id, question.title))
            return questions

    security.declareProtected(view, 'get_survey_answer')
    def get_survey_answer(self, uid, qid):
        survey = self.get_survey()
        if survey is not None and survey.meta_type == 'Naaya Mega Survey':
            question = getattr(survey, qid, None)
            if question:
                for answer in survey.objectValues('Naaya Survey Answer'):
                    if answer.respondent in [uid, 'signup:'+uid]:
                        try:
                            return question.get_value(getattr(answer.aq_base, qid))
                        except AttributeError:
                            return ''
    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/meeting_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST):
        """ """
        if self.survey_required and (self.registration_status() or
                                     self.isParticipant()):
            survey_ob = self.get_survey()
            if survey_ob is not None and survey_ob.meta_type == 'Naaya Mega Survey':
                answers = survey_ob.getAnswers()
                respondents = [a.respondent for a in answers]
                current_user = REQUEST.AUTHENTICATED_USER.getUserName()
                if current_user not in respondents:
                    REQUEST.RESPONSE.redirect('%s/%s' % (self.getSite().absolute_url(), self.survey_pointer))

        tmpl = self.get_custom_index_template()
        if tmpl is None:
            # no custom_index was configured, or the template is missing
            tmpl = self.getFormsTool()['meeting_index'].aq_base.__of__(self)
        return tmpl(REQUEST)

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'meeting_edit')

    security.declareProtected(view, 'menusubmissions')
    def menusubmissions(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self},
                            'naaya.content.meeting.meeting_menusubmissions')

    security.declareProtected(view, 'get_ics')
    def get_ics(self, REQUEST):
        """ Export this meeting as 'ics' """

        cal = vobject.iCalendar()
        cal.add('prodid').value = '-//European Environment Agency//Naaya//EN'
        cal.add('method').value = 'PUBLISH'
        cal.add('vevent')

        cal.vevent.add('uid').value = self.absolute_url() + '/get_ics'
        cal.vevent.add('url').value = self.absolute_url()
        cal.vevent.add('summary').value = self.title_or_id()
        cal.vevent.add('description').value = html2text(self.description)
        header = ('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN">\n<HTML>\n'
                  '<HEAD>\n<TITLE>' + self.title_or_id() +
                  '</TITLE>\n</HEAD>\n<BODY>\n')
        footer = '\n</BODY>\n</HTML>'
        cal.vevent.add('X-ALT-DESC;FMTTYPE=text/html').value = \
                                            header + self.description + footer
        cal.vevent.add('transp').value = 'OPAQUE'

        modif_time = DT2dt(self.bobobase_modification_time())
        cal.vevent.add('dtstamp').value = modif_time

        interval = getattr(self, 'interval', None)
        if interval is None:
            # old object, backwards compatibility code
            # should run updates.ConvertMeetingDates
            log.warning("%s needs patch to use Interval", self.absolute_url(1))
            cal.vevent.add('dtstart').value = DT2dt(self.start_date).date()
            cal.vevent.add('dtend').value = (DT2dt(self.end_date).date() +
                                             datetime.timedelta(days=1))
        else:
            if interval.all_day:
                cal.vevent.add('dtstart').value = interval.start_date.date()
                cal.vevent.add('dtend').value = (interval.end_date.date() +
                                                 datetime.timedelta(days=1))
            else:
                cal.vevent.add('dtstart').value = interval.start_date
                cal.vevent.add('dtend').value = interval.end_date

        loc = []
        if getattr(self, 'location', False):
            loc.append(self.location)
        if self.geo_address():
            loc.append(self.geo_address())

        if loc:
            cal.vevent.add('location').value = ', '.join(loc)

        ics_data = cal.serialize()

        REQUEST.RESPONSE.setHeader('Content-Type', 'text/calendar')
        REQUEST.RESPONSE.setHeader('Content-Disposition',
                           'attachment;filename=%s.ics' % self.getId())
        REQUEST.RESPONSE.write(ics_data)

    security.declareProtected(view, 'nfp_for_country')
    def nfp_for_country(self):
        """ """
        #if we are not in an Eionet meeting, NFP don't get special treatment
        if not self.is_eionet_meeting:
            return ''
        auth_tool = self.getAuthenticationTool()
        user_id = self.REQUEST.AUTHENTICATED_USER.getId()
        if user_id:
            ldap_groups = auth_tool.get_ldap_user_groups(user_id)
            for group in ldap_groups:
                if 'eionet-nfp-cc-' in group[0]:
                    return group[0].replace('eionet-nfp-cc-', '')
                if 'eionet-nfp-mc-'  in group[0]:
                    return group[0].replace('eionet-nfp-mc-', '')

    security.declareProtected(view, 'get_country')
    def get_country(self, country_code):
        """ """
        if country_code is None:
            return '-'
        return country_from_country_code.get(country_code, country_code)

    security.declareProtected(view, 'is_signup')
    def is_signup(self):
        """ """
        username = self.REQUEST.AUTHENTICATED_USER.getUserName()
        key = username.replace('signup:', '')
        return self.participants.getSubscriptions()._is_signup(key)

    ### Compatibility code

    security.declarePublic('start_date')
    @property
    def start_date(self):
        d = self.interval.start_date
        return DateTime(d.year, d.month, d.day)

    security.declarePublic('start_date')
    @property
    def end_date(self):
        d = self.interval.end_date
        return DateTime(d.year, d.month, d.day)

InitializeClass(NyMeeting)

manage_addNyMeeting_html = PageTemplateFile('zpt/meeting_manage_add', globals())
manage_addNyMeeting_html.kind = config['meta_type']
manage_addNyMeeting_html.action = 'addNyMeeting'

#Custom page templates
NaayaPageTemplateFile('zpt/meeting_menusubmissions', globals(),
        'naaya.content.meeting.meeting_menusubmissions')

config.update({
    'on_install': meeting_on_install,
    'constructors': (manage_addNyMeeting_html, addNyMeeting),
    'folder_constructors': [
            # NyFolder.manage_addNyMeeting_html = manage_addNyMeeting_html
            ('manage_addNyMeeting', manage_addNyMeeting_html),
            ('meeting_add_html', meeting_add_html),
            ('addNyMeeting', addNyMeeting),
        ],
    'add_method': addNyMeeting,
    'validation': issubclass(NyMeeting, NyValidation),
    '_class': NyMeeting,
})

def get_config():
    return config

from eionet_survey.eionet_survey import (EIONET_SURVEY_ID, EIONET_SURVEY_TITLE,
                           EIONET_SURVEY_QUESTIONS)
def _create_eionet_survey(container):
    manage_addMegaSurvey(container, EIONET_SURVEY_ID, EIONET_SURVEY_TITLE)
    eionet_survey = container._getOb(EIONET_SURVEY_ID)
    eionet_survey.meeting_eionet_survey = True
    eionet_survey.allow_anonymous = 1
    eionet_survey._p_changed = True
    for question in EIONET_SURVEY_QUESTIONS:
        eionet_survey.addWidget(**question)
    for widget in eionet_survey.objectValues():
        widget.locked = True
        widget._p_changed = True
    #Create validation_html and validation_onsubmit for custom validation
    validation_onsubmit = os.path.join(os.path.dirname(__file__), 'eionet_survey',
                         'validation_onsubmit.txt')
    manage_addPythonScript(eionet_survey, 'validation_onsubmit')
    script_content = open(validation_onsubmit, 'rb').read()
    params = 'datamodel, errors'
    script_title = 'Custom validation logic'
    eionet_survey._getOb('validation_onsubmit').ZPythonScript_edit(params, script_content)
    eionet_survey._getOb('validation_onsubmit').ZPythonScript_setTitle(script_title)
    validation_html = os.path.join(os.path.dirname(__file__), 'eionet_survey',
                         'validation_html.txt')
    validation_title = "Custom questionnaire HTML"
    manage_addPageTemplate(eionet_survey, 'validation_html', validation_title,
                           open(validation_html).read())



class MeetingPublishTraverse(DefaultPublishTraverse):

    def handle_approve(self, request):
        owner = self.context.getObjectOwner() or self.context.contributor
        self.context.inherit_view_permission()
        self.context.approveThis(True, owner, _send_notifications=False)

    def handle_unapprove(self, request):
        owner = self.context.getObjectOwner() or self.context.contributor
        self.context.approveThis(False, owner, _send_notifications=False)
        sm = getSecurityManager()
        newSecurityManager(request, SpecialUsers.system)
        self.context.dont_inherit_view_permission()
        setSecurityManager(sm)

    def publishTraverse(self, request, name):
        approved = getattr(self.context, 'approved', False)
        releasedate = getattr(self.context, 'releasedate', None)

        if releasedate:
            now = DateTime()
            # appropriate action if context is approved
            if now > releasedate and approved:
                pass
            elif now > releasedate and not approved:
                self.handle_approve(request)
            elif now < releasedate and approved:
                self.handle_unapprove(request)
            elif now < releasedate and not approved:
                pass

        return super(MeetingPublishTraverse, self).publishTraverse(request, name)

def handle_meeting_add(event):
    obj = event.context
    if not obj.meta_type == config['meta_type']:
        return
    now = DateTime()
    if getattr(event.context, 'releasedate') and event.context.releasedate > now:
        event.context.approveThis(False, _send_notifications=False)
        obj.dont_inherit_view_permission()
