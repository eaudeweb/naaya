"""Naaya Blob File"""

from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from App.ImageFile import ImageFile
from Globals import InitializeClass
from NyBlobFile import make_blobfile, trim_filename
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaBase.NyContentType import NY_CONTENT_BASE_SCHEMA
from Products.NaayaBase.NyContentType import NyContentData, NyContentType
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.constants import EXCEPTION_NOTAUTHORIZED
from Products.NaayaBase.constants import EXCEPTION_NOTAUTHORIZED_MSG
from Products.NaayaBase.constants import MESSAGE_SAVEDCHANGES
from Products.NaayaBase.constants import PERMISSION_EDIT_OBJECTS
from Products.NaayaCore.LayoutTool.LayoutTool import AdditionalStyle
from Products.NaayaCore.managers.utils import make_id, toAscii
from datetime import datetime
from interfaces import INyBFile
from naaya.content.base.events import NyContentObjectAddEvent
from naaya.content.base.events import NyContentObjectEditEvent
from naaya.content.bfile.utils import file_has_content, tmpl_version
from naaya.content.bfile.utils import get_view_adapter
from naaya.content.bfile.utils import strip_leading_underscores
from naaya.core import submitter
from naaya.core.zope2util import CaptureTraverse
from naaya.core.zope2util import abort_transaction_keep_session
from permissions import PERMISSION_ADD_BFILE
from persistent.dict import PersistentDict
from webdav.Lockable import ResourceLockedError
from zExceptions import NotFound
from zope.event import notify
from zope.interface import implements
import os
import sys

# module constants
DEFAULT_SCHEMA = {
    # add NyBFile-specific properties here
}
DEFAULT_SCHEMA.update(NY_CONTENT_BASE_SCHEMA)

# this dictionary is updated at the end of the module
config = {'product': 'NaayaContent',
          'module': 'bfile_item',
          'package_path': os.path.abspath(os.path.dirname(__file__)),
          'meta_type': 'Naaya Blob File',
          'label': 'File',
          'permission': PERMISSION_ADD_BFILE,
          'forms': ['bfile_add', 'bfile_edit', 'bfile_index',
                    'bfile_quickview_zipfile'],
          'add_form': 'bfile_add_html',
          'description': 'File objects that store data using ZODB BLOBs',
          'default_schema': DEFAULT_SCHEMA,
          'schema_name': 'NyBFile',
          '_module': sys.modules[__name__],
          'additional_style': AdditionalStyle('www/style.css', globals()),
          'icon': os.path.join(os.path.dirname(__file__), 'www', 'bfile.gif'),
          '_misc': {'NyBFile.gif': ImageFile('www/bfile.gif', globals()),
                    'NyBFile_marked.gif': ImageFile('www/bfile_marked.gif',
                                                    globals())},
          }


def bfile_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, config['meta_type'])
    return self.getFormsTool().getContent(
        {'here': self,
         'kind': config['meta_type'],
         'action': 'addNyBFile',
         'form_helper': form_helper,
         'submitter_info_html': submitter.info_html(self, REQUEST),
         },
        'bfile_add')


def _create_NyBFile_object(parent, id, contributor):
    id = make_id(parent, id=id, prefix='file')
    ob = NyBFile(id, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob


def addNyBFile(self, id='', REQUEST=None, contributor=None, **kwargs):
    """
    Create a BFile type of object.
    """
    if REQUEST is not None:
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs
    _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
    _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate',
                                                                ''))
    _uploaded_file = schema_raw_data.pop('uploaded_file', None)

    title = schema_raw_data.get('title', '')
    if not title:
        filename = trim_filename(getattr(_uploaded_file, 'filename', ''))
        base_filename = filename.rsplit('.', 1)[0]  # strip extension
        if base_filename:
            schema_raw_data['title'] = title = strip_leading_underscores(
                base_filename.decode('utf-8'))
    id = toAscii(id)
    id = make_id(self, id=id, title=title, prefix='file')
    if contributor is None:
        contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_NyBFile_object(self, id, contributor)

    form_errors = ob.process_submitted_form(schema_raw_data, _lang,
                                            _override_releasedate=_releasedate)

    if REQUEST is not None:
        submitter_errors = submitter.info_check(self, REQUEST, ob)
        form_errors.update(submitter_errors)

    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1])  # pick a random error
        else:
            abort_transaction_keep_session(REQUEST)
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            REQUEST.RESPONSE.redirect('%s/bfile_add_html' %
                                      self.absolute_url())
            return

    if file_has_content(_uploaded_file):
        ob._save_file(_uploaded_file, language=_lang, contributor=contributor)

    # process parameters
    if self.checkPermissionSkipApproval():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None

    _send_notif = kwargs.get('_send_notifications', True)
    ob.approveThis(approved, approved_by, _send_notifications=_send_notif)
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
        elif l_referer == 'bfile_add_html':
            self.setSession('referer', self.absolute_url())
            return ob.object_submitted_message(REQUEST)

    return ob.getId()


