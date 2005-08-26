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
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

#Python imports
from copy import deepcopy

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from Products.NaayaContent.constants import *
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyCheckControl import NyCheckControl
from event_item import event_item

#module constants
METATYPE_OBJECT = 'Naaya Event'
LABEL_OBJECT = 'Event'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya Event objects'
OBJECT_FORMS = ['event_add', 'event_edit', 'event_index']
OBJECT_CONSTRUCTORS = ['manage_addNyEvent_html', 'event_add_html', 'addNyEvent', 'importNyEvent']
OBJECT_ADD_FORM = 'event_add_html'
DESCRIPTION_OBJECT = 'This is Naaya Event type.'
PREFIX_OBJECT = 'ev'

manage_addNyEvent_html = PageTemplateFile('zpt/event_manage_add', globals())
manage_addNyEvent_html.kind = METATYPE_OBJECT
manage_addNyEvent_html.action = 'addNyEvent'

def event_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNyEvent'}, 'event_add')

def addNyEvent(self, id='', title='', description='', language='', coverage='', keywords='', sortorder='',
    location='', location_address='', location_url='', start_date='', end_date='', host='', agenda_url='',
    event_url='', details='', topitem='', event_type='', contact_person='', contact_email='', contact_phone='',
    contact_fax='', contributor=None, releasedate='', lang=None, REQUEST=None, **kwargs):
    """ """
    id = self.utCleanupId(id)
    if not id: id = PREFIX_OBJECT + self.utGenRandomId(6)
    try: sortorder = abs(int(sortorder))
    except: sortorder = DEFAULT_SORTORDER
    if topitem: topitem = 1
    else: topitem = 0
    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
    if self.checkPermissionPublishObjects():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    start_date = self.utConvertStringToDateTimeObj(start_date)
    end_date = self.utConvertStringToDateTimeObj(end_date)
    releasedate = self.utConvertStringToDateTimeObj(releasedate)
    if releasedate is None: releasedate = self.utGetTodayDate()
    if lang is None: lang = self.gl_get_selected_language()
    ob = NyEvent(id, title, description, coverage, keywords, sortorder,
        location, location_address, location_url, start_date, end_date, host, agenda_url,
        event_url, details, topitem, event_type, contact_person, contact_email, contact_phone, contact_fax,
        contributor, approved, approved_by, releasedate, lang)
    self.gl_add_languages(ob)
    ob.createDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
    self._setObject(id, ob)
    if REQUEST is not None:
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'event_manage_add' or l_referer.find('event_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'event_add_html':
            self.setSession('referer', self.absolute_url())
            REQUEST.RESPONSE.redirect('%s/note_html' % self.getSitePath())

def importNyEvent(self, id, attrs, content, properties):
    #this method is called during the import process
    addNyEvent(self, id=id,
        sortorder=attrs['sortorder'].encode('utf-8'),
        location_url=attrs['location_url'].encode('utf-8'),
        start_date=self.utConvertDateTimeObjToString(self.utGetDate(attrs['start_date'].encode('utf-8'))),
        end_date=self.utConvertDateTimeObjToString(self.utGetDate(attrs['end_date'].encode('utf-8'))),
        agenda_url=attrs['agenda_url'].encode('utf-8'),
        event_url=attrs['event_url'].encode('utf-8'),
        topitem=abs(int(attrs['topitem'].encode('utf-8'))),
        event_type=attrs['event_type'].encode('utf-8'),
        contact_person=attrs['contact_person'].encode('utf-8'),
        contact_email=attrs['contact_email'].encode('utf-8'),
        contact_phone=attrs['contact_phone'].encode('utf-8'),
        contact_fax=attrs['contact_fax'].encode('utf-8'),
        contributor=attrs['contributor'].encode('utf-8'))
    ob = self._getOb(id)
    for property, langs in properties.items():
        for lang in langs:
            ob._setLocalPropValue(property, lang, langs[lang])
    ob.approveThis(abs(int(attrs['approved'].encode('utf-8'))))
    ob.setReleaseDate(attrs['releasedate'].encode('utf-8'))
    self.recatalogNyObject(ob)

class NyEvent(NyAttributes, event_item, NyItem, NyCheckControl):
    """ """

    meta_type = METATYPE_OBJECT
    icon = 'misc_/NaayaContent/NyEvent.gif'
    icon_marked = 'misc_/NaayaContent/NyEvent_marked.gif'

    def manage_options(self):
        """ """
        l_options = ()
        if not self.hasVersion():
            l_options += ({'label': 'Properties', 'action': 'manage_edit_html'},)
        l_options += event_item.manage_options
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyItem.manage_options
        return l_options

    security = ClassSecurityInfo()

    def __init__(self, id, title, description, coverage, keywords, sortorder,
        location, location_address, location_url, start_date, end_date, host, agenda_url,
        event_url, details, topitem, event_type, contact_person, contact_email, contact_phone, contact_fax,
        contributor, approved, approved_by, releasedate, lang):
        """ """
        self.id = id
        event_item.__dict__['__init__'](self, title, description, coverage, keywords, sortorder, location,
            location_address, location_url, start_date, end_date, host, agenda_url, event_url,
            details, topitem, event_type, contact_person, contact_email, contact_phone, contact_fax, releasedate, lang)
        NyCheckControl.__dict__['__init__'](self)
        self.contributor = contributor
        self.approved = approved
        self.approved_by = approved_by

    security.declarePrivate('objectkeywords')
    def objectkeywords(self, lang):
        return u' '.join([self._objectkeywords(lang), self.getLocalProperty('details', lang)])

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
        for l in self.gl_get_languages():
            r.append('<location lang="%s" content="%s"/>' % (l, self.utXmlEncode(self.getLocalProperty('location', l))))
            r.append('<location_address lang="%s" content="%s"/>' % (l, self.utXmlEncode(self.getLocalProperty('location_address', l))))
            r.append('<host lang="%s" content="%s"/>' % (l, self.utXmlEncode(self.getLocalProperty('host', l))))
            r.append('<details lang="%s" content="%s"/>' % (l, self.utXmlEncode(selfself.getLocalProperty('details', l))))
        return ''.join(r)

    security.declarePrivate('syndicateThis')
    def syndicateThis(self, lang=None):
        l_site = self.getSite()
        if lang is None: lang = self.gl_get_selected_language()
        l_rdf = []
        l_rdf.append(self.syndicateThisHeader())
        l_rdf.append(self.syndicateThisCommon(lang))
        l_rdf.append('<dc:type>Event</dc:type>')
        l_rdf.append('<dc:format>text</dc:format>')
        l_rdf.append('<dc:source>%s</dc:source>' % self.utXmlEncode(l_site.getLocalProperty('publisher', lang)))
        l_rdf.append('<ev:startdate>%s</ev:startdate>' % self.utShowFullDateTimeHTML(self.start_date))
        l_rdf.append('<ev:enddate>%s</ev:enddate>' % self.utShowFullDateTimeHTML(self.end_date))
        l_rdf.append('<ev:location>%s</ev:location>' % self.utXmlEncode(self.getLocalProperty('location', lang)))
        l_rdf.append('<ev:organizer>%s</ev:organizer>' % self.utXmlEncode(self.getLocalProperty('host', lang)))
        l_rdf.append('<ev:type>%s</ev:type>' % self.utXmlEncode(self.getEventTypeTitle(self.event_type)))
        l_rdf.append(self.syndicateThisFooter())
        return ''.join(l_rdf)

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', language='', coverage='', keywords='', sortorder='',
        approved='', location='', location_address='', location_url='', start_date='', end_date='',
        host='', agenda_url='', topitem='', event_url='', details='', event_type='',
        contact_person='', contact_email='', contact_phone='', contact_fax='', releasedate='', REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        try: sortorder = abs(int(sortorder))
        except: sortorder = DEFAULT_SORTORDER
        if approved: approved = 1
        else: approved = 0
        start_date = self.utConvertStringToDateTimeObj(start_date)
        end_date = self.utConvertStringToDateTimeObj(end_date)
        if topitem: topitem = 1
        else: topitem = 0
        releasedate = self.utConvertStringToDateTimeObj(releasedate)
        if releasedate is None: releasedate = self.releasedate
        lang = self.gl_get_selected_language()
        self.save_properties(title, description, coverage, keywords, sortorder, location,
            location_address, location_url, start_date, end_date, host, agenda_url, event_url,
            details, topitem, event_type, contact_person, contact_email, contact_phone, contact_fax, releasedate, lang)
        self.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        if approved != self.approved:
            self.approved = approved
            if approved == 0: self.approved_by = None
            else: self.approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    #site actions
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'commitVersion')
    def commitVersion(self, REQUEST=None):
        """ """
        if (not self.checkPermissionEditObject()) or (self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName()):
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if not self.hasVersion():
            raise EXCEPTION_NOVERSION, EXCEPTION_NOVERSION_MSG
        self._local_properties_metadata = deepcopy(self.version._local_properties_metadata)
        self._local_properties = deepcopy(self.version._local_properties)
        self.sortorder = self.version.sortorder
        self.location_url = self.version.location_url
        self.start_date = self.version.start_date
        self.end_date = self.version.end_date
        self.agenda_url = self.version.agenda_url
        self.event_url = self.version.event_url
        self.topitem = self.version.topitem
        self.event_type = self.version.event_type
        self.contact_person = self.version.contact_person
        self.contact_email = self.version.contact_email
        self.contact_phone = self.version.contact_phone
        self.contact_fax = self.version.contact_fax
        self.releasedate = self.version.releasedate
        self.setProperties(deepcopy(self.version.getProperties()))
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
        self.version = event_item(self.title, self.description, self.coverage, self.keywords, self.sortorder,
            self.location, self.location_address, self.location_url, self.start_date, self.end_date,
            self.host, self.agenda_url, self.event_url, self.details, self.topitem, self.event_type, self.contact_person,
            self.contact_email, self.contact_phone, self.contact_fax, self.releasedate, self.gl_get_selected_language())
        self.version._local_properties_metadata = deepcopy(self._local_properties_metadata)
        self.version._local_properties = deepcopy(self._local_properties)
        self.version.setProperties(deepcopy(self.getProperties()))
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, title='', description='', coverage='', keywords='', sortorder='',
        location='', location_address='', location_url='', start_date='', end_date='', host='', agenda_url='',
        event_url='', details='', topitem='', event_type='', contact_person='', contact_email='', contact_phone='',
        contact_fax='', releasedate='', lang=None, REQUEST=None, RESPONSE=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        try: sortorder = abs(int(sortorder))
        except: sortorder = DEFAULT_SORTORDER
        start_date = self.utConvertStringToDateTimeObj(start_date)
        end_date = self.utConvertStringToDateTimeObj(end_date)
        if topitem: topitem = 1
        else: topitem = 0
        releasedate = self.utConvertStringToDateTimeObj(releasedate)
        if releasedate is None: releasedate = self.releasedate
        if lang is None: lang = self.gl_get_selected_language()
        if not self.hasVersion():
            #this object has not been checked out; save changes directly into the object
            self.save_properties(title, description, coverage, keywords, sortorder, location, location_address,
                location_url, start_date, end_date, host, agenda_url, event_url, details, topitem, event_type,
                contact_person, contact_email, contact_phone, contact_fax, releasedate, lang)
            self.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        else:
            #this object has been checked out; save changes into the version object
            if self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName():
                raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
            self.version.save_properties(title, description, coverage, keywords, sortorder, location, location_address,
                location_url, start_date, end_date, host, agenda_url, event_url, details, topitem, event_type,
                contact_person, contact_email, contact_phone, contact_fax, releasedate, lang)
            self.version.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))

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
        return self.getFormsTool().getContent({'here': self}, 'event_edit')

InitializeClass(NyEvent)
