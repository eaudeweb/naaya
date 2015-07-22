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
from os import mkdir, rename
from os.path import join

#Zope imports
from OFS.Folder import Folder
from Globals import InitializeClass, package_home
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from AccessControl.Role import RoleManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate import manage_addPageTemplate
from Products.ZCatalog.ZCatalog import ZCatalog
from ZPublisher import BeforeTraverse
import Products

#Product imports
from Products.Finshare.DocBase import DocBase
from Products.Finshare.DocFolder import DocFolder
from Products.Finshare.DocFile import DocFile
from Products.Finshare.DocURL import DocURL
from Products.Finshare.Constants import *
from Products.Finshare.DocContentTypes import DocContentTypes
from Products.Finshare.utils import batch_utils, utils
from Products.Finshare.DocZip import DocZip
from Products.Finshare.DocNotify import manage_addDocNotify
from Products.Finshare.DocAuth import manage_addAuthentication
from Products.Finshare.authentication.CookieCrumbler import CookieCrumbler

manage_addDocManagerForm = PageTemplateFile('zpt/DocManager/DocManager_manage_add', globals())

def manage_addDocManager (self, id, title, description, webmaster, REQUEST=None):
    """ add a new DocManager object """
    if id == '':
        id = utils().utGenRandomId()
    ownerinfo = REQUEST.AUTHENTICATED_USER.getUserName()
    ob = DocManager(id, title, description, webmaster, ownerinfo)
    ob._addRole(DOCMANAGER_ROLE_ADMINISTRATOR)
    ob._addRole(DOCMANAGER_ROLE_CONTRIBUTOR)
    self._setObject(id, ob)
    ob.loadDefaultContentTypes()
    ob.CreateCatalog()
    manage_addDocNotify(ob)
    manage_addAuthentication(ob)
    #ob.loadDefaultRoles()
    if REQUEST:
        return self.manage_main(self,REQUEST)


class DocManager(CookieCrumbler, Folder, DocBase, DocContentTypes, DocZip):
    """ DocManager object """

    meta_type = METATYPE_DMMANAGER
    icon = 'misc_/Finshare/DocManager'


    manage_options = (
        (Folder.manage_options[0],)
        +
        DocBase.manage_options
        +
        ({'label' : ITEM_MANAGE_OPTION_CONTENTTYPES, 'action' : 'manage_contenttypes_html'},)
        +
         (Folder.manage_options[5],
         Folder.manage_options[3],
         Folder.manage_options[6],)          
         )

    security = ClassSecurityInfo()

