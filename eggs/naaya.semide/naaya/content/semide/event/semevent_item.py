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
# The Initial Owner of the Original Code is EMWIS/SEMIDE.
# Code created by Finsiel Romania are
# Copyright (C) EMWIS/SEMIDE. All Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

#Python
import os
import sys
from copy import deepcopy

#Zope
from Acquisition import Implicit
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from App.ImageFile import ImageFile
from OFS.Image import cookId
from DateTime import DateTime
import zope.event

#Naaya
from naaya.content.base.constants import MUST_BE_NONEMPTY, MUST_BE_POSITIV_INT, MUST_BE_DATETIME
from Products.NaayaBase.constants import (PERMISSION_EDIT_OBJECTS, EXCEPTION_NOTAUTHORIZED,
EXCEPTION_NOTAUTHORIZED_MSG, EXCEPTION_NOVERSION, EXCEPTION_NOVERSION_MSG,
EXCEPTION_STARTEDVERSION_MSG, MESSAGE_SAVEDCHANGES, EXCEPTION_STARTEDVERSION)

from Products.Naaya.NyFolder import addNyFolder
from Products.NaayaCore.managers.utils import make_id, get_nsmap
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyFSContainer import NyFSContainer
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaBase.NyContentType import NyContentType, NyContentData, NY_CONTENT_BASE_SCHEMA
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyBase import rss_item_for_object
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from Products.Naaya.adapters import FolderMetaTypes

from naaya.content.base.events import NyContentObjectAddEvent
from naaya.content.base.events import NyContentObjectEditEvent
from naaya.core import submitter

from lxml import etree
from lxml.builder import ElementMaker

#module constants
METATYPE_OBJECT = 'Naaya Semide Event'
LABEL_OBJECT = 'Event'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya Semide Event objects'
OBJECT_FORMS = ['semevent_add', 'semevent_edit', 'semevent_index']
OBJECT_CONSTRUCTORS = ['manage_addNySemEvent_html', 'semevent_add_html', 'addNySemEvent', 'importNySemEvent']
OBJECT_ADD_FORM = 'semevent_add_html'
DESCRIPTION_OBJECT = 'This is Naaya Semide Event type.'
PREFIX_OBJECT = 'sev'
PROPERTIES_OBJECT = {
    'id':               (0, '', ''),
    'title':            (1, MUST_BE_NONEMPTY, 'The Title field must have a value.'),
    'description':      (0, '', ''),
    'coverage':         (1, MUST_BE_NONEMPTY, 'The Geographical coverage field must have a value.'),
    'keywords':         (0, '', ''),
    'sortorder':        (0, MUST_BE_POSITIV_INT, 'The Sort order field must contain a positive integer.'),
    'releasedate':      (0, MUST_BE_DATETIME, 'The Release date field must contain a valid date.'),
    'discussion':       (0, '', ''),
    'creator':          (0, '', ''),
    'creator_email':    (0, '', ''),
    'topitem':          (0, '', ''),
    'event_type':       (0, '', ''),
    'source':           (0, '', ''),
    'source_link':      (0, '', ''),
    'file_link':        (0, '', ''),
    'file_link_copy':   (0, '', ''),
    'subject':          (0, '', ''),
    'relation':         (0, '', ''),
    'organizer':        (0, '', ''),
    'duration':         (0, '', ''),
    'geozone':          (0, '', ''),
    'address':          (0, '', ''),
    'start_date':       (0, '', ''),
    'end_date':         (0, '', ''),
    'event_status':     (0, '', ''),
    'contact_person':   (0, '', ''),
    'contact_email':    (0, '', ''),
    'contact_phone':    (0, '', ''),
    'working_langs':    (0, '', ''),
    'lang':             (0, '', ''),
    'file':             (0, '', ''),
}

