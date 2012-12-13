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
import simplejson as json
from decimal import Decimal

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
from Products.NaayaBase.NyContentType import NyContentType, NyContentData, NY_CONTENT_BASE_SCHEMA, get_schema_helper_for_metatype
#from naaya.content.base.constants import *
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaCore.interfaces import ICSVImportExtraColumns
from Products.NaayaCore.GeoMapTool.managers import geocoding
from Products.NaayaCore.SchemaTool.widgets.geo import Geo
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from naaya.i18n.LocalPropertyManager import LocalProperty

import naaya.content.infofolder.skel as skel
from naaya.content.infofolder.permissions import PERMISSION_EDIT_INFO

#module constants
METATYPE_OBJECT = 'Naaya Info'
LABEL_OBJECT = 'Info'
PREFIX_OBJECT = 'Info'

DEFAULT_SCHEMA = {
    'website':               dict(sortorder=11, widget_type='String',
                label='Website url',required=True),
    'organisation_name':          dict(sortorder=20, widget_type='String',
                label='Organisation name',localized=True),
    'organisation_city':                  dict(sortorder=25, widget_type='String',
                label='Organisation city',localized=True),
    'organisation_country':               dict(sortorder=30, widget_type='Select',
                label='Organisation country',localized=True,list_id='countries'),
    'organisation_email':                 dict(sortorder=35, widget_type='String',
                label='Organisation email'),
    'contributor_first_name':dict(sortorder=45, widget_type='String',
                label='Contributor first name'),
    'contributor_last_name': dict(sortorder=50, widget_type='String',
                label='Contributor last name'),
    'contributor_email':     dict(sortorder=55, widget_type='String',
                label='Contributor email'),
    'contributor_telephone': dict(sortorder=60, widget_type='String',
                label='Contributor telephone'),
    'original_sdo_id':                dict(sortorder=75, widget_type='String',
                label='SDO Id', visible=False),
}

DEFAULT_SCHEMA.update(deepcopy(NY_CONTENT_BASE_SCHEMA))
DEFAULT_SCHEMA['title'].update(sortorder=10, label='Support title', localized=True)
DEFAULT_SCHEMA['description'].update(sortorder=40)
DEFAULT_SCHEMA['coverage'].update(visible=False)
DEFAULT_SCHEMA['keywords'].update(visible=False)
DEFAULT_SCHEMA['releasedate'].update(visible=False)
DEFAULT_SCHEMA['sortorder'].update(visible=False)
#DEFAULT_SCHEMA['geo_location'].update(visible=True)

sdo_info_add = NaayaPageTemplateFile('zpt/info_add', globals(), 'sdo_info_add')

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
        l_options += ({'label': 'Properties', 'action': 'edit_html'},)
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

    security.declarePrivate('objectkeywords')
    def objectkeywords(self, lang):
        return u' '.join([self._objectkeywords(lang), 
                        self.getLocalProperty('organisation_name', lang), 
                        self.getLocalProperty('organisation_city', lang),
                        self.getLocalProperty('organisation_country', lang),])

    security.declareProtected(PERMISSION_EDIT_INFO, 'saveProperties')
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

        self.last_modification = time.localtime()

        #geo-location: 'geo_location' should always be removed from the schema_raw_data
        #because the form should contain 'geo_location.lat' type of data
        if schema_raw_data.has_key('geo_location'):
            schema_raw_data.pop('geo_location')
        _city = schema_raw_data.get('organisation_city', None)
        _country = schema_raw_data.get('organisation_country', None)
        _address = ''
        if _city or _country:
            _address = _city + ', ' + _country
        if _address:
            old_geo_location = self.geo_location not in (None, Geo()) and self.geo_location.address != _address
            no_geo_location = self.geo_location in (None, Geo())
            if old_geo_location or no_geo_location:
                _lat, _lon = self.do_geocoding(_address)
            else:
                _lat, _lon = self.geo_location.lat, self.geo_location.lon
            schema_raw_data['geo_location.lat'] = _lat
            schema_raw_data['geo_location.lon'] = _lon
            schema_raw_data['geo_location.address'] = _address

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
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))

    #site actions
    security.declareProtected(view, 'index_html')
    index_html = NaayaPageTemplateFile('zpt/info_index', globals(), 'sdo_info_index')

    security.declareProtected(PERMISSION_EDIT_INFO, 'edit_html')
    edit_html = NaayaPageTemplateFile('zpt/info_edit', globals(), 'sdo_info_edit')

    def get_property_values(self, property_id):
        """ returns the values of the ref_list items if there is a reflist with the given id
        or the values of the property"""
        property_ids = getattr(self, property_id)
        if property_ids:
            property_ids = self.utConvertToList(property_ids)
        else:
            return []
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

    def do_geocoding(self, address):
        coordinates = geocoding.location_geocode(address)
        if coordinates != None:
            return coordinates
        return ('', '')

    _minimap_template = PageTemplateFile('zpt/minimap', globals())
    def minimap(self):
        if self.geo_location not in (None, Geo()):
            simplepoints = [{'lat': self.geo_location.lat, 'lon': self.geo_location.lon}]
        else:
            return ""
        json_simplepoints = json.dumps(simplepoints, default=json_encode)
        return self._minimap_template(points=json_simplepoints)

    def has_coordinates(self):
        """ check if the current object has map coordinates"""
        if self.geo_location:
            return self.geo_location.lat and self.geo_location.lon
        return False

    def has_organisation_details(self):
        """ check if the current object has any contact details"""
        if self.organisation_name or self.organisation_city or\
            self.organisation_country or self.organisation_email:
            return True
        return False

    def has_contributor(self):
        """ check if the current object has any contributor details"""
        if self.contributor_first_name or self.contributor_last_name or\
            self.contributor_email or self.contributor_telephone:
            return True
        return False

    def has_properties(self):
        """ check if the current object has any properties or extra properties"""
        category_ids = [info_category['property_id'] for info_category in\
            self.folder_categories+self.folder_extra_properties]
        for category_id in category_ids:
            if self.get_property_values(category_id):
                return True
        return False

InitializeClass(NyInfo)

def json_encode(ob):
    """ try to encode some known value types to JSON """
    if isinstance(ob, Decimal):
        return float(ob)
    raise ValueError

