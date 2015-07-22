#The contents of this file are subject to the Mozilla Public License
#Version 1.1 (the "License"); you may not use this file except in
#compliance with the License. You may obtain a copy of the License at
#http://www.mozilla.org/MPL/
#
#Software distributed under the License is distributed on an "AS IS"
#basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
#License for the specific language governing rights and limitations
#under the License.
#
#The Original Code is DocManager version 1.0
#
#The Initial Developer of the Original Code is  Finsiel Romania.
#Portions created by Finsiel Romania are Copyright (C) Finsiel Romania.
#All Rights Reserved.      
#
#Contributor(s): Alexandru Ghica, Adriana Baciu, COrnel Nitu.

#Zope imports
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view #xxx
from Globals import InitializeClass
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import Products

#Products import
from Products.Finshare.interfaces.IDocFolder import IDocFolder
from Products.Finshare.DocFile import addDocFile, manage_addDocFile_html
from Products.Finshare.DocURL import addDocURL, manage_addDocURL_html
from Products.Finshare.DocArticle import addDocArticle, manage_addDocArticle_html
from Products.Finshare.DocZip import DocZip
from Products.Finshare.DocBase import DocBase
from Products.Finshare.Constants import *


manage_addDocFolder_html = PageTemplateFile('zpt/DocFolder/folder_manage_add', globals())
manage_addDocFolder_html.FormAction = 'addDocFolder'

def addDocFolder(self, id='', title='', description='', abstract = '', releasedate = '',
                    approved = '', sortorder='', keywords='', coverage='', author= '', source = '',
                    maintainer_email='', REQUEST=None, RESPONSE=None):
    
    """ add a new DocFolder object """
    id = self.utCleanupId(id)
    if not id:
        id = 'fol%s' % self.utGenRandomId(6)
    try:
        sortorder = abs(int(sortorder))
    except:
        sortorder = 100

    if self.checkPermissionPublishObjects():
        approved = 1
    else:
        approved = 0

    if not releasedate:
        releasedate = self.utGetTodayDate()
    else:
        releasedate = self.utConvertStringToDateTimeObj(releasedate)

    creationdate = self.utGetTodayDate()
    ownerinfo = self.getAuthenticatedUser()

    ob = DocFolder(id, title, description, abstract, creationdate, releasedate, ownerinfo, approved, sortorder, keywords, coverage, author, source, maintainer_email)
    self._setObject(id, ob)

    if REQUEST is not None:
        referer = self.utSplitToList(REQUEST['HTTP_REFERER'], '/')[-1]
        if referer == 'manage_addDocFolder_html' or referer.find('manage_addDocFolder_html') != -1:
            return self.manage_main(self, REQUEST, update_menu = 1)
        elif referer == 'folder_add_html':
            REQUEST.RESPONSE.redirect(self.absolute_url(0) + '/note_html')


