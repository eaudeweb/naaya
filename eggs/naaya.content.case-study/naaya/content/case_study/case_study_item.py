from copy import deepcopy
import os
import sys

from Globals import InitializeClass
from App.ImageFile import ImageFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Acquisition import Implicit
from zope.event import notify
from naaya.content.base.events import NyContentObjectAddEvent
from naaya.content.base.events import NyContentObjectEditEvent
from zope.interface import implements

from Products.NaayaBase.NyContentType import NyContentType, NY_CONTENT_BASE_SCHEMA
from naaya.content.base.constants import *
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaBase.NyContentType import NyContentData
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaCore.LayoutTool.LayoutTool import AdditionalStyle
from Products.NaayaCore.managers.utils import slugify, uniqueId
from naaya.core import submitter
from naaya.core.zope2util import abort_transaction_keep_session

from interfaces import INyCaseStudy
from permissions import PERMISSION_ADD_CASE_STUDY

#module constants
PROPERTIES_OBJECT = {
    'id':                   (0, '', ''),
    'title':                (1, MUST_BE_NONEMPTY,
                            'The Title field must have a value.'),
    'spatial_scale':        (0, '', ''),
    'geographical_scope':   (0, '', ''),
    'status':               (0, '', ''),
    'website':              (0, '', ''),
    'description':          (0, '', ''),
    'additional_info':      (0, '', ''),
    'contact_person':       (0, '', ''),
    'sortorder':            (0, MUST_BE_POSITIV_INT,
                            'The Sort order field must contain a positive integer.'),
    'releasedate':          (0, MUST_BE_DATETIME,
                            'The Release date field must contain a valid date.'),
    'discussion':           (0, '', ''),
    'coverage':             (0, '', ''),
    'keywords':             (0, '', ''),
}

DEFAULT_SCHEMA = deepcopy(NY_CONTENT_BASE_SCHEMA)
DEFAULT_SCHEMA['spatial_scale'] = dict(sortorder=20, widget_type='Select',
                label='Spatial scale', list_id='case_study_spatial_scale',
                help_text=('Please tick the appropriate spatial scale '
                           'of the case-study.'), required=True)
DEFAULT_SCHEMA['geographical_scope'] = dict(sortorder=30,
                widget_type='SelectMultiple', label='Geographical scope',
                list_id='case_study_countries', required=True,
                help_text=('Please, select from the list, all countries that '
                           'are covered in the case-study.'))
DEFAULT_SCHEMA['status'] = dict(sortorder=40, widget_type='Select',
                label='Status', list_id='case_study_status', required=True,
                help_text='Please tick appropriate status of the case-study.')
DEFAULT_SCHEMA['website'] = dict(sortorder=50, widget_type='TextArea',
                label='Website and/or main references', localized=True,
                tinymce=True, help_text=('Please provide links to website '
                                         'and/or to the main publications.'))
DEFAULT_SCHEMA['description'].update(sortorder=60, required=True,
                label='Short description of the process and governance',
                help_text=('Please provide short text (preferably less than '
                           '2000 characters) to inform mainly about the '
                           'process and governance of the initiative '
                           '(stakeholders, time schedule, objectives, etc.).'))
DEFAULT_SCHEMA['additional_info'] = dict(sortorder=70, widget_type='TextArea',
                label='Additional information on the methods and content',
                localized=True, tinymce=True,
                help_text=('This field can be used to provide information on '
                           'the methods and content, including, for instance '
                           'the kind of analyses conducted (framing, mapping, '
                           'accounting, valuating, forward looking,...), the '
                           'list of ecosystems and ecosystem services assessed,'
                           ' the main result, etc.'))
DEFAULT_SCHEMA['contact_person'] = dict(sortorder=80, widget_type='TextArea',
                label='Contact person', tinymce=True, required=True,
                help_text=('Please indicate up to three contact persons, '
                'with their names and affiliations.'))
DEFAULT_SCHEMA['title'].update(help_text=('Please provide the full title of '
                                          'the case-study.'))
DEFAULT_SCHEMA['geo_location'].update(visible=False)
DEFAULT_SCHEMA['coverage'].update(visible=False)
DEFAULT_SCHEMA['keywords'].update(visible=False)
DEFAULT_SCHEMA['releasedate'].update(visible=False)
DEFAULT_SCHEMA['discussion'].update(visible=False)
DEFAULT_SCHEMA['sortorder'].update(visible=False)

from skel import CASE_STUDY_LISTS as LISTS

def setupContentType(site):
    ptool = site.getPortletsTool()
    for topics_list in LISTS:
        list_id = topics_list['list_id']
        list_title = topics_list['list_title']
        itopics = getattr(ptool, list_id, None)
        if not itopics:
            ptool.manage_addRefTree(list_id, list_title)
            itopics = getattr(ptool, list_id, None)
            for list_item in topics_list['list_items']:
                itopics.manage_addRefTreeNode(slugify(list_item), list_item)

