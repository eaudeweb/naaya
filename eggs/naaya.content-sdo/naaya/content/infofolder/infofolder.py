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
# Valentin Dumitru, Eau de Web
from Products.NaayaBase.constants import EXCEPTION_NOTAUTHORIZED,\
    EXCEPTION_NOTAUTHORIZED_MSG, PERMISSION_EDIT_OBJECTS, MESSAGE_SAVEDCHANGES,\
    EXCEPTION_STARTEDVERSION, EXCEPTION_STARTEDVERSION_MSG, EXCEPTION_NOVERSION,\
    EXCEPTION_NOVERSION_MSG

#Python imports
from datetime import datetime
from copy import deepcopy
import os, sys
import simplejson as json
from decimal import Decimal

#Zope imports
from Globals import InitializeClass
from App.ImageFile import ImageFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Acquisition import Implicit
from OFS.SimpleItem import Item
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zope.event import notify 
from naaya.content.base.events import NyContentObjectAddEvent, NyContentObjectEditEvent

#Product imports
from Products.NaayaBase.NyContentType import NyContentType, NY_CONTENT_BASE_SCHEMA
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaBase.NyContentType import NyContentData
from Products.NaayaBase.NyContainer import NyContainer
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from Products.NaayaCore.SchemaTool.widgets.geo import Geo
from Products.NaayaCore.managers.utils import make_id

from naaya.content.info import info_item

from constants import *
from skel import URL_CATEGORIES, EXTRA_PROPERTIES_LISTS
LISTS = URL_CATEGORIES + EXTRA_PROPERTIES_LISTS

METATYPE_OBJECT = 'Naaya InfoFolder'
ADDITIONAL_STYLE = open(ImageFile('www/InfoFolder.css', globals()).path).read()

DEFAULT_SCHEMA = deepcopy(NY_CONTENT_BASE_SCHEMA)
DEFAULT_SCHEMA['geo_location'].update(visible=True, sortorder=210)
DEFAULT_SCHEMA['coverage'].update(visible=False)
DEFAULT_SCHEMA['keywords'].update(visible=False)
DEFAULT_SCHEMA['releasedate'].update(visible=False)
DEFAULT_SCHEMA['discussion'].update(visible=False)
DEFAULT_SCHEMA['sortorder'].update(visible=False)

def setupContentType(site):
    ptool = site.getPortletsTool()
    for topics_list in LISTS:
        list_id = topics_list['list_id']
        list_title = topics_list['list_title']
        itopics = getattr(ptool, list_id, None)
        if not itopics:
            ptool.manage_addRefList(list_id, list_title)
            itopics = getattr(ptool, list_id, None)
            item_no = 0
            for list_item in topics_list['list_items']:
                item_no += 1
                itopics.manage_add_item(item_no, list_item)

# this dictionary is updated at the end of the module
config = {
        'product': 'NaayaContent',
        'module': 'infofolder',
        'package_path': os.path.abspath(os.path.dirname(__file__)),
        'meta_type': METATYPE_OBJECT,
        'label': 'InfoFolder',
        'permission': 'Naaya - Add Naaya InfoFolder objects',
        'forms': ['infofolder_add', 'infofolder_edit', 'infofolder_index'],
        'add_form': 'infofolder_add_html',
        'description': 'This is Naaya InfoFolder type.',
        'properties': {}, #TODO: REMOVE
        'default_schema': DEFAULT_SCHEMA,
        'schema_name': 'NyInfoFolder',
        '_module': sys.modules[__name__],
        'additional_style': ADDITIONAL_STYLE,
        'icon': os.path.join(os.path.dirname(__file__), 'www', 'NyInfoFolder.gif'),
        'on_install' : setupContentType,
        '_misc': {
                'NyInfoFolder.gif': ImageFile('www/NyInfoFolder.gif', globals()),
                'NyInfoFolder_marked.gif': ImageFile('www/NyInfoFolder_marked.gif', globals()),
            },
    }

def infofolder_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, config['meta_type'])
    return self.getFormsTool().getContent({'here': self, 'kind': config['meta_type'], 'action': 'addNyInfoFolder', 'form_helper': form_helper}, 'infofolder_add')

def _create_NyInfoFolder_object(parent, id, contributor):
    ob = NyInfoFolder(id, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def addNyInfoFolder(self, id='', REQUEST=None, contributor=None, **kwargs):
    """
    Create an infofolder type of object.
    """
    #process parameters
    if REQUEST is not None:
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs
    _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))

    id = make_id(self, id=id, title=schema_raw_data.get('title', ''), prefix='infofolder')
    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_NyInfoFolder_object(self, id, contributor)

    form_errors = ob.process_submitted_form(schema_raw_data, _lang)

    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1]) # pick a random error
        else:
            import transaction; transaction.abort() # because we already called _crete_NyZzz_object
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            return REQUEST.RESPONSE.redirect('%s/infofolder_add_html' % self.absolute_url())
            return

    if self.glCheckPermissionPublishObjects():
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
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'infofolder_manage_add' or l_referer.find('infofolder_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'infofolder_add_html':
            self.setSession('referer', self.absolute_url())
            return ob.object_submitted_message(REQUEST)
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())

    return ob.getId()

