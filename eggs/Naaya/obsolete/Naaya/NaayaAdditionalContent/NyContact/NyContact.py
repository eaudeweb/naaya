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
from contact_item import contact_item

#module constants
METATYPE_OBJECT = 'Naaya Contact'
LABEL_OBJECT = 'Contact'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya Contact objects'
OBJECT_FORMS = ['contact_add', 'contact_edit', 'contact_index']
OBJECT_CONSTRUCTORS = ['manage_addNyContact_html', 'contact_add_html', 'addNyContact', 'importNyContact']
OBJECT_ADD_FORM = 'contact_add_html'
DESCRIPTION_OBJECT = 'This is Naaya Contact type.'
PREFIX_OBJECT = 'contact'
PROPERTIES_OBJECT = {
    'id':           (0, '', ''),
    'title':        (1, MUST_BE_NONEMPTY, 'The Title field must have a value.'),
    'description':  (0, '', ''),
    'coverage':     (0, '', ''),
    'keywords':     (0, '', ''),
    'sortorder':    (0, MUST_BE_POSITIV_INT, 'The Sort order field must contain a positive integer.'),
    'releasedate':  (0, MUST_BE_DATETIME, 'The Release date field must contain a valid date.'),
    'discussion':   (0, '', ''),
    'personaltitle':(0, '', ''),
    'firstname':    (0, '', ''),
    'lastname':     (0, '', ''),
    'jobtitle':     (0, '', ''),
    'department':   (0, '', ''),
    'organisation': (0, '', ''),
    'postaladdress':(0, '', ''),
    'phone':        (0, '', ''),
    'fax':          (0, '', ''),
    'cellphone':    (0, '', ''),
    'email':        (0, '', ''),
    'webpage':      (0, '', ''),
    'lang':         (0, '', '')
}

manage_addNyContact_html = PageTemplateFile('zpt/contact_manage_add', globals())
manage_addNyContact_html.kind = METATYPE_OBJECT
manage_addNyContact_html.action = 'addNyContact'

def contact_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNyContact'}, 'contact_add')

def addNyContact(self, id='', title='', description='', coverage='', keywords='',
    sortorder='', personaltitle='', firstname='', lastname='', jobtitle='', department='', 
    organisation='', postaladdress='', phone='', fax='', cellphone='', email='', webpage='', 
    contributor=None, releasedate='', discussion='', contact_word='', lang=None, REQUEST=None, **kwargs):
    """
    Create an Contact type of object.
    """
    #process parameters
    id = self.utCleanupId(id)
    if not id: id = self.utGenObjectId(title)
    try: sortorder = abs(int(sortorder))
    except: sortorder = DEFAULT_SORTORDER
    #check mandatory fiels
    l_referer = ''
    if REQUEST is not None: l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
    if not(l_referer == 'contact_manage_add' or l_referer.find('contact_manage_add') != -1) and REQUEST:
        r = self.getSite().check_pluggable_item_properties(METATYPE_OBJECT, id=id, title=title, \
            description=description, coverage=coverage, keywords=keywords, sortorder=sortorder, \
            releasedate=releasedate, discussion=discussion, personaltitle=personaltitle, firstname=firstname, \
            lastname=lastname, jobtitle=jobtitle, department=department, organisation=organisation, \
            postaladdress=postaladdress, phone=phone, fax=fax, cellphone=cellphone, email=email, webpage=webpage)
    else:
        r = []

    #check Captcha/reCaptcha
    if not self.checkPermissionSkipCaptcha():
        captcha_validator = self.validateCaptcha(contact_word, REQUEST)
        if captcha_validator:
            r.extend(captcha_validator)

    if not len(r):
        #process parameters
        if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
        if self.glCheckPermissionPublishObjects():
            approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
        else:
            approved, approved_by = 0, None
        releasedate = self.process_releasedate(releasedate)
        if lang is None: lang = self.gl_get_selected_language()
        #check if the id is invalid (it is already in use)
        i = 0
        while self._getOb(id, None):
            i += 1
            id = '%s-%u' % (id, i)
        #create object
        ob = NyContact(id, title, description, coverage, keywords, sortorder, personaltitle, firstname, lastname, 
            jobtitle, department, organisation, postaladdress, phone, fax, cellphone, email, webpage, contributor, releasedate, lang)
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
            if l_referer == 'contact_manage_add' or l_referer.find('contact_manage_add') != -1:
                return self.manage_main(self, REQUEST, update_menu=1)
            elif l_referer == 'contact_add_html':
                self.setSession('referer', self.absolute_url())
                REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
    else:
        if REQUEST is not None:
            self.setSessionErrors(r)
            self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title, description=description, coverage=coverage, \
                keywords=keywords, sortorder=sortorder, releasedate=releasedate, discussion=discussion, personaltitle=personaltitle, \
                firstname=firstname, lastname=lastname, jobtitle=jobtitle, department=department, organisation=organisation, \
                postaladdress=postaladdress, phone=phone, fax=fax, cellphone=cellphone, email=email, webpage=webpage, lang=lang)
            return REQUEST.RESPONSE.redirect('%s/contact_add_html' % self.absolute_url())
        else:
            raise Exception, '%s' % ', '.join(r)
    return ob.getId()