#    def all_meta_types(self):
#        """ What can you put inside me? """
#        local_meta_types = [{'name': METATYPE_DMFOLDER, 'action': 'manage_addDocFolder_html', 'product': DOCMANAGER_PRODUCT_NAME},]
#        f = lambda x: x['name'] in ('Script (Python)', 'Image', 'Page Template')
#        for x in filter(f, Products.meta_types):
#            local_meta_types.append(x)
#        return local_meta_types

    security = ClassSecurityInfo()

    security.declareProtected(PERMISSION_ADD_DOC_FOLDER, 'manage_addDocFolder_html')
    manage_addDocFolder_html = DocFolder.manage_addDocFolder_html
    security.declareProtected(PERMISSION_ADD_DOC_FOLDER, 'addDocFolder')
    addDocFolder = DocFolder.addDocFolder
    
    
    def __init__(self, id, title, description, webmaster, ownerinfo):
        """ constructor """
        self.id = id
        self.title = title
        self.description = description
        self.webmaster = webmaster
        self.ownerinfo = ownerinfo
        self.numberresultsperpage = 10
        #DocBase.__dict__['__init__'](self)
        DocContentTypes.__dict__['__init__'](self)

    def manage_afterAdd(self, item, container):
        """ after add event """
        if item is self:
            handle = self.meta_type + '/' + self.getId()
            nc = BeforeTraverse.NameCaller(self.getId())
            BeforeTraverse.registerBeforeTraverse(container, nc, handle)
        self.loadDefaultRoles()
        try:
            self.createRepository()
            style_css = open(join(DOCMANAGER_PRODUCT_PATH,'zpt','DocManager','DocManager_style.zpt'))
            content = style_css.read()
            style_css.close()
            manage_addPageTemplate(self, id=DOCMANAGER_CSS, title='', text=content)

            style_css = open(join(DOCMANAGER_PRODUCT_PATH,'zpt','DocManager','DocManager_template.zpt'))
            content = style_css.read()
            style_css.close()
            manage_addPageTemplate(self, id=DOCMANAGER_TEMPLATE, title='', text=content)

            Folder.inheritedAttribute('manage_afterAdd')(self, item, container)
        except:
            pass

    def manage_beforeDelete(self, item, container):
        """ This method is called, when the object is deleted. """
        if item is self:
            handle = self.meta_type + '/' + self.getId()
            BeforeTraverse.unregisterBeforeTraverse(container, handle)
        Folder.inheritedAttribute('manage_beforeDelete')(self, item, container)

    def createRepository(self):
        """ create a folder in ...\VAR """
        try: mkdir(DOCMANAGER_VAR_PATH)
        except: pass
        try: mkdir(join(DOCMANAGER_VAR_PATH, self.id))
        except: pass


    #################
    #   ZMI FORMS   #
    #################

    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/DocManager/DocManager_manage_edit', globals())

    security.declareProtected(view_management_screens, 'manage_contenttypes_html')
    manage_contenttypes_html = PageTemplateFile('zpt/DocManager/DocManager_manage_contenttypes', globals())
        
    security.declareProtected(view_management_screens, 'manage_options_style')
    manage_options_style = PageTemplateFile('zpt/DocManager/DocManager_style_zmi', globals())

    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', webmaster='', REQUEST=None, **kwargs):
        """ update DocManager instance properties """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        self.title = title
        self.description = description
        self.webmaster = webmaster
        self._p_changed = 1
        if REQUEST is not None:
            if REQUEST.has_key('destination'):
                REQUEST.RESPONSE.redirect(REQUEST['destination'] + '?save=ok')
            else:
                REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER + '?save=ok')


    #################
    #   SITE FORMS  #
    #################

    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'index_html')
    index_html = PageTemplateFile('zpt/DocManager/DocManager_index', globals())

    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'menu_html')
    menu_html = PageTemplateFile('zpt/DocManager/DocManager_menu', globals())

    security.declareProtected(view, 'breadcrumbtrail_html')
    breadcrumbtrail_html = PageTemplateFile('zpt/DocManager/DocManager_breadcrumbtrail', globals())

    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'port_left_current_rank_html')
    port_left_current_rank_html = PageTemplateFile('zpt/DocManager/DocManager_port_left_current_rank', globals())

    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'port_left_rank_html')
    port_left_rank_html = PageTemplateFile('zpt/DocManager/DocManager_port_left_rank', globals())

    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'port_left_search_html')
    port_left_search_html = PageTemplateFile('zpt/DocManager/DocManager_port_left_search', globals())

    security.declareProtected(view, 'port_left_links_html')
    port_left_links_html = PageTemplateFile('zpt/DocManager/DocManager_port_left_links', globals())

    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'navigation_top_html')
    navigation_top_html = PageTemplateFile('zpt/DocManager/DocManager_navigation_top', globals())


    security.declareProtected(view, 'getBreadCrumbTrail')
    def getBreadCrumbTrail(self, REQUEST):
        """ generates the bread crumb trail """
        root = self.utGetRoot()
        breadcrumbs = []
        vRoot = REQUEST.has_key('VirtualRootPhysicalPath')
        PARENTS = REQUEST.PARENTS[:]
        PARENTS.reverse()
        if vRoot:
             root = REQUEST.VirtualRootPhysicalPath
             PARENTS = PARENTS[len(root)-1:]
        PARENTS.reverse()
        for crumb in PARENTS:
            if crumb.meta_type == 'DocFile':
                continue
            if crumb.id == 'acl_users':
                continue
            breadcrumbs.append(crumb)
            if crumb.meta_type == 'Finshare':
                break
        breadcrumbs.reverse()
        return breadcrumbs

    security.declareProtected(view, 'isDocFile')
    def isDocFile(self, meta_type):
        """ """
        if meta_type == METATYPE_DMFILE: return 1
        return 0

    ###########################
    #   CONTENT TYPES TAB     #
    ###########################

    security.declareProtected(view_management_screens, 'loadDefaultContentTypes')
    def loadDefaultContentTypes(self):
        """ loads default Content Types """
        images_path = join(DOCMANAGER_PRODUCT_IMAGES_PATH, 'ContentTypes')
        for contenttype in DOCMANAGER_CONTENTETYPES:
            #create content type
            picture_content = self.utRead(join(images_path, contenttype[2]), 'rb')
            self.createContentType(contenttype[0], contenttype[1], picture_content)

    security.declareProtected(view_management_screens, 'manageAddContentType')
    def manageAddContentType(self, id='', title='', picture='', REQUEST=None):
        """ creates a Content Type """
        self.createContentType(id, title, picture)
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_contenttypes_html?save=ok')

    security.declareProtected(view_management_screens, 'manageUpdateContentType')
    def manageUpdateContentType(self, id='', title='', picture='', REQUEST=None):
        """ updates a Content Type """
        self.modifyContentType(id, title, picture)
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_contenttypes_html?save=ok')

    security.declareProtected(view_management_screens, 'manageDeleteContentTypes')
    def manageDeleteContentTypes(self, id=[], REQUEST=None):
        """ deletes a Content Type """
        self.deleteContentType(self.utConvertToList(id))
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_contenttypes_html?save=ok')


    #########################
    #   LANGUAGE FUNCTIONS  #
    #########################