DEFAULT_SCHEMA = deepcopy(NY_CONTENT_BASE_SCHEMA)
DEFAULT_SCHEMA.update({
    'start_date':       dict(sortorder=100, widget_type="Date", data_type="date", label="Start date", required = True),
    'end_date':         dict(sortorder=110, widget_type="Date", data_type="date", label="End Date"),
    'duration':         dict(sortorder=120, widget_type="String", localized = True, label="Duration"),
    'organizer':        dict(sortorder=130, widget_type="String", localized = True, label="Organizer"),
    'address':          dict(sortorder=140, widget_type="String", localized = True, label="Address"),
    'geozone':          dict(sortorder=150, widget_type="Select", label="Geozone", list_id='event_geozone'),
    'event_type':       dict(sortorder=160, widget_type="Select", label="Type", list_id='event_types'),
    'subject':          dict(sortorder=170, widget_type="SelectMultiple", label="Subject"),
    'source':           dict(sortorder=180, widget_type="String", localized = True, label="Source"),
    'source_link':      dict(sortorder=190, widget_type="String", label="Source link"),
    'creator':          dict(sortorder=200, widget_type="String", label="Creator", visible=False, default=''),
    'creator_email':    dict(sortorder=210, widget_type="String", label="Creator e-mail", visible=False, default=''),
    'contact_person':   dict(sortorder=220, widget_type="String", localized = True, label="Contact name"),
    'contact_email':    dict(sortorder=230, widget_type="String", label="Contact e-mail"),
    'contact_phone':    dict(sortorder=240, widget_type="String", label="Contact phone"),
    'topitem':          dict(sortorder=250, widget_type="Checkbox", label="Is hot"),
    'relation':         dict(sortorder=250, widget_type="String", label="Relation"),
    'working_langs':    dict(sortorder=260, widget_type="SelectMultiple", label="Working langs"),
    'event_status':     dict(sortorder=270, widget_type="Select", label="Status", list_id='event_status'),
    'file_link':        dict(sortorder=280, widget_type="String", localized = True, label="File link", default='http://'),
})
DEFAULT_SCHEMA['sortorder'].update(visible=False)
DEFAULT_SCHEMA['releasedate'].update(visible=False)

config = {
    'product': 'NaayaContent',
    'module': 'NySemEvent',
    'package_path': os.path.abspath(os.path.dirname(__file__)),
    'meta_type': METATYPE_OBJECT,
    'label': LABEL_OBJECT,
    'permission': PERMISSION_ADD_OBJECT,
    'forms': OBJECT_FORMS,
    'add_form': OBJECT_ADD_FORM,
    'description': DESCRIPTION_OBJECT,
    'default_schema': DEFAULT_SCHEMA,
    'properties': PROPERTIES_OBJECT,
    'schema_name': 'NySemEvent',
    '_module': sys.modules[__name__],
    'icon': os.path.join(os.path.dirname(__file__), 'www', 'NySemEvent.gif'),
    '_misc': {
            'NySemEvent.gif': ImageFile('www/NySemEvent.gif', globals()),
            'NySemEvent_marked.gif': ImageFile('www/NySemEvent_marked.gif', globals()),
        },
}

manage_addNySemEvent_html = PageTemplateFile('zpt/semevent_manage_add', globals())
manage_addNySemEvent_html.kind = METATYPE_OBJECT
manage_addNySemEvent_html.action = 'addNySemEvent'

def semevent_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, config['meta_type'])
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNySemEvent', 'form_helper': form_helper}, 'semevent_add')

