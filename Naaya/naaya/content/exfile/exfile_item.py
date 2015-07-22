import os
import sys
import mimetypes

from zope import event as zope_event
from OFS.event import ObjectWillBeRemovedEvent
from OFS.Image import cookId
from zope.contenttype import guess_content_type
from Globals import InitializeClass
from App.ImageFile import ImageFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.Folder import Folder
from zope.event import notify
from naaya.content.base.events import NyContentObjectAddEvent
from naaya.content.base.events import NyContentObjectEditEvent
from zope.interface import implements
from interfaces import INyExFile

from Products.NaayaBase.NyContentType import NyContentType, NY_CONTENT_BASE_SCHEMA
from naaya.content.base.constants import *
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaBase.NyContentType import NyContentData
from Products.NaayaBase.NyFolderishVersioning import NyFolderishVersioning
from Products.NaayaBase.NyFSFile import NyFSFile
from Products.NaayaBase.NyBase import rss_item_for_object
from Products.NaayaCore.managers.utils import uniqueId, slugify, get_nsmap
from naaya.core import submitter
from naaya.core.zope2util import abort_transaction_keep_session

from permissions import PERMISSION_ADD_EXTENDED_FILE

from lxml import etree
from lxml.builder import ElementMaker

try:
    from Products.TextIndexNG2.Registry import ConverterRegistry
    txng_converters = 1
except ImportError:
    txng_converters = 0

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
    'file':             (0, '', ''),
    'url':              (0, '', ''),
    'lang':             (0, '', '')
}
DEFAULT_SCHEMA = {
    # add NyExFile-specific properties here
}
DEFAULT_SCHEMA.update(NY_CONTENT_BASE_SCHEMA)

# this dictionary is updated at the end of the module
config = {
        'product': 'NaayaContent',
        'module': 'exfile_item',
        'package_path': os.path.abspath(os.path.dirname(__file__)),
        'meta_type': 'Naaya Extended File',
        'label': 'ExFile',
        'permission': PERMISSION_ADD_EXTENDED_FILE,
        'forms': ['exfile_add', 'exfile_edit', 'exfile_index'],
        'add_form': 'exfile_add_html',
        'description': 'This is Naaya ExFile type.',
        'properties': PROPERTIES_OBJECT,
        'default_schema': DEFAULT_SCHEMA,
        'schema_name': 'NyExFile',
        '_module': sys.modules[__name__],
        'additional_style': None,
        'icon': os.path.join(os.path.dirname(__file__), 'www', 'exfile.gif'),
        '_misc': {
                'NyExFile.gif': ImageFile('www/exfile.gif', globals()),
                'NyExFile_marked.gif': ImageFile('www/exfile_marked.gif', globals()),
            },
    }

def exfile_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, config['meta_type'])
    return self.getFormsTool().getContent({
        'here': self,
        'kind': config['meta_type'],
        'action': 'addNyExFile',
        'form_helper': form_helper,
        'submitter_info_html': submitter.info_html(self, REQUEST),
    }, 'exfile_add')

