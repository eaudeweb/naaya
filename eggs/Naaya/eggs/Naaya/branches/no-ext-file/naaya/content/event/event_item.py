import os
import sys
import datetime

import vobject

from Globals import InitializeClass
from App.ImageFile import ImageFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Acquisition import Implicit
from zope.event import notify
from naaya.content.base.events import NyContentObjectAddEvent
from naaya.content.base.events import NyContentObjectEditEvent
from zope.interface import implements

from Products.NaayaBase.NyContentType import NyContentType, NY_CONTENT_BASE_SCHEMA
from naaya.content.base.constants import *
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaBase.NyContentType import NyContentData
from Products.NaayaBase.NyBase import rss_item_for_object
from Products.NaayaCore.managers.utils import slugify, uniqueId, get_nsmap
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from naaya.core.zope2util import DT2dt
from naaya.core import submitter
from naaya.core.zope2util import abort_transaction_keep_session

from interfaces import INyEvent
from permissions import PERMISSION_ADD_EVENT

from lxml import etree
from lxml.builder import ElementMaker

#module constants
DEFAULT_SCHEMA = {
    'location':         dict(sortorder=100, widget_type='String',   label='Event location'),
    'location_address': dict(sortorder=110, widget_type='String',   label='Location address'),
    'location_url':     dict(sortorder=120, widget_type='URL',      label='Location URL'),
    'start_date':       dict(sortorder=130, widget_type='Date',     label='Start date', data_type='date', required=True),
    'end_date':         dict(sortorder=140, widget_type='Date',     label='End date', data_type='date'),
    'host':             dict(sortorder=150, widget_type='String',   label='Host'),
    'agenda_url':       dict(sortorder=160, widget_type='URL',      label='Agenda URL'),
    'event_url':        dict(sortorder=170, widget_type='URL',      label='Event URL'),
    'details':          dict(sortorder=180, widget_type='TextArea', label='Details (HTML)', localized=True, tinymce=True),
    'topitem':          dict(sortorder=190, widget_type='Checkbox', label='On front', data_type='int'),
    'event_type':       dict(sortorder=200, widget_type='Select',   label='Type', translation_id='Type (translate as a noun)', list_id='event_types'),
    'contact_person':   dict(sortorder=210, widget_type='String',   label='Contact person'),
    'contact_email':    dict(sortorder=220, widget_type='String',   label='Contact email'),
    'contact_phone':    dict(sortorder=230, widget_type='String',   label='Contact phone'),
    'contact_fax':      dict(sortorder=240, widget_type='String',   label='Contact fax'),
}
DEFAULT_SCHEMA.update(NY_CONTENT_BASE_SCHEMA)

# this dictionary is updated at the end of the module
config = {
        'product': 'NaayaContent',
        'module': 'event_item',
        'package_path': os.path.abspath(os.path.dirname(__file__)),
        'meta_type': 'Naaya Event',
        'label': 'Event',
        'permission': PERMISSION_ADD_EVENT,
        'forms': ['event_add', 'event_edit', 'event_index'],
        'add_form': 'event_add_html',
        'description': 'This is Naaya Event type.',
        'default_schema': DEFAULT_SCHEMA,
        'schema_name': 'NyEvent',
        '_module': sys.modules[__name__],
        'additional_style': None,
        'icon': os.path.join(os.path.dirname(__file__), 'www', 'event.gif'),
        '_misc': {
                'NyEvent.gif': ImageFile('www/event.gif', globals()),
                'NyEvent_marked.gif': ImageFile('www/event_marked.gif', globals()),
            },
    }

def event_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, config['meta_type'])
    return self.getFormsTool().getContent({
        'here': self,
        'kind': config['meta_type'],
        'action': 'addNyEvent',
        'form_helper': form_helper,
        'submitter_info_html': submitter.info_html(self, REQUEST),
    }, 'event_add')