class LocalizedFileDownload(object):
    """
    Perform a download of `context` (must be instance of NyLocalizedBFile).

    This function should be used as the callback for CaptureTraverse;
    `path` will be the captured path for download. We only care about
    the first component, which should be the version requeseted for
    download.

    * `action` in GET == "view" indicates opening file in browser
    default value is "download" (optional)

    Path by default should be in form of:
        test-file/download/en/3/font-awesome-4.1.0.zip
    But it can also be (for BBB):
        test-file/download/font-awesome-4.1.0.zip
    """

    def __call__(self, context, path, REQUEST):
        if len(path) == 1:      # /download/filename.pdf
            ver = context.current_version
            if ver is None:
                raise NotFound
            return self.download(ver, context, REQUEST)
        elif len(path) == 2:    # /download/1/filename.pdf
            ver_number, name = path
            language = context.get_selected_language()
        elif len(path) != 3:
            raise NotFound("Path too big, does not match a scenario")
        else:                   # /download/en/1/filename.pdf
            language, ver_number, name = path

        if not ver_number.isdigit():
            raise NotFound("Version number is not a digit, %s" % ver_number)
        ver_number = int(ver_number)
        if ver_number <= 0:
            raise NotFound("Version number too small")

        versions = context.all_versions(language=language)

        ver = None
        for i in range(ver_number):
            try:
                ver = versions.next()
            except StopIteration:
                raise NotFound("Version not found, number too big")
            if i == ver_number - 1:
                break

        if ver is None:
            raise NotFound
        if ver.removed:
            raise NotFound("Version is removed")

        return self.download(ver, context, REQUEST)

    def download(self, ver, context, REQUEST):
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

localizedbfile_download = LocalizedFileDownload()


