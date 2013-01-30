import os
import sys
from StringIO import StringIO

from Globals import InitializeClass
from App.ImageFile import ImageFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import Products
from Acquisition import Implicit
from zope.event import notify
from naaya.content.base.events import NyContentObjectAddEvent
from naaya.content.base.events import NyContentObjectEditEvent
from zope.interface import implements
from interfaces import INyDocument, INyContentDocumentExport

from Products.NaayaBase.NyContentType import (NyContentType,
                                              NY_CONTENT_BASE_SCHEMA)
from naaya.content.base.constants import *
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyContainer import NyContainer
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaBase.NyImageContainer import NyImageContainer
from Products.NaayaBase.NyContentType import NyContentData
from Products.NaayaCore.managers.utils import slugify, uniqueId
from Products.NaayaCore.managers.interfaces import IZipExportObject
from Products.NaayaCore.managers.import_export import set_response_attachment
from naaya.core import submitter
from naaya.core.zope2util import get_site_manager

from permissions import PERMISSION_ADD_DOCUMENT

#global module constants
ID_PLACEHOLDER = 'placeholder_for_id'

#module constants
PROPERTIES_OBJECT = {
    'id':           (0, '', ''),
    'title':        (1, MUST_BE_NONEMPTY,
                        'The Title field must have a value.'),
    'description':  (0, '', ''),
    'coverage':     (0, '', ''),
    'keywords':     (0, '', ''),
    'sortorder':    (0, MUST_BE_POSITIV_INT,
                    'The Sort order field must contain a positive integer.'),
    'releasedate':  (0, MUST_BE_DATETIME,
                    'The Release date field must contain a valid date.'),
    'discussion':   (0, '', ''),
    'body':         (0, '', ''),
    'lang':         (0, '', '')
}
DEFAULT_SCHEMA = {
    'body': {
        'sortorder': 100,
        'widget_type': 'TextArea',
        'label': 'Body (HTML)',
        'localized': True,
        'tinymce': True
    },
}
DEFAULT_SCHEMA.update(NY_CONTENT_BASE_SCHEMA)

# this dictionary is updated at the end of the module
config = {
        'product': 'NaayaContent',
        'module': 'document_item',
        'package_path': os.path.abspath(os.path.dirname(__file__)),
        'meta_type': 'Naaya Document',
        'label': 'HTML Document',
        'permission': PERMISSION_ADD_DOCUMENT,
        'forms': ['document_add', 'document_edit', 'document_index'],
        'add_form': 'document_add',
        'description': 'This is Naaya Document type.',
        'properties': PROPERTIES_OBJECT,
        'default_schema': DEFAULT_SCHEMA,
        'schema_name': 'NyDocument',
        '_module': sys.modules[__name__],
        'additional_style': None,
        'icon': os.path.join(os.path.dirname(__file__), 'www', 'document.gif'),
        '_misc': {
                'NyDocument.gif': ImageFile('www/document.gif', globals()),
                'NyDocument_marked.gif': ImageFile('www/document_marked.gif',
                globals()),
            },
    }

def document_add(self, REQUEST=None, RESPONSE=None):
    """ """
    id = uniqueId(ID_PLACEHOLDER, lambda x: self._getOb(x, None) is not None)
    self.addNyDocument(id)
    if REQUEST:
        REQUEST.RESPONSE.redirect('%s/add_html' %
                                    self._getOb(id).absolute_url())
    else:
        return id