def uninstallContentType(site):
    ptool = site.getPortletsTool()
    for topics_list in LISTS:
        list_id = topics_list['list_id']
        itopics = getattr(ptool, list_id, None)
        if itopics:
            ptool.manage_delObjects(list_id)

# this dictionary is updated at the end of the module
config = {
        'product': 'NaayaCaseStudy',
        'module': 'case_study_item',
        'package_path': os.path.abspath(os.path.dirname(__file__)),
        'meta_type': 'Naaya Case Study',
        'label': 'Case Study',
        'permission': PERMISSION_ADD_CASE_STUDY,
        'forms': ['case_study_add', 'case_study_edit', 'case_study_index'],
        'add_form': 'case_study_add_html',
        'description': 'This is Naaya Case Study type.',
        'properties': PROPERTIES_OBJECT,
        'default_schema': DEFAULT_SCHEMA,
        'schema_name': 'NyCaseStudy',
        '_module': sys.modules[__name__],
        'additional_style': AdditionalStyle('www/case_study.css', globals()),
        'icon': os.path.join(os.path.dirname(__file__), 'www', 'case_study.png'),
        'on_install' : setupContentType,
        'on_uninstall' : uninstallContentType,
        '_misc': {
                'NyCaseStudy.png': ImageFile('www/case_study.png', globals()),
                'NyCaseStudy_marked.png': ImageFile('www/case_study_marked.png', globals()),
            },
    }

def case_study_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, config['meta_type'])
    return self.getFormsTool().getContent({
        'here': self,
        'kind': config['meta_type'],
        'action': 'addNyCaseStudy',
        'form_helper': form_helper,
        'submitter_info_html': submitter.info_html(self, REQUEST),
    }, 'case_study_add')

