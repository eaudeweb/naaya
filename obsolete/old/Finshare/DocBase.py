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
from DateTime import DateTime

#Zope imports
from OFS.Folder import Folder
from OFS.PropertyManager import PropertyManager
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
import OFS.ObjectManager
from OFS.SimpleItem import SimpleItem
from Products.ZCatalog.CatalogPathAwareness import CatalogAware
from AccessControl.Permissions import view_management_screens,view
from AccessControl import ClassSecurityInfo, getSecurityManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from Products.Finshare.Constants import *
from Products.Finshare.utils import batch_utils, utils


class DocBase(CatalogAware,
              PropertyManager,
              batch_utils,
              utils):
    """ DocBase object """

    _properties=(
        {'id':'id', 'type':'string','mode':''},
        {'id':'title', 'type':'string','mode':'w'},
        {'id':'description', 'type':'text','mode':'w'},
        {'id':'abstract', 'type':'string','mode':'w'},
        {'id':'creationdate', 'type':'date','mode':'w'},
        {'id':'releasedate', 'type':'date','mode':'w'},
        {'id':'ownerinfo', 'type':'string','mode':'w'},
        {'id':'approved', 'type':'boolean','mode':'w'},
        {'id':'sortorder', 'type':'int','mode':'w'},
        {'id':'language', 'type':'string','mode':'w'},
        {'id':'keywords', 'type':'string','mode':'w'},
        {'id':'coverage', 'type':'string','mode':'w'},
        {'id':'author', 'type':'string','mode':'w'},
        {'id':'source', 'type':'string','mode':'w'},
    )

    manage_options = (
        (
            {'label' : ITEM_MANAGE_OPTION_PROPERTIES, 'action' : 'manage_edit_html'},
            {'label' : ITEM_MANAGE_OPTION_VIEW, 'action' : 'index_html'},
        )
    )

    security = ClassSecurityInfo()

    def __init__(self):
        """ constructor """
        pass


    ################
    #   SESSION    #
    ################
    
 
    def is_skey(self, key):
        return self.REQUEST.SESSION.has_key(key)

    def get_skey(self, key, default=None):
        try: return self.REQUEST.SESSION[key]
        except: return default

    def set_skey(self, key, value=None):
        try: self.REQUEST.SESSION.set(key, value)
        except: pass

    def del_skey(self, key):
        try: self.REQUEST.SESSION.delete(key)
        except: pass

    def get_sThematicArea(self):
        try:
            if is_skey('thematic_area'):
                return get_skey('thematic_area')
            else:
                set_skey('thematic_area',1)
                return 1
        except: pass

    def set_sThematicArea(self, value=1):
        try:
            set_skey('thematic_area', value)
        except: pass

    ################
    #   GETTERS    #
    ################

    def getDMManagerMetaType(self):
        """ return DMManager meta_type """
        return METATYPE_DMMANAGER

    def getDMFileMetaType(self):
        """ return DMFile meta_type """
        return METATYPE_DMFILE

    def getDMURLMetaType(self):
        """ return DMURL meta_type """
        return METATYPE_DMURL

    def getDMFolderMetaType(self):
        """ return DMFolder meta_type """
        return METATYPE_DMFOLDER

    def getDMObjectsMetaType(self):
        """ retunr DMFile and DMURL meta_types """
        return METATYPE_OBJECTS

    security.declareProtected(view,'getObjectOwner')
    def getObjectOwner(self):
        """ returns ownerinfo """
        return self.ownerinfo

    def getObjectById(self, p_id):
        """ returns an object inside this one """
        try: return self._getOb(p_id)
        except: return None

    def getObjectsByIds(self, p_ids):
        """ returns a list of objects inside this one """
        return filter(lambda x: x is not None, map(lambda f, x: f(x, None), (self._getOb,)*len(p_ids), p_ids))

    def getSizeForObj(self, p_ob):
        """ transforms a file size in Kb, Mb .. """
        l_res = '&nbsp;'
        l_results = 0
        if p_ob.meta_type == METATYPE_DMURL:
            return l_res
        if p_ob.meta_type == METATYPE_DMARTICLE:            
            l_objects = p_ob.objectValues(METATYPE_OBJECTS)
            for l_ob in l_objects:
                #if l_ob.meta_type in METATYPE_OBJECTS:                
                l_results += l_ob.get_size()
            return self.getSize(l_results)    
        p_size = p_ob.get_size()
        return self.getSize(p_size)

    def getSize(self, p_float):
        """ transforms a file size in Kb, Mb .. """
        l_bytes = float(p_float)
        l_type = ''
        if l_bytes >= 1000:
            l_bytes = l_bytes/1024
            l_type = 'Kb'
            if l_bytes >= 1000:
                l_bytes = l_bytes/1024
                l_type = 'Mb'
            l_res = '%s %s' % ('%4.2f' % l_bytes, l_type)
        else:
            l_type = 'Bytes'
            l_res = '%s %s' % ('%4.0f' % l_bytes, l_type)
        return l_res


    #############################
    #   Export in xml format    #
    #############################

    security.declarePrivate('exportThisBaseProperties')
    def exportThisBaseProperties(self):
        """ exports base properties """
        return 'id="%s" title="%s" description="%s" language="%s" coverage="%s" keywords="%s" sortorder="%s" approved="%s" releasedate="%s"' % \
                (self.utXmlEncode(self.id),
                 self.utXmlEncode(self.title),
                 self.utXmlEncode(self.description),
                 self.utXmlEncode(self.language),
                 self.utXmlEncode(self.coverage),
                 self.utXmlEncode(self.keywords),
                 self.utXmlEncode(self.sortorder),
                 self.utXmlEncode(self.approved),
                 self.utXmlEncode(self.releasedate))

    security.declarePrivate('exportThisDynamicProperties')
    def exportThisDynamicProperties(self):
        """ exports dynamic properties """
        l_xml = []
        for l_dp in self.getDynamicPropertiesTool().getDynamicSearchableProperties(self.meta_type):
            l_xml.append('%s="%s"' % (self.utXmlEncode(l_dp.id), self.utXmlEncode(self.getPropertyValue(l_dp.id))))
        return ''.join(l_xml)

    security.declarePrivate('exportThis')
    def exportThis(self):
        """ export properties """
        return '<%s %s %s %s/>' % \
                (self.utXmlEncode(self.meta_type),
                 self.exportThisBaseProperties(),
                 self.exportThisCustomProperties(),
                 self.exportThisDynamicProperties())


    ###################
    #   Syndication   #
    ###################

    security.declarePrivate('syndicateThisHeader')
    def syndicateThisHeader(self):
        """ syndication header """
        return '<item rdf:about="%s">' % self.absolute_url(0)

    security.declarePrivate('syndicateThisFooter')
    def syndicateThisFooter(self):
        """ syndication footer """
        return '</item>'

    security.declarePrivate('syndicateThisCommon')
    def syndicateThisCommon(self):
        """ syndicate informations """
        l_rdf = []
        l_rdf.append('<link>%s</link>' % self.absolute_url())
        l_rdf.append('<dc:title>%s</dc:title>' % self.utXmlEncode(self.title_or_id()))
        l_rdf.append('<dc:identifier>%s</dc:identifier>' % self.absolute_url())
        l_rdf.append('<dc:date>%s</dc:date>' % self.utShowFullDateTime(self.releasedate))
        l_rdf.append('<dc:description>%s</dc:description>' % self.utXmlEncode(self.description))
        l_rdf.append('<dc:contributor>%s</dc:contributor>' % self.utXmlEncode(''))
        l_rdf.append('<dc:coverage>%s</dc:coverage>' % self.utXmlEncode(self.coverage))
        l_rdf.append('<dc:language>%s</dc:language>' % self.utXmlEncode(self.language))
        for l_k in self.keywords.split(' '):
            l_rdf.append('<dc:subject>%s</dc:subject>' % self.utXmlEncode(l_k))
        l_rdf.append('<dc:creator>%s</dc:creator>' % self.utXmlEncode(''))
        l_rdf.append('<dc:publisher>%s</dc:publisher>' % self.utXmlEncode(''))
        l_rdf.append('<dc:rights>%s</dc:rights>' % self.utXmlEncode(''))
        return ''.join(l_rdf)

    security.declarePrivate('getNamespacesForRdf')
    def getNamespacesForRdf(self):
        """ returns namespaces """
        return ' '.join(map(lambda x: str(x), DOCMANAGER_NAMESPACES))

    security.declarePrivate('syndicateSomething')
    def syndicateSomething(self, p_url, p_items=[]):
        """ syndicate informations """
        l_site = self.getDocManager()
        l_rdf = []
        l_rdf.append('<?xml version="1.0" encoding="utf-8"?>')
        l_rdf.append('<rdf:RDF %s>' % self.getNamespacesForRdf())
        l_rdf.append('<channel rdf:about="%s">' % l_site.absolute_url())
        l_rdf.append('<title>%s</title>' % l_site.utXmlEncode(self.title_or_id()))
        l_rdf.append('<link>%s</link>' % p_url)
        l_rdf.append('<description>%s</description>' % self.utXmlEncode(self.description))
        l_rdf.append('<dc:identifier>%s</dc:identifier>' % p_url)
        l_rdf.append('<dc:date>%s</dc:date>' % self.utShowFullDateTime(self.utGetTodayDate()))
        l_rdf.append('<dc:publisher>%s</dc:publisher>' % self.utXmlEncode(''))
        l_rdf.append('<dc:creator>%s</dc:creator>' % self.utXmlEncode(''))
        l_rdf.append('<dc:subject>%s</dc:subject>' % self.utXmlEncode(self.title_or_id()))
        l_rdf.append('<dc:language>en-us</dc:language>')
        l_rdf.append('<dc:rights>%s</dc:rights>' % self.utXmlEncode(''))
        l_rdf.append('<dc:source>%s</dc:source>' % self.utXmlEncode(''))
        l_rdf.append('<items>')
        l_rdf.append('<rdf:Seq>')
        for l_item in p_items:
            l_rdf.append('<rdf:li resource="%s"/>' % l_item.absolute_url())
        l_rdf.append('</rdf:Seq>')
        l_rdf.append('</items>')
        l_rdf.append('</channel>')
        for l_item in p_items:
            l_rdf.append(l_item.syndicateThis())
        l_rdf.append("</rdf:RDF>")
        self.REQUEST.RESPONSE.setHeader('content-type', 'text/xml')
        return ''.join(l_rdf)


    #####################
    #   OBJECTS COUNT   #
    #####################

    security.declareProtected(view, 'getDMFolders')
    def getDMFolders(self, approved=1):
        """ objectValues """
        return self.objectValues('DocFolder')
    
    def getDMArticles(self, approved=1):
        """ objectValues """
        return self.objectValues('DocArticle')

    security.declareProtected(view, 'getDMObjects')
    def getDMObjects(self):
        """ returns all the content inside the container """
        return self.objectValues(['DocFile' , 'DocURL', 'DocArticle'])

    security.declareProtected(view,'countFolderObjects')
    def countObjectsDMFolder(self, p_obj):
        """ return the number of objects inside the container """
        l_results = 0
        l_objects = p_obj.objectValues(METATYPE_ALL)
        for l_ob in l_objects:
            if l_ob.meta_type in METATYPE_OBJECTS:  l_results += 1
            else:
                l_all_childs = 0
                l_all_childs = self.countObjectsDMFolder(l_ob)
                l_results = l_results + l_all_childs
        return l_results

    def countObjectsDMArticle(self, p_obj):
        """ return the number of files inside the article """        
        l_objects = p_obj.objectValues(METATYPE_DMFILE)        
        return len(l_objects)
    
    security.declareProtected(view,'getDownloadInformation')
    def getDownloadInformation(self, p_ids):
        """ returns download information """
        l_folders = 0
        l_files = 0
        for k in p_ids:
            l_ob = self.getObjectById(k)
            if l_ob.meta_type == METATYPE_DMFOLDER:
                l_folders += 1
            if l_ob.meta_type == METATYPE_DMARTICLE:
                l_folders += 1    
            if l_ob.meta_type == METATYPE_DMFILE:
                l_files += 1
        return (l_folders, l_files)


    #############
    #   OTHER   #
    #############

    def testCurrentUserName(self):
        """ test if current user is same with the object's owner """
        return self.ownerinfo == self.getAuthenticatedUser()

    security.declarePrivate('approveThis')
    def approveThis(self, approved=1):
        """ approvement function """
        self.approved = approved
        self._p_changed = 1

    def manage_afterAdd(self, item, container):
        """ this method is called, whenever _setObject in DocManager gets called """
        try: Folder.inheritedAttribute('manage_afterAdd')(self, item, container)
        except: SimpleItem.inheritedAttribute('manage_afterAdd')(self, item, container)
        self.CatalogDMObject(self)
