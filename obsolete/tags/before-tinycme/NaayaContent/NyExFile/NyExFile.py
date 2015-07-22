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
    'downloadfilename': (0, '', ''),
    'content_type':     (0, '', ''),
    'lang':             (0, '', '')
}

manage_addNyExFile_html = PageTemplateFile('zpt/exfile_manage_add', globals())
manage_addNyExFile_html.kind = METATYPE_OBJECT
manage_addNyExFile_html.action = 'addNyExFile'

def exfile_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNyExFile'}, 'exfile_add')

def addNyExFile(self, id='', title='', description='', coverage='', keywords='', sortorder='',
    source='file', file='', url='', precondition='', content_type='', downloadfilename='',
    contributor=None, releasedate='', discussion='', lang=None, REQUEST=None, **kwargs):
    """
    Create a File type of object.
    """
    if source=='file': id = cookId(id, title, file)[0] #upload from a file
    id = self.utCleanupId(id)
    if id == '': id = PREFIX_OBJECT + self.utGenRandomId(6)
    if downloadfilename == '': downloadfilename = id
    try: sortorder = abs(int(sortorder))
    except: sortorder = DEFAULT_SORTORDER
    #check mandatory fiels
    l_referer = ''
    if REQUEST is not None: l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
    if not(l_referer == 'exfile_manage_add' or l_referer.find('exfile_manage_add') != -1) and REQUEST:
        r = self.getSite().check_pluggable_item_properties(METATYPE_OBJECT, id=id, title=title, \
            description=description, coverage=coverage, keywords=keywords, sortorder=sortorder, \
            releasedate=releasedate, discussion=discussion, file=file, url=url, \
            downloadfilename=downloadfilename)
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
        #create object
        ob = NyExFile(id, title, description, coverage, keywords, sortorder, '', precondition, content_type,
            downloadfilename, contributor, releasedate, lang)
        self.gl_add_languages(ob)
        ob.createDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        self._setObject(id, ob)
        #extra settings
        ob = self._getOb(id)
        ob.updatePropertiesFromGlossary(lang)
        ob.submitThis()
        ob.approveThis(approved, approved_by)
        ob.handleUpload(source, file, url, lang)
        ob.createversion(self.REQUEST.AUTHENTICATED_USER.getUserName(), lang)
        if discussion: ob.open_for_comments()
        self.recatalogNyObject(ob)
        self.notifyFolderMaintainer(self, ob)
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
                url=url, downloadfilename=downloadfilename, lang=lang)
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
                ob.set_content_type(object.attrs['content_type'].encode('utf-8'), lang)
                ob.set_precondition(object.attrs['precondition'].encode('utf-8'), lang)
                if lang != self.gl_get_selected_language():
                    #don't create version for selected language because
                    #has been already created in the addNyExFile method
                    ob.createversion(self.REQUEST.AUTHENTICATED_USER.getUserName(), lang)
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
        l_options = ()
        if not self.hasVersion():
            l_options += ({'label': 'Properties', 'action': 'manage_edit_html'},)
        l_options += exfile_item.manage_options
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyItem.manage_options
        return l_options

    security = ClassSecurityInfo()

    def __init__(self, id, title, description, coverage, keywords, sortorder, file, precondition,
        content_type, downloadfilename, contributor, releasedate, lang):
        """ """
        self.id = id
        exfile_item.__dict__['__init__'](self, id, title, description, coverage, keywords, sortorder, file,
            precondition, content_type, downloadfilename, releasedate, lang)
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
        for l in self.gl_get_languages():
            ra('<downloadfilename lang="%s"><![CDATA[%s]]></downloadfilename>' % (l, self.utToUtf8(self.getLocalProperty('downloadfilename', l))))
        for lang, fileitem in self.getFileItems().items():
            ra('<item lang="%s" file="%s" content_type="%s" precondition="%s" />' % \
            (lang,
                self.utBase64Encode(str(self.utNoneToEmpty(fileitem.data))),
                self.utXmlEncode(fileitem.content_type),
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
            data = str(fileitem.data)
            mimetype, encoding = guess_content_type(self.getId(), data)
            converter = ConverterRegistry.get(mimetype)
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
        if self.checkout: return self.version.content_type(lang)
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
                RESPONSE.setHeader('Content-Type', version_data[1])
                REQUEST.RESPONSE.setHeader('Content-Disposition', 'attachment;filename=' + utToUtf8(self.downloadfilename))
                return version_data[0]
            else:
                return 'Invalid version data!'
        else:
            return 'Invalid version id!'

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', coverage='',
        keywords='', sortorder='', approved='', precondition='', content_type='',
        downloadfilename='', releasedate='', discussion='', lang='', REQUEST=None, **kwargs):
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
        self.save_properties(title, description, coverage, keywords, sortorder, downloadfilename, releasedate, lang)
        self.set_content_type(content_type, lang)
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
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    security.declareProtected(view_management_screens, 'manageUpload')
    def manageUpload(self, source='file', file='', url='', version='', REQUEST=None):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if self.wl_isLocked():
            raise ResourceLockedError, "File is locked via WebDAV"
        lang = self.gl_get_selected_language()
        self.handleUpload(source, file, url, lang)
        if version:
            self.createversion(self.REQUEST.AUTHENTICATED_USER.getUserName(), lang)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    security.declareProtected(view_management_screens, 'manage_upload')
    def manage_upload(self):
        """ """
        raise EXCEPTION_NOTACCESIBLE, 'manage_upload'

    #site actions
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'commitVersion')
    def commitVersion(self, REQUEST=None):
        """ """
        if (not self.checkPermissionEditObject()) or (self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName()):
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if not self.hasVersion():
            raise EXCEPTION_NOVERSION, EXCEPTION_NOVERSION_MSG
        self._local_properties_metadata = deepcopy(self.version._local_properties_metadata)
        self._local_properties = deepcopy(self.version._local_properties)
        self.sortorder = self.version.sortorder
        self.downloadfilename = self.version.downloadfilename
        self.releasedate = self.version.releasedate
        self.setProperties(deepcopy(self.version.getProperties()))
        self.copyFileItems(self.version, self)
        self.checkout = 0
        self.checkout_user = None
        self.version = None
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
        self.version = exfile_item(self.id, self.title, self.description, self.coverage, self.keywords,
            self.sortorder, '', '', '', self.downloadfilename, self.releasedate, self.gl_get_selected_language())
        self.version._local_properties_metadata = deepcopy(self._local_properties_metadata)
        self.version._local_properties = deepcopy(self._local_properties)
        self.version.setProperties(deepcopy(self.getProperties()))
        self.copyFileItems(self, self.version)
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, title='', description='', coverage='', keywords='',
        sortorder='', content_type='', precondition='', downloadfilename='',
        releasedate='', discussion='', lang=None, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if not sortorder: sortorder = DEFAULT_SORTORDER
        if lang is None: lang = self.gl_get_selected_language()
        #check mandatory fiels
        r = self.getSite().check_pluggable_item_properties(METATYPE_OBJECT, title=title, \
            description=description, coverage=coverage, keywords=keywords, sortorder=sortorder, \
            releasedate=releasedate, discussion=discussion, downloadfilename=downloadfilename)
        if not len(r):
            sortorder = int(sortorder)
            if not self.hasVersion():
                #this object has not been checked out; save changes directly into the object
                releasedate = self.process_releasedate(releasedate, self.releasedate)
                self.save_properties(title, description, coverage, keywords, sortorder, downloadfilename, releasedate, lang)
                self.updatePropertiesFromGlossary(lang)
                self.set_content_type(content_type, lang)
                self.set_precondition(precondition, lang)
                self.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
            else:
                #this object has been checked out; save changes into the version object
                if self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName():
                    raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
                releasedate = self.process_releasedate(releasedate, self.version.releasedate)
                self.version.save_properties(title, description, coverage, keywords, sortorder, downloadfilename, releasedate, lang)
                self.version.set_content_type(content_type, lang)
                self.version.set_precondition(precondition, lang)
                self.version.updatePropertiesFromGlossary(lang)
                self.version.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
            if discussion: self.open_for_comments()
            else: self.close_for_comments()
            self._p_changed = 1
            self.recatalogNyObject(self)
            if REQUEST:
                self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))
        else:
            if REQUEST is not None:
                self.setSessionErrors(r)
                self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title, \
                    description=description, coverage=coverage, keywords=keywords, \
                    sortorder=sortorder, releasedate=releasedate, discussion=discussion, \
                    downloadfilename=downloadfilename, content_type=content_type)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))
            else:
                raise Exception, '%s' % ', '.join(r)

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveUpload')
    def saveUpload(self, source='file', file='', url='', version='', lang=None, REQUEST=None):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if self.wl_isLocked():
            raise ResourceLockedError, "File is locked via WebDAV"
        if lang is None: lang = self.gl_get_selected_language()
        if not self.hasVersion():
            #this object has not been checked out; save changes directly into the object
            self.handleUpload(source, file, url, lang)
            if version:
                self.createversion(self.REQUEST.AUTHENTICATED_USER.getUserName(), lang)
        else:
            #this object has been checked out; save changes into the version object
            if self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName():
                raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
            self.version.handleUpload(source, file, url, lang)
            if version:
                self.version.createversion(self.REQUEST.AUTHENTICATED_USER.getUserName(), lang)
        self.recatalogNyObject(self)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/exfile_manage_edit', globals())

    #site actions
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'exfile_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'exfile_edit')

    security.declareProtected(view, 'download')
    def download(self, REQUEST, RESPONSE):
        """ """
        RESPONSE.setHeader('Content-Type', self.content_type())
        RESPONSE.setHeader('Content-Length', self.size())
        RESPONSE.setHeader('Content-Disposition', 'attachment;filename=' + self.utToUtf8(self.downloadfilename))
        RESPONSE.setHeader('Pragma', 'public')
        RESPONSE.setHeader('Cache-Control', 'max-age=0')
        data = self.getFileItem(self.gl_get_selected_language()).data
        if type(data) is type(''):
            RESPONSE.setBase(None)
            return data
        while data is not None:
            RESPONSE.write(data.data)
            data=data.next
        return ''

    security.declareProtected(view, 'view')
    def view(self, REQUEST, RESPONSE):
        """ """
        RESPONSE.setHeader('Content-Type', self.content_type)
        RESPONSE.setHeader('Content-Length', self.size)
        RESPONSE.setHeader('Pragma', 'public')
        RESPONSE.setHeader('Cache-Control', 'max-age=0')
        RESPONSE.setHeader('Content-Disposition', 'inline; filename=%s' % self.utToUtf8(self.downloadfilename))
        data = self.getFileItem(self.gl_get_selected_language()).data
        if type(data) is type(''):
            RESPONSE.setBase(None)
            return data
        while data is not None:
            RESPONSE.write(data.data)
            data=data.next
        return ''

InitializeClass(NyExFile)