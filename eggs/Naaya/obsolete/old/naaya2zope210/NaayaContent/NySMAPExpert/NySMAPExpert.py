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
# The Initial Owner of the Original Code is SMAP Clearing House.
# All Rights Reserved.
#
# Authors:
#
# Alexandru Ghica, Eau de Web
# Cornel Nitu, Eau de Web
# Miruna Badescu, Eau de Web
# Alex Morega, Eau de Web

#Python imports
from copy import deepcopy
import os
import sys

#Zope imports
from OFS.Image import File, cookId
from App.ImageFile import ImageFile
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
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyVersioning import NyVersioning
from expert_item import expert_item

#module constants
METATYPE_OBJECT = 'Naaya SMAP Expert'
LABEL_OBJECT = 'Expert'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya SMAP Expert objects'
OBJECT_FORMS = ['expert_add', 'expert_edit', 'expert_index']
OBJECT_CONSTRUCTORS = ['manage_addNySMAPExpert_html', 'expert_add_html', 'addNySMAPExpert', 'importNySMAPExpert']
OBJECT_ADD_FORM = 'expert_add_html'
DESCRIPTION_OBJECT = 'This is Naaya SMAP Expert type.'
PREFIX_OBJECT = 'expert'
PROPERTIES_OBJECT = {
    'id':               (0, '', ''),
    'title':            (0, '', ''),
    'description':      (0, '', ''),
    'coverage':         (0, '', ''),
    'keywords':         (0, '', ''),
    'surname':          (1, MUST_BE_NONEMPTY, 'The Surname field must have a value.'),
    'name':             (1, MUST_BE_NONEMPTY, 'The Name field must have a value.'),
    'ref_lang':         (0, '', ''),
    'country':          (0, '', ''),
    'maintopics':       (0, '', ''),
    'subtopics':        (0, '', ''),
    'sortorder':        (0, MUST_BE_POSITIV_INT, 'The Sort order field must contain a positive integer.'),
    'releasedate':      (0, MUST_BE_DATETIME, 'The Release date field must contain a valid date.'),
    'discussion':       (0, '', ''),
    'file':             (0, '', ''),
    'downloadfilename': (0, '', ''),
    'content_type':     (0, '', ''),
    'email':            (0, '', ''),
    'lang':             (0, '', '')
}
DEFAULT_SCHEMA = {
    'surname':  dict(sortorder=100, widget_type='String', label='Surname', required=True),
    'name':     dict(sortorder=110, widget_type='String', label='Name', required=True),
    'ref_lang': dict(sortorder=120, widget_type='String', label='Working language(s)'),
    'country':  dict(sortorder=130, widget_type='Select', label='Country', list_id='countries'),
    'email':    dict(sortorder=140, widget_type='String', label='Email address'),
}
DEFAULT_SCHEMA.update(deepcopy(NY_CONTENT_BASE_SCHEMA))
DEFAULT_SCHEMA['title'].update(visible=False, required=False)
DEFAULT_SCHEMA['description'].update(visible=False)
DEFAULT_SCHEMA['coverage'].update(visible=False)
DEFAULT_SCHEMA['keywords'].update(visible=False)
DEFAULT_SCHEMA['releasedate'].update(visible=False)
DEFAULT_SCHEMA['discussion'].update(visible=False)
DEFAULT_SCHEMA['sortorder'].update(sortorder=200)

# this dictionary is updated at the end of the module
config = {
        'product': 'NaayaContent',
        'module': 'NySMAPExpert',
        'package_path': os.path.abspath(os.path.dirname(__file__)),
        'meta_type': 'Naaya SMAP Expert',
        'label': 'Expert',
        'permission': 'Naaya - Add Naaya SMAP Expert objects',
        'forms': ['expert_add', 'expert_edit', 'expert_index'],
        'add_form': 'expert_add_html',
        'description': 'This is Naaya SMAP Expert type.',
        'properties': PROPERTIES_OBJECT,
        'default_schema': DEFAULT_SCHEMA,
        'schema_name': 'NySMAPExpert',
        'import_string': 'importNySMAPExpert',
        '_module': sys.modules[__name__],
        'additional_style': None,
        'icon': os.path.join(os.path.dirname(__file__), 'www', 'NySMAPExpert.gif'),
        '_misc': {
                'NySMAPExpert.gif': ImageFile('www/NySMAPExpert.gif', globals()),
                'NySMAPExpert_marked.gif': ImageFile('www/NySMAPExpert_marked.gif', globals()),
            },
    }

