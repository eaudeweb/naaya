from copy import deepcopy
import os
import sys

from Globals import InitializeClass
from PIL import Image
from StringIO import StringIO
from App.FactoryDispatcher import FactoryDispatcher
from App.ImageFile import ImageFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Acquisition import Implicit
from zope.event import notify
from naaya.content.base.events import NyContentObjectAddEvent
from naaya.content.base.events import NyContentObjectEditEvent
from DateTime import DateTime
from zope.interface import implements

from Products.Naaya.adapters import FolderMetaTypes
from Products.NaayaBase.NyContentType import NY_CONTENT_BASE_SCHEMA
from naaya.content.base.constants import *
from Products.Naaya.NyFolder import NyFolder
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaBase.NyContentType import NyContentData
from Products.NaayaCore.managers.utils import slugify, uniqueId
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from naaya.core import submitter
from naaya.core.zope2util import abort_transaction_keep_session

from interfaces import INyHexfolder
from permissions import PERMISSION_ADD_HEXFOLDER

from lxml import etree
from lxml.builder import ElementMaker

#pluggable type metadata
PROPERTIES_OBJECT = {
    'id':               (0, '', ''),
    'title':            (1, MUST_BE_NONEMPTY, 'The Title field must have a value.'),
    'description':      (0, '', ''),
    'coverage':         (0, '', ''),
    'keywords':         (0, '', ''),
    'sortorder':        (0, MUST_BE_POSITIV_INT, 'The Sort order field must contain a positive integer.'),
    'releasedate':      (0, MUST_BE_DATETIME, 'The Release date field must contain a valid date.'),
    'resourceurl':      (0, '', ''),
    'source':           (0, '', ''),
    'lang':             (0, '', '')
}
DEFAULT_SCHEMA = {
    'intro':            dict(sortorder=15, widget_type='TextArea', label='Intro (short description)',
                             rows=10, columns=50, localized=True, tinymce=True),
    'layout_type':      dict(sortorder=10, widget_type='Select', label='Layout type',
                             list_id='hexfolder_layout_types', required=True,
                             help_text='Depending on the selected layout, one or more pictures and their metadata will be mandatory'),
    'target-groups':    dict(sortorder=100, widget_type='Select', label='Target groups',
                             list_id='target-groups'),
    'topics':           dict(sortorder=100, widget_type='Select', label='Topics',
                             list_id='topics'),
    'picture_0_title':   dict(sortorder=200, widget_type='String', label='Picture 1 title'),
    'picture_0_description':    dict(sortorder=201, widget_type='String', label='Picture 1 description'),
    'picture_0_long_description':    dict(sortorder=202, widget_type='TextArea',
                                          label='Picture 1 long description (for "Picture and text" layout)',
                                          localized=True, tinymce=True),
    'picture_0_url_text':   dict(sortorder=203, widget_type='String', label='Picture 1 URL text'),
    'picture_0_url':    dict(sortorder=204, widget_type='String', label='Picture 1 URL'),
    'picture_1_title':   dict(sortorder=210, widget_type='String', label='Picture 2 title'),
    'picture_1_description':    dict(sortorder=211, widget_type='String', label='Picture 2 description'),
    'picture_1_url_text':   dict(sortorder=212, widget_type='String', label='Picture 2 URL text'),
    'picture_1_url':    dict(sortorder=213, widget_type='String', label='Picture 2 URL'),
    'picture_2_title':   dict(sortorder=220, widget_type='String', label='Picture 3 title'),
    'picture_2_description':    dict(sortorder=221, widget_type='String', label='Picture 3 description'),
    'picture_2_url_text':   dict(sortorder=222, widget_type='String', label='Picture 3 URL text'),
    'picture_2_url':    dict(sortorder=223, widget_type='String', label='Picture 3 URL'),
    'picture_3_title':   dict(sortorder=230, widget_type='String', label='Picture 4 title'),
    'picture_3_description':    dict(sortorder=231, widget_type='String', label='Picture 4 description'),
    'picture_3_url_text':   dict(sortorder=232, widget_type='String', label='Picture 4 URL text'),
    'picture_3_url':    dict(sortorder=233, widget_type='String', label='Picture 4 URL'),
    'picture_4_title':   dict(sortorder=240, widget_type='String', label='Picture 5 title'),
    'picture_4_description':    dict(sortorder=241, widget_type='String', label='Picture 5 description'),
    'picture_4_url_text':   dict(sortorder=242, widget_type='String', label='Picture 5 URL text'),
    'picture_4_url':    dict(sortorder=243, widget_type='String', label='Picture 5 URL'),
}

