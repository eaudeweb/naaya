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
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Eau de Web
# Dragos Chirila

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
PROPERTIES_OBJECT = {
    'id':               (0, '', ''),
    'title':            (1, MUST_BE_NONEMPTY, 'The Title field must have a value.'),
    'description':      (0, '', ''),
    'coverage':         (0, '', ''),
    'keywords':         (0, '', ''),
    'sortorder':        (0, MUST_BE_POSITIV_INT, 'The Sort order field must contain a positive integer.'),
    'releasedate':      (0, MUST_BE_DATETIME, 'The Release date field must contain a valid date.'),
    'discussion':       (0, '', ''),
    'location':         (0, '', ''),
    'location_address': (0, '', ''),
    'location_url':     (0, '', ''),
    'start_date':       (0, MUST_BE_DATETIME, 'The Start date field must contain a valid date.'),
    'end_date':         (0, MUST_BE_DATETIME, 'The End date field must contain a valid date.'),
    'host':             (0, '', ''),
    'agenda_url':       (0, '', ''),
    'event_url':        (0, '', ''),
    'details':          (0, '', ''),
    'topitem':          (0, '', ''),
    'event_type':       (0, '', ''),
    'contact_person':   (0, '', ''),
    'contact_email':    (0, '', ''),
    'contact_phone':    (0, '', ''),
    'contact_fax':      (0, '', ''),
    'lang':             (0, '', '')
}

manage_addNyEvent_html = PageTemplateFile('zpt/event_manage_add', globals())
manage_addNyEvent_html.kind = METATYPE_OBJECT
manage_addNyEvent_html.action = 'addNyEvent'

def event_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNyEvent'}, 'event_add')

def addNyEvent(self, id='', title='', description='', coverage='',
    keywords='', sortorder='', location='', location_address='', location_url='',
    start_date='', end_date='', host='', agenda_url='', event_url='', details='',
    topitem='', event_type='', contact_person='', contact_email='',
    contact_phone='', contact_fax='', contributor=None, releasedate='',
    discussion='', lang=None, REQUEST=None, **kwargs):
    """
    Create an Event type of object.
    """
    form = kwargs.copy()
    if REQUEST:
        form.update(REQUEST.form)
    #process parameters
    id = self.utCleanupId(id)
    if not id: id = self.utGenObjectId(title)
    if not id: id = PREFIX_OBJECT + self.utGenRandomId(5)
    try: sortorder = abs(int(sortorder))
    except: sortorder = DEFAULT_SORTORDER
    if topitem: topitem = 1
    else: topitem = 0
    #check mandatory fiels
    l_referer = ''
    if REQUEST is not None: l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
    if not(l_referer == 'event_manage_add' or l_referer.find('event_manage_add') != -1) and REQUEST:
        r = self.getSite().check_pluggable_item_properties(METATYPE_OBJECT, id=id, title=title, \
            description=description, coverage=coverage, keywords=keywords, sortorder=sortorder, \
            releasedate=releasedate, discussion=discussion, location=location, location_address=location_address, \
            location_url=location_url, start_date=start_date, end_date=end_date, \
            host=host, agenda_url=agenda_url, event_url=event_url, details=details, \
            topitem=topitem, contact_person=contact_person, contact_email=contact_email, \
            contact_phone=contact_phone, contact_fax=contact_fax, event_type=event_type)
    else:
        r = []

    #check Captcha/reCaptcha
    if self.recaptcha_is_present():
        if not self.is_valid_recaptcha(self, REQUEST):
            r.append('Verification words do not match the ones in the picture.')
    else:
        contact_word = form.get('contact_word', '')
        if contact_word != self.getSession('captcha', ''):
            r.append('The word you typed does not match with the one shown in the image. Please try again.')

    self.delSession('captcha')

    if not len(r):
        #process parameters
        if lang is None: lang = self.gl_get_selected_language()
        if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
        if self.glCheckPermissionPublishObjects():
            approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
        else:
            approved, approved_by = 0, None
        start_date = self.utConvertStringToDateTimeObj(start_date)
        end_date = self.utConvertStringToDateTimeObj(end_date)
        releasedate = self.process_releasedate(releasedate)
        #check if the id is invalid (it is already in use)
        i = 0
        while self._getOb(id, None):
            i += 1
            id = '%s-%u' % (id, i)
        #create object
        ob = NyEvent(id, title, description, coverage, keywords, sortorder,
            location, location_address, location_url, start_date, end_date, host, agenda_url,
            event_url, details, topitem, event_type, contact_person, contact_email, contact_phone, contact_fax,
            contributor, releasedate, lang)
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
        #log post date
        auth_tool = self.getAuthenticationTool()
        auth_tool.changeLastPost(contributor)
        #redirect if case
        if REQUEST is not None:
            if l_referer == 'event_manage_add' or l_referer.find('event_manage_add') != -1:
                return self.manage_main(self, REQUEST, update_menu=1)
            elif l_referer == 'event_add_html':
                self.setSession('referer', self.absolute_url())
                REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
    else:
        if REQUEST is not None:
            self.setSessionErrors(r)
            self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title, \
                description=description, coverage=coverage, keywords=keywords, \
                sortorder=sortorder, releasedate=releasedate, discussion=discussion, \
                location=location, location_address=location_address, \
                location_url=location_url, start_date=start_date, end_date=end_date, \
                host=host, agenda_url=agenda_url, event_url=event_url, details=details, \
                topitem=topitem, contact_person=contact_person, contact_email=contact_email, \
                contact_phone=contact_phone, contact_fax=contact_fax, event_type=event_type, lang=lang)
            REQUEST.RESPONSE.redirect('%s/event_add_html' % self.absolute_url())
        else:
            raise Exception, '%s' % ', '.join(r)

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
                contributor=self.utEmptyToNone(attrs['contributor'].encode('utf-8')),
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