class NyBFile(NyContentData, NyAttributes, NyItem, NyCheckControl,
              NyValidation, NyContentType):
    """ """
    implements(INyBFile)

    meta_type = config['meta_type']
    meta_label = config['label']
    icon = 'misc_/NaayaContent/NyBFile.gif'
    icon_marked = 'misc_/NaayaContent/NyBFile_marked.gif'

    manage_options = (
        {'label': 'Properties', 'action': 'manage_edit_html'},
        {'label': 'Edit', 'action': 'manage_main'},
        {'label': 'View', 'action': 'index_html'},
    ) + NyItem.manage_options

    security = ClassSecurityInfo()

    def __init__(self, id, contributor):
        """ """
        self.id = id
        NyContentData.__init__(self)
        NyValidation.__dict__['__init__'](self)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor
        self._versions_i18n = PersistentDict()

    @property
    def versions_store(self):
        if not hasattr(self, '_versions_i18n'):
            self._versions_i18n = PersistentDict()
        return self._versions_i18n

    def all_versions(self, language=None):
        """ Returns all versions of objects.

        It only returns them for current language, and also all
        the non-i18n versions
        """

        for ver in getattr(self, '_versions', []):    #BBB
            yield ver

        if language is None:
            language = self.get_selected_language()

        if self.versions_store.has_key(language) == True:
            for ver in self.versions_store[language]:
                yield ver

    def isVersionable(self):
        """ BFile objects are not versionable

        # TODO: Should remove NyCheckControl inheritance and refactor code to not use
        # NyCheckControl methods.
        """
        return False

    security.declarePrivate('current_version')
    @property
    def current_version(self, language=None):
        versions = list(self.all_versions(language))
        cur = None
        for ver in versions:    # we want last item of this iter
            if not ver.removed:
                cur = ver
            continue
        return cur

    security.declareProtected(view, 'current_version_download_url')
    def current_version_download_url(self):
        language = self.get_selected_language()
        versions = self._versions_for_tmpl(language)
        if versions:
            return versions[-1]['url']
        else:
            return None

    def _save_file(self, the_file, language=None, contributor=""):
        """ """
        bf = make_blobfile(the_file,
                           removed=False,
                           timestamp=datetime.utcnow(),
                           contributor=contributor)

        if language is None:
            language = self.get_selected_language()
        _versions = self.versions_store.pop(language, None)

        if _versions == None:
            self._versions_i18n.update({language: [bf]})
        else:
            _versions.append(bf)
            self._versions_i18n.update({language: _versions})

    security.declarePrivate('remove_version')
    def remove_version(self, number, language=None, removed_by=None):
        """ Number is 0-based index of version
        """
        _versions = list(self.all_versions(language))

        ver = _versions[number] # this can raise errors. Very good

        if ver.removed:
            return

        ver.removed = True
        ver.removed_by = removed_by
        ver.removed_at = datetime.utcnow()
        ver.size = None

        f = ver.open_write()
        f.write('')
        f.close()

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
        _releasedate = self.process_releasedate(
            schema_raw_data.pop('releasedate', ''), self.releasedate)
        _uploaded_file = schema_raw_data.pop('uploaded_file', None)
        versions_to_remove = schema_raw_data.pop('versions_to_remove', [])

        form_errors = self.process_submitted_form(
            schema_raw_data, _lang, _override_releasedate=_releasedate)

        if form_errors:
            if REQUEST is not None:
                self._prepare_error_response(
                    REQUEST, form_errors, schema_raw_data)
                REQUEST.RESPONSE.redirect(
                    '%s/edit_html?lang=%s' % (self.absolute_url(), _lang))
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


    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if self.wl_isLocked():
            raise ResourceLockedError, "File is locked via WebDAV"

        if REQUEST is not None:
            schema_raw_data = dict(REQUEST.form)
        else:
            schema_raw_data = kwargs
        _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
        _releasedate = self.process_releasedate(
            schema_raw_data.pop('releasedate', ''), self.releasedate)
        schema_raw_data.pop('uploaded_file', None)
        versions_to_remove = schema_raw_data.pop('versions_to_remove', [])

        form_errors = self.process_submitted_form(
            schema_raw_data, _lang, _override_releasedate=_releasedate)
        if form_errors:
            raise ValueError(form_errors.popitem()[1])  # pick a random error

        user = self.REQUEST.AUTHENTICATED_USER.getUserName()

        # TODO: check this
        for ver_id in versions_to_remove:
            self.remove_version(int(ver_id) - 1, user)

        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_main?save=ok')

    def _versions_for_tmpl(self, language=None):
        """
        generate a dictionary with info about all versions, suitable for
        use in a page template
        """
        versions = [tmpl_version(self, ver, str(n+1)) for n, ver in
                    enumerate(self.all_versions(language))]
        versions = filter(lambda x: not x['removed'], versions)
        if versions:
            versions[-1]['is_current'] = True

        return versions

    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        language = self.get_selected_language()
        versions = self._versions_for_tmpl(language)
        options = {'versions': versions}
        if versions:
            options['current_version'] = versions[-1]

        template_vars = {'here': self, 'options': options}
        to_return = self.getFormsTool().getContent(template_vars, 'bfile_index')
        return to_return

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
        to_return = self.getFormsTool().getContent(template_vars, 'bfile_edit')

        return to_return

    #TODO: fix this
    security.declareProtected(view, 'version_at_date')
    def version_at_date(self, date):
        """ return the file version that was online at the given date """

        for version in self._versions_for_tmpl():
            if version['timestamp'] < date:
                candidate = version

        return candidate

    security.declareProtected(view, 'download')
    download = CaptureTraverse(localizedbfile_download)

InitializeClass(NyBFile)

config.update({
    'constructors': (addNyBFile,),
    'folder_constructors': [
        ('bfile_add_html', bfile_add_html),
        ('addNyBFile', addNyBFile),
    ],
    'add_method': addNyBFile,
    'validation': issubclass(NyBFile, NyValidation),
    '_class': NyBFile,
})


def get_config():
    return config