class DocFolder(DocBase, Folder, DocZip):
    """ implements IDocFolder as an independent, ZMI-manageable object """

    meta_type = METATYPE_DMFOLDER
    icon = 'misc_/Finshare/folder'
    icon_marked = 'misc_/Finshare/folder_marked'

    __implements__ = IDocFolder

    manage_options = (
        (Folder.manage_options[0],)
        +
        DocBase.manage_options
        +
         (Folder.manage_options[5],
         Folder.manage_options[3],
         Folder.manage_options[6],)
         )

    security = ClassSecurityInfo()

    def all_meta_types(self):
        """ What can you put inside me? """
        local_meta_types = [{'name': METATYPE_DMFOLDER, 'action': 'manage_addDocFolder_html', 'product': DOCMANAGER_PRODUCT_NAME},
                            {'name': METATYPE_DMARTICLE, 'action': 'manage_addDocArticle_html', 'product': DOCMANAGER_PRODUCT_NAME},]
        f = lambda x: x['name'] in ()
        for x in filter(f, Products.meta_types):
            local_meta_types.append(x)
        return local_meta_types

    def __init__(self, id, title, description, abstract, creationdate, releasedate, ownerinfo, approved, sortorder, keywords, coverage, author, source, maintainer_email,):
        self.id = id
        self.title = title
        self.description = description
        self.abstract = abstract
        self.creationdate = creationdate
        self.releasedate = releasedate
        self.ownerinfo = ownerinfo
        self.approved = approved
        self.sortorder = sortorder
        self.keywords = keywords
        self.coverage = coverage
        self.author = author
        self.source = source
        self.maintainer_email = maintainer_email


    ###########################
    #         ZMI FORMS       #
    ###########################

    security.declareProtected(PERMISSION_EDIT_DMOBJECTS, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/DocFolder/folder_manage_edit', globals())

    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', abstract='', releasedate = '', coverage='',
                         keywords='', sortorder='', maintainer_email='', approved='', source = '',
                         REQUEST=None, RESPONSE=None, **kwargs):
        """ See IDocFolder. """
        
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        try:
            sortorder = abs(int(sortorder))
        except:
            sortorder = 100
        if approved:
            approved = 1
        else:
            approved = 0
        self.title = title
        self.description = description
        self.abstract = abstract
        self.coverage = coverage
        self.keywords = keywords
        self.sortorder = sortorder
        self.maintainer_email = maintainer_email
        self.approved = approved
        self._p_changed = 1
        self.recatalogDMObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')


    #####################
    #   SITE FORMS      #
    #####################

    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'index_html')
    index_html = PageTemplateFile('zpt/DocFolder/folder_index', globals())

    security.declareProtected(PERMISSION_EDIT_DMOBJECTS, 'edit_html')
    edit_html = PageTemplateFile('zpt/DocFolder/folder_edit', globals())

    security.declareProtected(PERMISSION_EDIT_DMOBJECTS, 'upload_html')
    upload_html = PageTemplateFile('zpt/DocFolder/folder_upload', globals())

    security.declareProtected(PERMISSION_EDIT_DMOBJECTS, 'saveProperties')
    def saveProperties(self, title='', description='', coverage='', keywords='', sortorder='',
                        locator='', REQUEST=None, RESPONSE=None, **kwargs):
        """ See IDocFolder. """
        
        if not self.checkPermissionEditObjects():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        try:
            sortorder = abs(int(sortorder))
        except:
            sortorder = 100
        self.title = title
        self.description = description
        self.coverage = coverage
        self.keywords = keywords
        self.sortorder = sortorder
        self.locator = locator
        self._p_changed = 1
        self.recatalogDMObject(self)
        if REQUEST:
            REQUEST.RESPONSE.redirect('edit_html?dm_save=ok')

    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'index_rdf')
    def index_rdf(self, REQUEST=None, RESPONSE=None):
        """ See IDocFolder. """
        return self.syndicateSomething('%s/%s' % (self.absolute_url(), 'index_rdf'), self.getPublishedDMObjects())


    #################
    #   GETTERS     #
    #################

    #security.declarePrivate('getDocFolder')
    #def getDocFolder(self):
    #    """ returns the Document Folder """
    #    return self

    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'getDocFolderURL')
    def getDocFolderURL(self):
        """ See IDocFolder. """
        return self.absolute_url(0)

    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'getThematicAreas')
    def getThematicAreas(self):
        """ See IDocFolder. """
        return THEMATIC_AREA

    ########################
    #   General fuctions   #
    ########################

    #def indexThematicArea(self):
    #    return ''

    #security.declareProtected(view, 'getParentNode')
    #def getParentNode(self):
    #    """ returns parent """
    #    return string(aq_parent.absolute_url())

    security.declarePrivate('getPublishedDMObjects')
    def getPublishedDMObjects(self):
        """ See IDocFolder. """
        return self.utFilterObjsListByAttr(self.getDMObjects(), 'approved', 1)

    #security.declareProtected(PERMISSION_EDIT_DMOBJECTS, 'countPendingContent')
    #def countPendingContent(self):
    #    """ returns the number of unapproved objects """
    #    return len(self.getPendingContent())

    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'checkPermissionManageObects')
    def checkPermissionManageObjects(self,filter=''):
        """ See IDocFolder. """
        results = []
        select_all = 0
        delete_all = 0
        flag = 0        
        if filter and filter!='99':
            for folder in self.utFilterObjsListByAttr(self.getDMArticles(),'thematic_area', filter):
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
        
        for obj in self.utSortObjsListByAttr(self.getDMObjects(), 'sortorder', 0):
            del_permission = obj.checkPermissionDeleteObjects()
            if del_permission == 1 and flag == 0:
                flag = 1
                select_all = 1
                delete_all = 1
            edit_permission = obj.checkPermissionEditObject()
            if edit_permission == 1 and flag == 0:
                flag = 1
                select_all = 1
                delete_all = 1
            if (edit_permission and not obj.approved) or obj.approved:
                results.append((del_permission, edit_permission, obj))
        return (select_all, delete_all, results)


    security.declareProtected(PERMISSION_ADD_DOC_FOLDER, 'addDocFolder')
    addDocFolder = addDocFolder

    security.declareProtected(PERMISSION_ADD_DOC_FOLDER, 'manage_addDocFolder_html')
    manage_addDocFolder_html = manage_addDocFolder_html

    security.declareProtected(PERMISSION_ADD_DOC_URL, 'addDocURL')
    addDocURL = addDocURL

    security.declareProtected(PERMISSION_ADD_DOC_URL, 'manage_addDocURL_html')
    manage_addDocURL_html = manage_addDocURL_html

    security.declareProtected(PERMISSION_ADD_DOC_FILE, 'addDocFile')
    addDocFile = addDocFile

    security.declareProtected(PERMISSION_ADD_DOC_FILE, 'manage_addDocFile_html')
    manage_addDocFile_html = manage_addDocFile_html

    security.declareProtected(PERMISSION_ADD_DOC_ARTICLE, 'addDocArticle')
    addDocArticle = addDocArticle

    security.declareProtected(PERMISSION_ADD_DOC_ARTICLE, 'manage_addDocArticle_html')
    manage_addDocArticle_html = manage_addDocArticle_html

InitializeClass(DocFolder)

