from datetime import datetime
import os
import sys

from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view
from zExceptions import NotFound
from zope.event import notify
from zope.interface import implements
from persistent.dict import PersistentDict

from naaya.content.base.events import NyContentObjectAddEvent
from naaya.content.base.events import NyContentObjectEditEvent
from naaya.core.zope2util import CaptureTraverse

from Products.NaayaBase.NyContentType import (
    NyContentData, NyContentType)
from naaya.content.base.constants import *
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.constants import *
from Products.NaayaCore.managers.utils import make_id, toAscii
from naaya.core import submitter
from naaya.core.zope2util import abort_transaction_keep_session

from naaya.content.bfile.bfile_item import DEFAULT_SCHEMA
from naaya.content.bfile.NyBlobFile import make_blobfile, trim_filename
from naaya.content.bfile.utils import file_has_content, tmpl_version, get_view_adapter
from naaya.content.bfile.interfaces import INyBFile

from permissions import PERMISSION_ADD_LOCALIZED_BFILE

#ADDITIONAL_STYLE = open(ImageFile('www/style.css', globals()).path).read()

config = {
        'product': 'NaayaContent',
        'module': 'localizedbfile_item',
        'package_path': os.path.abspath(os.path.dirname(__file__)),
        'meta_type': 'Naaya Localized Blob File',
        'label': 'Localized File',
        'permission': PERMISSION_ADD_LOCALIZED_BFILE,
        'forms': ['localizedbfile_add', 'localizedbfile_edit', 'localizedbfile_index', 'localizedbfile_quickview_zipfile'],
        'add_form': 'localizedbfile_add_html',
        'description': 'Localized file objects that store data using ZODB BLOBs',
        'default_schema': DEFAULT_SCHEMA,
        'schema_name': 'NyLocalizedBFile',
        '_module': sys.modules[__name__],
 #       'additional_style': ADDITIONAL_STYLE,
        'icon': os.path.join(os.path.dirname(__file__), 'www', 'bfile.gif'),
        '_misc': {
        },
    }

def localizedbfile_add_html(self, REQUEST=None, RESPONSE=None):
    """ Create a Localized BFile object """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, config['meta_type'])

    d = {
            'here': self,
            'kind': config['meta_type'],
            'action': 'addNyLocalizedBFile',
            'form_helper': form_helper,
            'submitter_info_html': submitter.info_html(self, REQUEST),
        }

    to_return = self.getFormsTool().getContent(d, 'localizedbfile_add')

    return to_return

def _create_LocalizedNyBFile_object(parent, id, contributor):
    id = make_id(parent, id=id, prefix='localizedfile')
    ob = NyLocalizedBFile(id, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def addNyLocalizedBFile(self, id='', REQUEST=None, contributor=None, _lang=None, **kwargs):
    """Create a Localized BFile object"""
    if REQUEST is not None:
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs

    if _lang is None:
        _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))

    _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''))
    _uploaded_file = schema_raw_data.pop('uploaded_file', None)
    title = schema_raw_data.get('title', '')

    if not title:
        filename = trim_filename(getattr(_uploaded_file, 'filename', ''))
        base_filename = filename.rsplit('.', 1)[0] # strip extension
        if base_filename:
            schema_raw_data['title'] = title = base_filename.decode('utf-8')

    id = toAscii(id)
    id = make_id(self, id=id, title=title, prefix='file')

    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_LocalizedNyBFile_object(self, id, contributor)

    if _lang is None:
        _lang = ob.get_selected_language()
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
            REQUEST.RESPONSE.redirect('%s/localizedbfile_add_html' % self.absolute_url())
            return

    if file_has_content(_uploaded_file):
        ob._save_file(_uploaded_file, _lang, contributor)

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
        return ob.object_submitted_message(REQUEST)

    return ob.getId()

def localizedbfile_download(context, path, REQUEST):
    """
    Perform a download of `context` (must be instance of NyLocalizedBFile).

    This function should be used as the callback for CaptureTraverse;
    `path` will be the captured path for download. We only care about
    the first component, which should be the version requeseted for
    download.

    * `action` in GET == "view" indicates opening file in browser
    default value is "download" (optional)

    """
    try:
        ver_number = int(path[0]) - 1
        if ver_number < 0:
            raise IndexError
        language = context.get_selected_language()
        if language is None:
            language = context.get_default_lang_code()

        if (not context._versions) or (not context._versions[language]):
            raise NotFound
        ver = context._versions[language][ver_number]
        if ver.removed:
            raise IndexError
    except (IndexError, ValueError, KeyError), e:
        raise NotFound
    RESPONSE = REQUEST.RESPONSE
    action = REQUEST.form.get('action', 'download')
    if action == 'view':
        view_adapter = get_view_adapter(ver)
        if view_adapter is not None:
            return view_adapter(context)
        return ver.send_data(RESPONSE, as_attachment=False, REQUEST=REQUEST)
    elif action == 'download':
        return ver.send_data(RESPONSE, set_filename=False, REQUEST=REQUEST)
    else:
        raise NotFound