class infofolder(Implicit, NyContentData):
    """ """
    pass

class NyInfoFolder(infofolder, NyAttributes, NyContainer, NyContentType):
    """ """

    security = ClassSecurityInfo()
    meta_type = config['meta_type']
    meta_label = config['label']

    icon = 'misc_/NaayaContent/NyInfoFolder.gif'
    icon_marked = 'misc_/NaayaContent/NyInfoFolder_marked.gif'
    security.declareProtected(view, 'add_html')

    def manage_options(self):
        """ """
        l_options = ()
        l_options += infofolder.manage_options
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyItem.manage_options
        return l_options

    security.declareProtected(PERMISSION_ADD_INFO, 'addNyPhoto')
    addNyInfo = info_item.addNyInfo
    security.declareProtected(PERMISSION_ADD_INFO, 'info_add_html')
    info_add_html = info_item.info_add_html

    def __init__(self, id, contributor):
        """ """
        self.id = id
        infofolder.__init__(self)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor
        self.folder_categories = {}
        self.folder_extra_properties = {}

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

        form_errors = self.process_submitted_form(schema_raw_data, _lang)
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
        _folder_categories = schema_raw_data.pop('folder_categories', None)
        if _folder_categories:
            self.folder_categories = _folder_categories

        form_errors = self.process_submitted_form(schema_raw_data, _lang)

        if not form_errors:
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
        else:
            if REQUEST is not None:
                self._prepare_error_response(REQUEST, form_errors, schema_raw_data)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))
            else:
                raise ValueError(form_errors.popitem()[1]) # pick a random error

    #site pages
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'infofolder_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'infofolder_edit')

    def all_topic_lists(self, list_type):
        """Returns the list of id's of all the topic lists available
        within the list_type category (URL Category or Extra property)"""
        if list_type == 'URL_CATEGORIES':
            return [topic_list for topic_list in URL_CATEGORIES]
        if list_type == 'EXTRA_PROPERTIES_LISTS':
            list_of_lists = [topic_list for topic_list in EXTRA_PROPERTIES_LISTS]
            ptool = self.getPortletsTool()
            countries = getattr(ptool, 'countries', None)
            countries_list = [country.title for country in countries.get_list()]
            list_of_lists.append({'list_id': 'countries', 'list_title': 'Country',
                'list_items': countries_list})
            return list_of_lists

    def getTopics(self, category):
        ptool = self.getPortletsTool()
        topics = getattr(ptool, 'infofolder_topics', None)
        return [topics.get_item(topic) for topic in category if topics.get_collection().has_key(topic)]

    def is_single_select(self, list_id):
        if list_id in self.folder_categories:
            return self.folder_categories[list_id]
        if list_id in self.folder_extra_properties:
            return self.folder_extra_properties[list_id]
        return False

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'manageCategories')
    def manageCategories(self, REQUEST):
        """ """
        _folder_categories = REQUEST.get('folder_categories', None)
        _single_select_lists = REQUEST.get('single_select_lists', None)
        temp = {}
        if _folder_categories:
            for topic_list in _folder_categories:
                temp[topic_list] = topic_list in _single_select_lists
        redirect = REQUEST.get('redirect_url', None)
        if redirect == 'folder_categories_html':
            self.folder_categories = temp
        elif redirect == 'folder_extra_properties_html':
            self.folder_extra_properties = temp

        if REQUEST:
            redirect += '?save=ok'
            REQUEST.RESPONSE.redirect(redirect)

    folder_menusubmissions = PageTemplateFile('zpt/folder_menusubmissions', globals())
    folder_categories_html = PageTemplateFile('zpt/folder_categories', globals())
    folder_extra_properties_html = PageTemplateFile('zpt/folder_extra_properties', globals())

InitializeClass(NyInfoFolder)

def json_encode(ob):
    """ try to encode some known value types to JSON """
    if isinstance(ob, Decimal):
        return float(ob)
    raise ValueError

config.update({
    'constructors': (infofolder_add_html, addNyInfoFolder),
    'folder_constructors': [
            ('infofolder_add_html', infofolder_add_html),
            ('addNyInfoFolder', addNyInfoFolder),
        ],
    'add_method': addNyInfoFolder,
    'validation': issubclass(NyInfoFolder, NyValidation),
    '_class': NyInfoFolder,
})

def get_config():
    return config
