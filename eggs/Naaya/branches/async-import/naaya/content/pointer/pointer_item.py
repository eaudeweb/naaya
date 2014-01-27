import os
import sys

from Acquisition import Implicit
from Globals import InitializeClass
from App.ImageFile import ImageFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zope.event import notify

from Products.NaayaBase.NyContentType import NyContentType, NY_CONTENT_BASE_SCHEMA
from naaya.content.base.constants import *
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaBase.NyContentType import NyContentData
from Products.NaayaCore.managers.utils import slugify, uniqueId
from naaya.core import submitter
from naaya.core.zope2util import abort_transaction_keep_session
from naaya.content.base.events import NyContentObjectAddEvent
from naaya.content.base.events import NyContentObjectEditEvent

from permissions import PERMISSION_ADD_POINTER
from constants import META_TYPE_NAAYA_POINTER

#module constants
PROPERTIES_OBJECT = {
    'id':           (0, '', ''),
    'title':        (1, MUST_BE_NONEMPTY, 'The Title field must have a value.'),
    'description':  (0, '', ''),
    'coverage':     (0, '', ''),
    'keywords':     (0, '', ''),
    'sortorder':    (0, MUST_BE_POSITIV_INT, 'The Sort order field must contain a positive integer.'),
    'releasedate':  (0, MUST_BE_DATETIME, 'The Release date field must contain a valid date.'),
    'discussion':   (0, '', ''),
    'pointer':      (1, MUST_BE_NONEMPTY, 'The Pointer field must have a value.'),
    'lang':         (0, '', '')
}
DEFAULT_SCHEMA = {
    'redirect': dict(sortorder=100, widget_type='Checkbox', data_type='bool', label='Automatically redirect to the pointing item'),
    'pointer': dict(sortorder=110, widget_type='Pointer', label='Pointer'),
}
DEFAULT_SCHEMA.update(NY_CONTENT_BASE_SCHEMA)

# this dictionary is updated at the end of the module
config = {
        'product': 'NaayaContent',
        'module': 'pointer_item',
        'package_path': os.path.abspath(os.path.dirname(__file__)),
        'meta_type': META_TYPE_NAAYA_POINTER,
        'label': 'Pointer',
        'permission': PERMISSION_ADD_POINTER,
        'forms': ['pointer_add', 'pointer_edit', 'pointer_index'],
        'add_form': 'pointer_add_html',
        'description': 'This is Naaya Pointer type.',
        'properties': PROPERTIES_OBJECT,
        'default_schema': DEFAULT_SCHEMA,
        'schema_name': 'NyPointer',
        '_module': sys.modules[__name__],
        'additional_style': None,
        'icon': os.path.join(os.path.dirname(__file__), 'www', 'pointer.gif'),
        '_misc': {
                'NyPointer.gif': ImageFile('www/pointer.gif', globals()),
                'NyPointer_marked.gif': ImageFile('www/pointer_marked.gif', globals()),
            },
    }

def pointer_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, config['meta_type'])
    return self.getFormsTool().getContent({
        'here': self,
        'kind': config['meta_type'],
        'action': 'addNyPointer',
        'form_helper': form_helper,
        'submitter_info_html': submitter.info_html(self, REQUEST),
    }, 'pointer_add')

def _create_NyPointer_object(parent, id, contributor):
    id = uniqueId(slugify(id or 'pointer', removelist=[]),
                  lambda x: parent._getOb(x, None) is not None)
    ob = NyPointer(id, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def addNyPointer(self, id='', REQUEST=None, contributor=None, **kwargs):
    """
    Create a Pointer type of object.
    """
    if REQUEST is not None:
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs
    _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
    _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''))
    schema_raw_data.setdefault('locator', '')

    #Remove first '/'
    if ('pointer' in schema_raw_data and
        schema_raw_data['pointer'].startswith('/')):
        schema_raw_data['pointer'] = schema_raw_data['pointer'][1:]

    id = uniqueId(slugify(id or schema_raw_data.get('title', '') or 'pointer',
                          removelist=[]),
                  lambda x: self._getOb(x, None) is not None)
    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_NyPointer_object(self, id, contributor)

    form_errors = ob.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

    if REQUEST is not None:
        submitter_errors = submitter.info_check(self, REQUEST, ob)
        form_errors.update(submitter_errors)

    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1]) # pick a random error
        else:
            abort_transaction_keep_session(REQUEST)
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            REQUEST.RESPONSE.redirect('%s/pointer_add_html' % self.absolute_url())
            return

    #process parameters
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
        if l_referer == 'pointer_manage_add' or l_referer.find('pointer_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'pointer_add_html':
            self.setSession('referer', self.absolute_url())
            return ob.object_submitted_message(REQUEST)
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())

    return ob.getId()

