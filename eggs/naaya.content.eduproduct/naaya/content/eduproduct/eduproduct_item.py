from copy import deepcopy
import os
import sys

from Globals import InitializeClass
from App.ImageFile import ImageFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Acquisition import Implicit
from zope.interface import implements
from zope.event import notify

from naaya.content.base.events import NyContentObjectAddEvent
from naaya.content.base.events import NyContentObjectEditEvent
from Products.NaayaBase.NyContentType import NyContentType
from Products.NaayaBase.NyContentType import NY_CONTENT_BASE_SCHEMA
from naaya.content.base.constants import *
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyNonCheckControl import NyNonCheckControl
from Products.NaayaBase.NyContentType import NyContentData
from Products.NaayaCore.managers.utils import make_id

from interfaces import INyEduProduct
from permissions import PERMISSION_ADD_EDU_PRODUCT
import skel

DEFAULT_SCHEMA = {
    'product_type': dict(sortorder=100, widget_type='SelectMultiple',
                         label='Product type', list_id='product_type'),
    'target_group': dict(sortorder=110, widget_type='SelectMultiple',
                         label='Target group', list_id='target-group'),
    'theme': dict(sortorder=120, widget_type='SelectMultiple',
                  label='Theme', list_id='product_theme'),
    'details': dict(sortorder=130, widget_type='TextArea',
                    label='Details', localized=True, tinymce=True),
    'available_from': dict(sortorder=140, widget_type='Date',
                           label='Available from', data_type='date'),
    'available_until': dict(sortorder=150, widget_type='Date',
                            label='Available until', data_type='date'),
    'supplier': dict(sortorder=160, widget_type='String',
                     label='Supplier'),
    'supplier_url': dict(sortorder=170, widget_type='URL',
                         label='Supplier URL'),
    'contact_person': dict(sortorder=180, widget_type='String',
                           label='Contact person'),
    'contact_email': dict(sortorder=190, widget_type='String',
                          label='Contact email'),
    'contact_phone': dict(sortorder=200, widget_type='String',
                          label='Contact phone'),
}
DEFAULT_SCHEMA.update(deepcopy(NY_CONTENT_BASE_SCHEMA))
DEFAULT_SCHEMA['geo_location'].update(visible=True, required=True)
DEFAULT_SCHEMA['geo_type'].update(visible=True)

# this dictionary is updated at the end of the module
config = {
    'product': 'NaayaEduProduct',
    'module': 'eduproduct_item',
    'package_path': os.path.abspath(os.path.dirname(__file__)),
    'meta_type': 'Naaya Educational Product',
    'label': 'EduProduct',
    'permission': PERMISSION_ADD_EDU_PRODUCT,
    'forms': ['eduproduct_add', 'eduproduct_edit', 'eduproduct_index'],
    'add_form': 'eduproduct_add_html',
    'description': 'This is Naaya Educational Product type.',
    'default_schema': DEFAULT_SCHEMA,
    'schema_name': 'NyEduProduct',
    '_module': sys.modules[__name__],
    'additional_style': None,
    'icon': os.path.join(os.path.dirname(__file__), 'www', 'eduproduct.gif'),
    '_misc': {
        'NyEduProduct.gif': ImageFile('www/eduproduct.gif', globals()),
        'NyEduProduct_marked.gif': ImageFile('www/eduproduct_marked.gif',
                                             globals()),
        },
    }


def eduproduct_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, config['meta_type'])
    return self.getFormsTool().getContent(
        {'here': self, 'kind': config['meta_type'],
         'action': 'addNyEduProduct', 'form_helper': form_helper},
        'eduproduct_add')


def _create_NyEduProduct_object(parent, id, contributor):
    id = make_id(parent, id=id, prefix='eduproduct')
    ob = NyEduProduct(id, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob


def addNyEduProduct(self, id='', REQUEST=None, contributor=None, **kwargs):
    """
    Create an Educational Product type of object.
    """
    if REQUEST is not None:
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs
    _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
    _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate',
                                                                ''))
    recaptcha_response = schema_raw_data.get('g-recaptcha-response', '')

    id = make_id(self, id=id, title=schema_raw_data.get('title', ''),
                 prefix='ep')
    if contributor is None:
        contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_NyEduProduct_object(self, id, contributor)

    form_errors = ob.process_submitted_form(schema_raw_data, _lang,
                                            _override_releasedate=_releasedate)

    # check Captcha/reCaptcha
    if not self.checkPermissionSkipCaptcha():
        captcha_validator = self.validateCaptcha(recaptcha_response, REQUEST)
        if captcha_validator:
            form_errors['captcha'] = captcha_validator

    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1])  # pick a random error
        else:
            import transaction
            transaction.abort()
            # because we already called _crete_NyZzz_object
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            REQUEST.RESPONSE.redirect('%s/eduproduct_add_html' %
                                      self.absolute_url())
            return

    # process parameters
    if self.glCheckPermissionPublishObjects():
        approved, approved_by = (
            1, self.REQUEST.AUTHENTICATED_USER.getUserName())
    else:
        approved, approved_by = 0, None
    ob.approveThis(approved, approved_by)
    ob.submitThis()

    if ob.discussion:
        ob.open_for_comments()
    self.recatalogNyObject(ob)
    notify(NyContentObjectAddEvent(ob, contributor, schema_raw_data))
    # log post date
    auth_tool = self.getAuthenticationTool()
    auth_tool.changeLastPost(contributor)
    # redirect if case
    if REQUEST is not None:
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'eduproduct_manage_add' or l_referer.find(
                'eduproduct_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'eduproduct_add_html':
            self.setSession('referer', self.absolute_url())
            return ob.object_submitted_message(REQUEST)
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())

    return ob.getId()