def _create_NyCaseStudy_object(parent, id, contributor):
    id = uniqueId(slugify(id or 'case_study', removelist=[]),
                  lambda x: parent._getOb(x, None) is not None)
    ob = NyCaseStudy(id, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def addNyCaseStudy(self, id='', REQUEST=None, contributor=None, **kwargs):
    """
    Create a `NyCaseStudy` type of object.
    """
    #process parameters
    if REQUEST is not None:
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs

    _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
    _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''))

    id = uniqueId(slugify(id or schema_raw_data.get('title', '') or 'case_study',
                          removelist=[]),
                  lambda x: self._getOb(x, None) is not None)

    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_NyCaseStudy_object(self, id, contributor)

    form_errors = ob.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

    if REQUEST is not None:
        submitter_errors = submitter.info_check(self, REQUEST, ob)
        form_errors.update(submitter_errors)

    spatial_scale = schema_raw_data.get('spatial_scale')
    geographical_scope = schema_raw_data.get('geographical_scope', [])
    if (spatial_scale == 'regional-case-study-covers-more-one-country' and
        len(geographical_scope) < 2):
        form_errors.setdefault('geographical_scope', [])
        form_errors['geographical_scope'].append(
            'For regional case studies please select at least 2 countries')
    if (spatial_scale and
        spatial_scale != 'regional-case-study-covers-more-one-country' and
        len(geographical_scope) > 1):
        form_errors.setdefault('geographical_scope', [])
        form_errors['geographical_scope'].append(
            'For national or sub-national case studies please select exactly '
            'one country')

    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1]) # pick a random error
        else:
            abort_transaction_keep_session(REQUEST)
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            return REQUEST.RESPONSE.redirect('%s/case_study_add_html' % self.absolute_url())
            return

    if self.checkPermissionSkipApproval():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    ob.approveThis(approved, approved_by)
    ob.submitThis()

    self.recatalogNyObject(ob)
    notify(NyContentObjectAddEvent(ob, contributor, schema_raw_data))
    #log post date
    auth_tool = self.getAuthenticationTool()
    auth_tool.changeLastPost(contributor)
    #redirect if case
    if REQUEST is not None:
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'case_study_manage_add' or l_referer.find('case_study_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'case_study_add_html':
            self.setSession('referer', self.absolute_url())
            return ob.object_submitted_message(REQUEST)
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
        else: # undefined state (different referer, called in other context)
            return ob

    return ob.getId()

def importNyCaseStudy(self, param, id, attrs, content, properties, discussion, objects):
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

            ob = _create_NyCaseStudy_object(self, id, self.utEmptyToNone(attrs['contributor'].encode('utf-8')))
            ob.sortorder = attrs['sortorder'].encode('utf-8')
            ob.discussion = abs(int(attrs['discussion'].encode('utf-8')))
            ob.title = attrs['title'].encode('utf-8')
            ob.spatial_scale = attrs['spatial_scale'].encode('utf-8')
            ob.geographical_scope = attrs['geographical_scope'].encode('utf-8')
            ob.status = attrs['status'].encode('utf-8')
            ob.website = attrs['website'].encode('utf-8')
            ob.description = attrs['description'].encode('utf-8')
            ob.additional_info = attrs['additional_info'].encode('utf-8')
            ob.contact_person = attrs['contact_person'].encode('utf-8')

            for property, langs in properties.items():
                [ ob._setLocalPropValue(property, lang, langs[lang]) for lang in langs if langs[lang]!='' ]
            ob.approveThis(approved=abs(int(attrs['approved'].encode('utf-8'))),
                approved_by=self.utEmptyToNone(attrs['approved_by'].encode('utf-8')))
            if attrs['releasedate'].encode('utf-8') != '':
                ob.setReleaseDate(attrs['releasedate'].encode('utf-8'))
            ob.import_comments(discussion)
            self.recatalogNyObject(ob)

class case_study_item(Implicit, NyContentData):
    """ """

class NyCaseStudy(case_study_item, NyAttributes, NyItem, NyCheckControl, NyContentType):
    """ """

    implements(INyCaseStudy)

    meta_type = config['meta_type']
    meta_label = config['label']

    icon = 'misc_/NaayaContent/NyCaseStudy.png'
    icon_marked = 'misc_/NaayaContent/NyCaseStudy_marked.png'

    def manage_options(self):
        """ """
        l_options = ()
        if not self.hasVersion():
            l_options += ({'label': 'Properties', 'action': 'manage_edit_html'},)
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyItem.manage_options
        return l_options

    security = ClassSecurityInfo()

    def __init__(self, id, contributor):
        """ """
        self.id = id
        case_study_item.__init__(self)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        return 'title="%s" spatial_scale="%s" geographical_scope="%s" status="%s" website="%s" description="%s" additional_info="%s" contact_person="%s"' % \
            (self.utXmlEncode(self.title),
            self.utXmlEncode(self.spatial_scale),
            self.utXmlEncode(self.geographical_scope),
            self.utXmlEncode(self.status),
            self.utXmlEncode(self.website),
            self.utXmlEncode(self.description),
            self.utXmlEncode(self.additional_info),
            self.utXmlEncode(self.contact_person))

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
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    #site actions
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'commitVersion')
    def commitVersion(self, REQUEST=None):
        """ """
        user = self.REQUEST.AUTHENTICATED_USER.getUserName()
        if (not self.checkPermissionEditObject()) or (
            self.checkout_user != user):
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if not self.hasVersion():
            raise EXCEPTION_NOVERSION, EXCEPTION_NOVERSION_MSG
        self.copy_naaya_properties_from(self.version)
        self.checkout = 0
        self.checkout_user = None
        self.version = None
        self._p_changed = 1
        self.recatalogNyObject(self)
        notify(NyContentObjectEditEvent(self, user))
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
        self.version = case_study_item()
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
        _releasedate = self.process_releasedate(
            schema_raw_data.pop('releasedate', ''), obj.releasedate)

        form_errors = self.process_submitted_form(schema_raw_data, _lang,
            _override_releasedate=_releasedate)

        spatial_scale = schema_raw_data.get('spatial_scale')
        geographical_scope = schema_raw_data.get('geographical_scope')
        if (spatial_scale == 'regional-case-study-covers-more-one-country' and
            len(geographical_scope) < 2):
            form_errors.setdefault('geographical_scope', [])
            form_errors['geographical_scope'].append(
                'For regional case studies please select at least 2 countries')
        if (spatial_scale and
            spatial_scale != 'regional-case-study-covers-more-one-country' and
            len(geographical_scope) > 1):
            form_errors.setdefault('geographical_scope', [])
            form_errors['geographical_scope'].append(
                'For national or sub-national case studies please select exactly '
                'one country')

        if not form_errors:
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
        else:
            if REQUEST is not None:
                self._prepare_error_response(REQUEST, form_errors, schema_raw_data)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))
            else:
                raise ValueError(form_errors.popitem()[1]) # pick a random error

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/case_study_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'case_study_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        if self.hasVersion():
            obj = self.version
        else:
            obj = self
        return self.getFormsTool().getContent({'here': obj}, 'case_study_edit')

InitializeClass(NyCaseStudy)

manage_addNyCaseStudy_html = PageTemplateFile('zpt/case_study_manage_add', globals())
manage_addNyCaseStudy_html.kind = config['meta_type']
manage_addNyCaseStudy_html.action = 'addNyCaseStudy'

config.update({
    'constructors': (manage_addNyCaseStudy_html, addNyCaseStudy),
    'folder_constructors': [
            # NyFolder.manage_addNyCaseStudy_html = manage_addNyCaseStudy_html
            ('manage_addNyCaseStudy_html', manage_addNyCaseStudy_html),
            ('case_study_add_html', case_study_add_html),
            ('addNyCaseStudy', addNyCaseStudy),
            ('import_case_study_item', importNyCaseStudy),
        ],
    'add_method': addNyCaseStudy,
    'validation': issubclass(NyCaseStudy, NyValidation),
    '_class': NyCaseStudy,
})

def get_config():
    return config
