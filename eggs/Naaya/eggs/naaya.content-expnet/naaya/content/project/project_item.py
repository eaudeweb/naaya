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
# Cornel Nitu, Eau de Web

#Python imports
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
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zope.event import notify 
from naaya.content.base.events import NyContentObjectAddEvent, NyContentObjectEditEvent

#Product imports
from Products.NaayaBase.constants import EXCEPTION_NOTAUTHORIZED,\
    EXCEPTION_NOTAUTHORIZED_MSG, PERMISSION_EDIT_OBJECTS, MESSAGE_SAVEDCHANGES,\
    EXCEPTION_STARTEDVERSION, EXCEPTION_STARTEDVERSION_MSG, EXCEPTION_NOVERSION,\
    EXCEPTION_NOVERSION_MSG
from Products.NaayaBase.NyContentType import NyContentType, NY_CONTENT_BASE_SCHEMA
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaBase.NyContentType import NyContentData
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from Products.NaayaCore.SchemaTool.widgets.geo import Geo
from Products.NaayaCore.managers.utils import make_id

METATYPE_OBJECT = 'Naaya Project'

DEFAULT_SCHEMA = {
    'main_topics':  dict(sortorder=200, widget_type='SelectMultiple', label='Main topics covered', list_id='project_topics'),
    'sub_topics':   dict(sortorder=220, widget_type='SelectMultiple', label='Secondary topics covered', list_id='project_topics'),
}

DEFAULT_SCHEMA.update(deepcopy(NY_CONTENT_BASE_SCHEMA))
DEFAULT_SCHEMA['coverage'].update(visible=False)
DEFAULT_SCHEMA['keywords'].update(visible=False)
DEFAULT_SCHEMA['sortorder'].update(visible=False)
DEFAULT_SCHEMA['releasedate'].update(visible=False)
DEFAULT_SCHEMA['discussion'].update(visible=False)
DEFAULT_SCHEMA['geo_location'].update(visible=True)


def setupContentType(site):
    from skel import TOPICS
    ptool = site.getPortletsTool()
    itopics = getattr(ptool, 'project_topics', None)
    if not itopics:
        ptool.manage_addRefList('project_topics')
        for k, v in TOPICS.items():
            ptool.project_topics.manage_add_item(k, v)

    #Create catalog index if it doesn't exist
    ctool = site.getCatalogTool()
    try: 
        ctool.addIndex('topics', 'KeywordIndex', extra={'indexed_attrs' : 'main_topics, sub_topics'})
        ctool.manage_reindexIndex(['topics'])
    except: pass

# this dictionary is updated at the end of the module
config = {
        'product': 'NaayaContent',
        'module': 'project_item',
        'package_path': os.path.abspath(os.path.dirname(__file__)),
        'meta_type': METATYPE_OBJECT,
        'label': 'Project',
        'permission': 'Naaya - Add Naaya Project objects',
        'forms': ['project_add', 'project_edit', 'project_index'],
        'add_form': 'project_add_html',
        'description': 'This is Naaya Project type.',
        'properties': {}, #TODO: REMOVE
        'default_schema': DEFAULT_SCHEMA,
        'schema_name': 'NyProject',
        '_module': sys.modules[__name__],
        'icon': os.path.join(os.path.dirname(__file__), 'www', 'NyProject.gif'),
        'on_install' : setupContentType,
        '_misc': {
                'NyProject.gif': ImageFile('www/NyProject.gif', globals()),
                'NyProject_marked.gif': ImageFile('www/NyProject_marked.gif', globals()),
            },
    }

def project_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, config['meta_type'])
    return self.getFormsTool().getContent({'here': self, 'kind': config['meta_type'], 'action': 'addNyProject',
        'form_helper': form_helper}, 'project_add')

def _create_NyProject_object(parent, id, contributor):
    id = make_id(parent, id=id, prefix='project')
    ob = NyProject(id, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def addNyProject(self, id='', REQUEST=None, contributor=None, **kwargs):
    """
    Create an Project type of object.
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
    _project_word = schema_raw_data.get('project_word', '')

    id = make_id(self, id=id, title=schema_raw_data.get('title', ''), prefix='project')
    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_NyProject_object(self, id, contributor)

    form_errors = ob.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

    #check Captcha/reCaptcha
    if not self.checkPermissionSkipCaptcha():
        captcha_validator = self.validateCaptcha(_project_word, REQUEST)
        if captcha_validator:
            form_errors['captcha'] = captcha_validator

    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1]) # pick a random error
        else:
            import transaction; transaction.abort() # because we already called _crete_NyZzz_object
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            return REQUEST.RESPONSE.redirect('%s/project_add_html' % self.absolute_url())
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
        if l_referer == 'project_manage_add' or l_referer.find('project_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'project_add_html':
            self.setSession('referer', self.absolute_url())
            return ob.object_submitted_message(REQUEST)
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())

    return ob.getId()

def importNyProject(self, param, id, attrs, content, properties, discussion, objects):
    """
    @todo: Not implemented 
    """
    raise NotImplementedError

class project_item(Implicit, NyContentData):
    """ """
    pass


class NyProject(project_item, NyAttributes, NyItem, NyCheckControl, NyContentType):
    """ """

    meta_type = config['meta_type']
    meta_label = config['label']

    icon = 'misc_/NaayaContent/NyProject.gif'
    icon_marked = 'misc_/NaayaContent/NyProject_marked.gif'

    def manage_options(self):
        """ """
        l_options = ()
        l_options += project_item.manage_options
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyItem.manage_options
        return l_options

    security = ClassSecurityInfo()

    def __init__(self, id, contributor):
        """ """
        self.id = id
        project_item.__init__(self)
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
        self.version = project_item()
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
        return self.getFormsTool().getContent({'here': self}, 'project_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'project_edit')

    def getTopics(self, category):
        ptool = self.getPortletsTool()
        topics = getattr(ptool, 'project_topics', None)
        return [topics.get_item(topic) for topic in category if topics.get_collection().has_key(topic)]

    _minimap_template = PageTemplateFile('zpt/minimap', globals())
    def minimap(self):
        if self.geo_location not in (None, Geo()):
            simplepoints = [{'lat': self.geo_location.lat, 'lon': self.geo_location.lon}]
        elif self.aq_parent.geo_location not in (None, Geo()):
            simplepoints = [{'lat': self.aq_parent.geo_location.lat, 'lon': self.aq_parent.geo_location.lon}]
        else:
            return ""
        json_simplepoints = json.dumps(simplepoints, default=json_encode)
        return self._minimap_template(points=json_simplepoints)

    def has_coordinates(self):
        """ check if the current object has map coordinates"""
        if self.geo_location:
            return self.geo_location.lat and self.geo_location.lon
        return False

def json_encode(ob):
    """ try to encode some known value types to JSON """
    if isinstance(ob, Decimal):
        return float(ob)
    raise ValueError

InitializeClass(NyProject)

config.update({
    'constructors': (project_add_html, addNyProject),
    'folder_constructors': [
            ('project_add_html', project_add_html),
            ('addNyProject', addNyProject),
            ('import_project_item', importNyProject),
        ],
    'add_method': addNyProject,
    'validation': issubclass(NyProject, NyValidation),
    '_class': NyProject,
})

def get_config():
    return config



