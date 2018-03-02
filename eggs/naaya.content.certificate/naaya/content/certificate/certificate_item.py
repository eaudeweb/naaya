import os
import re
import sys
from copy import deepcopy
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Acquisition import Implicit
from App.ImageFile import ImageFile
from Globals import InitializeClass
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaBase.NyContentType import NyContentData
from Products.NaayaBase.NyContentType import NyContentType
from Products.NaayaBase.NyContentType import NY_CONTENT_BASE_SCHEMA
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.constants import EXCEPTION_NOTAUTHORIZED
from Products.NaayaBase.constants import EXCEPTION_NOTAUTHORIZED_MSG
from Products.NaayaBase.constants import MESSAGE_SAVEDCHANGES
from Products.NaayaBase.constants import PERMISSION_EDIT_OBJECTS
from Products.NaayaCore.managers.utils import slugify, uniqueId
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from interfaces import INyCertificate
from naaya.content.base.constants import MUST_BE_DATETIME
from naaya.content.base.constants import MUST_BE_NONEMPTY
from naaya.content.base.constants import MUST_BE_POSITIV_INT
from naaya.content.base.events import NyContentObjectAddEvent
from naaya.content.base.events import NyContentObjectEditEvent
from naaya.core import submitter
from naaya.core.utils import is_valid_email
from naaya.core.zope2util import abort_transaction_keep_session
from permissions import PERMISSION_ADD_CERTIFICATE
from zope.event import notify
from zope.interface import implements

# module constants
PROPERTIES_OBJECT = {
    'id': (0, '', ''),
    'title': (1, MUST_BE_NONEMPTY, 'The Title field must have a value.'),
    'description': (0, '', ''),
    'coverage': (0, '', ''),
    'keywords': (0, '', ''),
    'sortorder': (0, MUST_BE_POSITIV_INT,
                  'The Sort order field must contain a positive integer.'),
    'releasedate': (0, MUST_BE_DATETIME,
                    'The Release date field must contain a valid date.'),
    'discussion': (0, '', ''),
    'category': (1, MUST_BE_NONEMPTY, 'Please select at least one category'),
    'operational_level': (1, MUST_BE_NONEMPTY,
                          'Please select at least one operational level'),
    'sustainability': (1, MUST_BE_NONEMPTY,
                       'The sustainability field is mandatory'),
    'credibility': (1, MUST_BE_NONEMPTY, 'The credibility field is mandatory'),
    'certificate_services': (1, MUST_BE_NONEMPTY,
                             'Please select at least one service'),
    'organisation': (0, '', ''),
    'phone': (0, '', ''),
    'fax': (0, '', ''),
    'cellphone': (0, '', ''),
    'email': (0, '', ''),
    'webpage': (0, '', ''),
    'lang': (0, '', '')
}
DEFAULT_SCHEMA = {
    'category': dict(
        sortorder=100, widget_type='SelectMultiple', required=True,
        label='Certified categories',
        custom_template='portal_forms/schemawidget-certificate-category',
        help_text='Click on the items from the list below to '
                  'select/deselect them.'),
    'administrative_level': dict(
        sortorder=110, widget_type='SelectMultiple', label='Operation Level',
        list_id='administrative_level', required=True),
    'sustainability': dict(
        sortorder=120, widget_type='SelectMultiple', label='Sustainability',
        list_id='certificate_sustainability', required=True),
    'credibility': dict(
        sortorder=130, widget_type='SelectMultiple', label='Credibility',
        list_id='certificate_credibility', required=True),
    'certificate_services': dict(
        sortorder=140, widget_type='SelectMultiple', label='Service',
        list_id='certificate_services', required=True),
    'organisation': dict(sortorder=150, widget_type='String',
                         label='Organisation', localized=True, required=True),
    'phone': dict(sortorder=170, widget_type='String', label='Phone'),
    'fax': dict(sortorder=180, widget_type='String', label='Fax'),
    'cellphone': dict(sortorder=190, widget_type='String', label='Cell phone'),
    'email': dict(sortorder=200, widget_type='String', label='Email'),
    'webpage': dict(sortorder=210, widget_type='String', label='Webpage'),
}
DEFAULT_SCHEMA.update(deepcopy(NY_CONTENT_BASE_SCHEMA))
DEFAULT_SCHEMA['geo_location'].update(visible=True, required=True)
DEFAULT_SCHEMA['coverage'].update(glossary_id='countries_glossary',
                                  required=True, localized=False)
DEFAULT_SCHEMA['keywords'].update(glossary_id='keywords_glossary',
                                  required=True, localized=False)