def _create_NySemEvent_object(parent, id, contributor):
    id = make_id(parent, id=id, prefix=PREFIX_OBJECT)
    ob = NySemEvent(id, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def create_month_folder(self, contributor, schema_raw_data):
    #Creating archive folder
    start_date = self.utConvertStringToDateTimeObj(schema_raw_data.get('start_date', None))
    start_date_year = str(start_date.year())
    start_date_month = start_date.mm()

    year_folder = self._getOb(start_date_year, None)
    if year_folder is None:
        year_folder = self._getOb(addNyFolder(self, start_date_year,
            contributor=contributor, title="Events for %s" % start_date_year))

    month_folder = year_folder._getOb(start_date_month, None)
    if month_folder is None:
        month_folder = year_folder._getOb(addNyFolder(year_folder, start_date_month,
                        contributor=contributor,
                        title="Events for %s/%s" %
                        (start_date_year, start_date_month)))
    FolderMetaTypes(month_folder).add(config['meta_type'])
    return month_folder

def addNySemEvent(self, id='', REQUEST=None, contributor=None, **kwargs):
    """ """
    if REQUEST is not None:
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs

    #process parameters
    id = make_id(self, id=id, title=schema_raw_data.get('title', ''), prefix=PREFIX_OBJECT)
    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
    _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''))

    #Creating archive folder
    if schema_raw_data.get('archive'):
        try:
            month_folder = create_month_folder(self, contributor, schema_raw_data)
        except:
            month_folder = self
    else:
        month_folder = self

    ob = _create_NySemEvent_object(month_folder, id, contributor)
    form_errors = ob.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

    if REQUEST is not None:
        submitter_errors = submitter.info_check(self, REQUEST, ob)
        form_errors.update(submitter_errors)

    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1]) # pick a random error
        else:
            import transaction; transaction.abort() # because we already called _crete_NyZzz_object
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            return REQUEST.RESPONSE.redirect('%s/semevent_add_html' % self.absolute_url())

    ob.start_date = self.utConvertStringToDateTimeObj(schema_raw_data.get('start_date', None))
    ob.end_date = self.utConvertStringToDateTimeObj(schema_raw_data.get('end_date', None))

    if 'file' in schema_raw_data:
        ob.handleUpload(schema_raw_data['file'])

    if self.glCheckPermissionPublishObjects():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    ob.approveThis(approved, approved_by)
    ob.submitThis()
    ob.updatePropertiesFromGlossary(_lang)

    if ob.discussion: ob.open_for_comments()
    self.recatalogNyObject(ob)
    zope.event.notify(NyContentObjectAddEvent(ob, contributor, schema_raw_data))

    #log post date
    auth_tool = self.getAuthenticationTool()
    auth_tool.changeLastPost(contributor)
    #redirect if case
    if REQUEST is not None:
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'semevent_manage_add' or l_referer.find('semevent_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif 'semevent_add_html' in l_referer:
            self.setSession('referer', self.absolute_url())
            response = ob.object_submitted_message(REQUEST)
            if schema_raw_data.get('archive'):
                response = REQUEST.RESPONSE.redirect(self.absolute_url())
            return response
    return ob.getId()

def importNySemEvent(self, param, id, attrs, content, properties, discussion, objects):
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
            #Creating object and setting all object properties (taken from Schema)
            ob = _create_NySemEvent_object(self, id, self.utEmptyToNone(attrs['contributor'].encode('utf-8')))
            for prop in ob._get_schema().listPropNames():
                setattr(ob, prop, '')
            for k, v  in attrs.items():
                setattr(ob, k, v.encode('utf-8'))
            # Upload file
            if objects:
                obj = objects[0]
                data=self.utBase64Decode(obj.attrs['file'].encode('utf-8'))
                ctype = obj.attrs['content_type'].encode('utf-8')
                name = obj.attrs['name'].encode('utf-8')
                try:
                    size = int(obj.attrs['size'])
                except (TypeError, ValueError):
                    size = 0
                ob.update_data(data, ctype, size, name)
            # Update properties
            for property, langs in properties.items():
                [ ob._setLocalPropValue(property, lang, langs[lang]) for lang in langs if langs[lang]!='' ]
            ob.approveThis(approved=abs(int(attrs['approved'].encode('utf-8'))),
                approved_by=self.utEmptyToNone(attrs['approved_by'].encode('utf-8')))
            if attrs['releasedate'].encode('utf-8') != '':
                ob.setReleaseDate(attrs['releasedate'].encode('utf-8'))
            ob.import_comments(discussion)
            self.recatalogNyObject(ob)

class semevent_item(Implicit, NyContentData, NyFSContainer):
    """ """
    meta_type = METATYPE_OBJECT
class NySemEvent(semevent_item, NyAttributes, NyItem, NyCheckControl, NyContentType, NyValidation):
    """ """
    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT
    icon = 'misc_/NaayaContent/NySemEvent.gif'
    icon_marked = 'misc_/NaayaContent/NySemEvent_marked.gif'

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
        semevent_item.__init__(self)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor

    security.declareProtected(view, 'resource_type')
    def resource_type(self):
        return getattr(self, 'event_type', None)

    security.declareProtected(view, 'resource_status')
    def resource_status(self):
        return getattr(self, 'event_status', None)

    security.declareProtected(view, 'resource_date')
    def resource_date(self):
        return DateTime(getattr(self, 'start_date', None))

    security.declareProtected(view, 'resource_end_date')
    def resource_end_date(self):
        return DateTime(getattr(self, 'end_date', None)) or self.resource_date()

    security.declareProtected(view, 'resource_subject')
    def resource_subject(self):
        return ' '.join(getattr(self, 'subject', []))

    security.declarePrivate('objectkeywords')
    def objectkeywords(self, lang):
        return u' '.join([self._objectkeywords(lang), self.getLocalProperty('details', lang)])

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        return 'creator="%s" creator_email="%s" topitem="%s" event_type="%s" source_link="%s" contact_email="%s" contact_phone="%s" subject="%s" relation="%s" geozone="%s" start_date="%s" end_date="%s" event_status="%s" working_langs="%s"' % \
            (self.utXmlEncode(self.creator),
                self.utXmlEncode(self.creator_email),
                self.utXmlEncode(self.topitem),
                self.utXmlEncode(self.event_type),
                self.utXmlEncode(self.source_link),
                self.utXmlEncode(self.contact_email),
                self.utXmlEncode(self.contact_phone),
                self.utXmlEncode(self.subject),
                self.utXmlEncode(self.relation),
                self.utXmlEncode(self.geozone),
                self.utXmlEncode(self.utNoneToEmpty(self.start_date)),
                self.utXmlEncode(self.utNoneToEmpty(self.end_date)),
                self.utXmlEncode(self.event_status),
                self.utXmlEncode(self.working_langs))

    security.declarePrivate('export_this_body_custom')
    def export_this_body_custom(self):
        r = []
        ra = r.append
        for l in self.gl_get_languages():
            ra('<source lang="%s"><![CDATA[%s]]></source>' % (l, self.utToUtf8(self.getLocalProperty('source', l))))
            ra('<file_link lang="%s"><![CDATA[%s]]></file_link>' % (l, self.utToUtf8(self.getLocalProperty('file_link', l))))
            ra('<file_link_copy lang="%s"><![CDATA[%s]]></file_link_copy>' % (l, self.utToUtf8(self.getLocalProperty('file_link_copy', l))))
            ra('<organizer lang="%s"><![CDATA[%s]]></organizer>' % (l, self.utToUtf8(self.getLocalProperty('organizer', l))))
            ra('<duration lang="%s"><![CDATA[%s]]></duration>' % (l, self.utToUtf8(self.getLocalProperty('duration', l))))
            ra('<address lang="%s"><![CDATA[%s]]></address>' % (l, self.utToUtf8(self.getLocalProperty('address', l))))
            ra('<contact_person lang="%s"><![CDATA[%s]]></contact_person>' % (l, self.utToUtf8(self.getLocalProperty('contact_person', l))))
        if self.getSize():
            ra('<item file="%s" content_type="%s" size="%s" name="%s"/>' % (
                self.utBase64Encode(str(self.utNoneToEmpty(self.get_data()))),
                self.utXmlEncode(self.utToUtf8(self.getContentType())),
                self.utToUtf8(self.getSize()),
                self.utToUtf8(self.downloadfilename()))
        )
        return ''.join(r)

    security.declarePrivate('syndicateThis')
    def syndicateThis(self, lang=None):
        l_site = self.getSite()
        if lang is None: lang = self.gl_get_selected_language()
        item = rss_item_for_object(self, lang)
        nsmap = get_nsmap(self.getSyndicationTool().getNamespaceItemsList())
        Dc = ElementMaker(namespace=nsmap['dc'], nsmap=nsmap)
        Ev = ElementMaker(namespace=nsmap['ev'], nsmap=nsmap)
        Ut = ElementMaker(namespace=nsmap['ut'], nsmap=nsmap)
        item.extend(Dc.root(
            Dc.type('Event'),
            Dc.format(self.format()),
            Dc.source(self.getLocalProperty('source', lang)),
            Dc.creator(self.getLocalProperty('creator', lang)),
            Dc.publisher(l_site.getLocalProperty('publisher', lang)),
            Dc.relation(self.relation),
        ))
        for k in self.subject:
            theme_ob = self.getPortalThesaurus().getThemeByID(k, self.gl_get_selected_language())
            theme_name = theme_ob.theme_name
            if theme_name:
                item.append(Dc.subject(theme_name.strip()))
        item.extend(Ev.root(
            Ev.organizer(self.getLocalProperty('organizer', lang)),
            Ev.type(self.event_type),
            Ev.startdate(self.utShowFullDateTimeHTML(self.start_date))
            ))
        if self.end_date:
            item.append(Ev.enddate(self.utShowFullDateTimeHTML(self.end_date)))
        for k in self.getLocalProperty('keywords', lang).split(','):
            item.append(Ut.keyword(k))
        item.extend(Ut.root(
            Ut.creator_mail(self.creator_email),
            Ut.contact_name(self.getLocalProperty('contact_person', lang)),
            Ut.contact_mail(self.contact_email),
            Ut.contact_phone(self.contact_phone),
            Ut.event_type(self.event_type),
            Ut.file_link(self.getLocalProperty('file_link', lang)),
            Ut.file_link_copy(self.getLocalProperty('file_link_copy', lang)),
            Ut.source_link(self.source_link),
            Ut.organizer(self.getLocalProperty('organizer', lang)),
            Ut.geozone(self.geozone),
            Ut.address(self.getLocalProperty('address', lang)),
            Ut.duration(self.getLocalProperty('duration', lang)),
            Ut.event_status(self.event_status),
            Ut.start_date(self.utShowFullDateTimeHTML(self.start_date))
        ))
        if self.end_date:
            item.append(Ut.end_date(self.utShowFullDateTimeHTML(self.end_date)))
        return etree.tostring(item, xml_declaration=False, encoding="utf-8")

    #site actions
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'commitVersion')
    def commitVersion(self, REQUEST=None):
        """ """
        if (not self.checkPermissionEditObject()) or (self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName()):
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if not self.hasVersion():
            raise EXCEPTION_NOVERSION, EXCEPTION_NOVERSION_MSG

        self.copy_naaya_properties_from(self.version)
        self.checkout = 0
        self.checkout_user = None
        self.version = None
        self._p_changed = 1
        self.recatalogNyObject(self)

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
        self.version = semevent_item()
        self.version.copy_naaya_properties_from(self)
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject(): #Check if user can edit the content
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG

        if self.hasVersion():
            self = self.version
            if self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName():
                raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG

        if REQUEST is not None:
            schema_raw_data = dict(REQUEST.form)
        else:
            schema_raw_data = kwargs

        _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
        _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''))
        old_date = self.start_date
        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)
        if form_errors:
            if REQUEST is None:
                raise ValueError(form_errors.popitem()[1]) # pick a random error
            else:
                import transaction; transaction.abort() # because we already called _crete_NyZzz_object
                self._prepare_error_response(REQUEST, form_errors, schema_raw_data)
                return REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))

        self.end_date = self.utConvertStringToDateTimeObj(schema_raw_data.get('end_date', None))
        new_date = self.utConvertStringToDateTimeObj(schema_raw_data.get('start_date', None))

        moved = False
        if ((new_date.month(), new_date.year()) !=
            (old_date.month(), old_date.year())):
            self.start_date = new_date
            month_folder = create_month_folder(self.aq_parent.aq_parent.aq_parent, self.contributor, schema_raw_data)
            cut_data = self.aq_parent.manage_cutObjects([self.id, ])
            month_folder.manage_pasteObjects(cut_data)
            moved = True

        if 'file' in schema_raw_data: # Upload file
            self.handleUpload(schema_raw_data['file'])

        if schema_raw_data.get('discussion', None):
            self.open_for_comments()
        else:
            self.close_for_comments()
        self._p_changed = 1
        if moved:
            month_folder.recatalogNyObject(month_folder._getOb(self.getId()))
        else:
            self.recatalogNyObject(self)

        # Create log
        contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
        auth_tool = self.getAuthenticationTool()
        auth_tool.changeLastPost(contributor)

        zope.event.notify(NyContentObjectEditEvent(self, contributor))

        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            if moved: #Redirect to moved location
                url = month_folder._getOb(self.id).absolute_url()
            else:
                url = self.absolute_url()
            return REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (url, _lang))

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/semevent_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'semevent_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT}, 'semevent_edit')

    security.declarePublic('downloadfilename')
    def downloadfilename(self, version=False):
        """ """
        context = self
        if version and self.hasVersion():
            context = self.version
        attached_file = context.get_data(as_string=False)
        filename = getattr(attached_file, 'filename', [])
        if not filename:
            return self.title_or_id()
        return filename[-1]

    security.declareProtected(view, 'download')
    def download(self, REQUEST, RESPONSE):
        """ """
        version = REQUEST.get('version', False)
        RESPONSE.setHeader('Content-Type', self.getContentType())
        RESPONSE.setHeader('Content-Length', self.getSize())
        RESPONSE.setHeader('Content-Disposition', 'attachment;filename=' + self.downloadfilename(version=version))
        RESPONSE.setHeader('Pragma', 'public')
        RESPONSE.setHeader('Cache-Control', 'max-age=0')
        if version and self.hasVersion():
            return semevent_item.index_html(self.version, REQUEST, RESPONSE)
        return semevent_item.index_html(self, REQUEST, RESPONSE)

    security.declarePublic('getDownloadUrl')
    def getDownloadUrl(self):
        """ """
        site = self.getSite()
        file_path = self._get_data_name()
        media_server = getattr(site, 'media_server', '').strip()
        if not (media_server and file_path):
            return self.absolute_url() + '/download'
        file_path = (media_server,) + tuple(file_path)
        return '/'.join(file_path)

    security.declarePublic('getEditDownloadUrl')
    def getEditDownloadUrl(self):
        """ """
        site = self.getSite()
        file_path = self._get_data_name()
        media_server = getattr(site, 'media_server', '').strip()
        if not (media_server and file_path):
            return self.absolute_url() + '/download?version=1'
        file_path = (media_server,) + tuple(file_path)
        return '/'.join(file_path)

    def handleUpload(self, file):
        """
        Upload a file from disk.
        """
        filename = getattr(file, 'filename', '')
        if not filename:
            return
        self.manage_delObjects(self.objectIds())
        file_id = cookId('', '', file)[0]   #cleanup id
        self.manage_addFile(id=file_id, file=file)

InitializeClass(NySemEvent)

config.update({
    'constructors': (manage_addNySemEvent_html, addNySemEvent),
    'folder_constructors': [
            ('manage_addNySemEvent_html', manage_addNySemEvent_html),
            ('semevent_add_html', semevent_add_html),
            ('addNySemEvent', addNySemEvent),
            ('import_NySemEvent', importNySemEvent),
        ],
    'add_method': addNySemEvent,
    'validation': issubclass(NySemEvent, NyValidation),
    '_class': NySemEvent,
})

#Custom folder listing
NaayaPageTemplateFile('zpt/semevent_folder_index', globals(),
                      'semevent_folder_index')

def get_config():
    return config