def _create_NyExFile_object(parent, id, contributor):
    id = uniqueId(slugify(id or 'exfile', removelist=[]),
                  lambda x: parent._getOb(x, None) is not None)
    ob = NyExFile_extfile(id, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def addNyExFile(self, id='', REQUEST=None, contributor=None, **kwargs):
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
    if _source=='file': id = cookId(id, title, _file)[0] #upload from a file
    id = uniqueId(slugify(id or title or 'exfile', removelist=[]),
                  lambda x: self._getOb(x, None) is not None)

    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_NyExFile_object(self, id, contributor)

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
            REQUEST.RESPONSE.redirect('%s/exfile_add_html' % self.absolute_url())
            return

    #process parameters
    if self.checkPermissionSkipApproval():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    ob.submitThis()
    ob.approveThis(approved, approved_by)
    ob.handleUpload(_source, _file, _url, _lang)

    self.recatalogNyObject(ob)
    notify(NyContentObjectAddEvent(ob, contributor, schema_raw_data))
    #log post date
    auth_tool = self.getAuthenticationTool()
    auth_tool.changeLastPost(contributor)
    #redirect if case
    if REQUEST is not None:
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'exfile_manage_add' or l_referer.find('exfile_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'exfile_add_html':
            self.setSession('referer', self.absolute_url())
            return ob.object_submitted_message(REQUEST)
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())

    return ob.getId()

def importNyExFile(self, param, id, attrs, content, properties, discussion, objects):
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

            ob = _create_NyExFile_object(self, id,
                contributor=self.utEmptyToNone(attrs['contributor'].encode('utf-8'))
            )
            ob.sortorder = attrs['sortorder'].encode('utf-8')
            ob.discussion = abs(int(attrs['discussion'].encode('utf-8')))
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
            #import file items
            for object in objects:
                lang = object.attrs['lang'].encode('utf-8')
                ob.handleUpload('file',
                    self.utBase64Decode(object.attrs['file'].encode('utf-8')), '',
                    lang)
                ob.set_precondition(object.attrs['precondition'].encode('utf-8'), lang)
            ob.import_comments(discussion)
            self.recatalogNyObject(ob)

class file_item(NyFSFile, NyFolderishVersioning):
    """ """

    def __init__(self, id, title, file, precondition, content_type):
        """
        Constructor.
        """
        NyFSFile.__dict__['__init__'](self, id, title, file, content_type, precondition)
        #"dirty" trick to get rid of the File's title property
        try: del self.id
        except: pass
        NyFolderishVersioning.__dict__['__init__'](self)

    security = ClassSecurityInfo()
    #
    #override handlers
    #
    def getContentType(self):
        return self.get_data(as_string=False).getContentType()

    def _get_upload_file(self, source, file, url, parent):
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
                l_data, l_ctype = parent.grabFromUrl(url)
                if l_data is not None:
                    return l_data, l_ctype, None, ''
        return '', '', None, ''

    def handleUpload(self, source, file, url, parent):
        """
        Upload a file from disk or from a given URL.
        """
        data, ctype, size, filename = self._get_upload_file(source, file, url, parent)
        self.update_data(data, ctype, size, filename)

class exfile_item(NyContentData, Folder):
    """ """
    implements(INyExFile)

    meta_type = config['meta_type']

    __files = {}

    def __init__(self, id):
        NyContentData.__init__(self)
        Folder.__init__(self, id)

    # Backward compatible
    def _get_old_files(self):
        return self.__files

    def getFileItems(self):
        return self.objectItems('File')

    def copyFileItems(self, source, target):
        """ """
        if target.objectIds('File'):
            target.manage_delObjects(target.objectIds('File'))
        for lang, item in source.getFileItems():
            doc = file_item(lang, item.title, '', item.precondition, item.getContentType())
            target._setObject(lang, doc)
            doc = target._getOb(lang)
            doc.update_data(item.get_data(as_string=False))
            #doc.copyVersions(item)

    def getFileItem(self, lang=None):
        """ """
        if lang is None:
            lang = self.gl_get_selected_language()
        if not lang in self.objectIds():
            doc = file_item(lang, lang, None, '', '')
            self._setObject(lang, doc)
        return self._getOb(lang)

    def getFileItemData(self, lang=None, as_string=False):
        fileitem = self.getFileItem(lang)
        return fileitem.get_data(as_string=as_string)

    def size(self, lang=None):
        """ """
        if lang is None: lang = self.gl_get_selected_language()
        try: return self.getFileItem(lang).size
        except: return 0

    def get_size(self, lang=None):
        """ """
        if lang is None: lang = self.gl_get_selected_language()
        try: return self.getFileItem(lang).size
        except: return 0

    def content_type(self, lang=None):
        """ """
        if lang is None:
            lang = self.gl_get_selected_language()
        return self.getFileItem(lang).getContentType()

    def precondition(self, lang=None):
        """ """
        if lang is None: lang = self.gl_get_selected_language()
        try: return self.getFileItem(lang).precondition
        except: return ''

    def set_precondition(self, precondition, lang):
        """ """
        self.getFileItem(lang).precondition = precondition

    def handleUpload(self, source, file, url, lang=None):
        """
        Upload a file from disk or from a given URL.
        """
        if lang is None: lang = self.gl_get_selected_language()
        self.getFileItem(lang).handleUpload(source, file, url, self)

    def createversion(self, newdata, lang=None, **kwargs):
        """
        Creates a version.
        """
        if lang is None:
            lang = self.gl_get_selected_language()
        fileitem = self.getFileItem(lang)
        vdata = fileitem.get_data(as_string=False)
        if vdata.is_broken():
            return
        fileitem.createVersion(vdata, newdata, **kwargs)

    def getVersions(self, lang=None):
        """
        Returns the dictionary of older versions. This means that current
        version is removed because it cointains the current content of the
        object.
        """
        if lang is None:
            lang = self.gl_get_selected_language()
        fileitem = self.getFileItem(lang)
        return fileitem.getVersions()

class NyExFile_extfile(exfile_item, NyAttributes, NyItem, NyCheckControl, NyValidation, NyContentType):
    """ """

    meta_type = config['meta_type']
    meta_label = config['label']
    icon = 'misc_/NaayaContent/NyExFile.gif'
    icon_marked = 'misc_/NaayaContent/NyExFile_marked.gif'

    def manage_options(self):
        """ """
        l_options = ()
        if not self.hasVersion():
            l_options += ({'label': 'Properties', 'action': 'manage_edit_html'}, Folder.manage_options[0])
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyItem.manage_options

        return l_options

    security = ClassSecurityInfo()

    def __init__(self, id, contributor):
        """ """
        self.id = id
        exfile_item.__init__(self, id)
        NyValidation.__dict__['__init__'](self)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        return 'validation_status="%s" validation_date="%s" validation_by="%s" validation_comment="%s"' % \
            (self.utXmlEncode(self.validation_status),
                self.utXmlEncode(self.validation_date),
                self.utXmlEncode(self.validation_by),
                self.utXmlEncode(self.validation_comment))

    security.declarePrivate('export_this_body_custom')
    def export_this_body_custom(self):
        r = []
        ra = r.append
        for lang, fileitem in self.getFileItems():
            ra('<item lang="%s" file="%s" precondition="%s" />' % \
            (lang,
                self.utBase64Encode(str(self.utNoneToEmpty(fileitem.get_data()))),
                self.utXmlEncode(fileitem.precondition)))
        return ''.join(r)

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

    def _fileitemkeywords(self, lang):
        """ """
        res = ''
        if txng_converters:
            fileitem = self.getFileItem(lang)
            data = str(fileitem.get_data())
            mimetype, encoding = guess_content_type(self.getId(), data)
            try:
                converter = ConverterRegistry.get(mimetype)
            except:
                converter = False
            if converter:
                try:
                    res, encoding = converter.convert2(data, encoding, mimetype)
                except:
                    try:
                        res = converter.convert(data)
                    except:
                        pass
        return res

    security.declarePrivate('objectkeywords')
    def objectkeywords(self, lang=None):
        return u' '.join([self._objectkeywords(lang), self.toUnicode(self._fileitemkeywords(lang))])

    def getVersionContentType(self, lang):
        """ """
        if self.checkout:
            version = self._getOb('version')
            return version.content_type(lang)
        else: return self.content_type(lang)

    def toUnicode(self, p_string):
        #convert to unicode
        if not isinstance(p_string, unicode): return unicode(p_string, 'utf-8', errors='ignore')
        else: return p_string

    security.declarePublic('showVersionData')
    def showVersionData(self, vid=None, lang=None, REQUEST=None, RESPONSE=None):
        """ """
        if vid:
            if lang is None: lang = self.gl_get_selected_language()
            version_data = self.getFileItem(lang).getVersion(vid)
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
    def getVersionFilename(self, vid='', lang=None):
        """ Returns the filename for the given version id """
        if lang is None:
            lang = self.gl_get_selected_language()
        version = self.getFileItem(lang).getVersion(vid)
        filename = getattr(version, 'filename', [])
        if not filename:
            return ''
        return filename[-1]

    #XXX Should remove NyCheckControl inheritance and refactor code to not use
    # NyCheckControl methods.
    def isVersionable(self):
        """ File objects are not versionable
        """
        return False

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

        self.set_precondition(_precondition, _lang)

        if _approved != self.approved:
            if _approved == 0: _approved_by = None
            else: _approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
            self.approveThis(_approved, _approved_by)

        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_main?save=ok')

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
        version = self._getOb('version')
        self.copy_naaya_properties_from(version)
        self.copyFileItems(version, self)
        self.checkout = 0
        self.checkout_user = None
        if 'version' in self.objectIds():
            self.manage_delObjects(['version'])
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
        version = exfile_item(self.id)
        self._setObject('version', version)
        version = self._getOb('version')
        version.copy_naaya_properties_from(self)
        self.copyFileItems(self, version)
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'discardVersion')
    def discardVersion(self, REQUEST=None):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if not self.hasVersion():
            raise EXCEPTION_NOVERSION, EXCEPTION_NOVERSION_MSG
        self.checkout = 0
        self.checkout_user = None
        self.manage_delObjects(['version'])
        self.recatalogNyObject(self)
        if REQUEST:
            REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG

        if self.hasVersion():
            obj = self._getOb('version')
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

        self.set_precondition(_precondition, _lang)

        self._p_changed = 1
        self.recatalogNyObject(self)
        #log date
        contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
        auth_tool = self.getAuthenticationTool()
        auth_tool.changeLastPost(contributor)
        if REQUEST:
            notify(NyContentObjectEditEvent(self, contributor))
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))

    security.declarePrivate('switch_content_to_language')
    def switch_content_to_language(self, old_lang, new_lang):
        super(NyExFile_extfile, self).switch_content_to_language(old_lang, new_lang)
        # TODO: copy image content from old language to new language

        # old code (taken from NyFolder.switchToLanguage) was broken so it's commented out
        #files = self.getFileItems()
        #files[new_lang] = self.getFileItem(old_lang)
        #files = dict([(key, value) for key, value in files.items() if key != old_lang])
        #self.setFileItems(files)

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
            context = self
        else:
            version_ob = self._getOb('version')
            #this object has been checked out; save changes into the version object
            if self.checkout_user != username:
                raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
            context = version_ob

        # Create version
        if version:
            newdata = self.getFileItem(lang)._get_upload_file(source, file, url, self)[0]
            context.createversion(newdata, lang, username=username,
                                  modification_time=self.utGetTodayDate())
        else:
            fileitem = self.getFileItem(lang)
            ext_file = fileitem.get_data(as_string=False)
            zope_event.notify(ObjectWillBeRemovedEvent(
                ext_file, fileitem, ext_file.getId()))

        context.handleUpload(source, file, url, lang)
        self.recatalogNyObject(self)
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))

    def checkExFileLang(self, lang):
        """ Checks if there is a file uploaded for the given language. """

        return self.getFileItem(lang).size > 0

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_advanced_html')
    manage_advanced_html = PageTemplateFile('zpt/exfile_manage_advanced', globals())

    security.declareProtected(view_management_screens, 'manageAdvancedProperties')
    def manageAdvancedProperties(self, REQUEST=None, **kwargs):
        """ """
        if REQUEST:
            kwargs.update(REQUEST.form)

        langs = kwargs.get('langs', [])
        for lang in langs:
            filename = kwargs.get('filename_%s' % lang, '')
            filename = filename.split('/')
            filename = [x.strip() for x in filename if x]
            fileitem = self.getFileItem(lang)
            if not fileitem:
                return self.manage_advanced_html(REQUEST=REQUEST, update_menu=1)
            fileitem._update_properties(filename=filename)
        return self.manage_advanced_html(REQUEST=REQUEST, update_menu=1)

    #site actions
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'exfile_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'exfile_edit')

    def downloadfilename(self, lang=None, version=False):
        """ Return download file name
        """
        if lang is None:
            lang = self.gl_get_selected_language()
        context = self
        if version and self.hasVersion():
            context = self._getOb('version')
        lang_doc = self.getFileItem(lang)
        filename = lang_doc._get_data_name()
        if not filename:
            return context.title_or_id()
        if isinstance(filename, basestring):
            return filename
        return filename[-1]

    security.declareProtected(view, 'download')
    def download(self, REQUEST, RESPONSE):
        """ """
        lang = REQUEST.get('lang', self.gl_get_selected_language())
        version = REQUEST.get('version', False)
        RESPONSE.setHeader('Content-Type', self.content_type(lang))
        RESPONSE.setHeader('Content-Length', self.size())
        filename = self.downloadfilename(lang, version=False)
        filename = self.utSlugify(filename, removelist=[])
        RESPONSE.setHeader('Content-Disposition', 'attachment;filename=' + filename)
        RESPONSE.setHeader('Pragma', 'public')
        RESPONSE.setHeader('Cache-Control', 'max-age=0')
        if version and self.hasVersion():
            fileitem = self._getOb('version').getFileItem(lang)
        else:
            fileitem = self.getFileItem(lang)
        return fileitem.get_data()

    security.declareProtected(view, 'view')
    def view(self, REQUEST, RESPONSE):
        """ """
        lang = self.gl_get_selected_language()
        RESPONSE.setHeader('Content-Type', self.content_type(lang))
        RESPONSE.setHeader('Content-Length', self.size)
        RESPONSE.setHeader('Pragma', 'public')
        RESPONSE.setHeader('Cache-Control', 'max-age=0')
        RESPONSE.setHeader('Content-Disposition', 'inline; filename=%s' % self.downloadfilename(lang, version=False))
        fileitem = self.getFileItem(lang)
        return fileitem.get_data()

    security.declarePublic('getDownloadUrl')
    def getDownloadUrl(self):
        """ """
        site = self.getSite()
        fileitem = self.getFileItem(self.gl_get_selected_language())
        if not fileitem:
            return self.absolute_url() + '/download'

        file_path = fileitem._get_data_name()
        media_server = getattr(site, 'media_server', '').strip()
        if not (media_server and file_path):
            return self.absolute_url() + '/download'
        file_path = (media_server, ) + tuple(file_path)
        return '/'.join(file_path)

    security.declarePublic('getEditDownloadUrl')
    def getEditDownloadUrl(self, lang=None):
        """ """
        site = self.getSite()
        lang = lang or self.gl_get_selected_language()
        fileitem = self.getFileItem(lang)
        if not fileitem:
            return self.absolute_url() + '/download?lang=%s&amp;version=1' % lang

        file_path = fileitem._get_data_name()
        media_server = getattr(site, 'media_server', '').strip()
        if not (media_server and file_path):
            return self.absolute_url() + '/download?lang=%s&amp;version=1' % lang
        file_path = (media_server, ) + tuple(file_path)
        return '/'.join(file_path)

InitializeClass(NyExFile_extfile)

manage_addNyExFile_html = PageTemplateFile('zpt/exfile_manage_add', globals())
manage_addNyExFile_html.kind = config['meta_type']
manage_addNyExFile_html.action = 'addNyExFile'
config.update({
    'constructors': (manage_addNyExFile_html, addNyExFile),
    'folder_constructors': [
            # NyFolder.manage_addNyExFile_html = manage_addNyExFile_html
            ('manage_addNyExFile_html', manage_addNyExFile_html),
            ('exfile_add_html', exfile_add_html),
            ('addNyExFile', addNyExFile),
            ('import_exfile_item', importNyExFile),
        ],
    'add_method': addNyExFile,
    'validation': issubclass(NyExFile_extfile, NyValidation),
    '_class': NyExFile_extfile,
})

def get_config():
    return config
