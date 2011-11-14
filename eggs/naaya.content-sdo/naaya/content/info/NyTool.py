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
import os, sys, time
import transaction

#Zope imports
from Globals import InitializeClass
from App.ImageFile import ImageFile
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zope.event import notify
from naaya.content.base.events import NyContentObjectAddEvent, NyContentObjectEditEvent

#Product imports
from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaCore.managers.utils import make_id

from info_item import NyInfo, DEFAULT_SCHEMA
from naaya.content.infofolder import skel
from naaya.content.infofolder.permissions import PERMISSION_ADD_INFO

#module constants
INFO_TYPE = skel.INFO_TYPES['tools']
METATYPE_OBJECT = INFO_TYPE['meta_type']
LABEL_OBJECT = INFO_TYPE['meta_label']
PREFIX_OBJECT = INFO_TYPE['prefix']
OBJECT_FORMS = []
OBJECT_CONSTRUCTORS = ['sdo_info_add', 'addNyTool']
OBJECT_ADD_FORM = 'tool_add_html'
DESCRIPTION_OBJECT = 'This is Naaya Tool type.'

DEFAULT_SCHEMA = deepcopy(DEFAULT_SCHEMA)

#Define folder categories
DEFAULT_SCHEMA['sdo_tool_type'] = dict(sortorder=12, widget_type='Select',
                label='Tool type', list_id='sdo_tool_type', property_type='Sdo category')
DEFAULT_SCHEMA['sdo_tool_sort'] = dict(sortorder=13, widget_type='Select',
                label='Tool sort', list_id='sdo_tool_sort', property_type='Sdo category')

#Define folder extra properties
# None

# this dictionary is updated at the end of the module
config = {
        'product': 'NaayaContent', 
        'module': 'NyTool',
        'package_path': os.path.abspath(os.path.dirname(__file__)),
        'meta_type': METATYPE_OBJECT,
        'label': LABEL_OBJECT,
        'permission': PERMISSION_ADD_INFO,
        'forms': OBJECT_FORMS,
        'add_form': OBJECT_ADD_FORM,
        'description': DESCRIPTION_OBJECT,
        'default_schema': DEFAULT_SCHEMA,
        'schema_name': 'NyTool',
        '_module': sys.modules[__name__],
        'icon': os.path.join(os.path.dirname(__file__), 'www', 'NyInfo.gif'),
        '_misc': {
                'NyInfo.gif': ImageFile('www/NyInfo.gif', globals()),
                'NyInfo_marked.gif': ImageFile('www/NyInfo_marked.gif', globals()),
            },
    }

def tool_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    form_helper = get_schema_helper_for_metatype(self, METATYPE_OBJECT)
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT,
             'action': 'addNyTool', 'form_helper': form_helper}, 'sdo_info_add')

def _create_object(parent, id, title, contributor):
    ob = NyTool(id, title, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def addNyTool(self, id='', REQUEST=None, contributor=None, **kwargs):
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
    _contact_word = schema_raw_data.get('contact_word', '')

    #process parameters
    id = make_id(self, id=id, title=_title, prefix=PREFIX_OBJECT)
    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_object(self, id, _title, contributor)
    ob.last_modification = time.localtime()

    _city = schema_raw_data.get('organisation_city', None)
    _country = schema_raw_data.get('organisation_country', None)
    if _city or _country:
        #remove the empty geo_location string (default when the geo_location widget is hidden)
        if schema_raw_data.get('geo_location', None) == '':
            schema_raw_data.pop('geo_location')
        _address = _city + ', ' + _country
        schema_raw_data['geo_location.lat'], schema_raw_data['geo_location.lon'] = ob.do_geocoding(_address)
        schema_raw_data['geo_location.address'] = _address

    form_errors = ob.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

    #ON IMPORT:
    if REQUEST is None:
        #Overwrite the values of properties attached to single select lists
        #if the import data contains several values...
        for k, v in DEFAULT_SCHEMA.items():
            if DEFAULT_SCHEMA[k].has_key('property_type') and\
                DEFAULT_SCHEMA[k]['property_type'] in ['Sdo category', 'Sdo extra property']:
                if v['widget_type'] == 'Select':
                    if len(schema_raw_data[k]) == 1:
                        setattr(ob, k, schema_raw_data[k][0])
                    else:
                        setattr(ob, k, schema_raw_data[k])

    #check Captcha/reCaptcha
    if not self.checkPermissionSkipCaptcha():
        captcha_validator = self.validateCaptcha(_contact_word, REQUEST)
        if captcha_validator:
            form_errors['captcha'] = captcha_validator
    
    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1]) # pick a random error
        else:
            transaction.abort() # because we already called _crete_NyZzz_object
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            REQUEST.RESPONSE.redirect('%s/tool_add_html' % self.absolute_url())
            return

    #process parameters
    if self.glCheckPermissionPublishObjects():
        if REQUEST is None:
            approved = schema_raw_data.get('approved', 0)
            approved_by = schema_raw_data.get('approved_by', None)
        else:
            approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    ob.approveThis(approved, approved_by)
    ob.submitThis()

    if ob.discussion: ob.open_for_comments()

    self.recatalogNyObject(ob)
    notify(NyContentObjectAddEvent(ob, contributor, schema_raw_data))
    #log post date
    auth_tool = self.getAuthenticationTool()
    auth_tool.changeLastPost(contributor)
    #redirect if case
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect('%s/%s' % (self.absolute_url(), ob.id))
    transaction.commit()
    return ob.getId()

class NyTool(NyInfo):
    """ """
    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT

    def __init__(self, id, title, contributor):
        """ """
        self.id = id
        NyInfo.__dict__['__init__'](self, id, title, contributor)
        self.contributor = contributor

InitializeClass(NyTool)

config.update({
    'constructors': (tool_add_html, addNyTool),
    'folder_constructors': [
            ('tool_add_html', tool_add_html),
            ('addNyTool', addNyTool),
        ],
    'add_method': addNyTool,
    'validation': issubclass(NyTool, NyValidation),
    '_class': NyTool,
})

def get_config():
    return config
