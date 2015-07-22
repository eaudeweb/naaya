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

#Python imports
from copy import deepcopy

#Zope imports
from Globals        import InitializeClass
from AccessControl  import ClassSecurityInfo
from AccessControl.Permissions                  import view_management_screens, view
from Products.PageTemplates.PageTemplateFile    import PageTemplateFile

#Product imports
from Products.NaayaContent.constants    import *
from Products.NaayaBase.constants       import *
from Products.NaayaBase.NyItem          import NyItem
from Products.NaayaBase.NyAttributes    import NyAttributes
from Products.NaayaBase.NyCheckControl  import NyCheckControl
from semevent_item                      import semevent_item

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
    'start_date':       (1, MUST_BE_DATETIME_STRICT, 'The Start date field must contain a valid date.'),
    'end_date':         (0, '', ''),
    'event_status':     (0, '', ''),
    'contact_person':   (0, '', ''),
    'contact_email':    (0, '', ''),
    'contact_phone':    (0, '', ''),
    'working_langs':    (0, '', ''),
    'lang':             (0, '', '')
}

manage_addNySemEvent_html = PageTemplateFile('zpt/semevent_manage_add', globals())
manage_addNySemEvent_html.kind = METATYPE_OBJECT
manage_addNySemEvent_html.action = 'addNySemEvent'

def semevent_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNySemEvent'}, 'semevent_add')

