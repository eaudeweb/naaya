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
# Alex Morega, Eau de Web

#Python imports
from copy import deepcopy
import re
from cStringIO import StringIO

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from Products.NaayaBase.NyContentType import NyContentType, NY_CONTENT_BASE_SCHEMA
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
DEFAULT_SCHEMA = {
    'personaltitle':    dict(sortorder=100, widget_type='String', label='Personal title', localized=True),
    'firstname':        dict(sortorder=110, widget_type='String', label='First name', localized=True),
    'lastname':         dict(sortorder=120, widget_type='String', label='Last name', localized=True),
    'jobtitle':         dict(sortorder=130, widget_type='String', label='Job title', localized=True),
    'department':       dict(sortorder=140, widget_type='String', label='Department', localized=True),
    'organisation':     dict(sortorder=150, widget_type='String', label='Organisation', localized=True),
    'postaladdress':    dict(sortorder=160, widget_type='String', label='Postal address', localized=True),
    'phone':            dict(sortorder=170, widget_type='String', label='Phone'),
    'fax':              dict(sortorder=180, widget_type='String', label='Fax'),
    'cellphone':        dict(sortorder=190, widget_type='String', label='Cell phone'),
    'email':            dict(sortorder=200, widget_type='String', label='Email'),
    'webpage':          dict(sortorder=210, widget_type='String', label='Webpage'),
}
DEFAULT_SCHEMA.update(NY_CONTENT_BASE_SCHEMA)

manage_addNyContact_html = PageTemplateFile('zpt/contact_manage_add', globals())
manage_addNyContact_html.kind = METATYPE_OBJECT
manage_addNyContact_html.action = 'addNyContact'

def contact_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, METATYPE_OBJECT)
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNyContact', 'form_helper': form_helper}, 'contact_add')

def _create_NyContact_object(parent, id, contributor):
    i = 0
    while parent._getOb(id, None):
        i += 1
        id = '%s-%u' % (id, i)
    ob = NyContact(id, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def addNyContact(self, id='', REQUEST=None, contributor=None, **kwargs):
    """
    Create an Contact type of object.
    """
    #process parameters
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
    _contact_word = schema_raw_data.get('contact_word', '')
    _send_notifications = schema_raw_data.pop('_send_notifications', True)

    id = self.utCleanupId(id)
    if not id: id = self.utGenObjectId(schema_raw_data.get('title', ''))
    if not id: id = PREFIX_OBJECT + self.utGenRandomId(5)
    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_NyContact_object(self, id, contributor)

    form_errors = ob.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

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
            return REQUEST.RESPONSE.redirect('%s/contact_add_html' % self.absolute_url())
            return

    if self.glCheckPermissionPublishObjects():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    ob.approveThis(approved, approved_by)
    ob.submitThis()

    if ob.discussion: ob.open_for_comments()
    self.recatalogNyObject(ob)
    if _send_notifications:
        self.notifyFolderMaintainer(self, ob)
    #log post date
    auth_tool = self.getAuthenticationTool()
    auth_tool.changeLastPost(contributor)
    #redirect if case
    if REQUEST is not None:
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'contact_manage_add' or l_referer.find('contact_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'contact_add_html':
            self.setSession('referer', self.absolute_url())
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())

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

            ob = _create_NyContact_object(self, id, self.utEmptyToNone(attrs['contributor'].encode('utf-8')))
            ob.sortorder = attrs['sortorder'].encode('utf-8')
            ob.discussion = abs(int(attrs['discussion'].encode('utf-8')))
            ob.firstname = attrs['firstname'].encode('utf-8')
            ob.lastname = attrs['lastname'].encode('utf-8')
            ob.department = attrs['department'].encode('utf-8')
            ob.organisation = attrs['organisation'].encode('utf-8')
            ob.postaladdress = attrs['postaladdress'].encode('utf-8')
            ob.phone = attrs['phone'].encode('utf-8')
            ob.fax = attrs['fax'].encode('utf-8')
            ob.cellphone = attrs['cellphone'].encode('utf-8')
            ob.email = attrs['email'].encode('utf-8')
            ob.webpage = attrs['webpage'].encode('utf-8')

            for property, langs in properties.items():
                [ ob._setLocalPropValue(property, lang, langs[lang]) for lang in langs if langs[lang]!='' ]
            ob.approveThis(approved=abs(int(attrs['approved'].encode('utf-8'))),
                approved_by=self.utEmptyToNone(attrs['approved_by'].encode('utf-8')))
            if attrs['releasedate'].encode('utf-8') != '':
                ob.setReleaseDate(attrs['releasedate'].encode('utf-8'))
            ob.import_comments(discussion)
            self.recatalogNyObject(ob)

class NyContact(contact_item, NyAttributes, NyItem, NyCheckControl, NyContentType):
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

    def __init__(self, id, contributor):
        """ """
        self.id = id
        contact_item.__init__(self)
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
        if not self.firstname and not self.lastname:
            fn = self.utToUtf8(self.title_or_id())
            n = self.utToUtf8(self.title_or_id())
        else:
            fn ='%s %s %s' % (self.utToUtf8(self.personaltitle), self.utToUtf8(self.firstname), self.utToUtf8(self.lastname))
            n = '%s;%s;%s;%s;%s' % (self.utToUtf8(self.lastname), self.utToUtf8(self.firstname), '', self.utToUtf8(self.personaltitle), '')
        ra('BEGIN:VCARD')
        ra('CHARSET:UTF-8')
        ra('VERSION:2.1')
        ra('FN;CHARSET=UTF-8:%s' % fn)
        ra('N;CHARSET=UTF-8:%s' % n)
        ra('TITLE;CHARSET=UTF-8:%s' % self.utToUtf8(self.jobtitle))
        ra('ROLE;CHARSET=UTF-8:%s' % self.utToUtf8(self.jobtitle))
        ra('ORG;CHARSET=UTF-8:%s;%s' % (self.utToUtf8(self.organisation), self.utToUtf8(self.department)))
        ra('TEL;WORK:%s' % self.utToUtf8(self.phone))
        ra('TEL;FAX:%s' % self.utToUtf8(self.fax))
        ra('TEL;CELL:%s' % self.utToUtf8(self.cellphone))
        ra('ADR;WORK;CHARSET=UTF-8:;;%s;;;;' % self.utToUtf8(postaladdress))
        ra('EMAIL;INTERNET:%s' % self.utToUtf8(self.email))
        ra('URL:%s' % self.utToUtf8(self.webpage))
        ra('NOTE;CHARSET=UTF-8:%s' % self.utToUtf8(self.utStripAllHtmlTags(self.description)))
        ra('END:VCARD')
        
        if REQUEST:
            response = self.REQUEST.RESPONSE
            response.setHeader('content-type', 'text/x-vCard')
            response.setHeader('charset', 'UTF-8')
            response.setHeader('content-disposition', 'attachment; filename=%s.vcf' % self.id)
        
        return '\n'.join(r)

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
        if self.discussion: self.open_for_comments()
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
        self.version = contact_item()
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
            if self.discussion: self.open_for_comments()
            else: self.close_for_comments()
            self._p_changed = 1
            self.recatalogNyObject(self)
            #log date
            contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
            auth_tool = self.getAuthenticationTool()
            auth_tool.changeLastPost(contributor)
            if REQUEST:
                self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))
        else:
            if REQUEST is not None:
                self._prepare_error_response(REQUEST, form_errors, schema_raw_data)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))
            else:
                raise ValueError(form_errors.popitem()[1]) # pick a random error

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

