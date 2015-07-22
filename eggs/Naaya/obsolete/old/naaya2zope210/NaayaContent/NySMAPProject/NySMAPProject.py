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
# Alexandru Ghica
# Cornel Nitu
# Miruna Badescu

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

#Product imports
from Products.NaayaBase.NyContentType import NyContentType, NY_CONTENT_BASE_SCHEMA
from Products.NaayaContent.constants import *
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaBase.NyValidation import NyValidation
from project_item import project_item

#pluggable type metadata
METATYPE_OBJECT = 'Naaya SMAP Project'
LABEL_OBJECT = 'Project'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya SMAP Project objects'
OBJECT_FORMS = ['project_add', 'project_edit', 'project_index']
OBJECT_CONSTRUCTORS = ['manage_addNySMAPProject_html', 'project_add_html', 'addNySMAPProject', 'importNySMAPProject']
OBJECT_ADD_FORM = 'project_add_html'
DESCRIPTION_OBJECT = 'This is Naaya SMAP Project type.'
PREFIX_OBJECT = 'prj'
PROPERTIES_OBJECT = {
    'id':           (0, '', ''),
    'title':        (1, MUST_BE_NONEMPTY, 'The Title field must have a value.'),
    'description':  (0, '', ''),
    'coverage':     (0, '', ''),
    'keywords':     (0, '', ''),
    'sortorder':    (0, MUST_BE_POSITIV_INT, 'The Sort order field must contain a positive integer.'),
    'releasedate':  (0, MUST_BE_DATETIME, 'The Release date field must contain a valid date.'),
    'discussion':   (0, '', ''),
    'country':      (0, '', ''),
    'contact':      (0, '', ''),
    'donor':        (0, '', ''),
    'links':        (0, '', ''),
    'organisation': (0, '', ''),
    'location':     (0, '', ''),
    'main_issues':  (0, '', ''),
    'tools':        (0, '', ''),
    'budget':       (0, '', ''),
    'timeframe':    (0, '', ''),
    'priority_area':(0, '', ''),
    'focus':        (0, '', ''),
    'lang':         (0, '', '')
}
DEFAULT_SCHEMA = {
    'main_issues':  dict(sortorder=100, widget_type='String', label='Project scale'),
    'tools':        dict(sortorder=110, widget_type='TextArea', label='Tools'),
    'location':     dict(sortorder=120, widget_type='String', label='Locations', localized=True),
    'budget':       dict(sortorder=130, widget_type='String', label='Budget'),
    'timeframe':    dict(sortorder=140, widget_type='String', label='Timeframe'),
    'organisation': dict(sortorder=150, widget_type='String', label='Implementing organisation(s)', localized=True),
    'contact':      dict(sortorder=160, widget_type='TextArea', label='Contact', localized=True),
    'donor':        dict(sortorder=170, widget_type='TextArea', label='Donor(s)', localized=True),
    'links':        dict(sortorder=180, widget_type='TextArea', label='Links', localized=True),
    # non-schema properties: country, priority_area, focus
    # TODO: 'country' should be a schema property
}
DEFAULT_SCHEMA.update(deepcopy(NY_CONTENT_BASE_SCHEMA))
DEFAULT_SCHEMA['coverage'].update(visible=False)
DEFAULT_SCHEMA['keywords'].update(visible=False)
DEFAULT_SCHEMA['releasedate'].update(visible=False)
DEFAULT_SCHEMA['discussion'].update(visible=False)
DEFAULT_SCHEMA['sortorder'].update(visible=False)

# this dictionary is updated at the end of the module
config = {
        'product': 'NaayaContent',
        'module': 'NySMAPProject',
        'package_path': os.path.abspath(os.path.dirname(__file__)),
        'meta_type': 'Naaya SMAP Project',
        'label': 'Project',
        'permission': 'Naaya - Add Naaya SMAP Project objects',
        'forms': ['project_add', 'project_edit', 'project_index'],
        'add_form': 'project_add_html',
        'description': 'This is Naaya SMAP Project type.',
        'properties': PROPERTIES_OBJECT,
        'default_schema': DEFAULT_SCHEMA,
        'schema_name': 'NySMAPProject',
        'import_string': 'importNySMAPProject',
        '_module': sys.modules[__name__],
        'additional_style': None,
        'icon': os.path.join(os.path.dirname(__file__), 'www', 'NySMAPProject.gif'),
        '_misc': {
                'NySMAPProject.gif': ImageFile('www/NySMAPProject.gif', globals()),
                'NySMAPProject_marked.gif': ImageFile('www/NySMAPProject_marked.gif', globals()),
            },
    }