def addNySemEvent(self, id='', title='', description='', coverage='',
    keywords='', sortorder='', creator='', creator_email='',
    topitem='', event_type='', source='', source_link='', file_link='',
    file_link_copy='', subject=[], relation='', organizer='', duration='',
    geozone='', address='', start_date='', end_date='', event_status='',
    contact_person='', contact_email='', contact_phone='', working_langs=[],
    contributor=None, releasedate='', discussion='', lang=None, REQUEST=None, **kwargs):
    """
    Create an Event type of object.
    """
    #process parameters
    id = self.utCleanupId(id)
    if not id: id = self.generateItemId(PREFIX_OBJECT)
    try: sortorder = abs(int(sortorder))
    except: sortorder = DEFAULT_SORTORDER
    if topitem: topitem = 1
    else: topitem = 0
    #check mandatory fiels
    l_referer = ''
    if REQUEST is not None: l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
    if not(l_referer == 'semevent_manage_add' or l_referer.find('semevent_manage_add') != -1) and REQUEST:
        r = self.getSite().check_pluggable_item_properties(METATYPE_OBJECT, id=id, title=title, \
            description=description, coverage=coverage, keywords=keywords, sortorder=sortorder, \
            releasedate=releasedate, discussion=discussion, \
            creator=creator, creator_email=creator_email, topitem=topitem, \
            event_type=event_type, source=source, source_link=source_link, file_link=file_link, \
            file_link_copy=file_link_copy, subject=subject, relation=relation, organizer=organizer, \
            duration=duration, geozone=geozone, address=address, start_date=start_date, end_date=end_date, \
            event_status=event_status, contact_person=contact_person, contact_email=contact_email, \
            contact_phone=contact_phone, working_langs=working_langs)
    else:
        r = []
    if not len(r):
        #process parameters
        if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
        if self.glCheckPermissionPublishObjects():
            approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
        else:
            approved, approved_by = 0, None
        start_date = self.utConvertStringToDateTimeObj(start_date)
        end_date = self.utConvertStringToDateTimeObj(end_date)
        releasedate = self.process_releasedate(releasedate)
        subject = self.utConvertToList(subject)
        if lang is None: lang = self.gl_get_selected_language()
        #create object
        ob = NySemEvent(id, title, description, coverage, keywords, sortorder,
            creator, creator_email, topitem, event_type, source, source_link,
            file_link, file_link_copy, subject, relation, organizer, duration,
            geozone, address, start_date, end_date, event_status, contact_person,
            contact_email, contact_phone, working_langs, contributor, releasedate, lang)
        self.gl_add_languages(ob)
        ob.createDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        self._setObject(id, ob)
        #extra settings
        ob = self._getOb(id)
        ob.updatePropertiesFromGlossary(lang)
        ob.approveThis(approved, approved_by)
        ob.submitThis()
        if discussion: ob.open_for_comments()
        self.recatalogNyObject(ob)
        self.notifyFolderMaintainer(self, ob)
        #redirect if case
        if REQUEST is not None:
            if l_referer == 'semevent_manage_add' or l_referer.find('semevent_manage_add') != -1:
                return self.manage_main(self, REQUEST, update_menu=1)
            elif l_referer == 'semevent_add_html':
                self.setSession('referer', self.absolute_url())
                REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
    else:
        if REQUEST is not None:
            self.setSessionErrors(r)
            self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title, \
                description=description, coverage=coverage, keywords=keywords, \
                sortorder=sortorder, releasedate=releasedate, discussion=discussion, \
                creator=creator, creator_email=creator_email, topitem=topitem, \
                event_type=event_type, source=source, source_link=source_link, file_link=file_link, \
                file_link_copy=file_link_copy, subject=subject, relation=relation, organizer=organizer, \
                duration=duration, geozone=geozone, address=address, start_date=start_date, end_date=end_date, \
                event_status=event_status, contact_person=contact_person, contact_email=contact_email, \
                contact_phone=contact_phone, working_langs=working_langs)
            REQUEST.RESPONSE.redirect('%s/semevent_add_html' % self.absolute_url())
        else:
            raise Exception, '%s' % ', '.join(r)

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
            addNySemEvent(self, id=id,
                sortorder=attrs['sortorder'].encode('utf-8'),
                creator=attrs['creator'].encode('utf-8'),
                creator_email=attrs['creator_email'].encode('utf-8'),
                topitem=abs(int(attrs['topitem'].encode('utf-8'))),
                event_type=attrs['event_type'].encode('utf-8'),
                source_link=attrs['source_link'].encode('utf-8'),
                subject=eval(attrs['subject'].encode('utf-8')),
                relation=attrs['relation'].encode('utf-8'),
                geozone=attrs['geozone'].encode('utf-8'),
                working_langs=eval(attrs['working_langs'].encode('utf-8')),
                start_date=self.utConvertDateTimeObjToString(self.utGetDate(attrs['start_date'].encode('utf-8'))),
                end_date=self.utConvertDateTimeObjToString(self.utGetDate(attrs['end_date'].encode('utf-8'))),
                event_status=attrs['event_status'].encode('utf-8'),
                contributor=self.utEmptyToNone(attrs['contributor'].encode('utf-8')),
                contact_email=attrs['contact_email'].encode('utf-8'),
                contact_phone=attrs['contact_phone'].encode('utf-8'),
                discussion=abs(int(attrs['discussion'].encode('utf-8'))))
            ob = self._getOb(id)
            for property, langs in properties.items():
                [ ob._setLocalPropValue(property, lang, langs[lang]) for lang in langs if langs[lang]!='' ]
            ob.approveThis(approved=abs(int(attrs['approved'].encode('utf-8'))),
                approved_by=self.utEmptyToNone(attrs['approved_by'].encode('utf-8')))
            if attrs['releasedate'].encode('utf-8') != '':
                ob.setReleaseDate(attrs['releasedate'].encode('utf-8'))
            ob.import_comments(discussion)
            self.recatalogNyObject(ob)