# this dictionary is updated at the end of the module
config = {
    'product': 'NaayaContent',
    'module': 'certificate_item',
    'package_path': os.path.abspath(os.path.dirname(__file__)),
    'meta_type': 'Naaya Certificate',
    'label': 'Certificate',
    'permission': PERMISSION_ADD_CERTIFICATE,
    'forms': ['certificate_add', 'certificate_edit', 'certificate_index'],
    'add_form': 'certificate_add_html',
    'description': 'This is Naaya Certificate type.',
    'properties': PROPERTIES_OBJECT,
    'default_schema': DEFAULT_SCHEMA,
    'schema_name': 'NyCertificate',
    '_module': sys.modules[__name__],
    'additional_style': None,
    'icon': os.path.join(os.path.dirname(__file__), 'www', 'certificate.gif'),
    '_misc': {
        'NyCertificate.gif': ImageFile('www/certificate.gif', globals()),
        'NyCertificate_marked.gif': ImageFile('www/certificate_marked.gif',
                                              globals()),
    },
}


def certificate_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, config['meta_type'])
    return self.getFormsTool().getContent({
        'here': self,
        'kind': config['meta_type'],
        'action': 'addNyCertificate',
        'form_helper': form_helper,
        'submitter_info_html': submitter.info_html(self, REQUEST),
    }, 'certificate_add')


