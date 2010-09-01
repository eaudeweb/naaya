#Python imports
from copy import deepcopy
import os
import sys
import datetime
import vobject

#Zope imports
from Globals import InitializeClass
from App.ImageFile import ImageFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view, change_permissions
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zope.event import notify
from naaya.content.base.events import NyContentObjectAddEvent
from naaya.content.base.events import NyContentObjectEditEvent
from zope.interface import implements
import zLOG
from AccessControl.Permission import Permission

#Naaya imports
from Products.Naaya.NyFolder import NyFolder
from Products.NaayaBase.NyContentType import NyContentType, NY_CONTENT_BASE_SCHEMA
from naaya.content.base.constants import *
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyContentType import NyContentData
from Products.NaayaCore.managers.utils import make_id
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from naaya.core.zope2util import DT2dt
from interfaces import INyMeeting
from Products.Naaya.NySite import NySite

#Meeting imports
from naaya.content.meeting import WAITING_ROLE, PARTICIPANT_ROLE, ADMINISTRATOR_ROLE
from naaya.content.meeting import PERMISSION_PARTICIPATE_IN_MEETING, PERMISSION_ADMIN_MEETING
from participants import Participants
from email import EmailSender, configureEmailNotifications
from reports import MeetingReports
from subscriptions import SignupUsersTool

#module constants
DEFAULT_SCHEMA = {
    'start_date':           dict(sortorder=130, widget_type='Date',     label='Start date', data_type='date', required=True),
    'end_date':             dict(sortorder=140, widget_type='Date',     label='End date', data_type='date'),
    'location':             dict(sortorder=143, widget_type='String',   label='Organization/Building/Room'),
    'time':                 dict(sortorder=146, widget_type='String',   label='Time'),
    'max_participants':     dict(sortorder=150, widget_type='String',   label='Maximum number of participants', data_type='int'),
    'contact_person':       dict(sortorder=150, widget_type='String',   label='Contact person'),
    'contact_email':        dict(sortorder=160, widget_type='String',   label='Contact email', required=True),
    'survey_pointer':       dict(sortorder=230, widget_type='Pointer',  label='Link to the Meeting Survey', relative=True),
    'survey_required':      dict(sortorder=240, widget_type='Checkbox', label='Survey Required', data_type='bool'),
    'agenda_pointer':       dict(sortorder=310, widget_type='Pointer',  label='Link to the Meeting Agenda', relative=True),
    'minutes_pointer':      dict(sortorder=320, widget_type='Pointer',  label='Link to the Meeting Minutes', relative=True),
}
DEFAULT_SCHEMA.update(deepcopy(NY_CONTENT_BASE_SCHEMA))
DEFAULT_SCHEMA['geo_location'].update(visible=True, required=True)
DEFAULT_SCHEMA['geo_type'].update(visible=True)
DEFAULT_SCHEMA['coverage'].update(visible=False)

# this dictionary is updated at the end of the module
config = {
        'product': 'NaayaContent',
        'module': 'meeting',
        'package_path': os.path.abspath(os.path.dirname(__file__)),
        'meta_type': 'Naaya Meeting',
        'label': 'Meeting',
        'permission': 'Naaya - Add Naaya Meeting objects',
        'forms': ['meeting_add', 'meeting_edit', 'meeting_index'],
        'add_form': 'meeting_add_html',
        'description': 'This is Naaya Meeting type.',
        'default_schema': DEFAULT_SCHEMA,
        'schema_name': 'NyMeeting',
        '_module': sys.modules[__name__],
        'additional_style': None,
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
            },
    }

#add meeting reports to NySite
NySite.meeting_reports = MeetingReports('meeting_reports')

def meeting_on_install(site):
    """ """
    auth_tool = site.getAuthenticationTool()

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