class NySemEvent(NyAttributes, semevent_item, NyItem, NyCheckControl):
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
        l_options += semevent_item.manage_options
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyItem.manage_options
        return l_options

    security = ClassSecurityInfo()

    def __init__(self, id, title, description, coverage, keywords, sortorder,
        creator, creator_email, topitem, event_type, source, source_link,
        file_link, file_link_copy, subject, relation, organizer, duration, geozone,
        address, start_date, end_date, event_status, contact_person, contact_email,
        contact_phone, working_langs, contributor, releasedate, lang):
        """ """
        self.id = id
        semevent_item.__dict__['__init__'](self, title, description, coverage, keywords,
            sortorder, creator, creator_email, topitem, event_type, source,
            source_link, file_link, file_link_copy, subject, relation, organizer,
            duration, geozone, address, start_date, end_date, event_status,
            contact_person, contact_email, contact_phone, working_langs, releasedate, lang)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor

    security.declareProtected(view, 'resource_type')
    def resource_type(self):
        return self.event_type

    security.declareProtected(view, 'resource_status')
    def resource_status(self):
        return self.event_status

    security.declareProtected(view, 'resource_date')
    def resource_date(self):
        return self.start_date

    security.declareProtected(view, 'resource_end_date')
    def resource_end_date(self):
        return self.end_date

    security.declareProtected(view, 'resource_subject')
    def resource_subject(self):
        return ' '.join(self.subject)

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
        return ''.join(r)

    security.declarePrivate('syndicateThis')
    def syndicateThis(self, lang=None):
        l_site = self.getSite()
        if lang is None: lang = self.gl_get_selected_language()
        r = []
        ra = r.append
        ra(self.syndicateThisHeader())
        ra(self.syndicateThisCommon(lang))
        ra('<dc:type>Event</dc:type>')
        ra('<dc:format>%s</dc:format>' % self.utXmlEncode(self.format()))
        ra('<dc:source>%s</dc:source>' % self.utXmlEncode(self.getLocalProperty('source', lang)))
        ra('<dc:creator>%s</dc:creator>' % self.utXmlEncode(self.getLocalProperty('creator', lang)))
        ra('<dc:publisher>%s</dc:publisher>' % self.utXmlEncode(l_site.getLocalProperty('publisher', lang)))
        ra('<dc:relation>%s</dc:relation>' % self.utXmlEncode(self.relation))
        for k in self.subject:
            if k:
                theme_ob = self.getPortalThesaurus().getThemeByID(k, self.gl_get_selected_language())
                theme_name = theme_ob.theme_name
                if theme_name:
                    ra('<dc:subject>%s</dc:subject>' % self.utXmlEncode(theme_name.strip()))

        ra('<ev:startdate>%s</ev:startdate>' % self.utShowFullDateTimeHTML(self.start_date))
        ra('<ev:enddate>%s</ev:enddate>' % self.utShowFullDateTimeHTML(self.end_date))
        ra('<ev:organizer>%s</ev:organizer>' % self.utXmlEncode(self.getLocalProperty('organizer', lang)))
        ra('<ev:type>%s</ev:type>' % self.utXmlEncode(self.event_type))

        for k in self.getLocalProperty('keywords', lang).split(','):
            ra('<ut:keywords>%s</ut:keywords>' % self.utXmlEncode(k))
        ra('<ut:creator_mail>%s</ut:creator_mail>' % self.utXmlEncode(self.creator_email))
        ra('<ut:contact_name>%s</ut:contact_name>' % self.utXmlEncode(self.getLocalProperty('contact_person', lang)))
        ra('<ut:contact_mail>%s</ut:contact_mail>' % self.utXmlEncode(self.contact_email))
        ra('<ut:contact_phone>%s</ut:contact_phone>' % self.utXmlEncode(self.contact_phone))
        ra('<ut:event_type>%s</ut:event_type>' % self.utXmlEncode(self.event_type))
        ra('<ut:file_link>%s</ut:file_link>' % self.utXmlEncode(self.getLocalProperty('file_link', lang)))
        ra('<ut:file_link_copy>%s</ut:file_link_copy>' % self.utXmlEncode(self.getLocalProperty('file_link_copy', lang)))
        ra('<ut:source_link>%s</ut:source_link>' % self.utXmlEncode(self.source_link))
        ra('<ut:organizer>%s</ut:organizer>' % self.utXmlEncode(self.getLocalProperty('organizer', lang)))
        ra('<ut:geozone>%s</ut:geozone>' % self.utXmlEncode(self.geozone))
        ra('<ut:address>%s</ut:address>' % self.utXmlEncode(self.getLocalProperty('address', lang)))
        ra('<ut:duration>%s</ut:duration>' % self.utXmlEncode(self.getLocalProperty('duration', lang)))
        ra('<ut:start_date>%s</ut:start_date>' % self.utShowFullDateTimeHTML(self.start_date))
        ra('<ut:end_date>%s</ut:end_date>' % self.utShowFullDateTimeHTML(self.end_date))
        ra('<ut:event_status>%s</ut:event_status>' % self.utXmlEncode(self.event_status))
        ra(self.syndicateThisFooter())
        return ''.join(r)

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', coverage='', keywords='',
        sortorder='', approved='', creator='', creator_email='', topitem='',
        event_type='', source='', source_link='', file_link='', file_link_copy='',
        subject=[], relation='', organizer='', duration='', geozone='', address='', 
        start_date='', end_date='', event_status='', contact_person='',
        contact_email='', contact_phone='', working_langs=[], releasedate='',
        discussion='', lang='', REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        try: sortorder = abs(int(sortorder))
        except: sortorder = DEFAULT_SORTORDER
        working_langs = self.utConvertToList(working_langs)
        if topitem: topitem = 1
        else: topitem = 0
        if approved: approved = 1
        else: approved = 0
        subject = self.utConvertToList(subject)
        start_date = self.utConvertStringToDateTimeObj(start_date)
        end_date = self.utConvertStringToDateTimeObj(end_date)
        releasedate = self.process_releasedate(releasedate, self.releasedate)
        if not lang: lang = self.gl_get_selected_language()
        self.save_properties(title, description, coverage, keywords, sortorder,
            creator, creator_email, topitem, event_type, source,
            source_link, file_link, file_link_copy, subject, relation, organizer, duration, geozone,
            address, start_date, end_date, event_status, contact_person,
            contact_email, contact_phone, working_langs, releasedate, lang)
        self.updatePropertiesFromGlossary(lang)
        self.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        if approved != self.approved:
            if approved == 0: approved_by = None
            else: approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
            self.approveThis(approved, approved_by)
        self._p_changed = 1
        if discussion: self.open_for_comments()
        else: self.close_for_comments()
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
        self.sortorder =        self.version.sortorder
        self.creator =          self.version.creator
        self.creator_email =    self.version.creator_email
        self.topitem =          self.version.topitem
        self.event_type =       self.version.event_type
        self.source_link =      self.version.source_link
        self.file_link =        self.version.file_link
        self.file_link_copy =   self.version.file_link_copy
        self.subject =          self.version.subject
        self.relation =         self.version.relation
        self.geozone =          self.version.geozone
        self.start_date =       self.version.start_date
        self.end_date =         self.version.end_date
        self.event_status =     self.version.event_status
        self.releasedate =      self.version.releasedate
        self.releasedate =      self.version.releasedate
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
        self.version = semevent_item(self.title, self.description, self.coverage,
            self.keywords, self.sortorder, self.creator, self.creator_email,
            self.topitem, self.event_type, self.source, self.source_link,
            self.file_link, self.file_link_copy, self.subject, self.relation,
            self.organizer, self.duration, self.geozone, self.address, self.start_date,
            self.end_date, self.event_status, self.contact_person, self.contact_email,
            self.contact_phone, self.working_langs, self.releasedate, self.gl_get_selected_language())
        self.version._local_properties_metadata = deepcopy(self._local_properties_metadata)
        self.version._local_properties = deepcopy(self._local_properties)
        self.version.setProperties(deepcopy(self.getProperties()))
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, title='', description='', coverage='', keywords='',
        sortorder='', creator='', creator_email='', topitem='', event_type='',
        source='', source_link='', file_link='', file_link_copy='', subject=[],
        relation='', organizer='', duration='', geozone='', address='', start_date='',
        end_date='', event_status='', contact_person='', contact_email='', contact_phone='',
        working_langs=[], releasedate='', discussion='', lang=None, REQUEST=None, RESPONSE=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if not sortorder: sortorder = DEFAULT_SORTORDER
        working_langs = self.utConvertToList(working_langs)
        if topitem: topitem = 1
        else: topitem = 0
        subject = self.utConvertToList(subject)
        if lang is None: lang = self.gl_get_selected_language()
        #check mandatory fiels
        r = self.getSite().check_pluggable_item_properties(METATYPE_OBJECT, title=title, \
            description=description, coverage=coverage, keywords=keywords, sortorder=sortorder, \
            releasedate=releasedate, discussion=discussion, \
            creator=creator, creator_email=creator_email, topitem=topitem, \
            event_type=event_type, source=source, source_link=source_link, file_link=file_link, \
            file_link_copy=file_link_copy, subject=subject, relation=relation, organizer=organizer, \
            duration=duration, geozone=geozone, address=address, start_date=start_date, end_date=end_date, \
            event_status=event_status, contact_person=contact_person, contact_email=contact_email, \
            contact_phone=contact_phone, working_langs=working_langs)
        if not len(r):
            start_date = self.utConvertStringToDateTimeObj(start_date)
            end_date = self.utConvertStringToDateTimeObj(end_date)
            sortorder = int(sortorder)
            if not self.hasVersion():
                #this object has not been checked out; save changes directly into the object
                releasedate = self.process_releasedate(releasedate, self.releasedate)
                self.save_properties(title, description, coverage, keywords, sortorder,
                    creator, creator_email, topitem, event_type, source,
                    source_link, file_link, file_link_copy, subject, relation, organizer,
                    duration, geozone, address, start_date, end_date, event_status,
                    contact_person, contact_email, contact_phone, working_langs, releasedate, lang)
                self.updatePropertiesFromGlossary(lang)
                self.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
            else:
                #this object has been checked out; save changes into the version object
                if self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName():
                    raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
                releasedate = self.process_releasedate(releasedate, self.version.releasedate)
                self.version.save_properties(title, description, coverage, keywords, sortorder,
                    creator, creator_email, topitem, event_type, source,
                    source_link, file_link, file_link_copy, subject, relation, organizer,
                    duration, geozone, address, start_date, end_date, event_status,
                    contact_person, contact_email, contact_phone, working_langs, releasedate, lang)
                self.version.updatePropertiesFromGlossary(lang)
                self.version.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
            if discussion: self.open_for_comments()
            else: self.close_for_comments()
            self._p_changed = 1
            self.recatalogNyObject(self)
            if REQUEST:
                self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))
        else:
            if REQUEST is not None:
                self.setSessionErrors(r)
                self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title, \
                    description=description, coverage=coverage, keywords=keywords, \
                    sortorder=sortorder, releasedate=releasedate, discussion=discussion, \
                    creator=creator, creator_email=creator_email, topitem=topitem, \
                    event_type=event_type, source=source, source_link=source_link, file_link=file_link, \
                    file_link_copy=file_link_copy, subject=subject, relation=relation, organizer=organizer, \
                    duration=duration, geozone=geozone, address=address, start_date=start_date, end_date=end_date, \
                    event_status=event_status, contact_person=contact_person, contact_email=contact_email, \
                    contact_phone=contact_phone, working_langs=working_langs)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))
            else:
                raise Exception, '%s' % ', '.join(r)

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/semevent_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'semevent_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'semedit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'semevent_edit')

InitializeClass(NySemEvent)
