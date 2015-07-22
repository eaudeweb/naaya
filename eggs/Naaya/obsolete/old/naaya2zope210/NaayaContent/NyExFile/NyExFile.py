# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Eau de Web
# Dragos Chirila
# Alex Morega, Eau de Web

#Python imports
from copy import deepcopy

#Zope imports
from zope import event as zope_event
from OFS.event import ObjectWillBeRemovedEvent
from OFS.Image import File, cookId
from zope.contenttype import guess_content_type
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.Folder import Folder

#Product imports
from Products.NaayaBase.NyContentType import NyContentType, NY_CONTENT_BASE_SCHEMA
from Products.NaayaContent.constants import *
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyCheckControl import NyCheckControl
try:
    from Products.TextIndexNG2.Registry import ConverterRegistry
    txng_converters = 1
except ImportError:
    txng_converters = 0

# import METATYPE_OBJECT here so file_item can have access to it
METATYPE_OBJECT = 'Naaya Extended File'

from exfile_item import exfile_item

#module constants
LABEL_OBJECT = 'ExFile'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya Extended File objects'
OBJECT_FORMS = ['exfile_add', 'exfile_edit', 'exfile_index']
OBJECT_CONSTRUCTORS = ['manage_addNyExFile_html', 'exfile_add_html', 'addNyExFile', 'importNyExFile']
OBJECT_ADD_FORM = 'exfile_add_html'
DESCRIPTION_OBJECT = 'This is Naaya Extended File type.'
PREFIX_OBJECT = 'exfile'
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

manage_addNyExFile_html = PageTemplateFile('zpt/exfile_manage_add', globals())
manage_addNyExFile_html.kind = METATYPE_OBJECT
manage_addNyExFile_html.action = 'addNyExFile'

def exfile_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, METATYPE_OBJECT)
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNyExFile', 'form_helper': form_helper}, 'exfile_add')

def _create_NyExFile_object(parent, id, contributor):
    i = 0
    while parent._getOb(id, None):
        i += 1
        id = '%s-%u' % (id, i)
    ob = NyExFile(id, contributor)
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
    _contact_word = schema_raw_data.get('contact_word', '')
    _send_notifications = schema_raw_data.pop('_send_notifications', True)

    title = schema_raw_data.get('title', '')
    if _source=='file': id = cookId(id, title, _file)[0] #upload from a file

    id = self.utCleanupId(id)
    if not id: id = self.utGenObjectId(title)
    if not id: id = PREFIX_OBJECT + self.utGenRandomId(5)

    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_NyExFile_object(self, id, contributor)

    form_errors = ob.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

    #check Captcha/reCaptcha
    if not self.checkPermissionSkipCaptcha():
        captcha_validator = self.validateCaptcha(_contact_word, REQUEST)
        if captcha_validator:
            form_errors['captcha'] = captcha_validator

    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1]) # pick a random error
        else:
            import transaction; transaction.abort() # because we already called _crete_NyZzz_object
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            REQUEST.RESPONSE.redirect('%s/exfile_add_html' % self.absolute_url())
            return

    #process parameters
    if self.glCheckPermissionPublishObjects():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    ob.submitThis()
    ob.approveThis(approved, approved_by)
    ob.handleUpload(_source, _file, _url, _lang)

    if ob.discussion: ob.open_for_comments()
    self.recatalogNyObject(ob)
    if _send_notifications:
        self.notifyFolderMaintainer(self, ob)
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

class NyExFile(exfile_item, NyAttributes, NyItem, NyCheckControl, NyValidation, NyContentType):
    """ """

    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT
    icon = 'misc_/NaayaContent/NyExFile.gif'
    icon_marked = 'misc_/NaayaContent/NyExFile_marked.gif'

    def manage_options(self):
        """ """
        l_options = ()
        if not self.hasVersion():
            l_options += ({'label': 'Properties', 'action': 'manage_edit_html'}, Folder.manage_options[0])
        l_options += exfile_item.manage_options
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
        r = []
        ra = r.append
        l_site = self.getSite()
        if lang is None: lang = self.gl_get_selected_language()
        ra(self.syndicateThisHeader())
        ra(self.syndicateThisCommon(lang))
        ra('<dc:type>Text</dc:type>')
        ra('<dc:format>application</dc:format>')
        ra('<dc:source>%s</dc:source>' % self.utXmlEncode(l_site.getLocalProperty('publisher', lang)))
        ra('<dc:creator>%s</dc:creator>' % self.utXmlEncode(l_site.getLocalProperty('creator', lang)))
        ra('<dc:publisher>%s</dc:publisher>' % self.utXmlEncode(l_site.getLocalProperty('publisher', lang)))
        ra(self.syndicateThisFooter())
        return ''.join(r)

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
        if self.discussion: self.open_for_comments()
        else: self.close_for_comments()
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_main?save=ok')

    #site actions
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'commitVersion')
    def commitVersion(self, REQUEST=None):
        """ """
        if (not self.checkPermissionEditObject()) or (self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName()):
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

        if self.discussion: self.open_for_comments()
        else: self.close_for_comments()
        self._p_changed = 1
        self.recatalogNyObject(self)
        #log date
        contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
        auth_tool = self.getAuthenticationTool()
        auth_tool.changeLastPost(contributor)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))

    security.declarePrivate('switch_content_to_language')
    def switch_content_to_language(self, old_lang, new_lang):
        super(NyExFile, self).switch_content_to_language(old_lang, new_lang)
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
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
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
        return filename[-1]

    security.declareProtected(view, 'download')
    def download(self, REQUEST, RESPONSE):
        """ """
        lang = REQUEST.get('lang', self.gl_get_selected_language())
        version = REQUEST.get('version', False)
        RESPONSE.setHeader('Content-Type', self.content_type(lang))
        RESPONSE.setHeader('Content-Length', self.size())
        filename = self.downloadfilename(lang, version=False)
        filename = self.utCleanupId(filename)
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

InitializeClass(NyExFile)