def _create_NyEvent_object(parent, id, contributor):
    id = uniqueId(slugify(id or 'event', removelist=[]),
                  lambda x: parent._getOb(x, None) is not None)
    ob = NyEvent(id, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def addNyEvent(self, id='', REQUEST=None, contributor=None, **kwargs):
    """
    Create an Event type of object.
    """
    if REQUEST is not None:
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs
    _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
    _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''))
    schema_raw_data.setdefault('details', '')
    schema_raw_data.setdefault('resourceurl', '')
    schema_raw_data.setdefault('source', '')
    schema_raw_data.setdefault('topitem', '')

    id = uniqueId(slugify(id or schema_raw_data.get('title', '') or 'event',
                          removelist=[]),
                  lambda x: self._getOb(x, None) is not None)
    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_NyEvent_object(self, id, contributor)

    form_errors = ob.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

    if REQUEST is not None:
        submitter_errors = submitter.info_check(self, REQUEST, ob)
        form_errors.update(submitter_errors)

    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1]) # pick a random error
        else:
            abort_transaction_keep_session(REQUEST)
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            REQUEST.RESPONSE.redirect('%s/event_add_html' % self.absolute_url())
            return

    if self.checkPermissionSkipApproval():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    ob.approveThis(approved, approved_by)
    ob.submitThis()

    self.recatalogNyObject(ob)
    notify(NyContentObjectAddEvent(ob, contributor, schema_raw_data))
    #log post date
    auth_tool = self.getAuthenticationTool()
    auth_tool.changeLastPost(contributor)
    #redirect if case
    if REQUEST is not None:
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'event_manage_add' or l_referer.find('event_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'event_add_html':
            self.setSession('referer', self.absolute_url())
            return ob.object_submitted_message(REQUEST)
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
        else: # undefined state (different referer, called in other context)
            return ob

    return ob.getId()

def importNyEvent(self, param, id, attrs, content, properties, discussion, objects):
    #this method is called during the import process
    try: param = abs(int(param))
    except: param = 0
    if param == 3:
        #just try to delete the object
        try: self.manage_delObjects([id])
        except: pass
    else:
        ob = self._getOb(id, None)
        if param in [0, 1] or (param==2 and ob is None):
            if param == 1:
                #delete the object if exists
                try: self.manage_delObjects([id])
                except: pass

            ob = _create_NyEvent_object(self, id, self.utEmptyToNone(attrs['contributor'].encode('utf-8')))
            ob.sortorder = attrs['sortorder'].encode('utf-8')
            ob.discussion = abs(int(attrs['discussion'].encode('utf-8')))
            ob.location_url = attrs['location_url'].encode('utf-8')
            ob.start_date = self.utConvertDateTimeObjToString(self.utGetDate(attrs['start_date'].encode('utf-8')))
            ob.end_date = self.utConvertDateTimeObjToString(self.utGetDate(attrs['end_date'].encode('utf-8')))
            ob.agenda_url = attrs['agenda_url'].encode('utf-8')
            ob.event_url = attrs['event_url'].encode('utf-8')
            ob.topitem = abs(int(attrs['topitem'].encode('utf-8')))
            ob.event_type = attrs['event_type'].encode('utf-8')
            ob.contact_person = attrs['contact_person'].encode('utf-8')
            ob.contact_email = attrs['contact_email'].encode('utf-8')
            ob.contact_phone = attrs['contact_phone'].encode('utf-8')
            ob.contact_fax = attrs['contact_fax'].encode('utf-8')

            for property, langs in properties.items():
                [ ob._setLocalPropValue(property, lang, langs[lang]) for lang in langs if langs[lang]!='' ]
            ob.approveThis(approved=abs(int(attrs['approved'].encode('utf-8'))),
                approved_by=self.utEmptyToNone(attrs['approved_by'].encode('utf-8')))
            if attrs['releasedate'].encode('utf-8') != '':
                ob.setReleaseDate(attrs['releasedate'].encode('utf-8'))
            ob.import_comments(discussion)
            self.recatalogNyObject(ob)

class event_item(Implicit, NyContentData):
    """ """

class NyEvent(event_item, NyAttributes, NyItem, NyCheckControl, NyContentType):
    """ """

    implements(INyEvent)

    meta_type = config['meta_type']
    meta_label = config['label']
    icon = 'misc_/NaayaContent/NyEvent.gif'
    icon_marked = 'misc_/NaayaContent/NyEvent_marked.gif'

    def manage_options(self):
        """ """
        l_options = ()
        if not self.hasVersion():
            l_options += ({'label': 'Properties', 'action': 'manage_edit_html'},)
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyItem.manage_options
        return l_options

    security = ClassSecurityInfo()

    def __init__(self, id, contributor):
        """ """
        self.id = id
        event_item.__init__(self)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor

    security.declarePrivate('objectkeywords')
    def objectkeywords(self, lang):
        return u' '.join([self._objectkeywords(lang), self.getLocalProperty('details', lang), self.event_type, self.getLocalProperty('location_address', lang), self.getLocalProperty('location', lang)])

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        return 'location_url="%s" start_date="%s" end_date="%s" agenda_url="%s" event_url="%s" topitem="%s" event_type="%s" contact_person="%s" contact_email="%s" contact_phone="%s" contact_fax="%s"' % \
            (self.utXmlEncode(self.location_url),
                self.utXmlEncode(self.utNoneToEmpty(self.start_date)),
                self.utXmlEncode(self.utNoneToEmpty(self.end_date)),
                self.utXmlEncode(self.agenda_url),
                self.utXmlEncode(self.event_url),
                self.utXmlEncode(self.topitem),
                self.utXmlEncode(self.event_type),
                self.utXmlEncode(self.contact_person),
                self.utXmlEncode(self.contact_email),
                self.utXmlEncode(self.contact_phone),
                self.utXmlEncode(self.contact_fax))

    security.declarePrivate('export_this_body_custom')
    def export_this_body_custom(self):
        r = []
        ra = r.append
        for l in self.gl_get_languages():
            ra('<location lang="%s"><![CDATA[%s]]></location>' % (l, self.utToUtf8(self.getLocalProperty('location', l))))
            ra('<location_address lang="%s"><![CDATA[%s]]></location_address>' % (l, self.utToUtf8(self.getLocalProperty('location_address', l))))
            ra('<host lang="%s"><![CDATA[%s]]></host>' % (l, self.utToUtf8(self.getLocalProperty('host', l))))
            ra('<details lang="%s"><![CDATA[%s]]></details>' % (l, self.utToUtf8(self.getLocalProperty('details', l))))
        return ''.join(r)

    security.declarePrivate('syndicateThis')
    def syndicateThis(self, lang=None):
        l_site = self.getSite()
        if lang is None: lang = self.gl_get_selected_language()
        self.getLocalProperty('location')
        item = rss_item_for_object(self, lang)
        syndication_tool = self.getSyndicationTool()
        namespaces = syndication_tool.getNamespaceItemsList()
        nsmap = get_nsmap(namespaces)
        dc_namespace = nsmap['dc']
        ev_namespace = nsmap['ev']
        Dc = ElementMaker(namespace=dc_namespace, nsmap=nsmap)
        Ev = ElementMaker(namespace=ev_namespace, nsmap=nsmap)
        the_rest = Dc.root(
            Dc.type('Event'),
            Dc.format('text'),
            Dc.source(l_site.publisher),
            Dc.creator(l_site.creator),
            Dc.publisher(l_site.publisher),
            Ev.location(self.location),
            Ev.organizer(self.host),
            Ev.type(self.getPortalI18n().get_translation('', self.getEventTypeTitle(self.event_type))),
            Ev.startdate(self.utShowFullDateTimeHTML(self.start_date))
        )
        if self.end_date:
            the_rest.append(Ev.enddate(self.utShowFullDateTimeHTML(self.end_date)))
        item.extend(the_rest)
        return etree.tostring(item, xml_declaration=False, encoding="utf-8")

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
        if form_errors:
            raise ValueError(form_errors.popitem()[1]) # pick a random error

        if _approved != self.approved:
            if _approved == 0: _approved_by = None
            else: _approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
            self.approveThis(_approved, _approved_by)

        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    #site actions
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'commitVersion')
    def commitVersion(self, REQUEST=None):
        """ """
        user = self.REQUEST.AUTHENTICATED_USER.getUserName()
        if (not self.checkPermissionEditObject()) or (
            self.checkout_user != user):
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if not self.hasVersion():
            raise EXCEPTION_NOVERSION, EXCEPTION_NOVERSION_MSG
        self.copy_naaya_properties_from(self.version)
        self.checkout = 0
        self.checkout_user = None
        self.version = None
        self._p_changed = 1
        self.recatalogNyObject(self)
        notify(NyContentObjectEditEvent(self, user))
        if REQUEST: REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'startVersion')
    def startVersion(self, REQUEST=None):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if self.hasVersion():
            raise EXCEPTION_STARTEDVERSION, EXCEPTION_STARTEDVERSION_MSG
        self.checkout = 1
        self.checkout_user = self.REQUEST.AUTHENTICATED_USER.getUserName()
        self.version = event_item()
        self.version.copy_naaya_properties_from(self)
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG

        if self.hasVersion():
            obj = self.version
            if self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName():
                raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        else:
            obj = self

        if REQUEST is not None:
            schema_raw_data = dict(REQUEST.form)
        else:
            schema_raw_data = kwargs
        _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
        _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''), obj.releasedate)

        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

        if not form_errors:
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

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'change_topitem_status')
    def change_topitem_status(self, REQUEST=None):
        """ show/hide event on the front page """
        if self.topitem:
            self.topitem = False
        else:
            self.topitem = True

        self.recatalogNyObject(self)

        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/event_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'event_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        if self.hasVersion():
            obj = self.version
        else:
            obj = self
        return self.getFormsTool().getContent({'here': obj}, 'event_edit')

    def get_ics(self, REQUEST, RESPONSE):
        """ Export this event as 'ics' """

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

        if self.start_date is not None:
            cal.vevent.add('dtstart').value = DT2dt(self.start_date).date()
        if self.end_date is not None:
            cal.vevent.add('dtend').value = (DT2dt(self.end_date).date() +
                                             datetime.timedelta(days=1))

        loc = []
        if self.location:
            loc.append(self.location)
        if self.location_address:
            loc.append(self.location_address)
        if self.location_url:
            loc.append(self.location_url)

        if loc:
            cal.vevent.add('location').value = ', '.join(loc)

        ics_data = cal.serialize()

        #RESPONSE.setHeader('Content-Type', 'text/plain')
        RESPONSE.setHeader('Content-Type', 'text/calendar')
        RESPONSE.setHeader('Content-Disposition',
                           'attachment;filename=%s.ics' % self.getId())
        RESPONSE.write(ics_data)

InitializeClass(NyEvent)

manage_addNyEvent_html = PageTemplateFile('zpt/event_manage_add', globals())
manage_addNyEvent_html.kind = config['meta_type']
manage_addNyEvent_html.action = 'addNyEvent'

#Custom folder index for events
NaayaPageTemplateFile('zpt/event_folder_index', globals(), 'event_folder_index')

config.update({
    'constructors': (manage_addNyEvent_html, addNyEvent),
    'folder_constructors': [
            # NyFolder.manage_addNyEvent_html = manage_addNyEvent_html
            ('manage_addNyEvent_html', manage_addNyEvent_html),
            ('event_add_html', event_add_html),
            ('addNyEvent', addNyEvent),
            ('import_event_item', importNyEvent),
        ],
    'add_method': addNyEvent,
    'validation': issubclass(NyEvent, NyValidation),
    '_class': NyEvent,
})

def get_config():
    return config
