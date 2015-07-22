# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
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
# Copyright (C) European Environment Agency. All
# Rights Reserved.
#
# Authors:
# Alexandru Ghica, Adriana Baciu - Finsiel Romania


#Python imports

#Zope imports
from OFS.Image import File, cookId
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.SimpleItem import SimpleItem

#Product imports
from Products.Finshare.DocBase import DocBase
from Products.Finshare.Constants import *
from Products.Finshare.DocVersioning import DocVersioning
from Products.Finshare.DocHistory import DocHistory
from Products.Finshare.DocComments import DocComments


manage_addDocFile_html = PageTemplateFile('zpt/DocFile/file_manage_add', globals())
manage_addDocFile_html.FormAction = 'addDocFile'


def addDocFile(self, id='', title='', description='', releasedate='',approved='', sortorder='', language='', keywords='', coverage='', author='', source='', f_source='', file='', precondition='', content_type='', downloadfilename='', file_version='', status='', REQUEST=None, **kwargs):
    """ add a new DocFile object """
    id, title = cookId(id, title, file)
    #id = self.utCleanupId(id)
    if downloadfilename == '': downloadfilename = self.utCleanupId(id)
    id = 'file' + self.utGenRandomId(6)
    #if id == '': id = 'file' + self.utGenRandomId(6)    
    try: sortorder = abs(int(sortorder))
    except: sortorder = 100
    #if self.checkPermissionPublishObjects(): approved = 1
    approved = 1
    #else: approved = 0
    if not releasedate: releasedate = self.utGetTodayDate()
    else: releasedate = self.utConvertStringToDateTimeObj(releasedate)
    creationdate = self.utGetTodayDate()
    ownerinfo = self.getAuthenticatedUser()
    if file_version=='': file_version = '1.0'
    #create  object
    ob = DocFile( id, title, description, creationdate, releasedate, ownerinfo, approved, sortorder, language, keywords, coverage, author, source, f_source, precondition, content_type, downloadfilename, file_version, status)
    self._setObject(id, ob)
    ob = self._getOb(id)
    #history
    ob.createHistory(HISTORY_ADD)
    #upload data
    if file: ob.uploadFile(file)
    ob.CatalogDMObject(ob)
    if content_type: ob.content_type = content_type
    #create new version if case
    ob.createVersion()
    if REQUEST is not None:
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'manage_addDocFile_html' or l_referer.find('manage_addDocFile_html') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'file_add_html':
            REQUEST.RESPONSE.redirect(self.absolute_url(0))


class DocFile(DocBase, File, SimpleItem, DocVersioning, DocHistory, DocComments):
    """ DocFile class """

    meta_type = METATYPE_DMFILE
    icon = 'misc_/Finshare/file'
    icon_marked = 'misc_/Finshare/file_marked'

    manage_options = (
        ({'label' : ITEM_MANAGE_OPTION_PROPERTIES, 'action' : 'manage_edit_html'},)
        +
        DocVersioning.manage_options
        +
        (File.manage_options[5],
         File.manage_options[3],
         File.manage_options[6],)
    )


    security = ClassSecurityInfo()

    def __init__(self, id, title, description, creationdate, releasedate, ownerinfo, approved, sortorder, language, keywords, coverage, author, source, file, precondition, content_type, downloadfilename, file_version, status):
        """ constructor """
        self.id = id
        self.title = title
        self.description = description
        self.creationdate = creationdate
        self.releasedate = releasedate
        self.ownerinfo = ownerinfo
        self.approved = approved
        self.sortorder = sortorder
        self.language = language
        self.coverage = coverage
        self.keywords = keywords
        self.author = author
        self.source = source
        self.downloadfilename = downloadfilename
        self.file_version = file_version
        self.status = status
        File.__dict__['__init__'](self, id, title, file, content_type, precondition)
        DocVersioning.__dict__['__init__'](self)
        DocHistory.__dict__['__init__'](self)
        DocComments.__dict__['__init__'](self)


    ###########################
    #         ZMI FORMS       #
    ###########################

    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/DocFile/file_manage_edit', globals())

    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', releasedate='', language='', coverage='', keywords='', sortorder='', approved='', source='', f_source='', file='', precondition='', content_type='', downloadfilename='', file_version='', status='', REQUEST=None, **kwargs):
        """ updates DocFile instance properties """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if self.wl_isLocked():
            raise ResourceLockedError, EXCEPTION_WEBDAV
        try: sortorder = abs(int(sortorder))
        except: sortorder = 100
        if approved: approved = 1
        else: approved = 0
        self.title = title
        self.description = description
        self.language = language
        self.coverage = coverage
        self.keywords = keywords
        self.sortorder = sortorder
        self.approved = approved
        self.source = source
        self.precondition = precondition
        if file:
            self.uploadFile(file)
            self.createHistory(HISTORY_UPLOAD)
        #creates new version if case
        if file_version=='': file_version = self.file_version
        self.file_version = file_version
        self.status = status
        self.createVersion()
        self.downloadfilename = downloadfilename
        self.createHistory(HISTORY_EDIT)
        self._p_changed = 1
        self.recatalogDMObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')


    ######################
    #    SITE FORMS      #
    ######################

