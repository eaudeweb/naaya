import os
import sys
import mimetypes

from zope import event as zope_event
from OFS.event import ObjectWillBeRemovedEvent
from OFS.Image import cookId
from Globals import InitializeClass
from App.ImageFile import ImageFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.NaayaBase.NyFSFile import NyFSFile
from Products.NaayaBase.NyContentType import NyContentData
from zope.event import notify
from naaya.content.base.events import NyContentObjectAddEvent
from naaya.content.base.events import NyContentObjectEditEvent
from zope.interface import implements
from interfaces import INyFile

from Products.NaayaBase.NyContentType import NyContentType, NY_CONTENT_BASE_SCHEMA
from naaya.content.base.constants import *
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaBase.NyFolderishVersioning import NyFolderishVersioning
from Products.NaayaBase.NyBase import rss_item_for_object
from Products.NaayaCore.managers.utils import slugify, uniqueId, get_nsmap
from naaya.core import submitter
from naaya.core.zope2util import abort_transaction_keep_session

from permissions import PERMISSION_ADD_FILE

from lxml import etree
from lxml.builder import ElementMaker

#module constants
PROPERTIES_OBJECT = {
    'id':               (0, '', ''),
    'title':            (1, MUST_BE_NONEMPTY, 'The Title field must have a value.'),
    'description':      (0, '', ''),
    'coverage':         (0, '', ''),
    'keywords':         (0, '', ''),
    'sortorder':        (0, MUST_BE_POSITIV_INT, 'The Sort order field must contain a positive integer.'),
    'releasedate':      (0, MUST_BE_DATETIME, 'The Release date field must contain a valid date.'),
    'discussion':       (0, '', ''),
    'file':             (0, MUST_BE_NONEMPTY, ''),
    'url':              (0, '', ''),
    'lang':             (0, '', '')
}
DEFAULT_SCHEMA = {
    # add NyFile-specific properties here
}
DEFAULT_SCHEMA.update(NY_CONTENT_BASE_SCHEMA)

# this dictionary is updated at the end of the module
config = {
        'product': 'NaayaContent',
        'module': 'file_item',
        'package_path': os.path.abspath(os.path.dirname(__file__)),
        'meta_type': 'Naaya File',
        'label': 'File',
        'permission': PERMISSION_ADD_FILE,
        'forms': ['file_add', 'file_edit', 'file_index'],
        'add_form': 'file_add_html',
        'description': 'This is Naaya File type.',
        'properties': PROPERTIES_OBJECT,
        'default_schema': DEFAULT_SCHEMA,
        'schema_name': 'NyFile',
        '_module': sys.modules[__name__],
        'additional_style': None,
        'icon': os.path.join(os.path.dirname(__file__), 'www', 'file.gif'),
        '_misc': {
                'NyFile.gif': ImageFile('www/file.gif', globals()),
                'NyFile_marked.gif': ImageFile('www/file_marked.gif', globals()),
            },
    }

def file_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, config['meta_type'])
    return self.getFormsTool().getContent({
        'here': self,
        'kind': config['meta_type'],
        'action': 'addNyFile',
        'form_helper': form_helper,
        'submitter_info_html': submitter.info_html(self, REQUEST),
    }, 'file_add')