class NyEduProduct(Implicit, NyContentData, NyAttributes, NyItem,
                   NyNonCheckControl, NyValidation, NyContentType):
    """ """

    implements(INyEduProduct)

    meta_type = config['meta_type']
    meta_label = config['label']

    icon = 'misc_/NaayaContent/NyEduProduct.gif'
    icon_marked = 'misc_/NaayaContent/NyEduProduct_marked.gif'

    manage_options = (
        {'label': 'Properties', 'action': 'manage_edit_html'},
        {'label': 'View', 'action': 'index_html'},
    ) + NyItem.manage_options

    security = ClassSecurityInfo()

    def __init__(self, id, contributor):
        """ """
        self.id = id
        NyValidation.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor

    @property
    def start_date(self):
        return getattr(self, 'available_from', None)

    @property
    def end_date(self):
        return getattr(self, 'available_until', None)

    # zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')

    def manageProperties(self, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED(EXCEPTION_NOTAUTHORIZED_MSG)

        if REQUEST is not None:
            schema_raw_data = dict(REQUEST.form)
        else:
            schema_raw_data = kwargs
        _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
        _releasedate = self.process_releasedate(
            schema_raw_data.pop('releasedate', ''), self.releasedate)
        _approved = int(bool(schema_raw_data.pop('approved', False)))

        form_errors = self.process_submitted_form(
            schema_raw_data, _lang, _override_releasedate=_releasedate)
        if form_errors:
            raise ValueError(form_errors.popitem()[1])  # pick a random error

        if _approved != self.approved:
            if _approved == 0:
                _approved_by = None
            else:
                _approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
            self.approveThis(_approved, _approved_by)
        self._p_changed = 1
        if self.discussion:
            self.open_for_comments()
        else:
            self.close_for_comments()
        self.recatalogNyObject(self)
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')

    def saveProperties(self, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED(EXCEPTION_NOTAUTHORIZED_MSG)

        if REQUEST is not None:
            schema_raw_data = dict(REQUEST.form)
        else:
            schema_raw_data = kwargs
        _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
        _releasedate = self.process_releasedate(schema_raw_data.pop(
            'releasedate', ''), self.releasedate)

        form_errors = self.process_submitted_form(
            schema_raw_data, _lang, _override_releasedate=_releasedate)

        if not form_errors:
            if self.discussion:
                self.open_for_comments()
            else:
                self.close_for_comments()
            self._p_changed = 1
            self.recatalogNyObject(self)
            # log date
            contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
            auth_tool = self.getAuthenticationTool()
            auth_tool.changeLastPost(contributor)
            notify(NyContentObjectEditEvent(self, contributor))
            if REQUEST:
                self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES,
                                         date=self.utGetTodayDate())
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' %
                                          (self.absolute_url(), _lang))
        else:
            if REQUEST is not None:
                self._prepare_error_response(REQUEST, form_errors,
                                             schema_raw_data)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' %
                                          (self.absolute_url(), _lang))
            else:
                raise ValueError(form_errors.popitem()[1])  # pick an error

    # zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/eduproduct_manage_edit',
                                        globals())

    # site pages
    security.declareProtected(view, 'index_html')

    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self},
                                              'eduproduct_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')

    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self},
                                              'eduproduct_edit')

InitializeClass(NyEduProduct)


def on_install_eduproduct(site):
    portal_portlets = site.getPortletsTool()

    for tree_data in skel.ref_trees:
        tree_id = tree_data['id']
        if tree_id in portal_portlets.objectIds():
            continue

        tree_title = tree_data['title']
        portal_portlets.manage_addRefTree(tree_id, tree_title)
        tree_ob = portal_portlets[tree_id]

        for tree_item in tree_data['items']:
            tree_ob.manage_addRefTreeNode(tree_item['id'], tree_item['title'])

manage_addNyEduProduct_html = PageTemplateFile('zpt/eduproduct_manage_add',
                                               globals())
manage_addNyEduProduct_html.kind = config['meta_type']
manage_addNyEduProduct_html.action = 'addNyEduProduct'
config.update({
    'constructors': (manage_addNyEduProduct_html, addNyEduProduct),
    'folder_constructors': [
        ('manage_addNyEduProduct_html', manage_addNyEduProduct_html),
        ('eduproduct_add_html', eduproduct_add_html),
        ('addNyEduProduct', addNyEduProduct),
        ],
    'add_method': addNyEduProduct,
    'validation': issubclass(NyEduProduct, NyValidation),
    '_class': NyEduProduct,
    'on_install': on_install_eduproduct,
})


def get_config():
    return config
