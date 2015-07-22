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

#Python imports
from copy import deepcopy

#Zope imports
from OFS.Image import File, cookId
from OFS.content_types import guess_content_type
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from Products.NaayaContent.constants import *
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyCheckControl import NyCheckControl
from exfile_item import exfile_item
try:
    from Products.TextIndexNG2.Registry import ConverterRegistry
    txng_converters = 1
except ImportError:
    txng_converters = 0

#module constants
METATYPE_OBJECT = 'Naaya Extended File'
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

manage_addNyExFile_html = PageTemplateFile('zpt/exfile_manage_add', globals())
manage_addNyExFile_html.kind = METATYPE_OBJECT
manage_addNyExFile_html.action = 'addNyExFile'

def exfile_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNyExFile'}, 'exfile_add')

def addNyExFile(self, id='', title='', description='', coverage='', keywords='', sortorder='',
    source='file', file='', url='', precondition='', contributor=None,
    releasedate='', discussion='', lang=None, REQUEST=None, **kwargs):
    """
    Create a File type of object.
    """
    if source=='file': id = cookId(id, title, file)[0] #upload from a file
    id = self.utCleanupId(id)
    if not id: id = self.utGenObjectId(title)
    if not id: id = PREFIX_OBJECT + self.utGenRandomId(5)
    try: sortorder = abs(int(sortorder))
    except: sortorder = DEFAULT_SORTORDER
    #check mandatory fiels
    l_referer = ''
    if REQUEST is not None: l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
    if not(l_referer == 'exfile_manage_add' or l_referer.find('exfile_manage_add') != -1) and REQUEST:
        r = self.getSite().check_pluggable_item_properties(METATYPE_OBJECT, id=id, title=title, \
            description=description, coverage=coverage, keywords=keywords, sortorder=sortorder, \
            releasedate=releasedate, discussion=discussion, file=file, url=url)
    else:
        r = []
    if not len(r):
        #process parameters
        if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
        if self.glCheckPermissionPublishObjects():
            approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
        else:
            approved, approved_by = 0, None
        releasedate = self.process_releasedate(releasedate)
        if lang is None: lang = self.gl_get_selected_language()
        #check if the id is invalid (it is already in use)
        i = 0
        while self._getOb(id, None):
            i += 1
            id = '%s-%u' % (id, i)
        #create object
        ob = NyExFile(id, title, description, coverage, keywords, sortorder, '',
                      precondition, contributor, releasedate, lang)
        self.gl_add_languages(ob)
        ob.createDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        self._setObject(id, ob)
        #extra settings
        ob = self._getOb(id)
        ob.updatePropertiesFromGlossary(lang)
        ob.submitThis()
        ob.approveThis(approved, approved_by)
        ob.handleUpload(source, file, url, lang)
        if discussion: ob.open_for_comments()
        self.recatalogNyObject(ob)
        self.notifyFolderMaintainer(self, ob)
        #log post date
        auth_tool = self.getAuthenticationTool()
        auth_tool.changeLastPost(contributor)
        #redirect if case
        if REQUEST is not None:
            if l_referer == 'exfile_manage_add' or l_referer.find('exfile_manage_add') != -1:
                return self.manage_main(self, REQUEST, update_menu=1)
            elif l_referer == 'exfile_add_html':
                self.setSession('referer', self.absolute_url())
                REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
    else:
        if REQUEST is not None:
            self.setSessionErrors(r)
            self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title, \
                description=description, coverage=coverage, keywords=keywords, \
                sortorder=sortorder, releasedate=releasedate, discussion=discussion, \
                url=url, lang=lang)
            REQUEST.RESPONSE.redirect('%s/file_add_html' % self.absolute_url())
        else:
            raise Exception, '%s' % ', '.join(r)

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
            addNyExFile(self, id=id,
                sortorder=attrs['sortorder'].encode('utf-8'),
                contributor=self.utEmptyToNone(attrs['contributor'].encode('utf-8')),
                discussion=abs(int(attrs['discussion'].encode('utf-8'))))
            ob = self._getOb(id)
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