def _check_meeting_dates(self, form_errors):
    _startdate = getattr(self, 'start_date', '')
    _enddate = getattr(self, 'end_date', '')
    if _startdate and _enddate:
        if _startdate > _enddate:
            if 'start_date' not in form_errors:
                form_errors['start_date'] = []
            if 'end_date' not in form_errors:
                form_errors['end_date'] = []
            form_errors['start_date'].append('The start date should be before the end date')
            form_errors['end_date'].append('The start date should be before the end date')

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

    form_errors = ob.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)
    _check_meeting_dates(ob, form_errors)

    #check Captcha/reCaptcha
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

    if self.glCheckPermissionPublishObjects():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    ob.approveThis(approved, approved_by)
    ob.submitThis()

    # add change permission to administrator
    permission = Permission(change_permissions, (), ob)
    permission.setRoles([ADMINISTRATOR_ROLE])
    permission = Permission(PERMISSION_PARTICIPATE_IN_MEETING, (), ob)
    permission.setRoles([WAITING_ROLE, PARTICIPANT_ROLE, ADMINISTRATOR_ROLE])
    permission = Permission(PERMISSION_ADMIN_MEETING, (), ob)
    permission.setRoles([ADMINISTRATOR_ROLE])

    if ob.discussion: ob.open_for_comments()
    self.recatalogNyObject(ob)
    notify(NyContentObjectAddEvent(ob, contributor, schema_raw_data))
    #log post date
    auth_tool = self.getAuthenticationTool()
    auth_tool.changeLastPost(contributor)

    subobjects = ob.get_meta_types(1)
    default_subobjects = ['Naaya Folder', 'Naaya File', 'Naaya URL', 'Naaya Document', 'Naaya Forum', 'Naaya Mega Survey', 'Naaya Media File', 'Naaya Contact']
    subobjects = list(set(subobjects) & set(default_subobjects))
    ob.manageSubobjects(ny_subobjects=subobjects)

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

    security.declareProtected(PERMISSION_ADMIN_MEETING, 'getParticipants')
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
                self.utXmlEncode(self.utNoneToEmpty(self.start_date)),
                self.utXmlEncode(self.utNoneToEmpty(self.end_date)),
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
        r = []
        ra = r.append
        ra(self.syndicateThisHeader())
        ra(self.syndicateThisCommon(lang))
        ra('<dc:type>Meeting</dc:type>')
        ra('<dc:format>text</dc:format>')
        ra('<dc:source>%s</dc:source>' % self.utXmlEncode(l_site.getLocalProperty('publisher', lang)))
        ra('<dc:creator>%s</dc:creator>' % self.utXmlEncode(l_site.getLocalProperty('creator', lang)))
        ra('<dc:publisher>%s</dc:publisher>' % self.utXmlEncode(l_site.getLocalProperty('publisher', lang)))
        ra('<ev:startdate>%s</ev:startdate>' % self.utShowFullDateTimeHTML(self.start_date))
        ra('<ev:enddate>%s</ev:enddate>' % self.utShowFullDateTimeHTML(self.end_date))
        ra('<ev:location>%s</ev:location>' % self.utXmlEncode(self.geo_address()))
        ra('<ev:organizer>%s</ev:organizer>' % self.utXmlEncode(self.contact_person))
        ra('<ev:type>Meeting</ev:type>')
        ra(self.syndicateThisFooter())
        return ''.join(r)

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

        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)
        _check_meeting_dates(self, form_errors)
        if form_errors:
            raise ValueError(form_errors.popitem()[1]) # pick a random error

        if _approved != self.approved:
            if _approved == 0: _approved_by = None
            else: _approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
            self.approveThis(_approved, _approved_by)

        self._p_changed = 1
        if self.discussion: self.open_for_comments()
        else: self.close_for_comments()
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

        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)
        _check_meeting_dates(self, form_errors)

        if not form_errors:
            if self.discussion: self.open_for_comments()
            else: self.close_for_comments()
            self._p_changed = 1
            self.recatalogNyObject(self)
            #log date
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
        return self.checkPermission(PERMISSION_PARTICIPATE_IN_MEETING)

    def checkPermissionAdminMeeting(self):
        """ """
        return self.checkPermission(PERMISSION_ADMIN_MEETING)

    def checkPermissionChangePermissions(self):
        """ """
        return self.checkPermission(change_permissions)

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/meeting_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST):
        """ """
        if self.survey_required and self.checkPermissionParticipateInMeeting():
            site = self.getSite()
            path = str(self.survey_pointer)
            survey_ob = site.unrestrictedTraverse(path, None)
            if survey_ob is not None and survey_ob.meta_type == 'Naaya Mega Survey':
                answers = survey_ob.getAnswers()
                respondents = [a.respondent for a in answers]
                current_user = REQUEST.AUTHENTICATED_USER.getUserName()
                if current_user not in respondents:
                    REQUEST.RESPONSE.redirect('%s/%s' % (self.getSite().absolute_url(), self.survey_pointer))

        if self.publicinterface:
            l_index = self._getOb('index', None)
            if l_index is not None: return l_index()
        return self.getFormsTool().getContent({'here': self}, 'meeting_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'meeting_edit')

    security.declareProtected(view, 'menusubmissions')
    def menusubmissions(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self},
                            'naaya.content.meeting.meeting_menusubmissions')

    security.declareProtected(PERMISSION_PARTICIPATE_IN_MEETING, 'get_ics')
    def get_ics(self, REQUEST):
        """ Export this meeting as 'ics' """

        cal = vobject.iCalendar()
        cal.add('prodid').value = '-//European Environment Agency//Naaya//EN'
        cal.add('method').value = 'PUBLISH'
        cal.add('vevent')

        cal.vevent.add('uid').value = self.absolute_url() + '/get_ics'
        cal.vevent.add('url').value = self.absolute_url()
        cal.vevent.add('summary').value = self.title_or_id()
        cal.vevent.add('transp').value = 'OPAQUE'

        modif_time = DT2dt(self.bobobase_modification_time())
        cal.vevent.add('dtstamp').value = modif_time

        cal.vevent.add('dtstart').value = DT2dt(self.start_date).date()
        cal.vevent.add('dtend').value = (DT2dt(self.end_date).date() +
                                         datetime.timedelta(days=1))

        loc = []
        if self.geo_address():
            loc.append(self.geo_address())

        if loc:
            cal.vevent.add('location').value = ', '.join(loc)

        ics_data = cal.serialize()

        REQUEST.RESPONSE.setHeader('Content-Type', 'text/calendar')
        REQUEST.RESPONSE.setHeader('Content-Disposition',
                           'attachment;filename=%s.ics' % self.getId())
        REQUEST.RESPONSE.write(ics_data)

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