#    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'index_html')
#    index_html = PageTemplateFile('zpt/DocFile/file_index', globals())

    security.declareProtected(PERMISSION_EDIT_DMOBJECTS, 'edit_html')
    edit_html = PageTemplateFile('zpt/DocFile/file_edit', globals())

#    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'history_html')
#    history_html = PageTemplateFile('zpt/DocFile/file_history', globals())
#
#    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'comments_html')
#    comments_html = PageTemplateFile('zpt/DocFile/file_comments', globals())

    security.declareProtected(PERMISSION_EDIT_DMOBJECTS, 'saveProperties')
    def saveProperties(self, title='', description='', language='', coverage='', keywords='', sortorder='', f_source='', file='', content_type='', downloadfilename='', file_version='', status='', REQUEST=None, **kwargs):
        """ updates File instance properties """
        if not self.checkPermissionEditObjects():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if self.wl_isLocked():
            raise ResourceLockedError, EXCEPTION_WEBDAV
        try: sortorder = abs(int(sortorder))
        except: sortorder = 100
        self.title = title
        self.description = description
        self.language = language
        self.coverage = coverage
        self.keywords = keywords
        self.sortorder = sortorder
        if file:
            self.uploadFile(file)
            self.createHistory(HISTORY_UPLOAD)
        #create new version if case
        if file_version=='': file_version = self.file_version
        self.file_version = file_version
        self.status = status
        self.createVersion()
        self.createHistory(HISTORY_EDIT)
        self.downloadfilename = downloadfilename
        self._p_changed = 1
        self.recatalogDMObject(self)

        if REQUEST: REQUEST.RESPONSE.redirect(self.aq_parent.absolute_url(0))
