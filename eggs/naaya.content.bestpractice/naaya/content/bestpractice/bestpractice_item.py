"""Naaya Good Practice Destination"""
import os
import sys
import transaction
from copy import deepcopy

from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view
from App.ImageFile import ImageFile
from Globals import InitializeClass
from persistent.list import PersistentList
from zope.event import notify
from zope.interface import implements

from naaya.content.base.events import NyContentObjectAddEvent
from naaya.core.zope2util import CaptureTraverse
from interfaces import INyBestPractice

from Products.NaayaBase.NyContentType import (
    NyContentData, NY_CONTENT_BASE_SCHEMA)
from Products.NaayaBase.constants import PERMISSION_EDIT_OBJECTS
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaCore.managers.utils import make_id, toAscii
from naaya.core import submitter
from naaya.core.zope2util import abort_transaction_keep_session

from naaya.content.bfile.NyBlobFile import trim_filename
from naaya.content.bfile.utils import file_has_content
from naaya.content.bfile.bfile_item import localizedbfile_download as \
    bestpractice_download
from naaya.content.bfile.bfile_item import NyBFile

from permissions import PERMISSION_ADD_BESTPRACTICE
from naaya.content.bestpractice.skel import REF_TREES, KEYWORD_INDEXES

# module constants
DEFAULT_SCHEMA = {
    'personaltitle': dict(
        sortorder=110, widget_type='String', label='Personal title',
        localized=True),
    'firstname': dict(
        sortorder=120, widget_type='String', label='First name'),
    'lastname': dict(
        sortorder=130, widget_type='String', label='Last name'),
    'jobtitle': dict(
        sortorder=140, widget_type='String', label='Job title',
        localized=True),
    'department': dict(
        sortorder=150, widget_type='String', label='Department',
        localized=True),
    'organisation': dict(
        sortorder=160, widget_type='String', label='Organisation',
        localized=True),
    'postaladdress': dict(
        sortorder=170, widget_type='String', label='Postal address',
        localized=True),
    'phone': dict(
        sortorder=180, widget_type='String', label='Phone'),
    'fax': dict(
        sortorder=190, widget_type='String', label='Fax'),
    'cellphone': dict(
        sortorder=200, widget_type='String', label='Cell phone'),
    'email': dict(
        sortorder=210, widget_type='String', label='Email'),
    'webpage': dict(
        sortorder=220, widget_type='String', label='Webpage',
        localized=True),
    'facebook': dict(
        sortorder=230, widget_type='String', label='Facebook profile'),
    'linkedin': dict(
        sortorder=240, widget_type='String', label='Linked In profile'),
    'twitter': dict(
        sortorder=250, widget_type='String', label='Twitter profile'),
    'gstc_criteria': dict(
        sortorder=310, widget_type='SelectMultiple',
        label='GSTC Criteria for Destinations', list_id='gstc_criteria',
        required=True),
    'landscape_type': dict(
        sortorder=320, widget_type='Select', label='Landscape type',
        list_id='landscape_type', required=True),
    'topics': dict(
        sortorder=330, widget_type='SelectMultiple', label='Topics',
        list_id='topics', required=True),
    'category': dict(
        sortorder=340, widget_type='Select',
        label='Market place category',
        list_id='certificate_categories', required=True),
}
DEFAULT_SCHEMA.update(deepcopy(NY_CONTENT_BASE_SCHEMA))
DEFAULT_SCHEMA['coverage'].update(glossary_id='countries_glossary',
                                  label='Country',
                                  required=True, localized=False)
DEFAULT_SCHEMA['description'].update(
    label='Short description of content',
    custom_template='portal_forms/schemawidget-NyBestPractice-description',
    required=True)
DEFAULT_SCHEMA['geo_location'].update(visible=True, required=True)
DEFAULT_SCHEMA['geo_type'].update(
    custom_template='portal_forms/schemawidget-bestpractice-geo_type',
    visible=True)


def bestpractice_on_install(site):
    ptool = site.getPortletsTool()
    for tree in REF_TREES:
        if not getattr(ptool, tree[0], None):
            ptool.manage_addRefTree(tree[0])
            ref_tree = getattr(ptool, tree[0])
            for k, v in tree[1]:
                ref_tree.manage_addRefTreeNode(k, v)
    cat = site.getCatalogTool()
    reindex = []
    for index in KEYWORD_INDEXES:
        if index not in cat.indexes():
            cat.addIndex(index, 'KeywordIndex')
            reindex.append(index)
    cat.manage_reindexIndex(reindex)


def bestpractice_on_uninstall(site):
    cat = site.getCatalogTool()
    for index in KEYWORD_INDEXES:
        if index in cat.indexes():
            cat.delIndex(index)
            cat._p_changed = True
            transaction.commit()