def importNyContact(self, param, id, attrs, content, properties, discussion, objects):
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
            addNyContact(self, id=id,
                firstname=attrs['firstname'].encode('utf-8'),
                lastname=attrs['lastname'].encode('utf-8'),
                department=attrs['department'].encode('utf-8'),
                organisation=attrs['organisation'].encode('utf-8'),
                postaladdress=attrs['postaladdress'].encode('utf-8'),
                phone=attrs['phone'].encode('utf-8'),
                fax=attrs['fax'].encode('utf-8'),
                cellphone=attrs['cellphone'].encode('utf-8'),
                email=attrs['email'].encode('utf-8'),
                webpage=attrs['webpage'].encode('utf-8'),
                sortorder=attrs['sortorder'].encode('utf-8'),
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

class NyContact(NyAttributes, contact_item, NyItem, NyCheckControl):
    """ """

    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT

    icon = 'misc_/NaayaContent/NyContact.gif'
    icon_marked = 'misc_/NaayaContent/NyContact_marked.gif'

    def manage_options(self):
        """ """
        l_options = ()
        if not self.hasVersion():
            l_options += ({'label': 'Properties', 'action': 'manage_edit_html'},)
        l_options += contact_item.manage_options
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyItem.manage_options
        return l_options

    security = ClassSecurityInfo()

    def __init__(self, id, title, description, coverage, keywords, sortorder, personaltitle, firstname, 
        lastname, jobtitle, department, organisation, postaladdress, phone, fax, cellphone, email, webpage,
        contributor, releasedate, lang):
        """ """
        self.id = id
        contact_item.__dict__['__init__'](self, title, description, coverage, keywords, sortorder, personaltitle, 
            firstname, lastname, jobtitle, department, organisation, postaladdress, phone, fax, cellphone, email, 
            webpage, releasedate, lang)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor

    security.declarePrivate('objectkeywords')
    def objectkeywords(self, lang):
        return u' '.join([self._objectkeywords(lang), self.firstname, self.lastname, self.getLocalProperty('jobtitle', lang)])

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        return 'personaltitle="%s" firstname="%s" lastname="%s" department="%s" organisation="%s" postaladdress="%s" phone="%s" fax="%s" cellphone="%s" email="%s" webpage="%s"' % \
            (self.utXmlEncode(self.personaltitle), 
            self.utXmlEncode(self.firstname), 
            self.utXmlEncode(self.lastname), 
            self.utXmlEncode(self.department), 
            self.utXmlEncode(self.organisation), 
            self.utXmlEncode(self.postaladdress), 
            self.utXmlEncode(self.phone), 
            self.utXmlEncode(self.fax), 
            self.utXmlEncode(self.cellphone), 
            self.utXmlEncode(self.email), 
            self.utXmlEncode(self.webpage))

    security.declarePrivate('export_this_body_custom')
    def export_this_body_custom(self):
        r = []
        ra = r.append
        for l in self.gl_get_languages():
            ra('<personaltitle lang="%s"><![CDATA[%s]]></personaltitle>' % (l, self.utToUtf8(self.getLocalProperty('personaltitle', l))))
            ra('<jobtitle lang="%s"><![CDATA[%s]]></jobtitle>' % (l, self.utToUtf8(self.getLocalProperty('jobtitle', l))))
        return ''.join(r)

    security.declareProtected(view, 'export_vcard')
    def export_vcard(self, REQUEST=None):
        """ """
        r = []
        ra = r.append
        postaladdress = self.postaladdress
        postaladdress = postaladdress.replace('\r\n', ' ')
        ra('BEGIN:VCARD')
        ra('CHARSET:UTF-8')
        ra('VERSION:2.1')
        ra('FN;CHARSET=UTF-8:%s %s %s' % (self.utToUtf8(self.personaltitle), self.utToUtf8(self.firstname), self.utToUtf8(self.lastname)))
        ra('N;CHARSET=UTF-8:%s;%s;%s;%s;%s' % (self.utToUtf8(self.lastname), self.utToUtf8(self.firstname), '', self.utToUtf8(self.personaltitle), ''))
        ra('TITLE;CHARSET=UTF-8:%s' % self.utToUtf8(self.jobtitle))
        ra('ROLE;CHARSET=UTF-8:%s' % self.utToUtf8(self.jobtitle))
        ra('ORG;CHARSET=UTF-8:%s;%s' % (self.utToUtf8(self.organisation), self.utToUtf8(self.department)))
        ra('TEL;WORK:%s' % self.utToUtf8(self.phone))
        ra('TEL;FAX:%s' % self.utToUtf8(self.fax))
        ra('TEL;CELL:%s' % self.utToUtf8(self.cellphone))
        ra('ADR;WORK;CHARSET=UTF-8:;;%s;;;;' % self.utToUtf8(postaladdress))
        ra('EMAIL;INTERNET:%s' % self.utToUtf8(self.email))
        ra('URL:%s' % self.utToUtf8(self.webpage))
        ra('NOTE;CHARSET=UTF-8:%s' % self.utToUtf8(self.description))
        ra('END:VCARD')
        
        if REQUEST:
            response = self.REQUEST.RESPONSE
            response.setHeader('content-type', 'text/x-vCard')
            response.setHeader('charset', 'UTF-8')
            response.setHeader('content-disposition', 'attachment; filename=%s.vcf' % self.id)
        
        return '\n'.join(r)

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', coverage='', keywords='', sortorder='', 
        approved='', personaltitle='', firstname='', lastname='', jobtitle='', department='', 
        organisation='', postaladdress='', phone='', fax='', cellphone='', email='', webpage='', 
        releasedate='', discussion='', lang='', REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        try: sortorder = abs(int(sortorder))
        except: sortorder = DEFAULT_SORTORDER
        if approved: approved = 1
        else: approved = 0
        releasedate = self.process_releasedate(releasedate, self.releasedate)
        if not lang: lang = self.gl_get_selected_language()
        self.save_properties(title, description, coverage, keywords, sortorder, personaltitle, firstname, lastname, 
            jobtitle, department, organisation, postaladdress, phone, fax, cellphone, email, webpage,releasedate, lang)
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
        self.releasedate = self.version.releasedate
        self.firstname = self.version.firstname
        self.lastname = self.version.lastname
        self.department = self.version.department
        self.organisation = self.version.organisation
        self.postaladdress = self.version.postaladdress
        self.fax = self.version.fax
        self.phone = self.version.phone
        self.cellphone = self.version.cellphone
        self.email = self.version.email
        self.webpage = self.version.webpage
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
        self.version = contact_item(self.title, self.description, self.coverage, self.keywords, self.sortorder, self.personaltitle, 
            self.firstname, self.lastname, self.jobtitle, self.department, self.organisation, self.postaladdress, self.phone, 
            self.fax, self.cellphone, self.email, self.webpage, self.releasedate, self.gl_get_selected_language())
        self.version._local_properties_metadata = deepcopy(self._local_properties_metadata)
        self.version._local_properties = deepcopy(self._local_properties)
        self.version.setProperties(deepcopy(self.getProperties()))
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, title='', description='', coverage='', keywords='', sortorder='', personaltitle='', firstname='', 
        lastname='', jobtitle='', department='', organisation='', postaladdress='', phone='', fax='', cellphone='', email='', 
        webpage='', releasedate='', discussion='', lang=None, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if not sortorder: sortorder = DEFAULT_SORTORDER
        if lang is None: lang = self.gl_get_selected_language()
        #check mandatory fiels
        r = self.getSite().check_pluggable_item_properties(METATYPE_OBJECT, title=title, description=description, \
            coverage=coverage, keywords=keywords, sortorder=sortorder, releasedate=releasedate, discussion=discussion, \
            personaltitle=personaltitle, firstname=firstname, lastname=lastname, jobtitle=jobtitle, department=department, \
            organisation=organisation, postaladdress=postaladdress, phone=phone, fax=fax, cellphone=cellphone, email=email, webpage=webpage)
        if not len(r):
            sortorder = int(sortorder)
            if not self.hasVersion():
                #this object has not been checked out; save changes directly into the object
                releasedate = self.process_releasedate(releasedate, self.releasedate)
                self.save_properties(title, description, coverage, keywords, sortorder, personaltitle, firstname, lastname, 
                    jobtitle, department, organisation, postaladdress, phone, fax, cellphone, email, webpage, releasedate, lang)
                self.updatePropertiesFromGlossary(lang)
                self.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
            else:
                #this object has been checked out; save changes into the version object
                if self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName():
                    raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
                releasedate = self.process_releasedate(releasedate, self.version.releasedate)
                self.version.save_properties(title, description, coverage, keywords, sortorder, personaltitle, firstname, lastname, 
                    jobtitle, department, organisation, postaladdress, phone, fax, cellphone, email, webpage, releasedate, lang)
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
                self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title, description=description, coverage=coverage, \
                    keywords=keywords, sortorder=sortorder, releasedate=releasedate, discussion=discussion, personaltitle=personaltitle, \
                    firstname=firstname, lastname=lastname, jobtitle=jobtitle, department=department, organisation=organisation, \
                    postaladdress=postaladdress, phone=phone, fax=fax, cellphone=cellphone, email=email, webpage=webpage)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))
            else:
                raise Exception, '%s' % ', '.join(r)

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/contact_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'contact_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'contact_edit')

InitializeClass(NyContact)
