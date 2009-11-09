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
# Cristian Romanescu, Eau de Web
from Products.NaayaBase.constants import EXCEPTION_NOTAUTHORIZED,\
    EXCEPTION_NOTAUTHORIZED_MSG, PERMISSION_EDIT_OBJECTS, MESSAGE_SAVEDCHANGES,\
    EXCEPTION_STARTEDVERSION, EXCEPTION_STARTEDVERSION_MSG, EXCEPTION_NOVERSION,\
    EXCEPTION_NOVERSION_MSG

#Python imports
import re
from cStringIO import StringIO
import os, sys

#Zope imports
from Globals import InitializeClass
from App.ImageFile import ImageFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Acquisition import Implicit
from OFS.SimpleItem import Item

#Product imports
from Products.NaayaBase.NyContentType import NyContentType, NY_CONTENT_BASE_SCHEMA
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaBase.NyContentType import NyContentData
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile

DEFAULT_SCHEMA = {
    'address': dict(sortorder=110, widget_type='String', label='Address'),
    'webpage': dict(sortorder=120, widget_type='String', label='Webpage'),
    'phone': dict(sortorder=140, widget_type='String', label='Phone'),
    'fax': dict(sortorder=160, widget_type='String', label='Fax'),
    'picture': dict(sortorder=180, widget_type='String', label='Picture'),
    'main_topic': dict(sortorder=200, widget_type='SelectMultiple', label='Main topic', list_id='institution_topics'),
    'sub_topic': dict(sortorder=220, widget_type='SelectMultiple', label='Additional topics', list_id='institution_topics'),
}
DEFAULT_SCHEMA.update(NY_CONTENT_BASE_SCHEMA)

def setupContentType(site):
    #@TODO: initialize the list of topics (only and only once per site)
    values = { 1: 'unu', 2: 'doi' }
    ptool = site.getPortletsTool()
    itopics = getattr(ptool, 'institution_topics', None)
    if not itopics:
        ptool.manage_addRefList('institution_topics')
        for k, v in values.items():
            ptool.institution_topics.manage_add_item(k, v)


# this dictionary is updated at the end of the module
config = {
        'product': 'NaayaContent',
        'module': 'institution_item',
        'package_path': os.path.abspath(os.path.dirname(__file__)),
        'meta_type': 'Naaya Institution',
        'label': 'Institution',
        'permission': 'Naaya - Add Naaya Institution objects',
        'forms': ['institution_add', 'institution_edit', 'institution_index'],
        'add_form': 'institution_add_html',
        'description': 'This is Naaya Institution type.',
        'properties': {}, #TODO: REMOVE
        'default_schema': DEFAULT_SCHEMA,
        'schema_name': 'NyInstitution',
        '_module': sys.modules[__name__],
        'additional_style': None,
        'icon': os.path.join(os.path.dirname(__file__), 'www', 'NyInstitution.gif'),
        'on_install' : setupContentType,
        '_misc': {
                'NyInstitution.gif': ImageFile('www/NyInstitution.gif', globals()),
                'NyInstitution_marked.gif': ImageFile('www/NyInstitution_marked.gif', globals()),
            },
    }

def institution_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, config['meta_type'])
    return self.getFormsTool().getContent({'here': self, 'kind': config['meta_type'], 'action': 'addNyInstitution', 'form_helper': form_helper}, 'institution_add')