def expert_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, METATYPE_OBJECT)
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNySMAPExpert', 'form_helper': form_helper}, 'expert_add')

def _create_NySMAPExpert_object(parent, id, title, file, precondition, content_type, contributor):
    i = 0
    while parent._getOb(id, None):
        i += 1
        id = '%s-%u' % (id, i)
    ob = NySMAPExpert(id, title, file, precondition, content_type, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def addNySMAPExpert(self, id='', REQUEST=None, contributor=None, **kwargs):
    """
    Create a Expert type of object.
    """

    if REQUEST is not None:
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs
    _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
    _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''))

    _file = schema_raw_data.pop('file', '')
    _precondition = schema_raw_data.pop('precondition', '')
    _content_type = schema_raw_data.pop('content_type', '')
    _subtopics = schema_raw_data.pop('subtopics', '')
    _downloadfilename = schema_raw_data.pop('downloadfilename', '')
    _send_notifications = schema_raw_data.pop('_send_notifications', True)

    _subtopics = self.utConvertToList(_subtopics)
    res = {}
    for x in _subtopics:
        res[x.split('|@|')[0]] = ''
    _maintopics = res.keys()

    _title = '%s %s' % (schema_raw_data.get('surname',''), schema_raw_data.get('name',''))
    schema_raw_data['title'] = _title

    #process parameters
    if _downloadfilename == '': _downloadfilename = cookId('', _title, _file)[0]
    if id == '': id = PREFIX_OBJECT + self.utGenRandomId(6)
    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_NySMAPExpert_object(self, id, _title, '', _precondition, _content_type, contributor)

    form_errors = ob.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1]) # pick a random error
        else:
            import transaction; transaction.abort() # because we already called _crete_NyZzz_object
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            REQUEST.RESPONSE.redirect('%s/expert_add_html' % self.absolute_url())
            return

    #process parameters
    if self.glCheckPermissionPublishObjects():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    ob.submitThis()
    ob.approveThis(approved, approved_by)

    ob.subtopics = _subtopics
    ob.maintopics = _maintopics
    ob.downloadfilename = _downloadfilename

    ob.handleUpload(_file)

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
        if l_referer == 'expert_manage_add' or l_referer.find('expert_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'expert_add_html':
            self.setSession('referer', self.absolute_url())
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())

    return ob.getId()

def importNySMAPExpert(self, param, id, attrs, content, properties, discussion, objects):
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

            ob = _create_NyFile_object(self, id, '',
                file=self.utBase64Decode(attrs['file'].encode('utf-8')),
                precondition='',
                content_type='',
                contributor=self.utEmptyToNone(attrs['contributor'].encode('utf-8'))
            )

            ob.sortorder = attrs['sortorder'].encode('utf-8')
            ob.discussion = abs(int(attrs['discussion'].encode('utf-8')))

            ob.surname = attrs['surname'].encode('utf-8')
            ob.name = attrs['name'].encode('utf-8')
            ob.ref_lang = attrs['ref_lang'].encode('utf-8')
            ob.country = attrs['country'].encode('utf-8')
            ob.maintopics = attrs['maintopics'].encode('utf-8')
            ob.subtopics = eval(attrs['subtopics'].encode('utf-8'))
            ob.email = attrs['email'].encode('utf-8')
            ob.sortorder = attrs['sortorder'].encode('utf-8')
            ob.downloadfilename = attrs['downloadfilename'].encode('utf-8')
            ob.discussion = abs(int(attrs['discussion'].encode('utf-8')))

            #set the real content_type and precondition
            ob.content_type = attrs['content_type'].encode('utf-8')
            ob.precondition = attrs['precondition'].encode('utf-8')
            ob._p_changed = 1
            for property, langs in properties.items():
                [ ob._setLocalPropValue(property, lang, langs[lang]) for lang in langs if langs[lang]!='' ]
            ob.approveThis(approved=abs(int(attrs['approved'].encode('utf-8'))),
                approved_by=self.utEmptyToNone(attrs['approved_by'].encode('utf-8')))
            if attrs['releasedate'].encode('utf-8') != '':
                ob.setReleaseDate(attrs['releasedate'].encode('utf-8'))
            ob.import_comments(discussion)
            self.recatalogNyObject(ob)