# this dictionary is updated at the end of the module
config = {
    'product': 'NaayaContent',
    'module': 'bestpractice_item',
    'package_path': os.path.abspath(os.path.dirname(__file__)),
    'meta_type': 'Naaya Best Practice',
    'on_install': bestpractice_on_install,
    'on_uninstall': bestpractice_on_uninstall,
    'label': 'Good Practice Destination',
    'permission': PERMISSION_ADD_BESTPRACTICE,
    'forms': ['bestpractice_add', 'bestpractice_edit', 'bestpractice_index',
              'bestpractice_quickview_zipfile'],
    'add_form': 'bestpractice_add_html',
    'description': 'File objects that store data using ZODB BLOBs',
    'default_schema': DEFAULT_SCHEMA,
    'schema_name': 'NyBestPractice',
    '_module': sys.modules[__name__],
    'icon': os.path.join(os.path.dirname(__file__), 'www', 'bestpractice.gif'),
    '_misc': {
        'NyBestPractice.gif': ImageFile('www/bestpractice.gif', globals()),
        'NyBestPractice_marked.gif': ImageFile('www/bestpractice_marked.gif',
                                               globals()),
    },
}


def bestpractice_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, config['meta_type'])
    return self.getFormsTool().getContent({
        'here': self,
        'kind': config['meta_type'],
        'action': 'addNyBestPractice',
        'form_helper': form_helper,
        'submitter_info_html': submitter.info_html(self, REQUEST),
    }, 'bestpractice_add')


def _create_NyBestPractice_object(parent, id, contributor):
    id = make_id(parent, id=id, prefix='bestpractice')
    ob = NyBestPractice(id, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob


def addNyBestPractice(self, id='', REQUEST=None, contributor=None, **kwargs):
    """
    Create a BFile type of object.
    """
    if REQUEST is not None:
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs
    _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
    _releasedate = self.process_releasedate(
        schema_raw_data.pop('releasedate', ''))
    _uploaded_file = schema_raw_data.pop('uploaded_file', None)

    title = schema_raw_data.get('title', '')
    if not title:
        filename = trim_filename(getattr(_uploaded_file, 'filename', ''))
        base_filename = filename.rsplit('.', 1)[0]  # strip extension
        if base_filename:
            schema_raw_data['title'] = title = base_filename.decode('utf-8')
    id = toAscii(id)
    id = make_id(self, id=id, title=title, prefix='bestpractice')
    if contributor is None:
        contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_NyBestPractice_object(self, id, contributor)

    form_errors = ob.process_submitted_form(
        schema_raw_data, _lang, _override_releasedate=_releasedate)

    if REQUEST is not None:
        submitter_errors = submitter.info_check(self, REQUEST, ob)
        form_errors.update(submitter_errors)

    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1])  # pick a random error
        else:
            abort_transaction_keep_session(REQUEST)
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            REQUEST.RESPONSE.redirect(
                '%s/bestpractice_add_html' % self.absolute_url())
            return

    if file_has_content(_uploaded_file):
        ob._save_file(_uploaded_file, contributor)

    # process parameters
    if self.checkPermissionSkipApproval():
        approved, approved_by = (
            1, self.REQUEST.AUTHENTICATED_USER.getUserName())
    else:
        approved, approved_by = 0, None
    ob.approveThis(approved, approved_by)
    ob.submitThis()

    self.recatalogNyObject(ob)
    notify(NyContentObjectAddEvent(ob, contributor, schema_raw_data))
    # log post date
    auth_tool = self.getAuthenticationTool()
    auth_tool.changeLastPost(contributor)
    # redirect if case
    if REQUEST is not None:
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'bfile_manage_add' or l_referer.find(
                'bfile_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'bestpractice_add_html':
            self.setSession('referer', self.absolute_url())
            return ob.object_submitted_message(REQUEST)

    return ob.getId()


class NyBestPractice(NyBFile):
    """ """
    implements(INyBestPractice)

    meta_type = config['meta_type']
    meta_label = config['label']
    icon = 'misc_/NaayaContent/NyBestPractice.gif'
    icon_marked = 'misc_/NaayaContent/NyBestPractice_marked.gif'

    security = ClassSecurityInfo()

    def __init__(self, id, contributor):
        """ """
        self.id = id
        NyContentData.__init__(self)
        NyValidation.__dict__['__init__'](self)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor
        self._versions = PersistentList()

    security.declareProtected(view, 'index_html')

    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        versions = self._versions_for_tmpl()
        options = {'versions': versions}
        if versions:
            options['current_version'] = versions[-1]

        template_vars = {'here': self, 'options': options}
        self.notify_access_event(REQUEST)
        return self.getFormsTool().getContent(template_vars,
                                              'bestpractice_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')

    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        options = {'versions': self._versions_for_tmpl()}
        template_vars = {'here': self, 'options': options}
        return self.getFormsTool().getContent(template_vars,
                                              'bestpractice_edit')

    security.declareProtected(view, 'download')
    download = CaptureTraverse(bestpractice_download)


InitializeClass(NyBestPractice)

config.update({
    'constructors': (addNyBestPractice,),
    'folder_constructors': [
        ('bestpractice_add_html', bestpractice_add_html),
        ('addNyBestPractice', addNyBestPractice),
    ],
    'add_method': addNyBestPractice,
    'validation': issubclass(NyBestPractice, NyValidation),
    '_class': NyBestPractice,
})


def get_config():
    return config