#        #notify folder's maintainer about the new upload
#        if container.meta_type == METATYPE_DMFOLDER:
#            l_emails = self.getMaintainersEmails(container)
#            if len(l_emails) > 0:
#                self.getEmailTool().notifyMaintainerEmail(l_emails, self.administrator_email, item.id, self.absolute_url(), '%s/basketofapprovals_html' % container.absolute_url())

    def manage_beforeDelete(self, item, container):
        """ this method is called, when the object is deleted """
        self.UncatalogDMObject(self)
        try: Folder.inheritedAttribute('manage_beforeDelete')(self, item, container)
        except: SimpleItem.inheritedAttribute('manage_beforeDelete')(self, item, container)

    security.declarePrivate('setReleaseDate')
    def setReleaseDate(self, releasedate):
        """ sets release date """
        self.releasedate = self.utGetDate(releasedate)
        self._p_changed = 1

    def _object_keywords(self):
        """ keywords """
        l_values = [self.title, self.description, self.keywords]
        for l_dp in self.getDynamicPropertiesTool().getDynamicSearchableProperties(self.meta_type):
            l_values.append(self.getPropertyValue(l_dp.id))
        return ' '.join(l_values)

    security.declarePrivate('object_keywords')
    def object_keywords(self):
        """ keywords """
        return self._object_keywords()


    ####################
    #   PERMISSIONS    #
    ####################

    def checkPermission(self, p_permission):
        """ check permission """
        return getSecurityManager().checkPermission(p_permission, self)

    def checkPermissionViewObjects(self):
        """ permission view objects """
        return self.checkPermission(PERMISSION_VIEW_DMOBJECTS)

    def checkPermissionChgPropsObjects(self):
        """ permission change properties """
        return self.checkPermission(PERMISSION_CHANGE_PROPERTIES)

    def checkPermissionEditUsers(self):
        """ permission edit objects """
        return self.checkPermission(PERMISSION_EDIT_USERS)

    def checkPermissionPublishObjects(self):
        """ permission publish object """
        return self.checkPermission(PERMISSION_PUBLISH_DMOBJECTS)

    def checkPermissionEditObjects(self):
        """ permission edit object """
        return self.checkPermission(PERMISSION_EDIT_DMOBJECTS)

    def checkPermissionEditObject(self):
        """ permission edit object """
        return self.checkPermissionEditObjects() and (self.checkPermissionPublishObjects() or (self.getObjectOwner() == self.REQUEST.AUTHENTICATED_USER.getUserName()))

    def checkPermissionDeleteObjects(self):
        """ permission delete object """
        return self.checkPermission(PERMISSION_DELETE_DMOBJECTS)

    def checkPermissionDeleteObject(self):
        """ permission delete object """
        return self.checkPermissionDeleteObjects() and (self.checkPermissionPublishObjects() or (self.getObjectOwner() == self.REQUEST.AUTHENTICATED_USER.getUserName()))

    def checkPermissionCutObjects(self):
        """ permission cut object """
        return self.checkPermission(PERMISSION_PUBLISH_DMOBJECTS)

