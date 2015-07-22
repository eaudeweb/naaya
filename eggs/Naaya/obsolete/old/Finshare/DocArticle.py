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


#Zope imports
from OFS.Folder import Folder
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.Permissions import view_management_screens, view
from Products.ZCatalog.ZCatalog import ZCatalog
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from ZPublisher import BeforeTraverse
from OFS.Cache import Cacheable
from DocBase import DocBase
import Products
from DocComments import DocComments

#Products import
from Products.Finshare.DocFile import addDocFile, manage_addDocFile_html
from Products.Finshare.DocURL import addDocURL, manage_addDocURL_html
from Products.Finshare.Constants import *
from Products.Finshare.DocZip import DocZip


manage_addDocArticle_html = PageTemplateFile('zpt/DocArticle/article_manage_add', globals())
manage_addDocArticle_html.FormAction = 'addDocArticle'

def addDocArticle(self, id='', title='', description='', abstract = '', releasedate = '',
                  approved = '', sortorder='', keywords='', coverage='', author= '', source = '',
                  maintainer_email='', thematic_area='', source_type='', submit='', numberOfVotes='',
                  rank='', links='', REQUEST=None):
    """ add a new DocArticle object """
    id = self.utCleanupId(id)
    if not id: id = 'art' + self.utGenRandomId(6)
    try: sortorder = abs(int(sortorder))
    except: sortorder = 100
    #if self.checkPermissionPublishObjects():
    approved = 1
    #selse: approved = 0
    if not releasedate: releasedate = self.utGetTodayDate()
    else: releasedate = self.utConvertStringToDateTimeObj(releasedate)
    creationdate = self.utGetTodayDate()
    ownerinfo = self.getAuthenticatedUser()
    ob = DocArticle(id, title, description, abstract, creationdate, releasedate, ownerinfo, approved, sortorder, keywords, coverage, author, source, maintainer_email,thematic_area,source_type,numberOfVotes,rank, links)
    self._setObject(id, ob)
    self.notification.addArticle(id, title, thematic_area, description, author, creationdate)
    if REQUEST is not None:
        referer = self.utSplitToList(REQUEST['HTTP_REFERER'], '/')[-1]
        if referer == 'manage_addDocArticle_html' or referer.find('manage_addDocArticle_html') != -1:
            return self.manage_main(self, REQUEST, update_menu = 1)
        elif referer == 'article_add_html':
#            REQUEST.RESPONSE.redirect(self.REQUEST.HTTP_REFERER)
            REQUEST.RESPONSE.redirect(self.absolute_url(0) + '/note_html')
#            if submit != "Attach Document":
#                if REQUEST: REQUEST.RESPONSE.redirect(ob.id+'/edit_html?dm_save=ok') #index.html #edit_html?dm_save=ok
#            else:
#                if REQUEST: REQUEST.RESPONSE.redirect(ob.id+'/file_add_html')