#    def getLanguages(self):
#        """ returns the default languages list """
#        return LANGUAGES_LIST
#
#    def getPreselectedLanguage(self):
#        """ returns the preselected language"""
#        return PRESELECTED_LANGUAGE

    #################
    #   GETTERS     #
    #################

    def getDocManager(self):
        """ returns the Document Manager """
        return self

    security.declareProtected(view, 'getDocManager_template')
    def getDocManager_template(self):
        """ returns DocManager template """
        return self._getOb(DOCMANAGER_TEMPLATE)

    def getDocManagerUID(self):
        """ returns the Document Manager UID """
        return self.id

    def getDocManagerURL(self):
        """ returns the Document Manager URL """
        return self.absolute_url(0)    

    def getNumberOfResults(self):
        """ get the number of results """
        return self.numberresultsperpage

    def setNumberOfResults(self, results_number):
        """ set the number of results per page """
        self.numberresultsperpage = results_number

    def getStatuses(self):
        """ returns all statuses """
        return DOCMANAGER_STATUS

    def getDMMetaTypes(self, folder=0):
        """."""
        if folder==1: return METATYPE_OBJECTS
        else: return METATYPE_ALL

    def getTopDMFolders(self):
        """ returns top folders """
        return self.utSortObjsListByAttr(self.objectValues(METATYPE_DMFOLDER), 'sortorder', 0)


    #########################
    #   CATALOG FUNCTIONS   #
    #########################

    def getCatalogue(self):
        """ returns the catalog """
        if not hasattr(self, DOCMANAGER_CATALOG):
            return None
        return getattr(self, DOCMANAGER_CATALOG)

    def CreateCatalog(self):
        """ creates ZCatalog object """
        catalog = ZCatalog(DOCMANAGER_CATALOG, '')
        self._setObject(DOCMANAGER_CATALOG, catalog)
        catalog = self._getOb(DOCMANAGER_CATALOG)
        """ creates some indexes """
        available_indexes = catalog.indexes()
        available_metadata = catalog.schema()
        if not ('id' in available_indexes):
            catalog.addIndex('id', 'FieldIndex')
        if not ('id' in available_metadata):
            catalog.addColumn('id')

        if not ('meta_type' in available_indexes):
            catalog.addIndex('meta_type', 'FieldIndex')
        if not ('meta_type' in available_metadata):
            catalog.addColumn('meta_type')

        if not ('title' in available_indexes):
            catalog.addIndex('title', 'TextIndex')
        if not ('title' in available_metadata):
            catalog.addColumn('title')

        if not ('path' in available_indexes):
            catalog.addIndex('path', 'PathIndex')
        
        try:
            catalog.Vocabulary(id='Vocabulary', title='')
        except:
            pass

        if not ('description' in available_indexes):
            catalog.addIndex('description', 'TextIndex')
        
        if not ('abstract' in available_indexes):
            catalog.addIndex('abstract', 'TextIndex')
        
        if not ('author' in available_indexes):
            catalog.addIndex('author', 'TextIndex')
        
        if not ('keywords' in available_indexes):
            catalog.addIndex('keywords', 'FieldIndex')

        if not ('coverage' in available_indexes):
            catalog.addIndex('coverage', 'FieldIndex')
        
        catalog.addIndex('approved', 'TextIndex')

        if not ('indexThematicArea' in available_indexes):
            catalog.addIndex('indexThematicArea', 'FieldIndex')

        try:
            if not ('PrincipiaSearchSource' in available_indexes):
                catalog.addIndex('PrincipiaSearchSource', 'TextIndexNG2', extra={'default_encoding': 'utf-8', 'use_converters':1, 'autoexpand':1})
        except:
            pass

    def ClearCatalog(self):
        """ clear catalog """
        self.catalog.manage_catalogClear()

    def BuildCatalogPath(self, p_item):
        """ build a path for items to be added in catalog """
        return '/'.join(p_item.getPhysicalPath())

    def SearchCatalog(self, p_query, p_filter, file_query=0, thematic_query=[]):
        """ search Catalog defined indexes """
        __catalog = self.getCatalogue()

        results = []
        l_filter = {}
        l_filter['path'] = p_filter

        if p_query != '':
            criteria = l_filter.copy()
            criteria['title'] = p_query
            results.extend(__catalog(criteria))

        if p_query != '':
            criteria = l_filter.copy()
            criteria['description'] = p_query
            results.extend(__catalog(criteria))

        if p_query != '':
            criteria = l_filter.copy()
            criteria['keywords'] = p_query
            results.extend(__catalog(criteria))

        if p_query != '':
            criteria = l_filter.copy()
            criteria['abstract'] = p_query
            results.extend(__catalog(criteria))

        if p_query != '':
            criteria = l_filter.copy()
            criteria['author'] = p_query
            results.extend(__catalog(criteria))

        if thematic_query:
            if 'Tutti' in thematic_query:
                criteria = l_filter.copy()
                criteria['indexThematicArea'] = self.getThematicAreas()
                results.extend(__catalog(criteria))
            else:
                criteria = l_filter.copy()
                criteria['indexThematicArea'] = thematic_query
                results.extend(__catalog(criteria))

        if file_query:
            criteria = l_filter.copy()
            criteria['PrincipiaSearchSource'] = p_query
            results.extend(__catalog(criteria))

        #get objects
        results = map(__catalog.getobject,
                map(getattr, results, ('data_record_id_',)*len(results)))
        #eliminate duplicates
        return self.utElimintateDuplicates(results)

    def CatalogDMObject(self, p_ob):
        """ catalog objects """
        catalog = self.getCatalogue()
        catalog.catalog_object(p_ob, self.BuildCatalogPath(p_ob))

    def UncatalogDMObject(self, p_ob):
        """ uncatalog objects """
        catalog = self.getCatalogue()
        catalog.uncatalog_object(self.BuildCatalogPath(p_ob))

    def recatalogDMObject(self, p_ob):
        """ recatalog Issue objects """
        self.UncatalogDMObject(p_ob)
        self.CatalogDMObject(p_ob)


    ##########################################
    #   PERMISSIONS/ROLES/AUTHENTIFICATION   #
    ##########################################

    def __setRoles(self):
        """ sets the default roles """
        admin_permissions = []
        admin_permissions.extend(PERMISSIONS_ZOPE)
        admin_permissions.extend(PERMISSIONS_ADMINISTRATOR)

        self.manage_role(DOCMANAGER_ROLE_ADMINISTRATOR, admin_permissions)
        self.manage_role(DOCMANAGER_ROLE_CONTRIBUTOR, PERMISSIONS_CONTRIBUTOR)

    def loadDefaultRoles(self):
        """ sets the default roles """
        self.__setRoles()

    def getAuthenticatedUser(self):
        """ return the name of the authenticated user """
        return self.REQUEST.AUTHENTICATED_USER.getUserName()

    def getDMRoleAdministrator(self):
        """ returns the name of the resolver role """
        return DOCMANAGER_ROLE_ADMINISTRATOR

    def getDMRoleContributor(self):
        """ returns the name of the resolver role """
        return DOCMANAGER_ROLE_CONTRIBUTOR

    def isDMManagerAdministrator(self):
        """ test if current user is administrator """
        return self.REQUEST.AUTHENTICATED_USER.has_role(DOCMANAGER_ROLE_ADMINISTRATOR, self)

    def isDMManagerContributor(self):
        """ test if current user is contributor """
        return self.REQUEST.AUTHENTICATED_USER.has_role(DOCMANAGER_ROLE_CONTRIBUTOR, self)

    def getListUser(self):
        """ get the list of User objects """
        try: return self.__user.values()
        except: return None

    def getListUserAdministrator(self):
        """ get a list of User objects with Administrator role """
        try:
            users = self.__user.values()
            administrators = []
            for user in users:
                if self.getDMRoleAdministrator() in user.role:
                    administrators.append(user)
            return administrators
        except: return None

    def getListUserContributor(self):
        """ get a list of User objects with Contributor role """
        try:
            users = self.__user.values()
            contributors = []
            for user in users:
                if self.getDMRoleContributor() in user.role:
                    contributors.append(user)
            return contributors
        except: return None

    def getEmailTemplates(self):
        """ return the list of email templates """
        buf = []
        for obj in self.notification.objectValues():
            if not obj.id.endswith('_html'):
                buf.append(obj)
        return buf

    def getTemplate(self, id):
        try:
            return self.notification._getOb(id)
        except:
            return None

    def saveEmailTemplates(self, text_id='', html_id='', email_html='', 
                        email_text='', REQUEST=None, RESPONSE=None):
        """ save email templates """
        if REQUEST and REQUEST.has_key('TextButton'):
            obj = self.notification._getOb(text_id)
            obj.edit_template(obj.title, email_text)
            return RESPONSE.redirect('emailtemp_html?save=ok')
        if REQUEST and REQUEST.has_key('HtmlButton'):
            obj = self.notification._getOb(html_id)
            obj.edit_template(obj.title, email_html)
            return RESPONSE.redirect('emailtemp_html?save=ok')
        if REQUEST and REQUEST.has_key('CancelButton'):
            return RESPONSE.redirect('emailtemp_html')

    #############################################################################
    # GET THE MAINTAINERS EMAIL FROM CURRENT FOLDER UP TO THE DOCUMENT MANAGER  #
    #############################################################################

    def getMaintainersEmails(self, node):
        """ returns a list of emails for given folder until the Manager object """
        l_emails = []
        if node is self: return l_emails
        else:
            while 1:
                if node is self: break
                if node.maintainer_email != '' and node.maintainer_email not in l_emails:
                    l_emails.append(node.maintainer_email)
                node = node.getParentNode()
        return l_emails


    #################
    #    SITEMAP    #
    #################

    def __getSiteMap(self, root, showitems, expand, depth):
        """ returns the site map tree """
        l_tree = []
        if root is self:
            l_folders = root.getTopDMFolders()
        else:
            l_folders = root.getDMFolders()
        for l_folder in l_folders:
            if l_folder.hasDMFolders() or (l_folder.hasDMObjects() and showitems==1):
                if l_folder.absolute_url(1) in expand:
                    l_tree.append((l_folder, 0, depth))
                    if showitems:
                        for l_item in l_folder.getDMObjects():
                            l_tree.append((l_item, -1, depth+1))
                    l_tree.extend(self.__getSiteMap(l_folder, showitems, expand, depth+1))
                else:
                    l_tree.append((l_folder, 1, depth))
            else:
                l_tree.append((l_folder, -1, depth))
        return l_tree

    def getSiteMap(self, expand=[], root=None, showitems=0):
        """ returns the site map tree """
        if root is None:
            root = self
        return self.__getSiteMap(root, showitems, expand, 0)

    def processExpand(self, expand, node):
        """ expands node """
        return self.utJoinToList(self.addToList(expand, str(node)))

    def processCollapse(self, expand, node):
        """ collapses node """
        return self.utJoinToList(self.removeFromList(expand, str(node)))


    #####################
    #   TO SEE SEARCH   #
    #####################

    security.declareProtected(view, 'internalSearch')
    def internalSearch(self, query='', sort_expr='', order='', page_search_start='', thematic_query=[], file_query=0, where='all'):
        """ product search """
        try: page_search_start = int(page_search_start)
        except: page_search_start = 0
        if query or thematic_query:
            if where == 'all':
                path = ''
            else:
                path = where
            if type(query) == type(''):
                query = self.utStrEscapeForSearch(query)
            results = self.SearchCatalog(query, path, file_query, thematic_query)

            batch_obj = batch_utils(self.numberresultsperpage, len(results), page_search_start)
            if sort_expr!='' and order=='ascending':
                results = self.utSortObjsListByAttr(results, sort_expr, 0)   # sort ascending
            elif sort_expr!='' and order=='descending':
                results = self.utSortObjsListByAttr(results, sort_expr, 1)    #sort descending

            if len(results) > 0:
                paging_informations = batch_obj.butGetPagingInformations()
            else:
                paging_informations = (-1, 0, 0, -1, -1, 0, self.numberresultsperpage, [0])
            return (paging_informations, results[paging_informations[0]:paging_informations[1]])
        else:
            return []

    def getThematicAreas(self):
        return THEMATIC_AREA

    DocBase_manage_add = PageTemplateFile('zpt/DocBase/DocBase_macro_add', globals())
    DocBase_manage_edit = PageTemplateFile('zpt/DocBase/DocBase_macro_edit', globals())

    security.declareProtected(PERMISSION_EDIT_DMOBJECTS, 'DocManager_template_add')
    DocManager_template_add = PageTemplateFile('zpt/DocManager/DocManager_template_add', globals())

    security.declareProtected(view, 'DocManager_template_edit')
    DocManager_template_edit = PageTemplateFile('zpt/DocManager/DocManager_template_edit', globals())

    security.declareProtected(view, 'note_html')
    note_html = PageTemplateFile('zpt/DocManager/DocManager_note', globals())

    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'productmap_html')
    productmap_html = PageTemplateFile('zpt/DocManager/DocManager_map', globals())

    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'search_html')
    search_html = PageTemplateFile('zpt/DocManager/DocManager_search', globals())

    security.declareProtected(PERMISSION_CHANGE_PROPERTIES, 'properties_html')
    properties_html = PageTemplateFile('zpt/DocManager/DocManager_properties', globals())

    security.declareProtected(PERMISSION_CHANGE_PROPERTIES, 'emailtemp_html')
    emailtemp_html = PageTemplateFile('zpt/DocManager/DocManager_email_templates', globals())

    security.declareProtected(PERMISSION_CHANGE_PROPERTIES, 'emailedit_html')
    emailedit_html = PageTemplateFile('zpt/DocManager/DocManager_edit_email', globals())

    #user forms
    security.declareProtected(view, 'login_html')
    login_html = PageTemplateFile('zpt/DocAuth/login', globals())

    security.declareProtected(view, 'logout_html')
    logout_html = PageTemplateFile('zpt/DocAuth/logout', globals())

    security.declareProtected(view, 'forgotpassword_html')
    forgotpassword_html = PageTemplateFile('zpt/DocAuth/forgot_passwd', globals())

    security.declareProtected(view, 'registeruser_html')
    registeruser_html = PageTemplateFile('zpt/DocAuth/register_user', globals())

InitializeClass(DocManager)