def _create_NyInstitution_object(parent, id, contributor):
    i = 0
    while parent._getOb(id, None):
        i += 1
        id = '%s-%u' % (id, i)
    ob = NyInstitution(id, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def addNyInstitution(self, id='', REQUEST=None, contributor=None, **kwargs):
    """
    Create an Institution type of object.
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
    _institution_word = schema_raw_data.get('institution_word', '')

    id = self.utCleanupId(id)
    if not id: id = self.utGenObjectId(schema_raw_data.get('title', ''))
    if not id: id = 'institution' + self.utGenRandomId(5)
    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_NyInstitution_object(self, id, contributor)

    form_errors = ob.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

    #check Captcha/reCaptcha
    if not self.checkPermissionSkipCaptcha():
        captcha_validator = self.validateCaptcha(_institution_word, REQUEST)
        if captcha_validator:
            form_errors['captcha'] = captcha_validator

    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1]) # pick a random error
        else:
            import transaction; transaction.abort() # because we already called _crete_NyZzz_object
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            return REQUEST.RESPONSE.redirect('%s/institution_add_html' % self.absolute_url())
            return

    if self.glCheckPermissionPublishObjects():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    ob.approveThis(approved, approved_by)
    ob.submitThis()

    if ob.discussion: ob.open_for_comments()
    self.recatalogNyObject(ob)
    self.notifyFolderMaintainer(self, ob)
    #log post date
    auth_tool = self.getAuthenticationTool()
    auth_tool.changeLastPost(contributor)
    #redirect if case
    if REQUEST is not None:
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'institution_manage_add' or l_referer.find('institution_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'institution_add_html':
            self.setSession('referer', self.absolute_url())
            return ob.object_submitted_message(REQUEST)
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())

    return ob.getId()

def importNyInstitution(self, param, id, attrs, content, properties, discussion, objects):
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

            ob = _create_NyInstitution_object(self, id, self.utEmptyToNone(attrs['contributor'].encode('utf-8')))
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

class institution_item(Implicit, NyContentData):
    """ """

class NyInstitution(institution_item, NyAttributes, NyItem, NyCheckControl, NyContentType):
    """ """

    meta_type = config['meta_type']
    meta_label = config['label']

    icon = 'misc_/NaayaContent/NyInstitution.gif'
    icon_marked = 'misc_/NaayaContent/NyInstitution_marked.gif'

    def manage_options(self):
        """ """
        l_options = ()
        #if not self.hasVersion():
        #    l_options += ({'label': 'Properties', 'action': 'manage_edit_html'},)
        l_options += institution_item.manage_options
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyItem.manage_options
        return l_options

    security = ClassSecurityInfo()

    def __init__(self, id, contributor):
        """ """
        self.id = id
        institution_item.__init__(self)
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
        self.version = institution_item()
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
    #security.declareProtected(view_management_screens, 'manage_edit_html')
    #manage_edit_html = PageTemplateFile('zpt/institution_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'institution_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'institution_edit')

InitializeClass(NyInstitution)


#
class InstitutionLister(Implicit, Item):
    """
    Plug into the catalog to retrieve the list of institutions
    """
    def __init__(self, id):
        self.id = id

    _index_template = NaayaPageTemplateFile('zpt/institutions_list', globals(), 'institution')

    def index_html(self, REQUEST):
        """
        Render the list of institutions recorded for this site.
        """
        site = self.getSite()
        return self._index_template(REQUEST, institutions=[1,2,3])

    def query_institutions(self):
        """
        Retrieve the list of institutions
        """
        site = self.getSite()
        return site.getCatalogTool().getCatalogedObjects(meta_type='Naaya Institution', approved=1)


from Products.Naaya.NySite import NySite
NySite.list_institutions = InstitutionLister('list_institutions')




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

    institution_data = {
        'jobtitle': squash_list(vcard.title.value),
        'firstname': squash_list(vcard.n.value.given),
        'lastname': squash_list(vcard.n.value.family),
        'personaltitle': squash_list(vcard.n.value.prefix),
        'webpage': squash_list(vcard.url.value),
        'email': squash_list(vcard.email.value),
        'description': squash_list(vcard.note.value),
    }

    try:
        institution_data['organisation'] = squash_list(vcard.org.value[0])
    except IndexError:
        pass # no organisation entry

    try:
        institution_data['department'] = squash_list(vcard.org.value[1])
    except IndexError:
        pass # no department entry

    try:
        pa_line = vcard.contents['adr'][0].lineNumber
        raw_address = raw_lines[pa_line].split(':')[-1]
        postal_address = re.sub(r'[; ]+', ' ', raw_address).strip()
        institution_data['postaladdress'] = postal_address
    except IndexError:
        pass # no address in this vcard

    for phone_entry in vcard.contents['tel']:
        raw_line = raw_lines[phone_entry.lineNumber-1].strip()
        phone_location_m = _phone_pattern.match(raw_line)
        if phone_location_m is None:
            continue
        phone_location = _phone_map.get(phone_location_m.group(1), None)
        if phone_location is not None:
            institution_data[phone_location] = phone_entry.value
    return institution_data

def squash_list(data):
    if isinstance(data, list):
        return ' '.join(data)
    else:
        return data

#manage_addNyInstitution_html = PageTemplateFile('zpt/institution_manage_add', globals())
#manage_addNyInstitution_html.kind = config['meta_type']
#manage_addNyInstitution_html.action = 'addNyInstitution'
config.update({
    #'constructors': (manage_addNyInstitution_html, addNyInstitution),
    'constructors': (institution_add_html, addNyInstitution),
    'folder_constructors': [
            # NyFolder.manage_addNyInstitution_html = manage_addNyInstitution_html
            #('manage_addNyInstitution_html', manage_addNyInstitution_html),
            ('institution_add_html', institution_add_html),
            ('addNyInstitution', addNyInstitution),
            ('import_institution_item', importNyInstitution),
        ],
    'add_method': addNyInstitution,
    'validation': issubclass(NyInstitution, NyValidation),
    '_class': NyInstitution,
})

def get_config():
    return config