def project_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, METATYPE_OBJECT)
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNySMAPProject', 'form_helper': form_helper}, 'project_add')

def _create_NySMAPProject_object(parent, id, contributor):
    i = 0
    while parent._getOb(id, None):
        i += 1
        id = '%s-%u' % (id, i)
    ob = NySMAPProject(id, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def addNySMAPProject(self, id='', REQUEST=None, contributor=None, **kwargs):
    """
    Create a Project type of object.
    """

    if REQUEST is not None:
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs
    _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
    _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''))

    _country = self.utConvertToList(schema_raw_data.pop('country', ''))
    _focus = self.utConvertToList(schema_raw_data.pop('focus', ''))
    _send_notifications = schema_raw_data.pop('_send_notifications', True)

    res = {}
    for x in _focus:
        res[x.split('|@|')[0]] = ''
    _priority_area = res.keys()

    id = self.utCleanupId(id)
    if not id: id = self.utGenObjectId(schema_raw_data.get('title', ''))
    if not id: id = PREFIX_OBJECT + self.utGenRandomId(5)
    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_NySMAPProject_object(self, id, contributor)

    form_errors = ob.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1]) # pick a random error
        else:
            import transaction; transaction.abort() # because we already called _crete_NyZzz_object
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            REQUEST.RESPONSE.redirect('%s/project_add_html' % self.absolute_url())
            return

    #process parameters
    if self.glCheckPermissionPublishObjects():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    ob.submitThis()
    ob.approveThis(approved, approved_by)

    ob.country = _country
    ob.focus = _focus
    ob.priority_area = _priority_area

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
        if l_referer == 'project_manage_add' or l_referer.find('project_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'project_add_html':
            self.setSession('referer', self.absolute_url())
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())

    return ob.getId()

def importNySMAPProject(self, param, id, attrs, content, properties, discussion, objects):
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

            ob = _create_NySMAPProject_object(self, id, self.utEmptyToNone(attrs['contributor'].encode('utf-8')))
            ob.sortorder = attrs['sortorder'].encode('utf-8')
            ob.discussion = abs(int(attrs['discussion'].encode('utf-8')))

            ob.main_issues = attrs['main_issues'].encode('utf-8')
            ob.country = eval(attrs['country'].encode('utf-8'))
            ob.tools = attrs['tools'].encode('utf-8')
            ob.budget = attrs['budget'].encode('utf-8')
            ob.timeframe = attrs['timeframe'].encode('utf-8')
            ob.priority_area = attrs['priority_area'].encode('utf-8')
            ob.focus = eval(attrs['focus'].encode('utf-8'))

            for property, langs in properties.items():
                [ ob._setLocalPropValue(property, lang, langs[lang]) for lang in langs if langs[lang]!='' ]
            ob.approveThis(approved=abs(int(attrs['approved'].encode('utf-8'))),
                approved_by=self.utEmptyToNone(attrs['approved_by'].encode('utf-8')))
            if attrs['releasedate'].encode('utf-8') != '':
                ob.setReleaseDate(attrs['releasedate'].encode('utf-8'))
            ob.import_comments(discussion)
            self.recatalogNyObject(ob)