def _create_NyFile_object(parent, id, title, file, precondition, contributor):
    id = uniqueId(slugify(id or title or 'file', removelist=[]),
                  lambda x: parent._getOb(x, None) is not None)
    ob = NyFile_extfile(id, title, file, precondition, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def addNyFile(self, id='', REQUEST=None, contributor=None, **kwargs):
    """
    Create a File type of object.
    """

    if REQUEST is not None:
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs
    _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
    _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''))

    _source = schema_raw_data.pop('source', 'file')
    _file = schema_raw_data.pop('file', '')
    _url = schema_raw_data.pop('url', '')
    _precondition = schema_raw_data.pop('precondition', '')

    title = schema_raw_data.get('title', '')

    #process parameters
    if _source=='file': id = cookId(id, title, _file)[0] #upload from a file
    id = uniqueId(slugify(id or title or 'file', removelist=[]),
                  lambda x: self._getOb(x, None) is not None)
    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_NyFile_object(self, id, title, '', _precondition, contributor)

    form_errors = ob.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)
    if hasattr(_file, 'read') and not _file.read() and not _url:
        form_errors['file'] = ['File upload or URL is mandatory']

    if REQUEST is not None:
        submitter_errors = submitter.info_check(self, REQUEST, ob)
        form_errors.update(submitter_errors)

    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1]) # pick a random error
        else:
            abort_transaction_keep_session(REQUEST)
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            REQUEST.RESPONSE.redirect('%s/file_add_html' % self.absolute_url())
            return

    #process parameters
    if self.checkPermissionSkipApproval():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    ob.submitThis()

    _send_notif = kwargs.get('_send_notifications', True)
    ob.approveThis(approved, approved_by, _send_notifications=_send_notif)

    ob.handleUpload(_source, _file, _url)

    self.recatalogNyObject(ob)
    notify(NyContentObjectAddEvent(ob, contributor, schema_raw_data))
    #log post date
    auth_tool = self.getAuthenticationTool()
    auth_tool.changeLastPost(contributor)
    #redirect if case
    if REQUEST is not None:
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'file_manage_add' or l_referer.find('file_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'file_add_html':
            self.setSession('referer', self.absolute_url())
            return ob.object_submitted_message(REQUEST)
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
        else: # undefined state (different referer, called in other context)
            return ob

    return ob.getId()

def importNyFile(self, param, id, attrs, content, properties, discussion, objects):
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

            ob = _create_NyFile_object(self, id, '',
                file=self.utBase64Decode(attrs['file'].encode('utf-8')),
                precondition=attrs['precondition'].encode('utf-8'),
                contributor=self.utEmptyToNone(attrs['contributor'].encode('utf-8'))
            )

            ob.sortorder = attrs['sortorder'].encode('utf-8')
            ob.discussion = abs(int(attrs['discussion'].encode('utf-8')))
            ob.content_type = attrs['content_type'].encode('utf-8')
            ob._p_changed = 1
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

class file_item(NyContentData, NyFSFile):
    """ """
    meta_type = config['meta_type']

    def __init__(self, id, title, file, precondition):
        """
        Constructor.
        """
        NyFSFile.__init__(self, id, title, file, '', precondition)
        #"dirty" trick to get rid of the File's title property
        try: del self.title
        except: pass
        try: del self.id
        except: pass
        NyContentData.__init__(self)

    def del_file_title(self):
        """
        Removes the File's object 'title' property.
        We are using a LocalProperty 'title'.
        """
        try: del self.title
        except: pass
        self._p_changed = 1

    def getContentType(self):
        """Returns file content-type"""
        data = self.get_data(as_string=False)
        ctype = data.getContentType()
        if not ctype:
            return getattr(self, 'content_type', '')
        return ctype

    def _get_upload_file(self, source, file, url):
        """ grab file from disk or from a given url.
        Returns data, content_type, size, filename
        """
        if source=='file':
            if file != '':
                if hasattr(file, 'filename'):
                    filename = cookId('', '', file)[0]
                    if filename != '':
                        data, size = self._read_data(file)
                        content_type = mimetypes.guess_type(file.filename)[0]
                        if content_type is None:
                            content_type = self._get_content_type(file, data, self.__name__, 'application/octet-stream')
                        return data, content_type, size, filename
                else:
                    return file, '', None, ''
        elif source=='url':
            if url != '':
                l_data, l_ctype = self.grabFromUrl(url)
                if l_data is not None:
                    return l_data, l_ctype, None, ''
        return '', '', None, ''

    def handleUpload(self, source, file, url):
        """
        Upload a file from disk or from a given URL.
        """
        data, ctype, size, filename = self._get_upload_file(source, file, url)
        self.update_data(data, ctype, size, filename)

class NyFile_extfile(file_item, NyAttributes, NyItem, NyFolderishVersioning, NyCheckControl, NyValidation, NyContentType):
    """ """

    implements(INyFile)

    meta_type = config['meta_type']
    meta_label = config['label']
    icon = 'misc_/NaayaContent/NyFile.gif'
    icon_marked = 'misc_/NaayaContent/NyFile_marked.gif'

    def manage_options(self):
        """ """
        l_options = ()
        if not self.hasVersion():
            l_options += ({'label': 'Properties', 'action': 'manage_edit_html'},
                        {'label': 'Edit', 'action': 'manage_main'},)
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyItem.manage_options
        return l_options

    security = ClassSecurityInfo()

    def __init__(self, id, title, file, precondition, contributor):
        """ """
        self.id = id
        file_item.__init__(self, id, title, file, precondition)
        NyValidation.__dict__['__init__'](self)
        NyCheckControl.__dict__['__init__'](self)
        NyFolderishVersioning.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        return 'downloadfilename="%s" file="%s" content_type="%s" precondition="%s" validation_status="%s" validation_date="%s" validation_by="%s" validation_comment="%s"' % \
            (self.utXmlEncode(self.downloadfilename()),
                self.utBase64Encode(str(self.utNoneToEmpty(self.get_data()))),
                self.utXmlEncode(self.getContentType()),
                self.utXmlEncode(self.precondition),
                self.utXmlEncode(self.validation_status),
                self.utXmlEncode(self.validation_date),
                self.utXmlEncode(self.validation_by),
                self.utXmlEncode(self.validation_comment))

    security.declarePrivate('syndicateThis')
    def syndicateThis(self, lang=None):
        l_site = self.getSite()
        if lang is None: lang = self.gl_get_selected_language()
        item = rss_item_for_object(self, lang)
        syndication_tool = self.getSyndicationTool()
        namespaces = syndication_tool.getNamespaceItemsList()
        nsmap = get_nsmap(namespaces)
        dc_namespace = nsmap['dc']
        Dc = ElementMaker(namespace=dc_namespace, nsmap=nsmap)
        the_rest = Dc.root(
            Dc.type('Text'),
            Dc.format('application'),
            Dc.source(l_site.publisher),
            Dc.creator(l_site.creator),
            Dc.publisher(l_site.publisher)
            )
        item.extend(the_rest)
        return etree.tostring(item, xml_declaration=False, encoding="utf-8")

    security.declarePublic('showVersionData')
    def showVersionData(self, vid=None, REQUEST=None, RESPONSE=None):
        """ """
        if vid:
            version_data = self.getVersion(vid)
            if version_data is not None:
                #show data for file: set content type and return data
                RESPONSE.setHeader('Content-Type', version_data.getContentType())
                REQUEST.RESPONSE.setHeader('Content-Disposition', 'attachment;filename=' + self.utToUtf8(self.getVersionFilename(vid)))
                return version_data.index_html()
            else:
                return 'Invalid version data!'
        else:
            return 'Invalid version id!'

    security.declarePublic('getVersionFilename')
    def getVersionFilename(self, vid):
        """ Returns version filename"""
        version = self.getVersion(vid)
        filename = getattr(version, 'filename', [])
        if not filename:
            return ''
        return filename[-1]

    #zmi actions
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
        _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''), self.releasedate)
        _approved = int(bool(schema_raw_data.pop('approved', False)))

        _precondition = schema_raw_data.pop('precondition', '')

        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)
        if form_errors:
            raise ValueError(form_errors.popitem()[1]) # pick a random error

        self.precondition = _precondition

        if _approved != self.approved:
            if _approved == 0: _approved_by = None
            else: _approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
            self.approveThis(_approved, _approved_by)
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_main?save=ok')

    #XXX Should remove NyCheckControl inheritance and refactor code to not use
    # NyCheckControl methods.
    def isVersionable(self):
        """ File objects are not versionable
        """
        return False

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
        self.precondition = self.version.precondition
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
        self.version = file_item(self.id, self.title, '', self.precondition)
        self.version.copy_naaya_properties_from(self)
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'discardVersion')
    def discardVersion(self, REQUEST=None):
        """ """
        self.version.manage_beforeUpdate()
        NyFile_extfile.inheritedAttribute('discardVersion')(self, REQUEST)

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

        _source = schema_raw_data.pop('source', 'file')
        _file = schema_raw_data.pop('file', '')
        _url = schema_raw_data.pop('url', '')
        _precondition = schema_raw_data.pop('precondition', '')
        _version = schema_raw_data.pop('version', False)

        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

        if form_errors:
            if REQUEST is not None:
                self._prepare_error_response(REQUEST, form_errors, schema_raw_data)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))
                return
            else:
                raise ValueError(form_errors.popitem()[1]) # pick a random error

        # Upload file
        if _source:
            self.saveUpload(source=_source, file=_file, url=_url, version=_version, lang=_lang)

        self.precondition = _precondition

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

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveUpload')
    def saveUpload(self, source='file', file='', url='', version=True, lang=None, REQUEST=None):
        """ """
        if REQUEST:
            username = REQUEST.AUTHENTICATED_USER.getUserName()
        else:
            username = self.REQUEST.AUTHENTICATED_USER.getUserName()

        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if self.wl_isLocked():
            raise ResourceLockedError, "File is locked via WebDAV"

        if lang is None:
            lang = self.gl_get_selected_language()

        if not self.hasVersion():
            #this object has not been checked out; save changes directly into the object
            context = self
        else:
            #this object has been checked out; save changes into the version object
            if self.checkout_user != username:
                raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
            context = self.version

        if version:
            newdata = self._get_upload_file(source, file, url)[0]
            context.createVersion(self.get_data(as_string=False),
                newdata, username=username, modification_time=self.utGetTodayDate())
        else:
            ext_file = self.get_data(as_string=False)
            zope_event.notify(ObjectWillBeRemovedEvent(
                ext_file, self, ext_file.getId()))

        context.handleUpload(source, file, url)
        self.recatalogNyObject(self)

        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))

    security.declareProtected(view_management_screens, 'manage_advanced_html')
    manage_advanced_html = PageTemplateFile('zpt/file_manage_advanced', globals())

    security.declareProtected(view_management_screens, 'manageAdvancedProperties')
    def manageAdvancedProperties(self, REQUEST=None, **kwargs):
        """ """
        if REQUEST:
            kwargs.update(REQUEST.form)
        filename = kwargs.get('filename', '')
        filename = filename.split('/')
        filename = [x.strip() for x in filename if x]
        content_type = kwargs.get('content_type', '') or self.getContentType()
        self._update_properties(filename=filename, content_type=content_type)
        return self.manage_advanced_html(REQUEST=REQUEST, update_menu=1)

    #site actions
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        self.notify_access_event(REQUEST)
        return self.getFormsTool().getContent({'here': self}, 'file_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'file_edit')

    def downloadfilename(self, version=False):
        """ Return download file name
        """
        context = self
        if version and self.hasVersion():
            context = self._getOb('version')
        filename = context._get_data_name()
        if not filename:
            return context.title_or_id()
        return filename[-1]

    security.declareProtected(view, 'download')
    def download(self, REQUEST, RESPONSE):
        """ """
        version = REQUEST.get('version', False)
        RESPONSE.setHeader('Content-Type', self.getContentType())
        RESPONSE.setHeader('Content-Length', self.size)
        filename = self.utToUtf8(self.downloadfilename())
        filename = self.utSlugify(filename, removelist=[])
        RESPONSE.setHeader('Content-Disposition', 'attachment;filename=' + filename)
        RESPONSE.setHeader('Pragma', 'public')
        RESPONSE.setHeader('Cache-Control', 'max-age=0')
        self.notify_access_event(REQUEST, 'download')
        if version and self.hasVersion():
            return file_item.index_html(self.version, REQUEST, RESPONSE)
        return file_item.index_html(self, REQUEST, RESPONSE)

    security.declareProtected(view, 'view')
    def view(self, REQUEST, RESPONSE):
        """ """
        self.notify_access_event(REQUEST)
        RESPONSE.setHeader('Content-Type', self.getContentType())
        RESPONSE.setHeader('Content-Length', self.size)
        RESPONSE.setHeader('Pragma', 'public')
        RESPONSE.setHeader('Cache-Control', 'max-age=0')
        return file_item.index_html(self, REQUEST, RESPONSE)

    security.declarePublic('getDownloadUrl')
    def getDownloadUrl(self):
        """ """
        site = self.getSite()
        file_path = self._get_data_name()
        media_server = getattr(site, 'media_server', '').strip()
        if not (media_server and file_path):
            return self.absolute_url() + '/download'
        file_path = (media_server,) + tuple(file_path)
        return '/'.join(file_path)

    security.declarePublic('getEditDownloadUrl')
    def getEditDownloadUrl(self):
        """ """
        site = self.getSite()
        file_path = self._get_data_name()
        media_server = getattr(site, 'media_server', '').strip()
        if not (media_server and file_path):
            return self.absolute_url() + '/download?version=1'
        file_path = (media_server,) + tuple(file_path)
        return '/'.join(file_path)

InitializeClass(NyFile_extfile)

manage_addNyFile_html = PageTemplateFile('zpt/file_manage_add', globals())
manage_addNyFile_html.kind = config['meta_type']
manage_addNyFile_html.action = 'addNyFile'
config.update({
    'constructors': (manage_addNyFile_html, addNyFile),
    'folder_constructors': [
            # NyFolder.manage_addNyFile_html = manage_addNyFile_html
            ('manage_addNyFile_html', manage_addNyFile_html),
            ('file_add_html', file_add_html),
            ('addNyFile', addNyFile),
            ('import_file_item', importNyFile),
        ],
    'add_method': addNyFile,
    'validation': issubclass(NyFile_extfile, NyValidation),
    '_class': NyFile_extfile,
})

def get_config():
    return config