class DocArticle(DocBase, Folder, Cacheable, DocZip, DocComments):
    """ DocArticle object """

    meta_type = METATYPE_DMARTICLE
    icon = 'misc_/Finshare/article'
    icon_marked = 'misc_/Finshare/article_marked'

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

    security.declareProtected(view_management_screens, 'all_meta_types')
    def all_meta_types(self):
        """ What can you put inside me? """
        local_meta_types = [{'name': METATYPE_DMFILE, 'action': 'manage_addDocFile_html', 'product': DOCMANAGER_PRODUCT_NAME},
                            {'name': METATYPE_DMURL, 'action': 'manage_addDocURL_html', 'product': DOCMANAGER_PRODUCT_NAME},]
        f = lambda x: x['name'] in ()
        for x in filter(f, Products.meta_types):
            local_meta_types.append(x)
        return local_meta_types


    def __init__(self, id, title, description, abstract, creationdate, releasedate, ownerinfo, approved, sortorder, keywords, coverage, author, source, maintainer_email,thematic_area, source_type, numberOfVotes, rank, links):
        """ constructor """
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
        self.thematic_area = thematic_area
        self.source_type = source_type
        self.vote_dict = {}
        self.numberOfVotes = 0
        self.ranking = 0
        self.links = links
        DocComments.__dict__['__init__'](self)


    ###########################
    #         ZMI FORMS       #
    ###########################

    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/DocArticle/article_manage_edit', globals())

    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', abstract='', releasedate = '', coverage='', keywords='', sortorder='',
            maintainer_email='', approved='', source = '', thematic_area='', links='', source_type='', REQUEST=None, **kwargs):
        """ updates DocArticle instance properties """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        try: sortorder = abs(int(sortorder))
        except: sortorder = 100
        if approved: approved = 1
        else: approved = 0
        self.title = title
        self.description = description
        self.abstract = abstract
        self.coverage = coverage
        self.keywords = keywords
        self.sortorder = sortorder
        self.maintainer_email = maintainer_email
        self.approved = approved
        self.thematic_area = thematic_area
        self.source_type = source_type
        self.links= links
        self._p_changed = 1
        self.recatalogDMObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')


    #####################
    #   SITE FORMS      #
    #####################

    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'index_html')
    index_html = PageTemplateFile('zpt/DocArticle/article_index', globals())

    security.declareProtected(PERMISSION_EDIT_DMOBJECTS, 'edit_html')
    edit_html = PageTemplateFile('zpt/DocArticle/article_edit', globals())

    security.declareProtected(PERMISSION_EDIT_DMOBJECTS, 'upload_html')
    upload_html = PageTemplateFile('zpt/DocArticle/article_upload', globals())

    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'content_html')
    content_html = PageTemplateFile('zpt/DocArticle/article_content', globals())

    security.declareProtected(PERMISSION_EDIT_DMOBJECTS, 'saveProperties')
    def saveProperties(self, title='', abstract='', description='', coverage='', keywords='', sortorder='', locator='', thematic_area='', source_type='', source='', submit='', author='', links='', REQUEST=None, **kwargs):
        """ updates DocArticle instance properties """
        if not self.checkPermissionEditObjects():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        try: sortorder = abs(int(sortorder))
        except: sortorder = 100
        self.title = title
        self.author = author
        self.source = source
        self.description = description
        self.abstract = abstract
        self.coverage = coverage
        self.keywords = keywords
        self.sortorder = sortorder
        self.locator = locator
        self.thematic_area = thematic_area
        self.source_type = source_type
        self.links = links
        self._p_changed = 1
        self.recatalogDMObject(self)
        if submit != "Attach Document":
            if REQUEST: REQUEST.RESPONSE.redirect('edit_html?dm_save=ok') #index.html #edit_html?dm_save=ok
        else:
            if REQUEST: REQUEST.RESPONSE.redirect('file_add_html')

    def deleteFile(self, REQUEST=None):
        """ delete a contained file """
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
        if REQUEST and len(err_list)==0: REQUEST.RESPONSE.redirect('edit_html')
        else: REQUEST.RESPONSE.redirect('edit_html?err_list=%s' % self.utJoinToString(err_list, ','))

    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'index_rdf')
    def index_rdf(self, REQUEST=None, RESPONSE=None):
        """ view rdf """
        return self.syndicateSomething('%s/%s' % (self.absolute_url(), 'index_rdf'), self.getPublishedDMObjects())


    #################
    #   GETTERS     #
    #################

    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'getDocArticle')
    def getDocArticle(self):
        """ returns the Document Article """
        return self
    
    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'getDocArticleURL')
    def getDocArticleURL(self):
        """ returns the Document Article URL """
        return self.absolute_url(0)



    ########################
    #   General fuctions   #
    ########################
    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'getThematicAreas')
    def getThematicAreas(self):
        return THEMATIC_AREA

    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'getParentNode')
    def getParentNode(self):
        """ returns parent """
        return string(aq_parent.absolute_url())

    security.declarePrivate('getPublishedDMObjects')
    def getPublishedDMObjects(self):
        """ returns approved objects """
        return self.utFilterObjsListByAttr(self.getDMObjects(), 'approved', 1)

    security.declareProtected(PERMISSION_EDIT_DMOBJECTS, 'countPendingContent')
    def countPendingContent(self):
        """ returns the number of unapproved objects """
        return len(self.getPendingContent())

    security.declareProtected(PERMISSION_EDIT_DMOBJECTS, 'checkPermissionManageObects')
    def checkPermissionManageObjects(self,filter=''):
        """ returns containing objects of the current article """
        results = []
        select_all = 0
        delete_all = 0
        flag = 0                        
        if filter:                    
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

        for obj in self.utSortObjsListByAttr(self.getDMObjects(), 'creationdate', 0):
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