def _create_NyCertificate_object(parent, id, contributor):
    id = uniqueId(slugify(id or 'certificate', removelist=[]),
                  lambda x: parent._getOb(x, None) is not None)
    ob = NyCertificate(id, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob


def addNyCertificate(self, id='', REQUEST=None, contributor=None, **kwargs):
    """
    Create a `NyCertificate` type of object.
    """
    # process parameters
    if REQUEST is not None:
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs

    _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
    _releasedate = self.process_releasedate(
        schema_raw_data.pop('releasedate', ''))
    schema_raw_data.setdefault('details', '')
    schema_raw_data.setdefault('resourceurl', '')
    schema_raw_data.setdefault('source', '')
    schema_raw_data.setdefault('topitem', '')

    id = uniqueId(
        slugify(id or schema_raw_data.get('title', '') or 'certificate',
                removelist=[]),
        lambda x: self._getOb(x, None) is not None)

    if contributor is None:
        contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_NyCertificate_object(self, id, contributor)

    form_errors = ob.process_submitted_form(
        schema_raw_data, _lang, _override_releasedate=_releasedate)
    if not is_valid_email(schema_raw_data.get('email')):
        form_errors['email'] = ['Invalid email address']

    if REQUEST is not None:
        submitter_errors = submitter.info_check(self, REQUEST, ob)
        form_errors.update(submitter_errors)

    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1])  # pick a random error
        else:
            abort_transaction_keep_session(REQUEST)
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            return REQUEST.RESPONSE.redirect(
                '%s/certificate_add_html' % self.absolute_url())

    if self.checkPermissionSkipApproval():
        approved = 1
        approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    ob.approveThis(approved, approved_by,
                   _send_notifications=schema_raw_data.get(
                       '_send_notifications'))
    ob.submitThis()

    self.recatalogNyObject(ob)
    notify(NyContentObjectAddEvent(ob, contributor, schema_raw_data))
    # log post date
    auth_tool = self.getAuthenticationTool()
    auth_tool.changeLastPost(contributor)
    # redirect if case
    if REQUEST is not None:
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'certificate_manage_add' or l_referer.find(
                'certificate_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'certificate_add_html':
            self.setSession('referer', self.absolute_url())
            return ob.object_submitted_message(REQUEST)
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
        else:  # undefined state (different referer, called in other context)
            return ob

    return ob.getId()


def importNyCertificate(self, param, id, attrs, content, properties,
                        discussion, objects):
    # this method is called during the import process
    try:
        param = abs(int(param))
    except:
        param = 0
    if param == 3:
        # just try to delete the object
        try:
            self.manage_delObjects([id])
        except:
            pass
    else:
        ob = self._getOb(id, None)
        if param in [0, 1] or (param == 2 and ob is None):
            if param == 1:
                # delete the object if exists
                try:
                    self.manage_delObjects([id])
                except:
                    pass

            ob = _create_NyCertificate_object(
                self, id,
                self.utEmptyToNone(attrs['contributor'].encode('utf-8')))
            ob.sortorder = attrs['sortorder'].encode('utf-8')
            ob.discussion = abs(int(attrs['discussion'].encode('utf-8')))
            ob.organisation = attrs['organisation'].encode('utf-8')
            ob.phone = attrs['phone'].encode('utf-8')
            ob.fax = attrs['fax'].encode('utf-8')
            ob.cellphone = attrs['cellphone'].encode('utf-8')
            ob.email = attrs['email'].encode('utf-8')
            ob.webpage = attrs['webpage'].encode('utf-8')

            for property, langs in properties.items():
                [ob._setLocalPropValue(property, lang, langs[lang])
                    for lang in langs if langs[lang] != '']
            ob.approveThis(
                approved=abs(int(attrs['approved'].encode('utf-8'))),
                approved_by=self.utEmptyToNone(
                    attrs['approved_by'].encode('utf-8')))
            if attrs['releasedate'].encode('utf-8') != '':
                ob.setReleaseDate(attrs['releasedate'].encode('utf-8'))
            ob.import_comments(discussion)
            self.recatalogNyObject(ob)


class certificate_item(Implicit, NyContentData):
    """ """


class NyCertificate(certificate_item, NyAttributes, NyItem, NyCheckControl,
                    NyContentType):
    """ """

    implements(INyCertificate)

    meta_type = config['meta_type']
    meta_label = config['label']

    icon = 'misc_/NaayaContent/NyCertificate.gif'
    icon_marked = 'misc_/NaayaContent/NyCertificate_marked.gif'

    def manage_options(self):
        """ """
        l_options = ()
        if not self.hasVersion():
            l_options += ({'label': 'Properties',
                           'action': 'manage_edit_html'},)
        l_options += ({'label': 'View',
                       'action': 'index_html'},) + NyItem.manage_options
        return l_options

    security = ClassSecurityInfo()

    def __init__(self, id, contributor):
        """ """
        self.id = id
        certificate_item.__init__(self)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor

    security.declarePrivate('objectkeywords')

    def objectkeywords(self, lang):
        return u' '.join(
            [self._objectkeywords(lang), ])

    security.declarePrivate('export_this_tag_custom')

    def export_this_tag_custom(self):
        return 'organisation="%s" ' \
            'phone="%s" fax="%s" cellphone="%s" email="%s" webpage="%s"' % \
            (self.utXmlEncode(self.organisation),
             self.utXmlEncode(self.phone),
             self.utXmlEncode(self.fax),
             self.utXmlEncode(self.cellphone),
             self.utXmlEncode(self.email),
             self.utXmlEncode(self.webpage))

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
        self.recatalogNyObject(self)
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    # site actions
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')

    def saveProperties(self, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED(EXCEPTION_NOTAUTHORIZED_MSG)

        if self.hasVersion():
            obj = self.version
            if self.checkout_user != \
                    self.REQUEST.AUTHENTICATED_USER.getUserName():
                raise EXCEPTION_NOTAUTHORIZED(EXCEPTION_NOTAUTHORIZED_MSG)
        else:
            obj = self

        if REQUEST is not None:
            schema_raw_data = dict(REQUEST.form)
        else:
            schema_raw_data = kwargs
        _lang = schema_raw_data.pop(
            '_lang', schema_raw_data.pop('lang', None))
        _releasedate = self.process_releasedate(
            schema_raw_data.pop('releasedate', ''), obj.releasedate)

        form_errors = self.process_submitted_form(
            schema_raw_data, _lang, _override_releasedate=_releasedate)
        if not is_valid_email(schema_raw_data.get('email')):
            form_errors['email'] = ['Invalid email address']

        if not form_errors:
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
                REQUEST.RESPONSE.redirect(
                    '%s/edit_html?lang=%s' % (self.absolute_url(), _lang))
        else:
            if REQUEST is not None:
                self._prepare_error_response(
                    REQUEST, form_errors, schema_raw_data)
                REQUEST.RESPONSE.redirect(
                    '%s/edit_html?lang=%s' % (self.absolute_url(), _lang))
            else:
                raise ValueError(form_errors.popitem()[1])  # pick an error

    # zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/certificate_manage_edit',
                                        globals())

    # site pages
    security.declareProtected(view, 'index_html')

    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        self.notify_access_event(REQUEST)
        return self.getFormsTool().getContent({'here': self},
                                              'certificate_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')

    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        if self.hasVersion():
            obj = self.version
        else:
            obj = self
        return self.getFormsTool().getContent({'here': obj},
                                              'certificate_edit')

InitializeClass(NyCertificate)

_phone_map = {'WORK': 'phone', 'FAX': 'fax', 'CELL': 'cellphone'}
_phone_pattern = re.compile(r'^TEL;(\w+?)\:')


manage_addNyCertificate_html = PageTemplateFile('zpt/certificate_manage_add',
                                                globals())
manage_addNyCertificate_html.kind = config['meta_type']
manage_addNyCertificate_html.action = 'addNyCertificate'
config.update({
    'constructors': (manage_addNyCertificate_html, addNyCertificate),
    'folder_constructors': [
        ('manage_addNyCertificate_html', manage_addNyCertificate_html),
        ('certificate_add_html', certificate_add_html),
        ('addNyCertificate', addNyCertificate),
        ('import_certificate_item', importNyCertificate),
    ],
    'add_method': addNyCertificate,
    'validation': issubclass(NyCertificate, NyValidation),
    '_class': NyCertificate,
})


def get_config():
    return config