#    def checkPermissionCutObject(self):
#        """ permission cut object """
#        return self.checkPermissionCutObjects() and (self.checkPermissionPublishObjects() or (self.getObjectOwner() == self.REQUEST.AUTHENTICATED_USER.getUserName()))

    def checkPermissionAddFolders(self):
        """ permission add DMFolder object """
        return self.checkPermission(PERMISSION_ADD_DOC_FOLDER)

    def checkPermissionAddFiles(self):
        """ permission add DMFile object """
        return self.checkPermission(PERMISSION_ADD_DOC_FILE)

    def checkPermissionAddUrls(self):
        """ permission add DMURL object """
        return self.checkPermission(PERMISSION_ADD_DOC_URL)

    def checkPermissionCopyObjects(self):
        """ permission copy object """
        return self.checkPermission(PERMISSION_PUBLISH_DMOBJECTS)

    def checkPermissionPasteObjects(self):
        """ permission paste object """
        return self.checkPermission(PERMISSION_EDIT_DMOBJECTS)

    def checkPermissionUploadObjects(self):
        """ permission upload object """
        return self.checkPermission(PERMISSION_EDIT_DMOBJECTS)


    #########################
    #   CONTENT FUNCTIONS   #
    #########################

    security.declareProtected(view, 'hasDMContent')
    def hasDMContent(self):
        """ test if content """
        return self.hasDMObjects() or self.hasDMFolders()

    security.declareProtected(view, 'hasDMFolders')
    def hasDMFolders(self):
        """ test if contains any DocFolder """
        return len(self.getDMFolders()) > 0

    security.declareProtected(view, 'hasDMObjects')
    def hasDMObjects(self):
        """ test if contains any DocFile or DocUrl """
        return len(self.getDMObjects()) > 0


    ##############################################################
    #   CUT/COPY/PASTE/DELETE/BULK UPLOAD/DOWNLOAD OPERATIONS    #
    ##############################################################

    security.declareProtected(PERMISSION_EDIT_DMOBJECTS, 'copyObjects')
    def copyObjects(self, REQUEST=None):
        """ copy objects """
        id_list = self.utConvertToList(REQUEST.get('id', []))
        try: self.manage_copyObjects(id_list, REQUEST)
        except: pass
        if REQUEST: REQUEST.RESPONSE.redirect('index_html')

    security.declareProtected(PERMISSION_DELETE_DMOBJECTS, 'cutObjects')
    def cutObjects(self, REQUEST=None):
        """ cut objects """
        id_list = self.utConvertToList(REQUEST.get('id', []))
        try: self.manage_cutObjects(id_list, REQUEST)
        except: pass
        if REQUEST: REQUEST.RESPONSE.redirect('index_html')

    security.declareProtected(view, 'hasObjectsToPaste')
    def hasObjectsToPaste(self):
        """ test if any objects to paste """
        return self.cb_dataValid()

    security.declareProtected(PERMISSION_EDIT_DMOBJECTS, 'pasteObjects')
    def pasteObjects(self, REQUEST=None):
        """ paste objects """
        try: self.manage_pasteObjects(None, REQUEST)
        except: pass
        if REQUEST: REQUEST.RESPONSE.redirect('index_html')