DEFAULT_SCHEMA.update(deepcopy(NY_CONTENT_BASE_SCHEMA))
DEFAULT_SCHEMA['coverage'].update(widget_type='Glossary', label='Country', glossary_id='countries_glossary')
DEFAULT_SCHEMA['sortorder'].update(visible=True)
PICTURE_SCHEMA = {
    'picture_0': 'Picture 1',
    'picture_1': 'Picture 2',
    'picture_2': 'Picture 3',
    'picture_3': 'Picture 4',
    'picture_4': 'Picture 5'
}

# this dictionary is updated at the end of the module
config = {
        'product': 'NaayaContent',
        'module': 'hexfolder_item',
        'package_path': os.path.abspath(os.path.dirname(__file__)),
        'meta_type': 'Naaya Hex Folder',
        'label': 'Hex Folder',
        'permission': PERMISSION_ADD_HEXFOLDER,
        'forms': ['hexfolder_add', 'hexfolder_edit', 'hexfolder_index_1',
                  'hexfolder_index_2', 'hexfolder_index_3', 'hexfolder_index_4'],
        'add_form': 'hexfolder_add_html',
        'description': 'This is Naaya Hex Folder type.',
        'properties': PROPERTIES_OBJECT,
        'default_schema': DEFAULT_SCHEMA,
        'schema_name': 'NyHexfolder',
        '_module': sys.modules[__name__],
        'additional_style': None,
        'icon': os.path.join(os.path.dirname(__file__), 'www', 'hexfolder.gif'),
        '_misc': {
                'NyHexfolder.gif': ImageFile('www/hexfolder.gif', globals()),
                'NyHexfolder_marked.gif': ImageFile('www/hexfolder_marked.gif', globals()),
            },
    }

def hexfolder_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, config['meta_type'])
    return self.getFormsTool().getContent({
        'here': self,
        'kind': config['meta_type'],
        'action': 'addNyHexfolder',
        'form_helper': form_helper,
        'submitter_info_html': submitter.info_html(self, REQUEST),
    }, 'hexfolder_add')