#    security.declareProtected(PERMISSION_ADD_DOC_FOLDER, 'addDocFolder')
#    addDocFolder = addDocFolder
#    security.declareProtected(PERMISSION_ADD_DOC_FOLDER, 'manage_addDocFolder_html')
#    manage_addDocFolder_html = manage_addDocFolder_html

    security.declareProtected(PERMISSION_ADD_DOC_URL, 'addDocURL')
    addDocURL = addDocURL
    security.declareProtected(PERMISSION_ADD_DOC_URL, 'manage_addDocURL_html')
    manage_addDocURL_html = manage_addDocURL_html

    security.declareProtected(PERMISSION_ADD_DOC_FILE, 'addDocFile')
    addDocFile = addDocFile
    security.declareProtected(PERMISSION_ADD_DOC_FILE, 'manage_addDocFile_html')
    manage_addDocFile_html = manage_addDocFile_html


    def getThematicArea(self):
        return self.thematic_area

    def getThematicAreaText(self):
        return THEMATIC_AREA[int(self.thematic_area)]

    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'saveComment')
    def saveComment(self, doc_title='', doc_comment='', doc_email='', REQUEST=None):
        """ creates a comment """
        l_message = 'dm_save=err&doc_title=%s&doc_comment=%s&doc_email=%s' % (doc_title, doc_comment, doc_email)
        if self.utStrAllNotEmpty(doc_title, doc_comment, doc_email): # and (self.utIsEmailValid(doc_email) or len(doc_email)==0):
            self.createComment(doc_title, doc_comment, doc_email)
#            self.createHistory(HISTORY_COMMENT)
            l_message = 'dm_save=ok'
        if REQUEST: REQUEST.RESPONSE.redirect('index_html')

    def deleteComment(self,p_comment_uid,REQUEST=None):
        """ deletes a comment entry """
        self.delete_comment(p_comment_uid)        
        if REQUEST: REQUEST.RESPONSE.redirect('index_html')

     #expect vote as integer
    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'voteThisDocument')
    def voteThisDocument(self,rank=0):
        """allows voting"""
        self.vote_dict[self.REQUEST.AUTHENTICATED_USER.getUserName()] = rank
        self.numberOfVotes = self.getNumberOfVotes()
        self.ranking = self.getRanking()
        self.REQUEST.RESPONSE.redirect('index_html')


    def getNumberOfVotes(self):
        return len(self.vote_dict)

    def getRanking(self):
        sum = 0
        if len(self.vote_dict) > 0:
            for note in self.vote_dict.values():
                sum += int(note)
            return round(sum/len(self.vote_dict))
        else:
            return 'NaN'

    def alreadyVoted(self):
        if self.vote_dict.has_key(self.REQUEST.AUTHENTICATED_USER.getUserName()):
            return 1
        else:
            return 0

    def indexThematicArea(self):
        return THEMATIC_AREA[int(self.thematic_area)]

    def currentVote(self):
        if self.alreadyVoted():
            return self.vote_dict[self.REQUEST.AUTHENTICATED_USER.getUserName()]
        else:
            return -1


InitializeClass(DocArticle)