class NyLocalizedBFile(NyContentData, NyAttributes, NyItem, NyCheckControl, NyValidation, NyContentType):
    """ """
    implements(INyBFile)

    meta_type = config['meta_type']
    meta_label = config['label']

    manage_options = (
        {'label': 'Properties', 'action': 'manage_edit_html'},
        {'label': 'Edit', 'action': 'manage_main'},
        {'label': 'View', 'action': 'index_html'},
    ) + NyItem.manage_options

    security = ClassSecurityInfo()

    def __init__(self, id, contributor):
        self.id = id
        NyContentData.__init__(self)
        NyValidation.__dict__['__init__'](self)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor
        self._versions = PersistentDict()

    security.declarePrivate('current_version')
    @property
    def current_version(self):
        language = self.get_selected_language()
        hasKey = self._versions.has_key(language)
        if hasKey == True:
            _versions = self._versions[language]
            for ver in reversed(_versions):
                if not ver.removed:
                    return ver
        else:
            return None

    security.declareProtected(view, 'current_version_download_url')
    def current_version_download_url(self):
        language = self.get_selected_language()
        versions = self._versions_for_tmpl(language)
        if versions:
            return versions[-1]['url']
        else:
            return None

    security.declarePrivate('remove_version')
    def remove_version(self, number, language, removed_by=None):

        if (not self._versions[language]) or (not self._versions[language][number]):
            raise ValueError # pick a random error

        ver = self._versions[language][number]

        if ver.removed:
            return

        ver.removed = True
        ver.removed_by = removed_by
        ver.removed_at = datetime.utcnow()
        ver.size = None

        f = ver.open_write()
        f.write('')
        f.close()

    def _save_file(self, the_file, language, contributor):
        """ """
        bf = make_blobfile(the_file,
                           removed=False,
                           timestamp=datetime.utcnow(),
                           contributor=contributor)
        _versions = self._versions.pop(language, None)

        if _versions == None:
            toAdd = [bf]
            newD = {language:toAdd}
            self._versions.update(newD)
        else:
            _versions.append(bf)
            newD = {language:_versions}
            self._versions.update(newD)

    def _versions_for_tmpl(self, language):
        """ """
        hasKey = self._versions.has_key(language)
        if hasKey == True:
            _versions = self._versions[language]
            versions = [tmpl_version(self, ver, str(n+1))
                        for n, ver in enumerate(_versions)
                        if not ver.removed]
            if versions:
                versions[-1]['is_current'] = True

            return versions
        else:
            return None

    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        language = self.get_selected_language()
        versions = self._versions_for_tmpl(language)
        options = {'versions': versions}
        if versions:
            options['current_version'] = versions[-1]

        template_vars = {'here': self, 'options': options}
        to_return = self.getFormsTool().getContent(template_vars, 'localizedbfile_index')
        return to_return

    def isVersionable(self):
        """ Localized BFiles are not versionable"""
        return False

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG

        if REQUEST is not None:
            schema_raw_data = dict(REQUEST.form)
        else:
            schema_raw_data = kwargs
        _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
        _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''), self.releasedate)
        _uploaded_file = schema_raw_data.pop('uploaded_file', None)
        versions_to_remove = schema_raw_data.pop('versions_to_remove', [])

        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

        if form_errors:
            if REQUEST is not None:
                self._prepare_error_response(REQUEST, form_errors, schema_raw_data)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))
                return
            else:
                raise ValueError(form_errors.popitem()[1]) # pick a random error

        contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

        for ver_id in reversed(versions_to_remove):
            self.remove_version(int(ver_id) - 1, _lang, contributor)

        self._p_changed = 1
        self.recatalogNyObject(self)
        #log date
        auth_tool = self.getAuthenticationTool()
        auth_tool.changeLastPost(contributor)

        if file_has_content(_uploaded_file):
            self._save_file(_uploaded_file, _lang, contributor)

        notify(NyContentObjectEditEvent(self, contributor))

        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES,
                                     date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' %
                                      (self.absolute_url(), _lang))

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        hasKey = REQUEST.form.has_key('lang')
        if hasKey == False:
            language = self.get_selected_language()
        else:
            language = REQUEST.form['lang']

        options = {'versions': self._versions_for_tmpl(language)}
        template_vars = {'here': self, 'options': options}
        to_return = self.getFormsTool().getContent(template_vars, 'localizedbfile_edit')

        return to_return

    security.declareProtected(view, 'download')
    download = CaptureTraverse(localizedbfile_download)


config.update({
    'constructors': (addNyLocalizedBFile,),
    'folder_constructors': [
            ('localizedbfile_add_html', localizedbfile_add_html),
            ('addNyLocalizedBFile', addNyLocalizedBFile),
            ],
    'add_method': addNyLocalizedBFile,
    'validation': issubclass(NyLocalizedBFile, NyValidation),
    '_class': NyLocalizedBFile,
            })

def get_config():
    return config