import vobject
from vobject.vcard import ParseError
_phone_map = {'WORK': 'phone', 'FAX': 'fax', 'CELL': 'cellphone'}
_phone_pattern = re.compile(r'^TEL;(\w+?)\:')
def parse_vcard_data(raw_data):
    try:
        vcard = vobject.readOne(StringIO(raw_data), validate=True)
    except ParseError:
        raise ValueError

    raw_lines = raw_data.split('\n')

    contact_data = {
        'jobtitle': squash_list(vcard.title.value),
        'firstname': squash_list(vcard.n.value.given),
        'lastname': squash_list(vcard.n.value.family),
        'personaltitle': squash_list(vcard.n.value.prefix),
        'webpage': squash_list(vcard.url.value),
        'email': squash_list(vcard.email.value),
        'description': squash_list(vcard.note.value),
    }

    try:
        contact_data['organisation'] = squash_list(vcard.org.value[0])
    except IndexError:
        pass # no organisation entry

    try:
        contact_data['department'] = squash_list(vcard.org.value[1])
    except IndexError:
        pass # no department entry

    try:
        pa_line = vcard.contents['adr'][0].lineNumber
        raw_address = raw_lines[pa_line].split(':')[-1]
        postal_address = re.sub(r'[; ]+', ' ', raw_address).strip()
        contact_data['postaladdress'] = postal_address
    except IndexError:
        pass # no address in this vcard

    for phone_entry in vcard.contents['tel']:
        raw_line = raw_lines[phone_entry.lineNumber-1].strip()
        phone_location_m = _phone_pattern.match(raw_line)
        if phone_location_m is None:
            continue
        phone_location = _phone_map.get(phone_location_m.group(1), None)
        if phone_location is not None:
            contact_data[phone_location] = phone_entry.value
    return contact_data

def squash_list(data):
    if isinstance(data, list):
        return ' '.join(data)
    else:
        return data