def importNyPointer(self, param, id, attrs, content, properties, discussion, objects):
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

            ob = _create_NyPointer_object(self, id, self.utEmptyToNone(attrs['contributor'].encode('utf-8')))
            ob.sortorder = attrs['sortorder'].encode('utf-8')
            ob.discussion = abs(int(attrs['discussion'].encode('utf-8')))
            ob.pointer = attrs['pointer'].encode('utf-8')

            for property, langs in properties.items():
                [ ob._setLocalPropValue(property, lang, langs[lang]) for lang in langs if langs[lang]!='' ]
            ob.approveThis(approved=abs(int(attrs['approved'].encode('utf-8'))),
                approved_by=self.utEmptyToNone(attrs['approved_by'].encode('utf-8')))
            if attrs['releasedate'].encode('utf-8') != '':
                ob.setReleaseDate(attrs['releasedate'].encode('utf-8'))
            ob.checkThis(attrs['validation_status'].encode('utf-8'),
                attrs['validation_comment'].encode('utf-8'),
                attrs['validation_by'].encode('utf-8'),
                attrs['validation_date'].encode('utf-8'))
            ob.import_comments(discussion)
            self.recatalogNyObject(ob)

class pointer_item(Implicit, NyContentData):
    """ """
    redirect = True

class NyPointer(pointer_item, NyAttributes, NyItem, NyCheckControl, NyValidation, NyContentType):
    """ """

    meta_type = config['meta_type']
    meta_label = config['label']
    icon = 'misc_/NaayaContent/NyPointer.gif'
    icon_marked = 'misc_/NaayaContent/NyPointer_marked.gif'

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
        pointer_item.__init__(self)
        NyValidation.__dict__['__init__'](self)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        return 'pointer="%s" validation_status="%s" validation_date="%s" validation_by="%s" validation_comment="%s"' % \
            (self.utXmlEncode(self.pointer),
                self.utXmlEncode(self.validation_status),
                self.utXmlEncode(self.validation_date),
                self.utXmlEncode(self.validation_by),
                self.utXmlEncode(self.validation_comment))

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

        #Remove first '/'
        if ('pointer' in schema_raw_data and
            schema_raw_data['pointer'].startswith('/')):
            schema_raw_data['pointer'] = schema_raw_data['pointer'][1:]

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
        #check permissions
        self.checkout = 1
        self.checkout_user = self.REQUEST.AUTHENTICATED_USER.getUserName()
        self.version = pointer_item()
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
            #Remove first '/'
        if ('pointer' in schema_raw_data and
            schema_raw_data['pointer'].startswith('/')):
            schema_raw_data['pointer'] = schema_raw_data['pointer'][1:]

        _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
        _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''), obj.releasedate)

        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

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
    manage_edit_html = PageTemplateFile('zpt/pointer_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        from AccessControl import getSecurityManager

        #Remove first '/'
        pointer = self.pointer
        if self.pointer.startswith('/'):
            pointer = self.pointer[1:]

        obj = self.getSite().unrestrictedTraverse(pointer.encode('utf-8'),
                                                  None)
        can_view = getSecurityManager().checkPermission(view, obj)
        params = {'here': self, 'restricted': 0, 'missing': 0}

        if obj and self.redirect:
            if can_view:
                REQUEST.RESPONSE.redirect(obj.absolute_url())
            else:
                params['restricted'] = 1
                return self.getFormsTool().getContent(params, 'pointer_index')
        elif not obj:
            params['missing'] = 1
            return self.getFormsTool().getContent(params, 'pointer_index')
        else:
            return self.getFormsTool().getContent(params, 'pointer_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        if self.hasVersion():
            obj = self.version
        else:
            obj = self
        return self.getFormsTool().getContent({'here': obj}, 'pointer_edit')

InitializeClass(NyPointer)

manage_addNyPointer_html = PageTemplateFile('zpt/pointer_manage_add', globals())
manage_addNyPointer_html.kind = config['meta_type']
manage_addNyPointer_html.action = 'addNyPointer'
config.update({
    'constructors': (manage_addNyPointer_html, addNyPointer),
    'folder_constructors': [
            # NyFolder.manage_addNyPointer_html = manage_addNyPointer_html
            ('manage_addNyPointer_html', manage_addNyPointer_html),
            ('pointer_add_html', pointer_add_html),
            ('addNyPointer', addNyPointer),
            ('import_pointer_item', importNyPointer),
        ],
    'add_method': addNyPointer,
    'validation': issubclass(NyPointer, NyValidation),
    '_class': NyPointer,
})

def get_config():
    return config