#        if REQUEST: REQUEST.RESPONSE.redirect('edit_html?dm_save=ok')

    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'saveComment')
    def saveComment(self, doc_title='', doc_comment='', doc_email='', REQUEST=None):
        """ creates a comment """
        l_message = 'dm_save=err&doc_title=%s&doc_comment=%s&doc_email=%s' % (doc_title, doc_comment, doc_email)
        if self.utStrAllNotEmpty(doc_title, doc_comment, doc_email) and (self.utIsEmailValid(doc_email) or len(doc_email)==0):
            self.createComment(doc_title, doc_comment, doc_email)
            self.createHistory(HISTORY_COMMENT)
            l_message = 'dm_save=ok'
        if REQUEST: REQUEST.RESPONSE.redirect('comments_html?%s' % l_message)

    security.declareProtected(PERMISSION_EDIT_DMOBJECTS, 'uploadFile')
    def uploadFile(self, file):
        """ asociates a file to the DocFile object """
        data, size = self._read_data(file)
        content_type=self._get_content_type(file, data, self.__name__, 'undefined')
        self.update_data(data, content_type, size)
        self._p_changed = 1

    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'download')
    def download(self, REQUEST, RESPONSE):
        """ set for download asociated file """
        self.REQUEST.RESPONSE.setHeader('Content-Type', self.content_type)
        self.REQUEST.RESPONSE.setHeader('Content-Length', self.size)
        self.REQUEST.RESPONSE.setHeader('Content-Disposition', 'attachment;filename=' + self.downloadfilename)
        return DocFile.inheritedAttribute('index_html')(self, REQUEST, RESPONSE)

    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'getDownloadInfo')
    def getDownloadInfo(self):
        """ returns download information """
        return self.downloadfilename + ' (' + self.content_type + ', ' + self.getSizeForObj(self) + ')'

    def indexThematicArea(self):
        return ''

    #############################
    #   Export in xml format    #
    #############################

    security.declarePrivate('exportThisCustomProperties')
    def exportThisCustomProperties(self):
        """ exports custom properties """
        return 'downloadfilename="%s" file="%s" content_type="%s" precondition="%s"' % \
                (self.utXmlEncode(self.downloadfilename),
                 self.utBase64Encode(str(self.utNoneToEmpty(self.data))),
                 self.utXmlEncode(self.content_type),
                 self.utXmlEncode(self.precondition))


    #################
    #   Versioning  #
    #################

    security.declarePrivate('objectDataForVersion')
    def objectDataForVersion(self):
        #returns the data that will be stored in a version
        # can be a property value or a list of properties or any structure
        return (str(self.data), self.content_type)

    security.declarePrivate('objectDataForVersionCompare')
    def objectDataForVersionCompare(self):
        #returns the object property that is reprezentative for that object
        #it will support a crc32 comparation againts an older version
        #in order to determine if is the same value
        return str(self.data)

    security.declarePrivate('objectVersionDataForVersionCompare')
    def objectVersionDataForVersionCompare(self, p_version_data):
        #returns the version piece that is reprezentative for a that version
        #it will support a crc32 comparation againts the object data
        #in order to determine if is the same value
        return p_version_data[0]

    security.declarePrivate('versionForObjectData')
    def versionForObjectData(self, p_version_data=None):
        #restores the object data based on a version data
        self.update_data(p_version_data[0], p_version_data[1], len(p_version_data[0]))
        self._p_changed = 1

    security.declareProtected(PERMISSION_VIEW_DMOBJECTS,'showVersionData')
    def showVersionData(self, vid=None, REQUEST=None, RESPONSE=None):
        """ returns version's data """
        if vid:
            version_data = self.getVersion(vid)
            if version_data is not None:
                #show data for file: set content type and return data
                RESPONSE.setHeader('Content-Type', version_data[0][1])
                RESPONSE.setHeader('Content-Length', version_data[2])
                RESPONSE.setHeader('Content-Disposition', 'attachment;filename=' + version_data[1])
                return version_data[0][0]
            else:
                return 'Invalid version data!'
        else:
            return 'Invalid version id!'

    def deleteOldVersion(self,p_version_uid,REQUEST=None):
        """ deletes a comment entry """
        self.delete_oldversion(p_version_uid)
        if REQUEST: REQUEST.RESPONSE.redirect(self.aq_parent.absolute_url(0) + '/index_html')

    ###################
    #   Syndication   #
    ###################

    security.declarePrivate('syndicateThis')
    def syndicateThis(self):
        """ syndicate informations """
        l_rdf = []
        l_rdf.append(self.syndicateThisHeader())
        l_rdf.append(self.syndicateThisCommon())
        l_rdf.append('<dc:type>Text</dc:type>')
        l_rdf.append('<dc:format>application</dc:format>')
        l_rdf.append('<dc:source>%s</dc:source>' % self.utXmlEncode(''))
        l_rdf.append(self.syndicateThisFooter())
        return ''.join(l_rdf)

InitializeClass(DocFile)