class NyExFile(NyAttributes, exfile_item, NyItem, NyCheckControl, NyValidation):
    """ """

    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT
    icon = 'misc_/NaayaContent/NyExFile.gif'
    icon_marked = 'misc_/NaayaContent/NyExFile_marked.gif'

    def manage_options(self):
        """ """
        return exfile_item.manage_options

    security = ClassSecurityInfo()

    def __init__(self, id, title, description, coverage, keywords, sortorder,
                 file, precondition, contributor, releasedate, lang):
        """ """
        self.id = id
        exfile_item.__dict__['__init__'](self, id, title, description, coverage, keywords, sortorder, file,
            precondition, releasedate, lang)
        NyValidation.__dict__['__init__'](self)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor

    #override handlers
    def manage_afterAdd(self, item, container):
        """
        This method is called, whenever _setObject in ObjectManager gets called.
        """
        NyExFile.inheritedAttribute('manage_afterAdd')(self, item, container)
        self.catalogNyObject(self)

    def manage_beforeDelete(self, item, container):
        """
        This method is called, when the object is deleted.
        """
        NyExFile.inheritedAttribute('manage_beforeDelete')(self, item, container)
        self.uncatalogNyObject(self)

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

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', coverage='',
        keywords='', sortorder='', approved='', precondition='',
        releasedate='', discussion='', lang='', REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if self.wl_isLocked():
            raise ResourceLockedError, "File is locked via WebDAV"
        try: sortorder = abs(int(sortorder))
        except: sortorder = DEFAULT_SORTORDER
        if approved: approved = 1
        else: approved = 0
        releasedate = self.process_releasedate(releasedate, self.releasedate)
        if not lang: lang = self.gl_get_selected_language()
        self.save_properties(title, description, coverage, keywords, sortorder, releasedate, lang)
        self.set_precondition(precondition, lang)
        self.updatePropertiesFromGlossary(lang)
        self.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        if approved != self.approved:
            if approved == 0: approved_by = None
            else: approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
            self.approveThis(approved, approved_by)
        self._p_changed = 1
        if discussion: self.open_for_comments()
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
        self._local_properties_metadata = deepcopy(version._local_properties_metadata)
        self._local_properties = deepcopy(version._local_properties)
        self.sortorder = version.sortorder
        self.releasedate = version.releasedate
        self.setProperties(deepcopy(version.getProperties()))
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
        version = exfile_item(self.id, self.title, self.description, self.coverage, self.keywords,
                              self.sortorder, '', '',
                              self.releasedate, self.gl_get_selected_language())
        self._setObject('version', version)
        version = self._getOb('version')
        version._local_properties_metadata = deepcopy(self._local_properties_metadata)
        version._local_properties = deepcopy(self._local_properties)
        version.setProperties(deepcopy(self.getProperties()))
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
    def saveProperties(self, title='', description='', coverage='', keywords='',
        sortorder='', precondition='',
        releasedate='', discussion='', lang=None, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if not sortorder: sortorder = DEFAULT_SORTORDER
        if lang is None: lang = self.gl_get_selected_language()
        #check mandatory fiels
        r = self.getSite().check_pluggable_item_properties(METATYPE_OBJECT, title=title,
            description=description, coverage=coverage, keywords=keywords, sortorder=sortorder,
            releasedate=releasedate, discussion=discussion)
        # If errors return
        if len(r):
            if REQUEST is None:
                raise Exception, '%s' % ', '.join(r)
            self.setSessionErrors(r)
            self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title,
                description=description, coverage=coverage, keywords=keywords,
                sortorder=sortorder, releasedate=releasedate, discussion=discussion)
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))
            return
        #
        # Save properties
        #
        # Upload file
        file_form = dict([(key, value) for key, value in kwargs.items()])
        if REQUEST:
            file_form.update(REQUEST.form)
        source = file_form.get('source', None)
        if source:
            attached_file = file_form.get('file', '')
            attached_url = file_form.get('url', '')
            version = file_form.get('version', False)
            self.saveUpload(source=source, file=attached_file, url=attached_url, version=version, lang=lang)
        # Update properties
        sortorder = int(sortorder)
        if not self.hasVersion():
            #this object has not been checked out; save changes directly into the object
            releasedate = self.process_releasedate(releasedate, self.releasedate)
            self.save_properties(title, description, coverage, keywords, sortorder, releasedate, lang)
            self.updatePropertiesFromGlossary(lang)
            self.set_precondition(precondition, lang)
            self.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        else:
            #this object has been checked out; save changes into the version object
            if self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName():
                raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
            version = self._getOb('version')
            releasedate = self.process_releasedate(releasedate, version.releasedate)
            version.save_properties(title, description, coverage, keywords, sortorder, releasedate, lang)
            version.set_precondition(precondition, lang)
            version.updatePropertiesFromGlossary(lang)
            version.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        if discussion: self.open_for_comments()
        else: self.close_for_comments()
        self._p_changed = 1
        self.recatalogNyObject(self)
        #log date
        contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
        auth_tool = self.getAuthenticationTool()
        auth_tool.changeLastPost(contributor)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))

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
