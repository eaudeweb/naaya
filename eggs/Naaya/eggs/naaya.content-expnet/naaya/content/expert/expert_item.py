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
# Valentin Dumitru, Eau de Web

#Python imports
from copy import deepcopy
import os
import sys

#Zope imports
from Globals import InitializeClass
from App.ImageFile import ImageFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Acquisition import Implicit

#Product imports
from Products.NaayaBase.NyContentType import NyContentType, NY_CONTENT_BASE_SCHEMA
from naaya.content.base.constants import *
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaBase.NyContentType import NyContentData

#module constants
METATYPE_OBJECT = 'Naaya Expert'
LABEL_OBJECT = 'Expert'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya Expert objects'
OBJECT_FORMS = ['expert_add', 'expert_edit', 'expert_index']
OBJECT_CONSTRUCTORS = ['expert_add_html', 'addNyExpert']
OBJECT_ADD_FORM = 'expert_add_html'
DESCRIPTION_OBJECT = 'This is Naaya Expert type.'
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
    'content_type':     (0, '', ''),
    'email':            (0, '', ''),
    'lang':             (0, '', '')
}
DEFAULT_SCHEMA = {
    'surname':  dict(sortorder=100, widget_type='String', label='Surname', required=True, localized=True),
    'name':     dict(sortorder=110, widget_type='String', label='Name', required=True, localized=True),
    'ref_lang': dict(sortorder=120, widget_type='String', label='Working language(s)', localized=True),
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
        'module': 'expert_item',
        'package_path': os.path.abspath(os.path.dirname(__file__)),
        'meta_type': METATYPE_OBJECT,
        'label': LABEL_OBJECT,
        'permission': PERMISSION_ADD_OBJECT,
        'forms': OBJECT_FORMS,
        'add_form': OBJECT_ADD_FORM,
        'description': DESCRIPTION_OBJECT,
        'properties': PROPERTIES_OBJECT,
        'default_schema': DEFAULT_SCHEMA,
        'schema_name': 'NyExpert',
        'import_string': 'importNyExpert',
        '_module': sys.modules[__name__],
        'additional_style': None,
        'icon': os.path.join(os.path.dirname(__file__), 'www', 'NyExpert.gif'),
        '_misc': {
                'NyExpert.gif': ImageFile('www/NyExpert.gif', globals()),
                'NyExpert_marked.gif': ImageFile('www/NyExpert_marked.gif', globals()),
            },
    }

def expert_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, METATYPE_OBJECT)
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNyExpert', 'form_helper': form_helper}, 'expert_add')

def _create_NyExpert_object(parent, id, title, content_type, contributor):
    i = 0
    while parent._getOb(id, None):
        i += 1
        id = '%s-%u' % (id, i)
    ob = NyExpert(id, title, content_type, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def addNyExpert(self, id='', REQUEST=None, contributor=None, **kwargs):
    """
    Create a Expert type of object.
    """

    if REQUEST is not None:
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs
    _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
    _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''))

    _content_type = schema_raw_data.pop('content_type', '')
    _subtopics = schema_raw_data.pop('subtopics', '')
    _send_notifications = schema_raw_data.pop('_send_notifications', True)

    _subtopics = self.utConvertToList(_subtopics)
    res = {}
    for x in _subtopics:
        res[x.split('|@|')[0]] = ''
    _maintopics = res.keys()

    _title = '%s %s' % (schema_raw_data.get('surname',''), schema_raw_data.get('name',''))
    schema_raw_data['title'] = _title
    _contact_word = schema_raw_data.get('contact_word', '')

    #process parameters
    id = self.utCleanupId(id)
    if not id: id = self.utGenObjectId(_title)
    if not id: id = 'expert' + self.utGenRandomId(5)

    if id == '': id = PREFIX_OBJECT + self.utGenRandomId(6)
    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_NyExpert_object(self, id, _title, _content_type, contributor)

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
            REQUEST.RESPONSE.redirect('%s/expert_add_html' % self.absolute_url())
            return

    #process parameters
    if self.glCheckPermissionPublishObjects():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    ob.approveThis(approved, approved_by)
    ob.submitThis()

    ob.subtopics = _subtopics
    ob.maintopics = _maintopics

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

def importNyExpert(self, param, id, attrs, content, properties, discussion, objects):
    #this method is called during the import process
    raise NotImplementedError

class expert_item(Implicit, NyContentData):
    """ """

class NyExpert(expert_item, NyAttributes, NyItem, NyCheckControl, NyValidation, NyContentType):
    """ """
    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT
    icon = 'misc_/NaayaContent/NyExpert.gif'
    icon_marked = 'misc_/NaayaContent/NyExpert_marked.gif'

    def manage_options(self):
        """ """
        l_options = ()
        l_options += expert_item.manage_options
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyItem.manage_options
        #l_options += NyVersioning.manage_options
        return l_options

    security = ClassSecurityInfo()

    def __init__(self, id, title, content_type, contributor):
        """ """
        self.id = id
        expert_item.__init__(self)
        NyValidation.__dict__['__init__'](self)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        raise NotImplementedError

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

        _content_type = schema_raw_data.pop('content_type', '')
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

    #site actions
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'commitVersion')
    def commitVersion(self, REQUEST=None):
        """ """
        raise NotImplementedError

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'startVersion')
    def startVersion(self, REQUEST=None):
        """ """
        raise NotImplementedError

    def isVersionable(self):
        """ Expert objects are not versionable
        """
        return False

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
        _url = schema_raw_data.pop('url', '')
        _version = schema_raw_data.pop('version', False)

        _content_type = schema_raw_data.pop('content_type', '')
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

    #site actions
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'expert_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'expert_edit')

InitializeClass(NyExpert)

config.update({
    'constructors': (expert_add_html, addNyExpert),
    'folder_constructors': [
            ('expert_add_html', expert_add_html),
            ('addNyExpert', addNyExpert),
            (config['import_string'], importNyExpert),
        ],
    'add_method': addNyExpert,
    'validation': issubclass(NyExpert, NyValidation),
    '_class': NyExpert,
})

def get_config():
    return config
