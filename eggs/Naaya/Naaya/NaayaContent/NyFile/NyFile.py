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
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

#Python imports
from copy import deepcopy

#Zope imports
from OFS.Image import File, cookId
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
from Products.NaayaBase.NyVersioning import NyVersioning
from file_item import file_item

#module constants
METATYPE_OBJECT = 'Naaya File'
LABEL_OBJECT = 'File'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya File objects'
OBJECT_FORMS = ['file_add', 'file_edit', 'file_index']
OBJECT_CONSTRUCTORS = ['manage_addNyFile_html', 'file_add_html', 'addNyFile']
OBJECT_ADD_FORM = 'file_add_html'
TOBE_VALIDATED = 1
DESCRIPTION_OBJECT = 'This is Naaya File type.'
PREFIX_OBJECT = 'file'

manage_addNyFile_html = PageTemplateFile('zpt/file_manage_add', globals())
manage_addNyFile_html.kind = METATYPE_OBJECT
manage_addNyFile_html.action = 'addNyFile'

def file_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNyFile'}, 'file_add')

def addNyFile(self, id='', title='', description='', coverage='', keywords='', sortorder='',
    source='file', file='', url='', precondition='', content_type='', downloadfilename='',
    contributor=None, releasedate='', lang=None, REQUEST=None, **kwargs):
    """ """
    if source=='file': id, title = cookId(id, title, file) #upload from a file
    elif source=='url': l_data, l_ctype = self.grabFromUrl(url) #upload from an url
    id = self.utCleanupId(id)
    if id == '': id = PREFIX_OBJECT + self.utGenRandomId(6)
    if downloadfilename == '': downloadfilename = id
    try: sortorder = abs(int(sortorder))
    except: sortorder = DEFAULT_SORTORDER
    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
    if self.checkPermissionPublishObjects():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    releasedate = self.utConvertStringToDateTimeObj(releasedate)
    if releasedate is None:
        releasedate = self.utGetTodayDate()
    if lang is None: lang = self.gl_get_selected_language()
    ob = NyFile(id, title, description, coverage, keywords, sortorder, '', precondition, content_type,
        downloadfilename, contributor, approved, approved_by, releasedate, lang)
    self.gl_add_languages(ob)
    ob.createDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
    self._setObject(id, ob)
    ob = self._getOb(id)
    ob.handleUpload(source, file, url)
    ob.createVersion()
    if REQUEST is not None:
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'file_manage_add' or l_referer.find('file_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'file_add_html':
            self.setSession('referer', self.absolute_url())
            REQUEST.RESPONSE.redirect('%s/note_html' % self.getSitePath())

class NyFile(NyAttributes, NyItem, file_item, NyVersioning, NyCheckControl, NyValidation):
    """ """

    meta_type = METATYPE_OBJECT
    icon = 'misc_/NaayaContent/NyFile.gif'
    icon_marked = 'misc_/NaayaContent/NyFile_marked.gif'

    def manage_options(self):
        """ """
        l_options = ()
        if not self.hasVersion():
            l_options += ({'label' : 'Properties', 'action' : 'manage_edit_html'},)
        l_options += file_item.manage_options
        l_options += ({'label' : 'View', 'action' : 'index_html'},) + NyItem.manage_options
        l_options += NyVersioning.manage_options
        return l_options

    security = ClassSecurityInfo()

    def __init__(self, id, title, description, coverage, keywords, sortorder, file, precondition,
        content_type, downloadfilename, contributor, approved, approved_by, releasedate, lang):
        """ """
        file_item.__dict__['__init__'](self, id, title, description, coverage, keywords, sortorder, file,
            precondition, content_type, downloadfilename, releasedate, lang)
        self.id = id
        self.contributor = contributor
        self.approved = approved
        self.approved_by = approved_by
        NyVersioning.__dict__['__init__'](self)
        NyCheckControl.__dict__['__init__'](self)
        NyValidation.__dict__['__init__'](self)

    security.declarePrivate('exportThisCustomProperties')
    def exportThisCustomProperties(self):
        return 'downloadfilename="%s" file="%s" content_type="%s" precondition="%s"' % \
                (self.utXmlEncode(self.downloadfilename),
                 self.utBase64Encode(str(self.utNoneToEmpty(self.data))),
                 self.utXmlEncode(self.content_type),
                 self.utXmlEncode(self.precondition))

    security.declarePrivate('syndicateThis')
    def syndicateThis(self):
        l_rdf = []
        l_rdf.append(self.syndicateThisHeader())
        l_rdf.append(self.syndicateThisCommon())
        l_rdf.append('<dc:type>Text</dc:type>')
        l_rdf.append('<dc:format>application</dc:format>')
        l_rdf.append('<dc:source>%s</dc:source>' % self.utXmlEncode(self.publisher))
        l_rdf.append(self.syndicateThisFooter())
        return ''.join(l_rdf)

    security.declarePrivate('objectDataForVersion')
    def objectDataForVersion(self):
        return (str(self.data), self.content_type)

    security.declarePrivate('objectDataForVersionCompare')
    def objectDataForVersionCompare(self):
        return str(self.data)

    security.declarePrivate('objectVersionDataForVersionCompare')
    def objectVersionDataForVersionCompare(self, p_version_data):
        return p_version_data[0]

    security.declarePrivate('versionForObjectData')
    def versionForObjectData(self, p_version_data=None):
        self.update_data(p_version_data[0], p_version_data[1], len(p_version_data[0]))
        self._p_changed = 1

    security.declarePublic('showVersionData')
    def showVersionData(self, vid=None, REQUEST=None, RESPONSE=None):
        """ """
        if vid:
            version_data = self.getVersion(vid)
            if version_data is not None:
                #show data for file: set content type and return data
                RESPONSE.setHeader('Content-Type', version_data[1])
                REQUEST.RESPONSE.setHeader('Content-Disposition', 'attachment;filename=' + self.downloadfilename)
                return version_data[0]
            else:
                return 'Invalid version data!'
        else:
            return 'Invalid version id!'

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', language='', coverage='', keywords='',
                         sortorder='', approved='', precondition='', content_type='',
                         downloadfilename='', releasedate='', REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if self.wl_isLocked():
            raise ResourceLockedError, "File is locked via WebDAV"
        try: sortorder = abs(int(sortorder))
        except: sortorder = DEFAULT_SORTORDER
        if approved: approved = 1
        else: approved = 0
        releasedate = self.utConvertStringToDateTimeObj(releasedate)
        if releasedate is None: releasedate = self.utGetTodayDate()
        lang = self.gl_get_selected_language()
        self.save_properties(title, description, coverage, keywords, sortorder, downloadfilename, releasedate, lang)
        self.content_type = content_type
        self.precondition = precondition
        self.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        if approved != self.approved:
            self.approved = approved
            if approved == 0: self.approved_by = None
            else: self.approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    security.declareProtected(view_management_screens, 'manageUpload')
    def manageUpload(self, source='file', file='', url='', version='', REQUEST=None):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if self.wl_isLocked():
            raise ResourceLockedError, "File is locked via WebDAV"
        self.handleUpload(source, file, url)
        if version: self.createVersion()
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
        self.update_data(self.version.data, self.version.content_type)
        self.content_type = self.version.content_type
        self.precondition = self.version.precondition
        self.releasedate = self.version.releasedate
        self.setProperties(deepcopy(self.version.getProperties()))
        self.checkout = 0
        self.checkout_user = None
        self.version = None
        self.createVersion()
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
        self.version = file_item(self.id, self.title, self.description, self.coverage, self.keywords,
            self.sortorder, self.data, self.precondition, self.content_type, self.downloadfilename,
            self.releasedate, self.gl_get_selected_language())
        self.version.update_data(self.data, self.content_type)
        self.version._local_properties_metadata = deepcopy(self._local_properties_metadata)
        self.version._local_properties = deepcopy(self._local_properties)
        self.version.setProperties(deepcopy(self.getProperties()))
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, title='', description='', coverage='', keywords='', sortorder='',
        content_type='', precondition="", downloadfilename='', releasedate='', lang=None, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        try: sortorder = abs(int(sortorder))
        except: sortorder = DEFAULT_SORTORDER
        releasedate = self.utConvertStringToDateTimeObj(releasedate)
        if releasedate is None: releasedate = self.utGetTodayDate()
        if lang is None: lang = self.gl_get_selected_language()
        if not self.hasVersion():
            #this object has not been checked out; save changes directly into the object
            self.save_properties(title, description, coverage, keywords, sortorder, downloadfilename, releasedate, lang)
            self.content_type = content_type
            self.precondition = precondition
            self.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        else:
            #this object has been checked out; save changes into the version object
            if self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName():
                raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
            self.version.save_properties(title, description, coverage, keywords, sortorder, downloadfilename, releasedate, lang)
            self.version.content_type = content_type
            self.version.precondition = precondition
            self.version.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))

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
            self.handleUpload(source, file, url)
            if version: self.createVersion()
        else:
            #this object has been checked out; save changes into the version object
            if self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName():
                raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
            self.version.handleUpload(source, file, url)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/file_manage_edit', globals())

    #site actions
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'file_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'file_edit')

    security.declareProtected(view, 'download')
    def download(self, REQUEST, RESPONSE):
        """ """
        self.REQUEST.RESPONSE.setHeader('Content-Type', self.content_type)
        self.REQUEST.RESPONSE.setHeader('Content-Length', self.size)
        self.REQUEST.RESPONSE.setHeader('Content-Disposition', 'attachment;filename=' + self.downloadfilename)
        return file_item.inheritedAttribute('index_html')(self, REQUEST, RESPONSE)

InitializeClass(NyFile)