class NySMAPExpert(expert_item, NyAttributes, NyItem, NyCheckControl, NyContentType):
    """ """

    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT
    icon = 'misc_/NaayaContent/NySMAPExpert.gif'
    icon_marked = 'misc_/NaayaContent/NySMAPExpert_marked.gif'

    def manage_options(self):
        """ """
        l_options = ()
        if not self.hasVersion():
            l_options += ({'label': 'Properties', 'action': 'manage_edit_html'},)
        l_options += expert_item.manage_options
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyItem.manage_options
        #l_options += NyVersioning.manage_options
        return l_options

    security = ClassSecurityInfo()

    def __init__(self, id, title, file, precondition, content_type, contributor):
        """ """
        self.id = id
        expert_item.__init__(self, id, title, precondition, content_type, contributor)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor

    security.declarePrivate('objectkeywords')
    def objectkeywords(self, lang):
        return u' '.join([self._objectkeywords(lang), self.surname, self.name])

    security.declareProtected(view, 'resource_area_exp')
    def resource_area_exp(self):
        return self.maintopics

    security.declareProtected(view, 'resource_focus_exp')
    def resource_focus_exp(self):
        return ' '.join(self.subtopics)

    security.declareProtected(view, 'resource_country')
    def resource_country(self):
        return self.country

    #override handlers
    def manage_afterAdd(self, item, container):
        """
        This method is called, whenever _setObject in ObjectManager gets called.
        """
        NySMAPExpert.inheritedAttribute('manage_afterAdd')(self, item, container)
        self.catalogNyObject(self)

    def manage_beforeDelete(self, item, container):
        """
        This method is called, when the object is deleted.
        """
        NySMAPExpert.inheritedAttribute('manage_beforeDelete')(self, item, container)
        self.uncatalogNyObject(self)

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        return 'surname="%s" name="%s" ref_lang="%s" country="%s" maintopics="%s" subtopics="%s" email="%s" downloadfilename="%s" file="%s" content_type="%s" precondition="%s"' % \
            (self.utXmlEncode(self.surname),
                self.utXmlEncode(self.name),
                self.utXmlEncode(self.ref_lang),
                self.utXmlEncode(self.country),
                self.utXmlEncode(self.maintopics),
                self.utXmlEncode(self.subtopics),
                self.utXmlEncode(self.email),
                self.utXmlEncode(self.downloadfilename),
                self.utBase64Encode(str(self.utNoneToEmpty(self.data))),
                self.utXmlEncode(self.content_type),
                self.utXmlEncode(self.precondition))

    security.declarePrivate('syndicateThis')
    def syndicateThis(self, lang=None):
        r = []
        ra = r.append
        l_site = self.getSite()
        if lang is None: lang = self.gl_get_selected_language()
        ra(self.syndicateThisHeader())
        ra(self.syndicateThisCommon(lang))
        ra('<dc:type>Text</dc:type>')
        ra('<dc:format>application</dc:format>')
        ra('<dc:source>%s</dc:source>' % self.utXmlEncode(l_site.getLocalProperty('publisher', lang)))
        ra('<dc:creator>%s</dc:creator>' % self.utXmlEncode(l_site.getLocalProperty('creator', lang)))
        ra('<dc:publisher>%s</dc:publisher>' % self.utXmlEncode(l_site.getLocalProperty('publisher', lang)))
        ra(self.syndicateThisFooter())
        return ''.join(r)

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if self.wl_isLocked():
            raise ResourceLockedError, "File is locked via WebDAV"

        if REQUEST is not None:
            schema_raw_data = dict(REQUEST.form)
        else:
            schema_raw_data = kwargs
        _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
        _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''), self.releasedate)
        _approved = int(bool(schema_raw_data.pop('approved', False)))

        _content_type = schema_raw_data.pop('content_type', '')
        _precondition = schema_raw_data.pop('precondition', '')
        _subtopics = schema_raw_data.pop('subtopics', '')

        _subtopics = self.utConvertToList(_subtopics)
        res = {}
        for x in _subtopics:
            res[x.split('|@|')[0]] = ''
        _maintopics = res.keys()

        schema_raw_data['title'] = self.title

        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)
        if form_errors:
            raise ValueError(form_errors.popitem()[1]) # pick a random error

        self.content_type = _content_type
        self.precondition = _precondition
        self.subtopics = _subtopics
        self.maintopics = _maintopics

        if _approved != self.approved:
            if _approved == 0: _approved_by = None
            else: _approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
            self.approveThis(_approved, _approved_by)
        self._p_changed = 1
        if self.discussion: self.open_for_comments()
        else: self.close_for_comments()
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_main?save=ok')

    security.declareProtected(view_management_screens, 'manageUpload')
    def manageUpload(self, file='', REQUEST=None):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if self.wl_isLocked():
            raise ResourceLockedError, "File is locked via WebDAV"
        self.downloadfilename = self.handleUpload(file)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    security.declareProtected(view_management_screens, 'manage_upload')
    def manage_upload(self):
        """ """
        raise EXCEPTION_NOTACCESIBLE, 'manage_upload'

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
        self.copy_naaya_properties_from(self.version)
        self.update_data(self.version.data, self.version.content_type)
        self.checkout = 0
        self.checkout_user = None
        self.version = None
        #self.createVersion(self.REQUEST.AUTHENTICATED_USER.getUserName())
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
        self.version = expert_item(self.id, self.title, '', self.precondition, '')
        self.version.copy_naaya_properties_from(self)
        self.version.update_data(self.data, self.content_type)
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

        _source = schema_raw_data.pop('source', 'file')
        _file = schema_raw_data.pop('file', '')
        _url = schema_raw_data.pop('url', '')
        _precondition = schema_raw_data.pop('precondition', '')
        _version = schema_raw_data.pop('version', False)

        _content_type = schema_raw_data.pop('content_type', '')
        _precondition = schema_raw_data.pop('precondition', '')
        _subtopics = schema_raw_data.pop('subtopics', '')

        _subtopics = self.utConvertToList(_subtopics)
        res = {}
        for x in _subtopics:
            res[x.split('|@|')[0]] = ''
        _maintopics = res.keys()

        schema_raw_data['title'] = obj.title

        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

        if form_errors:
            if REQUEST is not None:
                self._prepare_error_response(REQUEST, form_errors, schema_raw_data)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))
                return
            else:
                raise ValueError(form_errors.popitem()[1]) # pick a random error

        obj.content_type = _content_type
        obj.precondition = _precondition
        obj.subtopics = _subtopics
        obj.maintopics = _maintopics

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

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveUpload')
    def saveUpload(self, file='', lang=None, REQUEST=None):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if self.wl_isLocked():
            raise ResourceLockedError, "File is locked via WebDAV"
        if lang is None: lang = self.gl_get_selected_language()
        if not self.hasVersion():
            #this object has not been checked out; save changes directly into the object
            self.downloadfilename = self.handleUpload(file)
            #if version: self.createVersion(self.REQUEST.AUTHENTICATED_USER.getUserName())
        else:
            #this object has been checked out; save changes into the version object
            if self. checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName():
                raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
            self.version.downloadfilename = self.version.handleUpload(file)
        self.recatalogNyObject(self)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/expert_manage_edit', globals())

    #site actions
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'expert_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'expert_edit')

    security.declareProtected(view, 'download')
    def download(self, REQUEST, RESPONSE):
        """ """
        self.REQUEST.RESPONSE.setHeader('Content-Type', self.content_type)
        self.REQUEST.RESPONSE.setHeader('Content-Length', self.size)
        self.REQUEST.RESPONSE.setHeader('Content-Disposition', self.ut_content_disposition(self.downloadfilename))
        return expert_item.inheritedAttribute('index_html')(self, REQUEST, RESPONSE)

    security.declareProtected(view, 'view')
    def view(self, REQUEST, RESPONSE):
        """ """
        self.REQUEST.RESPONSE.setHeader('Content-Type', self.content_type)
        self.REQUEST.RESPONSE.setHeader('Content-Length', self.size)
        return expert_item.inheritedAttribute('index_html')(self, REQUEST, RESPONSE)

InitializeClass(NySMAPExpert)

manage_addNySMAPExpert_html = PageTemplateFile('zpt/expert_manage_add', globals())
manage_addNySMAPExpert_html.kind = METATYPE_OBJECT
manage_addNySMAPExpert_html.action = 'addNySMAPExpert'
config.update({
    'constructors': (manage_addNySMAPExpert_html, addNySMAPExpert),
    'folder_constructors': [
            # NyFolder.manage_addNySMAPExpert_html = manage_addNySMAPExpert_html
            ('manage_addNySMAPExpert_html', manage_addNySMAPExpert_html),
            ('expert_add_html', expert_add_html),
            ('addNySMAPExpert', addNySMAPExpert),
            (config['import_string'], importNySMAPExpert),
        ],
    'add_method': addNySMAPExpert,
    'validation': issubclass(NySMAPExpert, NyValidation),
    '_class': NySMAPExpert,
})

def get_config():
    return config