def _create_NyDocument_object(parent, id, contributor):
    id = uniqueId(slugify(id, removelist=[]),
                  lambda x: parent._getOb(x, None) is not None)
    ob = NyDocument(id, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def addNyDocument(self, id='', REQUEST=None, contributor=None, **kwargs):
    """
    Create a Document type of object.
    """
    if REQUEST is not None:
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs
    _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
    _releasedate = self.process_releasedate(
                                schema_raw_data.pop('releasedate', ''))
    schema_raw_data.setdefault('body', '')
    _submit = bool(kwargs.get('submitted', 0))

    id = uniqueId(slugify(id or schema_raw_data.get('title', '') or
                  ID_PLACEHOLDER, removelist=[]),
                  lambda x: self._getOb(x, None) is not None)
    if contributor is None:
        contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_NyDocument_object(self, id, contributor)
    ob._setLocalPropValue('title', _lang, '')

    sortorder_widget = ob._get_schema().getWidget('sortorder')
    schema_raw_data.setdefault('sortorder', sortorder_widget.default)

    form_errors = ob.process_submitted_form(schema_raw_data, _lang,
                    _override_releasedate=_releasedate, _all_values=_submit)
    if form_errors:
        raise ValueError(form_errors.popitem()[1]) # pick a random error

    if _submit:
        ob.submitThis()

    self.recatalogNyObject(ob)
    #log post date
    auth_tool = self.getAuthenticationTool()
    auth_tool.changeLastPost(contributor)
    #redirect if case
    if REQUEST is not None:
        if REQUEST.has_key('submitted'): ob.submitThis()
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if (l_referer == 'document_manage_add' or
           l_referer.find('document_manage_add') != -1):
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'document_add':
            self.setSession('referer', self.absolute_url())
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
    return ob.getId()

def importNyDocument(self, param, id, attrs, content, properties, discussion,
                     objects):
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

            contributor = self.utEmptyToNone(
                                attrs['contributor'].encode('utf-8'))
            if contributor is None:
                contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
            ob = _create_NyDocument_object(self, id, contributor)
            ob.sortorder = attrs['sortorder'].encode('utf-8')
            ob.discussion = abs(int(attrs['discussion'].encode('utf-8')))

            for property, langs in properties.items():
                [ ob._setLocalPropValue(property, lang, langs[lang])
                  for lang in langs if langs[lang]!='' ]
            ob.approveThis(
                approved=abs(int(attrs['approved'].encode('utf-8'))),
                approved_by=self.utEmptyToNone(
                    attrs['approved_by'].encode('utf-8')))
            if attrs['releasedate'].encode('utf-8') != '':
                ob.setReleaseDate(attrs['releasedate'].encode('utf-8'))
            ob.checkThis(attrs['validation_status'].encode('utf-8'),
                attrs['validation_comment'].encode('utf-8'),
                attrs['validation_by'].encode('utf-8'),
                attrs['validation_date'].encode('utf-8'))
            ob.submitThis()
            ob.import_comments(discussion)
            self.recatalogNyObject(ob)
        for object in objects:
            self.import_data_custom(ob, object)

class document_item(Implicit, NyContentData):
    """ """

class NyDocument(document_item, NyAttributes, NyContainer, NyCheckControl,
                 NyValidation, NyContentType):
    """ """

    implements(INyDocument, INyContentDocumentExport)

    meta_type = config['meta_type']
    meta_label = config['label']
    icon = 'misc_/NaayaContent/NyDocument.gif'
    icon_marked = 'misc_/NaayaContent/NyDocument_marked.gif'

    def manage_options(self):
        """ """
        l_options = (NyContainer.manage_options[0],)
        if not self.hasVersion():
            l_options += ({
                'label': 'Properties',
                'action': 'manage_edit_html'
            },)
        l_options += ({
            'label': 'View',
            'action': 'index_html'
        },) + NyContainer.manage_options[3:8]
        return l_options

    def all_meta_types(self, interfaces=None):
        """ """
        y = []
        additional_meta_types = ['Image']
        for x in Products.meta_types:
            if x['name'] in additional_meta_types:
                y.append(x)
        return y

    security = ClassSecurityInfo()

    def __init__(self, id, contributor):
        """ """
        self.id = id
        document_item.__init__(self)
        NyValidation.__dict__['__init__'](self)
        NyCheckControl.__dict__['__init__'](self)
        NyContainer.__dict__['__init__'](self)
        self.contributor = contributor
        self.imageContainer = NyImageContainer(self, True)

    security.declarePrivate('objectkeywords')
    def objectkeywords(self, lang):
        return u' '.join([self._objectkeywords(lang),
                          self.getLocalProperty('body', lang)])

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        return ('validation_status="%s" validation_date="%s" '
               'validation_by="%s" validation_comment="%s"') % \
            (self.utXmlEncode(self.validation_status),
                self.utXmlEncode(self.validation_date),
                self.utXmlEncode(self.validation_by),
                self.utXmlEncode(self.validation_comment))

    security.declarePrivate('export_this_body_custom')
    def export_this_body_custom(self):
        r = []
        ra = r.append
        for l in self.gl_get_languages():
            ra('<body lang="%s"><![CDATA[%s]]></body>' % (l,
                self.utToUtf8(self.getLocalProperty('body', l))))
        for i in self.getUploadedImages():
            ra('<img param="0" id="%s" content="%s" />' % \
                (self.utXmlEncode(i.id()), self.utXmlEncode(
                self.utBase64Encode(str(i.data)))))
        return ''.join(r)

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
        _releasedate = self.process_releasedate(
            schema_raw_data.pop('releasedate', ''), self.releasedate)
        _approved = int(bool(schema_raw_data.pop('approved', False)))

        form_errors = self.process_submitted_form(schema_raw_data, _lang,
                            _override_releasedate=_releasedate)
        if form_errors:
            raise ValueError(form_errors.popitem()[1]) # pick a random error

        if _approved != self.approved:
            if _approved == 0: _approved_by = None
            else: _approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
            self.approveThis(_approved, _approved_by)
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    security.declareProtected(view_management_screens, 'submitThis')
    def submit_this(self, REQUEST=None):
        """ """
        self.submitThis()
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    #site actions
    security.declareProtected(config['permission'], 'process_add')
    def process_add(self, REQUEST, **kwargs):
        """ """
        schema_raw_data = dict(REQUEST.form)
        _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
        _releasedate = self.process_releasedate(
            schema_raw_data.pop('releasedate', ''), self.releasedate)

        parent = self.getParentNode()
        id = uniqueId(slugify(schema_raw_data.get('title', '') or
                      ID_PLACEHOLDER, removelist=[]),
                      lambda x: parent._getOb(x, None) is not None)

        schema_raw_data['title'] = schema_raw_data.get('title', '')
        schema_raw_data['description'] = schema_raw_data.get('description', '')
        schema_raw_data['body'] = schema_raw_data.get('body', '')

        #check mandatory fiels
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]

        form_errors = self.process_submitted_form(schema_raw_data, _lang,
                                _override_releasedate=_releasedate)

        submitter_errors = submitter.info_check(self.aq_parent, REQUEST, self)
        form_errors.update(submitter_errors)

        if not form_errors:
            #replace the old id with the new one
            #(for absolute URLs or pictures)

            parent.manage_renameObjects([self.id], [id])
            if self.checkPermissionSkipApproval():
                approved = 1
                approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
            else:
                approved = 0
                approved_by = None

            self.approveThis(approved, approved_by)
            self.submitThis()
            self.recatalogNyObject(self)
            notify(NyContentObjectAddEvent(self, self.contributor,
                                           schema_raw_data))
            self.setSession('referer', self.getParentNode().absolute_url())
            return self.object_submitted_message(REQUEST)
            REQUEST.RESPONSE.redirect('%s/messages_html' %
                                        self.getParentNode().absolute_url())
        else:
            #XXX: `l_referer` is not used
            l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
            self._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            REQUEST.RESPONSE.redirect('%s/add_html' % self.absolute_url())

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
        if REQUEST: REQUEST.RESPONSE.redirect('%s/index_html' %
                                                self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'startVersion')
    def startVersion(self, REQUEST=None):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if self.hasVersion():
            raise EXCEPTION_STARTEDVERSION, EXCEPTION_STARTEDVERSION_MSG
        self.checkout = 1
        self.checkout_user = self.REQUEST.AUTHENTICATED_USER.getUserName()
        self.version = document_item()
        self.version.copy_naaya_properties_from(self)
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('%s/edit_html' %
            self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG

        if self.hasVersion():
            obj = self.version
            if (self.checkout_user !=
                self.REQUEST.AUTHENTICATED_USER.getUserName()):
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

        if not form_errors:
            self._p_changed = 1
            self.recatalogNyObject(self)
            #log date
            contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
            auth_tool = self.getAuthenticationTool()
            auth_tool.changeLastPost(contributor)
            notify(NyContentObjectEditEvent(self, contributor))
            if REQUEST:
                self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES,
                                date=self.utGetTodayDate())
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (
                                self.absolute_url(), _lang))
        else:
            if REQUEST is not None:
                self._prepare_error_response(REQUEST, form_errors,
                                                schema_raw_data)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (
                                            self.absolute_url(), _lang))
            else:
                # pick a random error
                raise ValueError(form_errors.popitem()[1])
    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/document_manage_edit', globals())

    #site pages
    security.declareProtected(config['permission'], 'add_html')
    def add_html(self, REQUEST=None, RESPONSE=None):
        """ """
        from Products.NaayaBase.NyContentType import \
                                        get_schema_helper_for_metatype
        form_helper = get_schema_helper_for_metatype(self, config['meta_type'])
        parent = self.aq_parent
        return self.getFormsTool().getContent({
            'here': self,
            'kind': config['meta_type'],
            'action': 'process_add',
            'form_helper': form_helper,
            'submitter_info_html': submitter.info_html(parent, REQUEST),
        }, 'document_add')

    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        self.notify_access_event(REQUEST)
        return self.getFormsTool().getContent({'here': self}, 'document_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        if self.hasVersion():
            obj = self.version
        else:
            obj = self
        return self.getFormsTool().getContent({'here': obj}, 'document_edit')

InitializeClass(NyDocument)

manage_addNyDocument_html = PageTemplateFile('zpt/document_manage_add',
                                                globals())
manage_addNyDocument_html.kind = config['meta_type']
manage_addNyDocument_html.action = 'addNyDocument'
config.update({
    'constructors': (manage_addNyDocument_html, addNyDocument),
    'folder_constructors': [
            # NyFolder.manage_addNyDocument_html = manage_addNyDocument_html
            ('manage_addNyDocument_html', manage_addNyDocument_html),
            ('document_add', document_add),
            ('addNyDocument', addNyDocument),
            ('import_document_item', importNyDocument),
        ],
    'add_method': addNyDocument,
    'validation': issubclass(NyDocument, NyValidation),
    '_class': NyDocument,
})

def get_config():
    return config

def do_export(context, REQUEST):
    """ Export the document as a html file """
    sm = get_site_manager(context)
    target = sm.queryAdapter(context, IZipExportObject)
    if target.skip:
        context.setSessionErrorsTrans("You don't have permission "
            "to download this document")
        return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)
    data = target.data
    if isinstance(data, unicode):
        data = data.encode('utf-8')
    output = StringIO()
    output.write(data)
    set_response_attachment(REQUEST.RESPONSE, target.filename,
            'text/html; charset=utf-8', output.len)
    return output.getvalue()