class NyEvent(NyAttributes, event_item, NyItem, NyCheckControl):
    """ """

    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT
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
        contributor, releasedate, lang):
        """ """
        self.id = id
        event_item.__dict__['__init__'](self, title, description, coverage,
            keywords, sortorder, location, location_address, location_url,
            start_date, end_date, host, agenda_url, event_url, details,
            topitem, event_type, contact_person, contact_email, contact_phone,
            contact_fax, releasedate, lang)
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
        r = []
        ra = r.append
        ra(self.syndicateThisHeader())
        ra(self.syndicateThisCommon(lang))
        ra('<dc:type>Event</dc:type>')
        ra('<dc:format>text</dc:format>')
        ra('<dc:source>%s</dc:source>' % self.utXmlEncode(l_site.getLocalProperty('publisher', lang)))
        ra('<dc:creator>%s</dc:creator>' % self.utXmlEncode(l_site.getLocalProperty('creator', lang)))
        ra('<dc:publisher>%s</dc:publisher>' % self.utXmlEncode(l_site.getLocalProperty('publisher', lang)))
        ra('<ev:startdate>%s</ev:startdate>' % self.utShowFullDateTimeHTML(self.start_date))
        ra('<ev:enddate>%s</ev:enddate>' % self.utShowFullDateTimeHTML(self.end_date))
        ra('<ev:location>%s</ev:location>' % self.utXmlEncode(self.getLocalProperty('location', lang)))
        ra('<ev:organizer>%s</ev:organizer>' % self.utXmlEncode(self.getLocalProperty('host', lang)))
        ra('<ev:type>%s</ev:type>' % self.utXmlEncode(self.getPortalTranslations().translate('', self.getEventTypeTitle(self.event_type))))
        ra(self.syndicateThisFooter())
        return ''.join(r)

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', coverage='',
        keywords='', sortorder='', approved='', location='', location_address='',
        location_url='', start_date='', end_date='', host='', agenda_url='',
        topitem='', event_url='', details='', event_type='', contact_person='',
        contact_email='', contact_phone='', contact_fax='', releasedate='',
        discussion='', lang='', REQUEST=None, **kwargs):
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
        releasedate = self.process_releasedate(releasedate, self.releasedate)
        if not lang: lang = self.gl_get_selected_language()
        self.save_properties(title, description, coverage, keywords, sortorder, location,
            location_address, location_url, start_date, end_date, host, agenda_url, event_url,
            details, topitem, event_type, contact_person, contact_email, contact_phone, contact_fax, releasedate, lang)
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
        contact_fax='', releasedate='', discussion='', lang=None, REQUEST=None, RESPONSE=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if not sortorder: sortorder = DEFAULT_SORTORDER
        if topitem: topitem = 1
        else: topitem = 0
        if lang is None: lang = self.gl_get_selected_language()
        #check mandatory fiels
        r = self.getSite().check_pluggable_item_properties(METATYPE_OBJECT, title=title, \
            description=description, coverage=coverage, keywords=keywords, sortorder=sortorder, \
            releasedate=releasedate, discussion=discussion, location=location, location_address=location_address, \
            location_url=location_url, start_date=start_date, end_date=end_date, \
            host=host, agenda_url=agenda_url, event_url=event_url, details=details, \
            topitem=topitem, contact_person=contact_person, contact_email=contact_email, \
            contact_phone=contact_phone, contact_fax=contact_fax, event_type=event_type)
        if not len(r):
            sortorder = int(sortorder)
            start_date = self.utConvertStringToDateTimeObj(start_date)
            end_date = self.utConvertStringToDateTimeObj(end_date)
            if not self.hasVersion():
                #this object has not been checked out; save changes directly into the object
                releasedate = self.process_releasedate(releasedate, self.releasedate)
                self.save_properties(title, description, coverage, keywords, sortorder, location, location_address,
                    location_url, start_date, end_date, host, agenda_url, event_url, details, topitem, event_type,
                    contact_person, contact_email, contact_phone, contact_fax, releasedate, lang)
                self.updatePropertiesFromGlossary(lang)
                self.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
            else:
                #this object has been checked out; save changes into the version object
                if self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName():
                    raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
                releasedate = self.process_releasedate(releasedate, self.version.releasedate)
                self.version.save_properties(title, description, coverage, keywords, sortorder, location, location_address,
                    location_url, start_date, end_date, host, agenda_url, event_url, details, topitem, event_type,
                    contact_person, contact_email, contact_phone, contact_fax, releasedate, lang)
                self.version.updatePropertiesFromGlossary(lang)
                self.version.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
            if discussion: self.open_for_comments()
            else: self.close_for_comments()

            self._p_changed = 1
            self.recatalogNyObject(self)
            #log date
            contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
            auth_tool = self.getAuthenticationTool()
            auth_tool.changeLastPost(contributor)

            if REQUEST:
                self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))
        else:
            if REQUEST is not None:
                self.setSessionErrors(r)
                self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title, \
                    description=description, coverage=coverage, keywords=keywords, \
                    sortorder=sortorder, releasedate=releasedate, discussion=discussion, \
                    location=location, location_address=location_address, \
                    location_url=location_url, start_date=start_date, end_date=end_date, \
                    host=host, agenda_url=agenda_url, event_url=event_url, details=details, \
                    topitem=topitem, contact_person=contact_person, contact_email=contact_email, \
                    contact_phone=contact_phone, contact_fax=contact_fax, event_type=event_type)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))
            else:
                raise Exception, '%s' % ', '.join(r)

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