def _create_NyHexfolder_object(parent, id, contributor):
    id = uniqueId(slugify(id or 'hexfolder', removelist=[]),
                  lambda x: parent._getOb(x, None) is not None)
    ob = NyHexfolder(id, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def addNyHexfolder(self, id='', REQUEST=None, contributor=None, **kwargs):
    """
    Create a Hex Folder type of object.
    """
    parent = self
    if isinstance(self, FactoryDispatcher):
        parent = self.Destination()

    if REQUEST is not None:
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs
    _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
    _folder_meta_types = schema_raw_data.pop('folder_meta_types', '')
    _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate',
                                                                ''))
    _picture_0 = schema_raw_data.pop('picture_0', '')
    _picture_1 = schema_raw_data.pop('picture_1', '')
    _picture_2 = schema_raw_data.pop('picture_2', '')
    _picture_3 = schema_raw_data.pop('picture_3', '')
    _picture_4 = schema_raw_data.pop('picture_4', '')
    site = self.getSite()

    id = uniqueId(slugify(id or schema_raw_data.get('title', '') or 'hexfolder',
                          removelist=[]),
                  lambda x: self._getOb(x, None) is not None)
    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_NyHexfolder_object(self, id, contributor)

    form_errors = ob.hexfolder_submitted_form(
        schema_raw_data, REQUEST, _lang, _override_releasedate=_releasedate)

    if REQUEST is not None:
        submitter_errors = submitter.info_check(self, REQUEST, ob)
        form_errors.update(submitter_errors)

    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1]) # pick a random error
        else:
            abort_transaction_keep_session(REQUEST)
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            REQUEST.RESPONSE.redirect('%s/hexfolder_add_html' % self.absolute_url())
            return

    for i in range(5):
        ob.setPicture(eval("_picture_%s" % i), i)

    ob_meta_types = FolderMetaTypes(ob)
    parent_meta_types = FolderMetaTypes(parent)
    # extra settings
    if _folder_meta_types == '':
        # inherit allowed meta types from the parent folder or portal
        if parent.meta_type == site.meta_type:
            # parent is portal, use defaults
            ob_meta_types.set_values(None)
        else:
            if not parent_meta_types.has_custom_value:
                # if parent uses defaults, so should `ob`
                ob_meta_types.set_values(None)
            else:
                ob_meta_types.set_values(parent_meta_types.get_values())
    else:
        ob_meta_types.set_values(self.utConvertToList(_folder_meta_types))

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
        if l_referer == 'hexfolder_manage_add' or l_referer.find('hexfolder_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'hexfolder_add_html':
            self.setSession('referer', self.absolute_url())
            return ob.object_submitted_message(REQUEST)
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
        else: # undefined state (different referer, called in other context)
            return ob

    return ob.getId()

def importNyHexfolder(self, param, id, attrs, content, properties, discussion, objects):
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

            ob = _create_NyHexfolder_object(self, id, self.utEmptyToNone(attrs['contributor'].encode('utf-8')))
            ob.sortorder = attrs['sortorder'].encode('utf-8')
            for i in range(5):
                setattr(ob, "picture_" + str(i), self.utBase64Decode(attrs['picture_' + str(i)].encode('utf-8')))
            ob.resourceurl = attrs['resourceurl'].encode('utf-8')

            for property, langs in properties.items():
                [ ob._setLocalPropValue(property, lang, langs[lang]) for lang in langs if langs[lang]!='' ]
            ob.approveThis(approved=abs(int(attrs['approved'].encode('utf-8'))),
                approved_by=self.utEmptyToNone(attrs['approved_by'].encode('utf-8')))
            if attrs['releasedate'].encode('utf-8') != '':
                ob.setReleaseDate(attrs['releasedate'].encode('utf-8'))
            ob.import_comments(discussion)
            self.recatalogNyObject(ob)

class hexfolder_item(Implicit, NyContentData):
    """ """
    picture_0 = None
    picture_1 = None
    picture_2 = None
    picture_3 = None
    picture_4 = None

    def setPicture(self, p_picture, count):
        """
        Upload picture.
        """
        if p_picture != '':
            if hasattr(p_picture, 'filename'):
                if p_picture.filename != '':
                    l_read = p_picture.read()
                    if l_read != '':
                        p_picture.seek(0)
                        p_picture = Image.open(p_picture)
                        format = p_picture.format
                        aspect = float(p_picture.size[0]) / float(
                            p_picture.size[1])
                        p_picture = p_picture.resize((640, int(640/aspect)),
                                                     Image.ANTIALIAS)
                        picture = StringIO()
                        p_picture.save(picture, format)
                        picture.seek(0)
                        setattr(self, "picture_%s" % count, picture.read())
                        self._p_changed = 1
            else:
                setattr(self, "picture_%s" % count, p_picture)
                self._p_changed = 1

    def delPicture(self, count):
        """
        Delete the picture with index.
        """
        setattr(self, "picture_%s" % count, None)
        self._p_changed = 1

class NyHexfolder(hexfolder_item, NyFolder):
    """ """

    implements(INyHexfolder)

    meta_type = config['meta_type']
    meta_label = config['label']
    icon = 'misc_/NaayaContent/NyHexfolder.gif'
    icon_marked = 'misc_/NaayaContent/NyHexfolder_marked.gif'

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
        hexfolder_item.__init__(self)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor

    def getPicture(self, count, version=None, REQUEST=None):
        """ """
        REQUEST.RESPONSE.setHeader('Content-type', 'image/jpeg')
        if version is None:
            return getattr(self, "picture_%s" % count)
        else:
            if self.checkout:
                return getattr(self.version, "picture_%s" % count)
            else:
                return getattr(self, "picture_%s" % count)

    #zmi actions
    def manage_FTPget(self):
        """ Return body for ftp """
        return self.details

    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG

        if REQUEST is not None:
            schema_raw_data = dict(REQUEST.form)
        else:
            schema_raw_data = kwargs
        releasedate = self.process_releasedate(releasedate, self.releasedate)
        _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
        _approved = int(bool(schema_raw_data.pop('approved', False)))
        _picture_0 = schema_raw_data.pop('picture_0', '')
        _picture_1 = schema_raw_data.pop('picture_1', '')
        _picture_2 = schema_raw_data.pop('picture_2', '')
        _picture_3 = schema_raw_data.pop('picture_3', '')
        _picture_4 = schema_raw_data.pop('picture_4', '')
        _del_picture_0 = schema_raw_data.pop('del_picture_0', '')
        _del_picture_1 = schema_raw_data.pop('del_picture_1', '')
        _del_picture_2 = schema_raw_data.pop('del_picture_2', '')
        _del_picture_3 = schema_raw_data.pop('del_picture_3', '')
        _del_picture_4 = schema_raw_data.pop('del_picture_4', '')

        form_errors = self.hexfolder_submitted_form(schema_raw_data, REQUEST,
                                                    _lang)
        if form_errors:
            raise ValueError(form_errors.popitem()[1]) # pick a random error

        if _approved != self.approved:
            if _approved == 0: _approved_by = None
            else: _approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
            self.approveThis(_approved, _approved_by)
        
        self.releasedate = releasedate

        for i in range(5):
            if eval("_del_picture_%s" % i) != '':
                self.delPicture(i)
            else:
                self.setPicture(eval("_picture_%s" % i), i)
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    #site actions
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
        _picture_0 = schema_raw_data.pop('picture_0', '')
        _picture_1 = schema_raw_data.pop('picture_1', '')
        _picture_2 = schema_raw_data.pop('picture_2', '')
        _picture_3 = schema_raw_data.pop('picture_3', '')
        _picture_4 = schema_raw_data.pop('picture_4', '')
        _del_picture_0 = schema_raw_data.pop('del_picture_0', '')
        _del_picture_1 = schema_raw_data.pop('del_picture_1', '')
        _del_picture_2 = schema_raw_data.pop('del_picture_2', '')
        _del_picture_3 = schema_raw_data.pop('del_picture_3', '')
        _del_picture_4 = schema_raw_data.pop('del_picture_4', '')

        _releasedate = self.process_releasedate(
            schema_raw_data.pop('releasedate', ''), self.releasedate)
        
        form_errors = self.hexfolder_submitted_form(
            schema_raw_data, REQUEST, _lang,
            _override_releasedate=_releasedate)

        if not form_errors:

            for i in range(5):
                if eval("_del_picture_%s" % i) != '':
                    self.delPicture(i)
                else:
                    self.setPicture(eval("_picture_%s" % i), i)

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
            abort_transaction_keep_session(REQUEST)
            if REQUEST is not None:
                self._prepare_error_response(REQUEST, form_errors, schema_raw_data)
                self.setSession('del_picture_0', _del_picture_0)
                self.setSession('del_picture_1', _del_picture_1)
                self.setSession('del_picture_2', _del_picture_2)
                self.setSession('del_picture_3', _del_picture_3)
                self.setSession('del_picture_4', _del_picture_4)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))
            else:
                raise ValueError(form_errors.popitem()[1]) # pick a random error

        #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/hexfolder_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        self.notify_access_event(REQUEST)

        return self.getFormsTool().getContent({'here': self}, self.layout_type)

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        if self.hasVersion():
            obj = self.version
        else:
            obj = self
        return self.getFormsTool().getContent({'here': obj}, 'hexfolder_edit')

    def hexfolder_submitted_form(
            self, REQUEST_form, REQUEST, _lang=None, _all_values=True,
            _override_releasedate=None):
        """
        this should be used for the hexfolder instead of
        process_submitted_form
        """
        form_errors = super(NyHexfolder, self).process_submitted_form(
            REQUEST_form, _lang, _all_values, _override_releasedate)
        if REQUEST_form.get('layout_type'):
            # update form errors based on layout type
            # pass REQUEST.form instead of the stripped-down schema_raw_data
            # where many objects were popped out
            self._check_picture_info(dict(REQUEST.form), form_errors)
        return form_errors

    def _check_picture_info(self, REQUEST_form, form_errors):
        layout_type = REQUEST_form.get('layout_type')
        if layout_type == 'hexfolder_index_1':
            # all pictures are mandatory
            # all urls are mandatory
            # all url texts are mandatory
            mandatory_fields = [
                'picture_0', 'picture_1', 'picture_2', 'picture_3',
                'picture_4', 'picture_0_url', 'picture_1_url',
                'picture_2_url', 'picture_3_url', 'picture_4_url',
                'picture_0_url_text', 'picture_1_url_text',
                'picture_2_url_text', 'picture_3_url_text',
                'picture_4_url_text']
        elif layout_type == 'hexfolder_index_2':
            # all pictures are mandatory
            # all urls are mandatory
            # all url texts are mandatory
            # all descriptions are mandatory
            # all titles are mandatory
            mandatory_fields = [
                'picture_0', 'picture_1', 'picture_2', 'picture_3',
                'picture_4', 'picture_0_url', 'picture_1_url',
                'picture_2_url', 'picture_3_url', 'picture_4_url',
                'picture_0_url_text', 'picture_1_url_text',
                'picture_2_url_text', 'picture_3_url_text',
                'picture_4_url_text', 'picture_0_title', 'picture_1_title',
                'picture_2_title', 'picture_3_title', 'picture_4_title',
                'picture_0_description', 'picture_1_description',
                'picture_2_description', 'picture_3_description',
                'picture_4_description']
        elif layout_type == 'hexfolder_index_3':
            # first three pictures are mandatory
            # first three urls are mandatory
            # first three descriptions are mandatory
            # first three titles are mandatory
            mandatory_fields = [
                'picture_0', 'picture_1', 'picture_2', 'picture_0_url',
                'picture_1_url', 'picture_2_url', 'picture_0_title',
                'picture_1_title', 'picture_2_title', 'picture_0_description',
                'picture_1_description', 'picture_2_description']
        elif layout_type == 'hexfolder_index_4':
            # first picture is mandatory
            # fist picture description is mandatory
            mandatory_fields = [
                'picture_0', 'picture_0_long_description']
        for field in mandatory_fields:
            if not REQUEST_form.get(field):
                try:
                    field_label = DEFAULT_SCHEMA[field]['label']
                except KeyError:
                    field_label = PICTURE_SCHEMA[field]
                if PICTURE_SCHEMA.get(field):
                    # pictures have a more complicated case
                    # the picture can already be saved on the object
                    # and we need to check if the user has not selected it
                    # to be deleted
                    if not getattr(self, field) or REQUEST_form.get(
                            'del_%s' % field):
                        form_errors.setdefault(field, [])
                        form_errors[field].append('%s is mandatory' %
                                                  field_label)
                else:
                    form_errors.setdefault(field, [])
                    form_errors[field].append('%s is mandatory' % field_label)


InitializeClass(NyHexfolder)

manage_addNyHexfolder_html = PageTemplateFile('zpt/hexfolder_manage_add', globals())
manage_addNyHexfolder_html.kind = config['meta_type']
manage_addNyHexfolder_html.action = 'addNyHexfolder'

#Custom folder index for hexfolder
NaayaPageTemplateFile('zpt/hexfolder_folder_index', globals(), 'hexfolder_folder_index')

config.update({
    'constructors': (manage_addNyHexfolder_html, addNyHexfolder),
    'folder_constructors': [
            # NyFolder.manage_addNyHexfolder_html = manage_addNyHexfolder_html
            ('manage_addNyHexfolder_html', manage_addNyHexfolder_html),
            ('hexfolder_add_html', hexfolder_add_html),
            ('addNyHexfolder', addNyHexfolder),
            ('import_hexfolder_item', importNyHexfolder),
        ],
    'add_method': addNyHexfolder,
    'validation': issubclass(NyHexfolder, NyValidation),
    '_class': NyHexfolder,
})

def get_config():
    return config