class NySMAPProject(project_item, NyAttributes, NyItem, NyCheckControl, NyContentType):
    """ """

    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT
    icon = 'misc_/NaayaContent/NySMAPProject.gif'
    icon_marked = 'misc_/NaayaContent/NySMAPProject_marked.gif'

    def manage_options(self):
        """ """
        l_options = ()
        if not self.hasVersion():
            l_options += ({'label': 'Properties', 'action': 'manage_edit_html'},)
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

    security.declarePrivate('objectkeywords')
    def objectkeywords(self, lang):
        return u' '.join([self._objectkeywords(lang), self.getLocalProperty('donor', lang),
                        self.getLocalProperty('organisation', lang), self.getLocalProperty('contact', lang),
                        self.getLocalProperty('location', lang)])

    security.declareProtected(view, 'resource_area')
    def resource_area(self):
        return self.priority_area

    security.declareProtected(view, 'resource_focus')
    def resource_focus(self):
        return ' '.join(self.focus)

    security.declareProtected(view, 'resource_country')
    def resource_country(self):
        return ' '.join(self.country)

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        return 'priority_area="%s" budget="%s" timeframe="%s" focus="%s" main_issues="%s" tools="%s" country="%s"'% \
            (self.utXmlEncode(self.priority_area),
                self.utXmlEncode(self.budget),
                self.utXmlEncode(self.utNoneToEmpty(self.timeframe)),
                self.utXmlEncode(self.focus),
                self.utXmlEncode(self.main_issues),
                self.utXmlEncode(self.tools),
                self.utXmlEncode(self.country))

    security.declarePrivate('export_this_body_custom')
    def export_this_body_custom(self):
        r = []
        ra = r.append
        for l in self.gl_get_languages():
            ra('<donor lang="%s"><![CDATA[%s]]></donor>' % (l, self.utToUtf8(self.getLocalProperty('donor', l))))
            ra('<contact lang="%s"><![CDATA[%s]]></contact>' % (l, self.utToUtf8(self.getLocalProperty('contact', l))))
            ra('<organisation lang="%s"><![CDATA[%s]]></organisation>' % (l, self.utToUtf8(self.getLocalProperty('organisation', l))))
            ra('<location lang="%s"><![CDATA[%s]]></location>' % (l, self.utToUtf8(self.getLocalProperty('location', l))))
            ra('<links lang="%s"><![CDATA[%s]]></links>' % (l, self.utToUtf8(self.getLocalProperty('links', l))))
        return ''.join(r)

    security.declarePrivate('syndicateThis')
    def syndicateThis(self, lang=None):
        l_site = self.getSite()
        if lang is None: lang = self.gl_get_selected_language()
        r = []
        ra = r.append
        ra(self.syndicateThisHeader())
        ra(self.syndicateThisCommon(lang))
        ra('<dc:type>Text</dc:type>')
        ra('<dc:format>text</dc:format>')
        ra('<dc:source>%s</dc:source>' % self.utXmlEncode(self.getLocalProperty('source', lang)))
        ra('<dc:creator>%s</dc:creator>' % self.utXmlEncode(l_site.getLocalProperty('creator', lang)))
        ra('<dc:publisher>%s</dc:publisher>' % self.utXmlEncode(l_site.getLocalProperty('publisher', lang)))
        ra(self.syndicateThisFooter())
        return ''.join(r)

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

        _country = self.utConvertToList(schema_raw_data.pop('country', ''))
        _focus = self.utConvertToList(schema_raw_data.pop('focus', ''))

        res = {}
        for x in _focus:
            res[x.split('|@|')[0]] = ''
        _priority_area = res.keys()

        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)
        if form_errors:
            raise ValueError(form_errors.popitem()[1]) # pick a random error

        self.country = _country
        self.focus = _focus
        self.priority_area = _priority_area

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
        self.country = self.version.country
        self.focus = self.version.focus
        self.priority_area = self.version.priority_area
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
        self.version.country = self.country
        self.version.focus = self.focus
        self.version.priority_area = self.priority_area
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

        _country = self.utConvertToList(schema_raw_data.pop('country', ''))
        _focus = self.utConvertToList(schema_raw_data.pop('focus', ''))

        res = {}
        for x in _focus:
            res[x.split('|@|')[0]] = ''
        _priority_area = res.keys()

        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

        if not form_errors:
            if self.discussion: self.open_for_comments()
            else: self.close_for_comments()

            obj.country = _country
            obj.focus = _focus
            obj.priority_area = _priority_area

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

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'checkFocus')
    def checkFocus(self, priority_area, focus_id):
        """ """
        for f in self.focus:
            if f == '%s|@|%s' % (priority_area, focus_id):
                return True
        return False

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/project_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'project_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'project_edit')

InitializeClass(NySMAPProject)
manage_addNySMAPProject_html = PageTemplateFile('zpt/project_manage_add', globals())
manage_addNySMAPProject_html.kind = METATYPE_OBJECT
manage_addNySMAPProject_html.action = 'addNySMAPProject'
config.update({
    'constructors': (manage_addNySMAPProject_html, addNySMAPProject),
    'folder_constructors': [
            # NyFolder.manage_addNySMAPProject_html = manage_addNySMAPProject_html
            ('manage_addNySMAPProject_html', manage_addNySMAPProject_html),
            ('project_add_html', project_add_html),
            ('addNySMAPProject', addNySMAPProject),
            (config['import_string'], importNySMAPProject),
        ],
    'add_method': addNySMAPProject,
    'validation': issubclass(NySMAPProject, NyValidation),
    '_class': NySMAPProject,
})

def get_config():
    return config
