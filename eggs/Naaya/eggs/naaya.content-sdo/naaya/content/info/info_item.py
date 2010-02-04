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
from OFS.SimpleItem import Item
from zope.event import notify
from naaya.content.base.events import NyContentObjectAddEvent, NyContentObjectEditEvent

#Product imports
from Products.NaayaBase.NyContentType import NyContentType, NY_CONTENT_BASE_SCHEMA, get_schema_helper_for_metatype
from naaya.content.base.constants import *
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaBase.NyContentType import NyContentData
from Products.NaayaCore.managers.utils import utils, make_id
from Products.NaayaCore.interfaces import ICSVImportExtraColumns
from Products.Localizer.LocalPropertyManager import LocalProperty

import naaya.content.infofolder.skel as skel

#module constants
METATYPE_OBJECT = 'Naaya Info'
LABEL_OBJECT = 'Info'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya Info objects'
OBJECT_FORMS = ['info_add', 'info_edit', 'info_index']
OBJECT_CONSTRUCTORS = ['add_html', 'addNyInfo']
OBJECT_ADD_FORM = 'add_html'
DESCRIPTION_OBJECT = 'This is Naaya Info type.'
PREFIX_OBJECT = 'Info'
ADDITIONAL_STYLE = open(ImageFile('www/Info.css', globals()).path).read()

DEFAULT_SCHEMA = {
    'website':               dict(sortorder=11, widget_type='String',
                label='Website url',required=True),
    'organisation':          dict(sortorder=20, widget_type='String',
                label='Organisation',localized=True),
    'city':                  dict(sortorder=25, widget_type='String',
                label='City',localized=True),
    'country':               dict(sortorder=30, widget_type='Select',
                label='Country',localized=True,list_id='countries'),
    'email':                 dict(sortorder=35, widget_type='String', label='Email'),
    'contributor_first_name':dict(sortorder=55, widget_type='String', label='First name'),
    'contributor_last_name': dict(sortorder=60, widget_type='String', label='Last name'),
    'contributor_email':     dict(sortorder=65, widget_type='String', label='Email'),
    'contributor_telephone': dict(sortorder=70, widget_type='String', label='Telephone'),
}

DEFAULT_SCHEMA.update(deepcopy(NY_CONTENT_BASE_SCHEMA))
DEFAULT_SCHEMA['title'].update(sortorder=10, label='Support title', localized=True)
DEFAULT_SCHEMA['description'].update(sortorder=40)
DEFAULT_SCHEMA['coverage'].update(visible=False)
DEFAULT_SCHEMA['keywords'].update(visible=False)
DEFAULT_SCHEMA['releasedate'].update(visible=False)
DEFAULT_SCHEMA['discussion'].update(visible=False)
DEFAULT_SCHEMA['sortorder'].update(visible=False)

# this dictionary is updated at the end of the module
config = {
        'product': 'NaayaContent',
        'module': 'info_item',
        'package_path': os.path.abspath(os.path.dirname(__file__)),
        'meta_type': METATYPE_OBJECT,
        'label': LABEL_OBJECT,
        'permission': PERMISSION_ADD_OBJECT,
        'forms': OBJECT_FORMS,
        'add_form': OBJECT_ADD_FORM,
        'description': DESCRIPTION_OBJECT,
        'default_schema': DEFAULT_SCHEMA,
        'schema_name': 'NyInfo',
        '_module': sys.modules[__name__],
        'icon': os.path.join(os.path.dirname(__file__), 'www', 'NyInfo.gif'),
        'additional_style': ADDITIONAL_STYLE,
        '_misc': {
                'NyInfo.gif': ImageFile('www/NyInfo.gif', globals()),
                'NyInfo_marked.gif': ImageFile('www/NyInfo_marked.gif', globals()),
            },
    }

def add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    form_helper = get_schema_helper_for_metatype(self, METATYPE_OBJECT)
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT,
                                            'action': 'addNyInfo', 'form_helper': form_helper},
                                            'info_add')

def _create_object(parent, id, title, contributor):
    ob = NyInfo(id, title, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def addNyInfo(self, id='', REQUEST=None, contributor=None, **kwargs):
    """
    Create a Info type of object.
    """
    if REQUEST is not None:
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs
    _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
    _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''))
    _send_notifications = schema_raw_data.pop('_send_notifications', True)
    _title = schema_raw_data['title']
    #process parameters
    id = make_id(self, id=id, title=_title, prefix=PREFIX_OBJECT)
    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_object(self, id, _title, contributor)

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
            REQUEST.RESPONSE.redirect('%s/add_html' % self.absolute_url())
            return

    #process parameters
    if self.glCheckPermissionPublishObjects():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    ob.approveThis(approved, approved_by)
    ob.submitThis()

    if ob.discussion: ob.open_for_comments()

    notify(NyContentObjectAddEvent(ob, contributor, schema_raw_data))
    #log post date
    auth_tool = self.getAuthenticationTool()
    auth_tool.changeLastPost(contributor)
    #redirect if case
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect('%s/%s' % (self.absolute_url(), ob.id))
    return ob.getId()

class info_item(Implicit, NyContentData):
    """ """

class NyInfo(info_item, NyAttributes, NyItem, NyCheckControl, NyValidation, NyContentType):
    """ """
    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT
    icon = 'misc_/NaayaContent/NyInfo.gif'
    icon_marked = 'misc_/NaayaContent/NyInfo_marked.gif'

    def manage_options(self):
        """ """
        l_options = ()
        l_options += info_item.manage_options
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyItem.manage_options
        return l_options

    security = ClassSecurityInfo()

    def __init__(self, id, title, contributor):
        """ """
        self.id = id
        info_item.__init__(self)
        NyValidation.__dict__['__init__'](self)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor

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

        schema_raw_data['title'] = self.title

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
        if REQUEST: REQUEST.RESPONSE.redirect('manage_main?save=ok')

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

        schema_raw_data['title'] = obj.title

        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

        if form_errors:
            if REQUEST is not None:
                self._prepare_error_response(REQUEST, form_errors, schema_raw_data)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))
                return
            else:
                raise ValueError(form_errors.popitem()[1]) # pick a random error

        if self.discussion: self.open_for_comments()
        else: self.close_for_comments()

        self._p_changed = 1
        self.recatalogNyObject(self)
        #log date
        contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
        auth_tool = self.getAuthenticationTool()
        auth_tool.changeLastPost(contributor)
        notify(NyContentObjectEditEvent(self, contributor))
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))

    #site actions
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'info_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'info_edit')

    def get_property_values(self, property_id):
        """ returns the values of the ref_list items if there is a reflist with the given id
        or the values of the propery"""
        property_ids = self.utConvertToList(getattr(self, property_id))
        try:
            ref_list_items = self.get_ref_list_items(property_id)
            property_values = [ref_list_item.title for ref_list_item in ref_list_items if ref_list_item.id in property_ids]
        except:
            property_values = property_ids
        return property_values

    def get_ref_list_items(self, ref_list_id):
        ref_list_items = self.get_ref_list(ref_list_id)
        return ref_list_items.get_list()

    def get_ref_list(self, ref_list_id):
        ptool = self.getPortletsTool()
        ref_list = getattr(ptool, ref_list_id, None)
        return ref_list

InitializeClass(NyInfo)

config.update({
    'constructors': (add_html, addNyInfo),
    'folder_constructors': [
            ('add_html', add_html),
            ('addNyInfo', addNyInfo),
        ],
    'add_method': addNyInfo,
    'validation': issubclass(NyInfo, NyValidation),
    '_class': NyInfo,
})

def get_config():
    return config
