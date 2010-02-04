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
from zope.event import notify
from naaya.content.base.events import NyContentObjectAddEvent, NyContentObjectEditEvent

#Product imports
from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaBase.constants import *
from Products.NaayaCore.managers.utils import utils, make_id

import info_item
from naaya.content.infofolder import skel

#module constants
INFO_TYPE = skel.INFO_TYPES['enterprises']
METATYPE_OBJECT = INFO_TYPE['meta_type']
LABEL_OBJECT = INFO_TYPE['meta_label']
PREFIX_OBJECT = INFO_TYPE['prefix']
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya Enterprise objects'
OBJECT_FORMS = ['enterprise_add', 'enterprise_edit', 'enterprise_index']
OBJECT_CONSTRUCTORS = ['add_html', 'addNyEnterprise']
OBJECT_ADD_FORM = 'add_html'
DESCRIPTION_OBJECT = 'This is Naaya Enterprise type.'

DEFAULT_SCHEMA = deepcopy(info_item.DEFAULT_SCHEMA)
DEFAULT_SCHEMA['sdo_type_of_initiative'] = dict(sortorder=12, widget_type='Select',
                label='Type of initiative', localized=True, list_id='sdo_type_of_initiative')
DEFAULT_SCHEMA['sdo_nature_of_initiative'] = dict(sortorder=13, widget_type='SelectMultiple',
                label='Nature of initiative', localized=True, list_id='sdo_nature_of_initiative')
DEFAULT_SCHEMA['sdo_topic_coverage'] = dict(sortorder=14, widget_type='SelectMultiple',
                label='Topic coverage', localized=True, list_id='sdo_topic_coverage')
DEFAULT_SCHEMA['sdo_services'] = dict(sortorder=15, widget_type='SelectMultiple',
                label='Services', localized=True, list_id='sdo_services')
DEFAULT_SCHEMA['sdo_geographic_scope'] = dict(sortorder=16, widget_type='SelectMultiple',
                label='Geographic scope', localized=True, list_id='sdo_geographic_scope')


# this dictionary is updated at the end of the module
config = {
        'product': 'NaayaContent', 
        'module': 'NyEnterprise',
        'package_path': os.path.abspath(os.path.dirname(__file__)),
        'meta_type': METATYPE_OBJECT,
        'label': LABEL_OBJECT,
        'permission': PERMISSION_ADD_OBJECT,
        'forms': OBJECT_FORMS,
        'add_form': OBJECT_ADD_FORM,
        'description': DESCRIPTION_OBJECT,
        'default_schema': DEFAULT_SCHEMA,
        'schema_name': 'NyEnterprise',
        '_module': sys.modules[__name__],
        'icon': os.path.join(os.path.dirname(__file__), 'www', 'NyInfo.gif'),
        '_misc': {
                'NyInfo.gif': ImageFile('www/NyInfo.gif', globals()),
                'NyInfo_marked.gif': ImageFile('www/NyInfo_marked.gif', globals()),
            },
    }

def add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    form_helper = get_schema_helper_for_metatype(self, METATYPE_OBJECT)
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT,
             'action': 'addNyEnterprise', 'form_helper': form_helper}, 'info_add')

def _create_object(parent, id, title, contributor):
    ob = NyEnterprise(id, title, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def addNyEnterprise(self, id='', REQUEST=None, contributor=None, **kwargs):
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

class NyEnterprise(info_item.NyInfo):
    """ """
    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT

    security = ClassSecurityInfo()

    def __init__(self, id, title, contributor):
        """ """
        self.id = id
        NyValidation.__dict__['__init__'](self)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor

    #site actions
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'info_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'info_edit')

InitializeClass(NyEnterprise)

config.update({
    'constructors': (add_html, addNyEnterprise),
    'folder_constructors': [
            ('add_html', add_html),
            ('addNyEnterprise', addNyEnterprise),
        ],
    'add_method': addNyEnterprise,
    'validation': issubclass(NyEnterprise, NyValidation),
    '_class': NyEnterprise,
})

def get_config():
    return config