#    security.declareProtected(PERMISSION_DELETE_DMOBJECTS, 'deleteObjects')
    security.declareProtected(PERMISSION_EDIT_DMOBJECTS, 'deleteObjects')
    def deleteObjects(self, REQUEST=None):
        """ delete objects """
        id_list = self.utConvertToList(REQUEST.get('id', []))
        del_list = []
        err_list = []
        for l_id in id_list:
            l_ob = self._getOb(l_id)
            edit_permission = l_ob.checkPermissionEditObject()
            if edit_permission: del_list.append(l_id)
            else:
                l_ob = self._getOb(l_id)
                err_list.append(l_ob.title_or_id())
        try: self.manage_delObjects(del_list)
        except: pass
        if REQUEST and len(err_list)==0: REQUEST.RESPONSE.redirect('index_html')
        else: REQUEST.RESPONSE.redirect('index_html?err_list=%s' % self.utJoinToString(err_list, ','))

    security.declareProtected(view, 'downloadObjects')
    def downloadObjects(self, REQUEST=None):
        """ downloads objects """
        l_id_list = self.utConvertToList(REQUEST.get('id', []))
        l_list = self.utJoinToString(l_id_list)
        if REQUEST: REQUEST.RESPONSE.redirect('download_html?files=%s' % l_list)

    security.declareProtected(view, 'downloadComments')
    def downloadComments(self, p_meta_type):
        """ return the comments for download """
        if p_meta_type == METATYPE_DMURL:
            return DOWNLOAD_IMPOSSIBLE
        return DOWNLOAD_POSSIBLE

    security.declareProtected(PERMISSION_EDIT_DMOBJECTS, 'uploadMultiple')
    def uploadMultiple(self, file='', REQUEST=None):
        """ uploads objects """
        l_message = self.manage_addZipFile(file)
        if REQUEST: REQUEST.RESPONSE.redirect('upload_html?dm_save=%s&dm_msg=%s' % (l_message[1], l_message[0]))


    #############################
    #   BASKET OF APPROVALS     #
    #############################

    security.declareProtected(PERMISSION_PUBLISH_DMOBJECTS, 'updateBasketOfApprovals')
    def updateBasketOfApprovals(self, REQUEST=None):
        """ changes the objects status """
        app_list = self.utConvertToList(REQUEST.get('app', []))
        del_list = self.utConvertToList(REQUEST.get('del', []))
        self.approveContent(app_list)
        self.deleteContent(del_list)
        if REQUEST: REQUEST.RESPONSE.redirect('basketofapprovals_html')

    security.declareProtected(PERMISSION_PUBLISH_DMOBJECTS, 'approveContent')
    def approveContent(self, item_ids=[]):
        """ approves objects """
        for item_id in item_ids:
            self.approveDMObject(item_id)

    security.declareProtected(PERMISSION_PUBLISH_DMOBJECTS, 'approveDMObject')
    def approveDMObject(self, p_id):
        """ approves an object """
        try:
            ob = self._getOb(p_id)
            ob.approveThis()
            self.recatalogDMObject(ob)
        except: pass


    security.declareProtected(PERMISSION_PUBLISH_DMOBJECTS, 'deleteContent')
    def deleteContent(self, item_ids=[]):
        """ delets objects """
        for item_id in item_ids:
            self.deleteDMObject(item_id)

    security.declarePrivate('deleteDMObject')
    def deleteDMObject(self, id):
        """ deletes an object """
        try: self._delObject(id)
        except: pass

    security.declareProtected(view, 'checkPermissionManageFolders')
    def checkPermissionManageFolders(self,filter=''):
        """ returns containing folders of the current folder """
        results = []
        select_all = 0
        delete_all = 0
        flag= 0                
        for folder in self.utSortObjsListByAttr(self.getDMFolders(), 'creationdate', 1):
            del_permission = folder.checkPermissionDeleteObjects()
            if del_permission == 1 and flag == 0:
                flag = 1
                select_all = 1
                delete_all = 1
            edit_permission = folder.checkPermissionEditObject()
            if edit_permission == 1 and flag == 0:
                flag = 1
                select_all = 1
                delete_all = 1
            if (edit_permission and not folder.approved) or folder.approved:
                results.append((del_permission, edit_permission, folder))
        return (select_all, delete_all, results)

    security.declareProtected(PERMISSION_EDIT_DMOBJECTS, 'getPendingContent')
    def getPendingContent(self):
        l_result = self.getPendingDMFolders()
        l_result.extend(self.getPendingDMObjects())
        return l_result

    security.declarePrivate('getPendingDMFolders')
    def getPendingDMFolders(self):
        """ returns panding folders """
        return self.utFilterObjsListByAttr(self.getDMFolders(), 'approved', 0)

    security.declarePrivate('getPendingDMObjects')
    def getPendingDMObjects(self):
        """ returns pending objects """
        return self.utFilterObjsListByAttr(self.getDMObjects(), 'approved', 0)

    security.declarePrivate('hasPendingContent')
    def hasPendingContent(self):
        """ test if pending content """
        return self.hasPendingDMFolders() or self.hasPendingDMObjects()

    security.declarePrivate('hasPendingDMFolders')
    def hasPendingDMFolders(self):
        """ test if pending folders """
        return len(self.getPendingDMFolders()) > 0

    security.declarePrivate('hasPendingDMObjects')
    def hasPendingDMObjects(self):
        """ test if pending objects """
        return len(self.getPendingDMObjects()) > 0


    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'menusubmissions')
    menusubmissions = PageTemplateFile('zpt/DocBase/DocBase_menusubmissions', globals())

    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'menuoperations')
    menuoperations = PageTemplateFile('zpt/DocBase/DocBase_menuoperations', globals())

    security.declareProtected(PERMISSION_EDIT_DMOBJECTS, 'basketofapprovals_html')
    basketofapprovals_html = PageTemplateFile('zpt/DocBase/DocBase_basketofapprovals', globals())

    security.declareProtected(PERMISSION_ADD_DOC_FOLDER, 'folder_add_html')
    folder_add_html = PageTemplateFile('zpt/DocFolder/folder_add', globals())
    folder_add_html.FormAction = 'addDocFolder'

    security.declareProtected(PERMISSION_ADD_DOC_FOLDER, 'article_add_html')
    article_add_html = PageTemplateFile('zpt/DocArticle/article_add', globals())
    article_add_html.FormAction = 'addDocArticle'

    security.declareProtected(PERMISSION_ADD_DOC_URL, 'url_add_html')
    url_add_html = PageTemplateFile('zpt/DocURL/url_add', globals())
    url_add_html.FormAction = 'addDocURL'

    security.declareProtected(PERMISSION_ADD_DOC_FILE, 'file_add_html')
    file_add_html = PageTemplateFile('zpt/DocFile/file_add', globals())
    file_add_html.FormAction = 'addDocFile'

    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'download_html')
    download_html = PageTemplateFile('zpt/DocBase/DocBase_download', globals())

    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'help_html')
    help_html = PageTemplateFile('zpt/DocBase/DocBase_help', globals())

InitializeClass(DocBase)