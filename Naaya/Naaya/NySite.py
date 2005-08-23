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
# The Original Code is EEAWebUpdate version 0.1
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by CMG and Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

#Python imports
from os.path import join
from urllib import quote

#Zope imports
from OFS.Folder import Folder, manage_addFolder
from OFS.Image import manage_addImage
from OFS.DTMLMethod import addDTMLMethod
from OFS.DTMLDocument import addDTMLDocument
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.Permissions import view_management_screens, view
from ZPublisher import BeforeTraverse
from Products.SiteErrorLog.SiteErrorLog import manage_addErrorLog
import Products

#Product imports
from constants import *
from Products.NaayaBase.constants import *
from Products.NaayaCore.constants import *
from Products.NaayaContent import *
from Products.NaayaContent.constants import *
from Products.NaayaCore.PropertiesTool.PropertiesTool import manage_addPropertiesTool
from Products.NaayaCore.CatalogTool.CatalogTool import manage_addCatalogTool
from Products.NaayaCore.TranslationsTool.TranslationsTool import manage_addTranslationsTool
from Products.NaayaCore.DynamicPropertiesTool.DynamicPropertiesTool import manage_addDynamicPropertiesTool
from Products.NaayaCore.SyndicationTool.SyndicationTool import manage_addSyndicationTool
from Products.NaayaCore.EmailTool.EmailTool import manage_addEmailTool
from Products.NaayaCore.AuthenticationTool.AuthenticationTool import manage_addAuthenticationTool
from Products.NaayaCore.AuthenticationTool.CookieCrumbler import CookieCrumbler
from Products.NaayaCore.PortletsTool.PortletsTool import manage_addPortletsTool
from Products.NaayaCore.PortletsTool.managers.portlets_manager import portlets_manager
from Products.NaayaCore.FormsTool.FormsTool import manage_addFormsTool
from Products.NaayaCore.LayoutTool.LayoutTool import manage_addLayoutTool
from Products.NaayaCore.ImportExportTool.ImportExportTool import manage_addImportExportTool
from Products.NaayaBase.NyBase import NyBase
from Products.NaayaBase.NyEpozToolbox import NyEpozToolbox
from Products.NaayaBase.NyImport import NyImport
from Products.NaayaBase.NyPermissions import NyPermissions
from Products.NaayaCore.managers.utils import utils, list_utils, batch_utils, file_utils
from Products.NaayaCore.managers.catalog_tool import catalog_tool
from Products.NaayaCore.managers.urlgrab_tool import urlgrab_tool
from Products.NaayaCore.managers.search_tool import search_tool
from Products.NaayaCore.managers.session_manager import session_manager
from Products.NaayaCore.PropertiesTool.managers.contenttypes_tool import contenttypes_tool
from Products.NaayaCore.PropertiesTool.managers.events_tool import events_tool
from Products.Localizer.Localizer import manage_addLocalizer
from Products.Localizer.MessageCatalog import manage_addMessageCatalog
from Products.Localizer.LocalPropertyManager import LocalPropertyManager, LocalProperty
from managers.skel_parser import skel_parser
from NyFolder import NyFolder, addNyFolder

#constructor
manage_addNySite_html = PageTemplateFile('zpt/site_manage_add', globals())
def manage_addNySite(self, id='', title='', lang=None, REQUEST=None):
    """ """
    ut = utils()
    id = ut.utCleanupId(id)
    if not id: id = PREFIX_SITE + ut.utGenRandomId(6)
    portal_uid = '%s_%s' % (PREFIX_SITE, ut.utGenerateUID())
    self._setObject(id, NySite(id, portal_uid, title, lang))
    self._getOb(id).loadDefaultData()
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class NySite(CookieCrumbler, LocalPropertyManager, Folder,
    NyBase, NyEpozToolbox, NyPermissions, NyImport,
    utils, list_utils, file_utils,
    catalog_tool,
    search_tool,
    contenttypes_tool,
    events_tool,
    session_manager,
    portlets_manager):
    """ """

    meta_type = METATYPE_NYSITE
    icon = 'misc_/Naaya/Site.gif'

    manage_options = (
        Folder.manage_options
        +
        (
            {'label': 'Control Panel', 'action': 'manage_controlpanel_html'},
        )
        +
        NyImport.manage_options
    )

    security = ClassSecurityInfo()

    title = LocalProperty('title')
    site_title = LocalProperty('site_title')
    site_subtitle = LocalProperty('site_subtitle')
    description = LocalProperty('description')
    publisher = LocalProperty('publisher')
    contributor = LocalProperty('contributor')
    creator = LocalProperty('creator')
    rights = LocalProperty('rights')

    def __init__(self, id, portal_uid, title, lang):
        """ """
        self.id = id
        self.__portal_uid = portal_uid
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('site_title', lang, title)
        self._setLocalPropValue('site_subtitle', lang, u'')
        self._setLocalPropValue('description', lang, u'')
        self._setLocalPropValue('publisher', lang, u'')
        self._setLocalPropValue('contributor', lang, u'')
        self._setLocalPropValue('creator', lang, u'')
        self._setLocalPropValue('rights', lang, u'')
        self.adt_meta_types = []
        self.search_age = 1
        self.numberresultsperpage = 10
        self.number_latest_uploads = DEFAULT_NUMBERLATESTUPLOADS
        self.number_announcements = DEFAULT_NUMBERANNOUNCEMENTS
        self.notify_on_errors = 1
        self.http_proxy = ''
        self.repository_url = ''
        self.mail_server_name = DEFAULT_MAILSERVERNAME
        self.mail_server_port = DEFAULT_MAILSERVERPORT
        self.administrator_email = ''
        self.portal_url = ''
        self.maintopics = []
        self.keywords_glossary = None
        self.coverage_glossary = None
        self.__pluggable_installed_content = {}
        contenttypes_tool.__dict__['__init__'](self)
        events_tool.__dict__['__init__'](self)
        CookieCrumbler.__dict__['__init__'](self)
        catalog_tool.__dict__['__init__'](self)
        search_tool.__dict__['__init__'](self)
        portlets_manager.__dict__['__init__'](self)

    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self):
        """ """
        self.manage_addProperty('management_page_charset', 'utf-8', 'string')
        languages = [DEFAULT_PORTAL_LANGUAGE_CODE]
        manage_addTranslationsTool(self, languages)
        manage_addLocalizer(self, TITLE_LOCALIZER, languages)
        manage_addCatalogTool(self, languages)
        manage_addPropertiesTool(self)
        manage_addDynamicPropertiesTool(self)
        manage_addAuthenticationTool(self)
        manage_addSyndicationTool(self)
        manage_addEmailTool(self)
        manage_addPortletsTool(self)
        manage_addFormsTool(self)
        manage_addLayoutTool(self)
        manage_addImportExportTool(self)
        manage_addErrorLog(self)
        self.loadSkeleton(join(NAAYA_PRODUCT_PATH, 'skel'))

    security.declarePrivate('loadSkeleton')
    def loadSkeleton(self, skel_path):
        """ """
        #load site skeleton
        skel_handler, error = skel_parser().parse(self.futRead(join(skel_path, 'skel.xml'), 'r'))
        if skel_handler is not None:
            properties_tool = self.getPropertiesTool()
            formstool_ob = self.getFormsTool()
            layouttool_ob = self.getLayoutTool()
            syndicationtool_ob = self.getSyndicationTool()
            portletstool_ob = self.getPortletsTool()
            emailtool_ob = self.getEmailTool()
            authenticationtool_ob = self.getAuthenticationTool()
            #load forms
            if skel_handler.root.forms is not None:
                for form in skel_handler.root.forms.forms:
                    content = self.futRead(join(skel_path, 'forms', '%s.zpt' % form.id), 'r')
                    form_ob = formstool_ob._getOb(form.id, None)
                    if form_ob is None:
                        formstool_ob.manage_addTemplate(id=form.id, title=form.title, file='')
                        form_ob = formstool_ob._getOb(form.id, None)
                    form_ob.pt_edit(text=content, content_type='')
            #load skins
            if skel_handler.root.layout is not None:
                for skin in skel_handler.root.layout.skins:
                    layouttool_ob.manage_addSkin(id=skin.id, title=skin.title)
                    skin_ob = layouttool_ob._getOb(skin.id)
                    for template in skin.templates:
                        content = self.futRead(join(skel_path, 'layout', skin.id, '%s.zpt' % template.id), 'r')
                        skin_ob.manage_addTemplate(id=template.id, title=template.title, file='')
                        skin_ob._getOb(template.id).pt_edit(text=content, content_type='')
                    for scheme in skin.schemes:
                        skin_ob.manage_addScheme(id=scheme.id, title=scheme.title)
                        scheme_ob = skin_ob._getOb(scheme.id)
                        for style in scheme.styles:
                            content = self.futRead(join(skel_path, 'layout', skin.id, scheme.id, '%s.css' % style.id), 'r')
                            scheme_ob.manage_addStyle(id=style.id, title=style.title, file=content)
                        for image in scheme.images:
                            content = self.futRead(join(skel_path, 'layout', skin.id, scheme.id, image.id), 'rb')
                            scheme_ob.manage_addImage(id=image.id, file='', title=image.title)
                            image_ob = scheme_ob._getOb(image.id)
                            image_ob.update_data(data=content)
                            image_ob._p_changed=1
                layouttool_ob.manageLayout(skel_handler.root.layout.default_skin_id, skel_handler.root.layout.default_scheme_id)
                #load logos
                content = self.futRead(join(skel_path, 'layout', 'logo.gif'), 'rb')
                image_ob = layouttool_ob._getOb('logo.gif', None)
                if image_ob is None:
                    layouttool_ob.manage_addImage(id='logo.gif', file='', title='Site logo')
                    image_ob = layouttool_ob._getOb('logo.gif')
                image_ob.update_data(data=content)
                image_ob._p_changed=1
                content = self.futRead(join(skel_path, 'layout', 'logobis.gif'), 'rb')
                image_ob = layouttool_ob._getOb('logobis.gif', None)
                if image_ob is None:
                    layouttool_ob.manage_addImage(id='logobis.gif', file='', title='Site secondary logo')
                    image_ob = layouttool_ob._getOb('logobis.gif')
                image_ob.update_data(data=content)
                image_ob._p_changed=1
            #load pluggable content types
            if skel_handler.root.pluggablecontenttypes is not None:
                for pluggablecontenttype in skel_handler.root.pluggablecontenttypes.pluggablecontenttypes:
                    self.manage_install_pluggableitem(meta_type=pluggablecontenttype.meta_type)
            #load syndication
            if skel_handler.root.syndication is not None:
                for namespace in skel_handler.root.syndication.namespaces:
                    syndicationtool_ob.createNamespaceItem(namespace.id, namespace.prefix, namespace.value)
                for channeltype in skel_handler.root.syndication.channeltypes:
                    syndicationtool_ob.add_channeltype_item(channeltype.id, channeltype.title)
                for channel in skel_handler.root.syndication.localchannels:
                    language = self.utEmptyToNone(channel.language)
                    type = self.utEmptyToNone(channel.type)
                    syndicationtool_ob.manage_addLocalChannel(channel.id, channel.title, channel.description, language, type, channel.objmetatype.split(','), channel.numberofitems, 1)
                for channel in skel_handler.root.syndication.remotechannels:
                    syndicationtool_ob.manage_addRemoteChannel(channel.id, channel.title, channel.url, channel.numbershownitems, 1)
            #load portlets and links lists
            if skel_handler.root.portlets is not None:
                for portlet in skel_handler.root.portlets.portlets:
                    content = self.futRead(join(skel_path, 'portlets', '%s.zpt' % portlet.id), 'r')
                    self.create_portlet_special(portlet.id, portlet.title, content)
                for linkslist in skel_handler.root.portlets.linkslists:
                    linkslist_ob = portletstool_ob._getOb(linkslist.id, None)
                    if linkslist_ob is None:
                        portletstool_ob.manage_addLinksList(linkslist.id, linkslist.title, linkslist.portlet)
                        linkslist_ob = portletstool_ob._getOb(linkslist.id)
                    else:
                        linkslist_ob.manage_delete_links(linkslist_ob.get_links_collection().keys())
                    for link in linkslist.links:
                        try: relative = abs(int(link.relative))
                        except: relative = 0
                        try: order = abs(int(link.order))
                        except: order = 0
                        linkslist_ob.add_link_item(link.id, link.title, link.description, link.url, relative, link.permission, order)
                portletstool_ob.manage_left_portlets(skel_handler.root.portlets.left.split(','))
                portletstool_ob.manage_center_portlets(skel_handler.root.portlets.center.split(','))
            #load properties
            if skel_handler.root.properties is not None:
                for language in skel_handler.root.properties.languages:
                    properties_tool.manage_addLanguage(language.code)
                for eventtype in skel_handler.root.properties.eventtypes:
                    self.createEventType(eventtype.id, eventtype.title)
                for contenttype in skel_handler.root.properties.contenttypes:
                    content = self.futRead(join(skel_path, 'contenttypes', contenttype.picture), 'rb')
                    self.createContentType(contenttype.id, contenttype.title, content)
            #load email templates
            if skel_handler.root.emails is not None:
                for emailtemplate in skel_handler.root.emails.emailtemplates:
                    content = self.futRead(join(skel_path, 'emails', '%s.txt' % emailtemplate.id), 'r')
                    emailtool_ob.manage_addEmailTemplate(emailtemplate.id, emailtemplate.title, content)
            #load security permissions and roles
            if skel_handler.root.security is not None:
                for permission in skel_handler.root.security.permissions:
                    authenticationtool_ob.addPermission(permission.name, permission.description, permission.permissions)
                for role in skel_handler.root.security.roles:
                    authenticationtool_ob.addRole(role.name, role.permissions)
            #set subobjects for folders
            self.getPropertiesTool().manageSubobjects(subobjects=None, ny_subobjects=self.get_meta_types(1))
            #load default content
            if skel_handler.root.content is not None:
                for folder in skel_handler.root.content.folders:
                    self.loadFolderData(self, folder)
                properties_tool.manageMainTopics(skel_handler.root.content.maintopics.split(','))
            #other stuff
            if skel_handler.root.others is not None:
                if skel_handler.root.others.robots is not None:
                    content = self.futRead(join(skel_path, 'others', 'robots.txt'), 'r')
                    file_ob = self._getOb('robots.txt', None)
                    if file_ob is None:
                        self.manage_addFile(id='robots.txt', file='', title='')
                        file_ob = self._getOb('robots.txt')
                    file_ob.update_data(data=content)
                    file_ob._p_changed=1
                if skel_handler.root.others.favicon is not None:
                    content = self.futRead(join(skel_path, 'others', 'favicon.ico'), 'rb')
                    image_ob = self._getOb('favicon.ico', None)
                    if image_ob is None:
                        self.manage_addImage(id='favicon.ico', file='', title='')
                        image_ob = self._getOb('favicon.ico')
                    image_ob.update_data(data=content)
                    image_ob._p_changed=1
                if skel_handler.root.others.images is not None:
                    self.manage_addFolder(ID_IMAGESFOLDER, 'Images')

    security.declarePrivate('loadFolderData')
    def loadFolderData(self, node, folder):
        #create default folders structure
        if folder.meta_types == '': meta_types = ''
        else: meta_types = folder.meta_types.split(',')
        folder_ob = node._getOb(folder.id, None)
        if folder_ob is None:
            addNyFolder(node, folder.id, folder.title, folder.description, folder.coverage, folder.keywords,
                folder.sortorder, folder.publicinterface, folder.maintainer_email, meta_types)
            folder_ob = node._getOb(folder.id)
        folder_ob.modifyPublicInterface(folder.index_html)
        for item in folder.items:
            if item.type == METATYPE_NYDOCUMENT:
                folder_ob.addNyDocument(id=item.id, title=item.title, description=item.description,
                    coverage=item.coverage, keywords=item.keywords, sortorder=item.sortorder,
                    body=item.body)
        for item in folder.folders:
            self.loadFolderData(folder_ob, item)

    #overwrite handlers
    def manage_beforeDelete(self, item, container):
        """ This method is called, when the object is deleted. """
        if item is self:
            handle = self.meta_type + '/' + self.getId()
            BeforeTraverse.unregisterBeforeTraverse(container, handle)
        Folder.inheritedAttribute('manage_beforeDelete')(self, item, container)

    def updatePath(self):
        """ """
        handle = self.meta_type + '/' + self.getId()
        nc = BeforeTraverse.NameCaller(self.getId())
        BeforeTraverse.registerBeforeTraverse(self, nc, handle)

    def manage_afterAdd(self, item, container):
        """ This method is called, whenever _setObject in ObjectManager gets called. """
        if item is self:
            handle = self.meta_type + '/' + self.getId()
            container = item
            #container = self.utGetROOT()
            nc = BeforeTraverse.NameCaller(self.getId())
            BeforeTraverse.registerBeforeTraverse(container, nc, handle)
        Folder.inheritedAttribute('manage_afterAdd')(self, item, container)

    #api
    def get_site_uid(self): return self.__portal_uid

    def get_constant(self, c): return eval(c)

    def get_meta_types(self, folder=0):
        #returns a list with objects metatypes
        if folder==1: return [METATYPE_FOLDER] + self.get_pluggable_installed_meta_types()
        else: return self.get_pluggable_installed_meta_types()

    def getProductsMetaTypes(self):
        #returns a list with all meta types
        return [x['name'] for x in self.filtered_meta_types()]

    #objects getters
    def getSite(self): return self
    def getPropertiesTool(self): return self._getOb(ID_PROPERTIESTOOL)
    def getPortletsTool(self): return self._getOb(ID_PORTLETSTOOL)
    def getAuthenticationTool(self): return self._getOb(ID_AUTHENTICATIONTOOL)
    def getDynamicPropertiesTool(self): return self._getOb(ID_DYNAMICPROPERTIESTOOL)
    def getCatalogTool(self): return self._getOb(ID_CATALOGTOOL)
    def getLayoutTool(self): return self._getOb(ID_LAYOUTTOOL)
    def getSyndicationTool(self): return self._getOb(ID_SYNDICATIONTOOL)
    def getEmailTool(self): return self._getOb(ID_EMAILTOOL)
    def getFormsTool(self): return self._getOb(ID_FORMSTOOL)
    def getLocalizer(self): return self._getOb('Localizer')
    def getPortalTranslations(self): return self._getOb(ID_TRANSLATIONSTOOL)
    def getImportExportTool(self): return self._getOb(ID_IMPORTEXPORTTOOL)
    def getImagesFolder(self): return self._getOb(ID_IMAGESFOLDER)

    #objects absolute/relative path getters
    def getSitePath(self, p=0): return self.absolute_url(p)
    def getPropertiesToolPath(self, p=0): return self._getOb(ID_PROPERTIESTOOL).absolute_url(p)
    def getPortletsToolPath(self, p=0): return self._getOb(ID_PORTLETSTOOL).absolute_url(p)
    def getAuthenticationToolPath(self, p=0): return self._getOb(ID_AUTHENTICATIONTOOL).absolute_url(p)
    def getDynamicPropertiesToolPath(self, p=0): return self._getOb(ID_DYNAMICPROPERTIESTOOL).absolute_url(p)
    def getCatalogToolPath(self, p=0): return self._getOb(ID_CATALOGTOOL).absolute_url(p)
    def getLayoutToolPath(self, p=0): return self._getOb(ID_LAYOUTTOOL).absolute_url(p)
    def getSyndicationToolPath(self, p=0): return self._getOb(ID_SYNDICATIONTOOL).absolute_url(p)
    def getEmailToolPath(self, p=0): return self._getOb(ID_EMAILTOOL).absolute_url(p)
    def getFormsToolPath(self, p=0): return self._getOb(ID_FORMSTOOL).absolute_url(p)
    def getImportExportToolPath(self, p=0): return self._getOb(ID_IMPORTEXPORTTOOL).absolute_url(p)
    def getFolderByPath(self, p_folderpath): return self.unrestrictedTraverse(p_folderpath, None)

    def getFolderMainParent(self, p_folder):
        #returns the main parent of the given folder
        l_parent = p_folder
        while l_parent.getParentNode().meta_type != self.meta_type:
            l_parent = l_parent.getParentNode()
        return l_parent

    def getAllParents(self, p_folder):
        #returns all parents of a folder, without aquisition
        l_parent = p_folder
        l_result = [l_parent]
        while l_parent.getParentNode().meta_type != self.meta_type:
            l_parent = l_parent.getParentNode()
            l_result.append(l_parent)
        return l_result

    def get_containers(self):
        #this method returns all container type that can be used in an export operation
        return self.objectValues(METATYPE_FOLDER)

    #api
    def getMainFolders(self):
        #returns a list with all folders objects at the first level
        #that are approved and sorted by 'order' property
        return self.utSortObjsListByAttr([x for x in self.objectValues(METATYPE_FOLDER) if x.approved==1], 'sortorder', 0)

    def getMainTopics(self):
        #returns the list of main topic folders
        #sorted by 'order' property
        return self.utSortObjsListByAttr(filter(lambda x: x is not None, map(lambda f, x: f(x, None), (self._getOb,)*len(self.maintopics), self.maintopics)), 'sortorder', 0)

    def getLatestUploads(self, howmany=None):
        #returns a list with the latest uploaded objects in the site
        #which are approved
        #the number of objects can be set by modifing the property 'number_latest_uploads'
        if howmany is None:
            howmany = self.number_latest_uploads
        return self.getCatalogedObjects(meta_type=self.get_meta_types(), approved=1, howmany=howmany, path=['/'.join(x.getPhysicalPath()) for x in self.getMainTopics()])

    def getFoldersWithPendingItems(self):
        #returns a list with all folders that contains pending(draft) objects
        d = {}
        for x in self.getCatalogedObjects(METATYPE_FOLDER):
            c = len(x.getPendingContent())
            if c > 0: #this folder has pending content
                p = self.getFolderMainParent(x)
                url = p.absolute_url(1)
                if not d.has_key(url): d[url] = [p, []]
                d[url][1].append((x, c))
        return d

    def getCheckedOutObjects(self):
        #return a list with all checked out objects in the portal (open versions)
        return self.getCatalogCheckedOutObjects()

    def getBreadCrumbTrail(self, REQUEST):
        #generates the bread crumb trail
        root = self.utGetROOT()
        breadcrumbs = []
        vRoot = REQUEST.has_key('VirtualRootPhysicalPath')
        PARENTS = REQUEST.PARENTS[:]
        PARENTS.reverse()
        if vRoot:
             root = REQUEST.VirtualRootPhysicalPath
             PARENTS = PARENTS[len(root)-1:]
        PARENTS.reverse()
        for crumb in PARENTS:
            breadcrumbs.append(crumb)
            if crumb.meta_type == self.meta_type:
                break
        breadcrumbs.reverse()
        return breadcrumbs

    def grabFromUrl(self, p_url):
        #it gets the content from the given url
        try:
            l_urlgrab = urlgrab_tool()
            l_http_proxy = self.http_proxy
            if l_http_proxy != '':
                l_urlgrab.proxies['http'] = l_http_proxy
            webPage = l_urlgrab.open(p_url)
            data = webPage.read()
            ctype = webPage.headers['Content-Type']
            return (data, ctype)
        except:
            return (None, 'text/x-unknown-content-type')

    def getMaintainersEmails(self, node):
        #returns a list of emails for given folder until the site object
        l_emails = []
        if node is self: return l_emails
        else:
            while 1:
                if node == self: break
                if node.maintainer_email != '' and node.maintainer_email not in l_emails:
                    l_emails.append(node.maintainer_email)
                node = node.getParentNode()
        return l_emails

    def processDynamicProperties(self, meta_type, REQUEST=None, keywords={}):
        """ """
        if REQUEST:
            for l_prop in self.getDynamicPropertiesTool().getDynamicProperties(meta_type):
                keywords[l_prop.id] = REQUEST.get(l_prop.id, '')
        return keywords

    def getItemsAge(self): return self.search_age
    def setItemsAge(self, age): self.search_age = age
    def getNumberOfResults(self): return self.numberresultsperpage
    def setNumberOfResults(self, results_number): self.numberresultsperpage = results_number

    #layer over the Localizer and MessageCatalog
    #the scope is to centralize the list of available languages
    def gl_get_all_languages(self): return self.get_all_languages()
    def gl_get_languages(self): return self.get_languages()
    def gl_get_languages_mapping(self): return self.get_languages_mapping()
    def gl_get_default_language(self): return self.get_default_language()
    def gl_get_selected_language(self): return self.get_selected_language()
    def gl_get_languages_map(self):
        lang, langs, r = self.gl_get_selected_language(), self.get_available_languages(), []
        for x in langs:
            r.append({'id': x, 'title': self.gl_get_language_name(x), 'selected': x==lang})
        return r
    def gl_get_language_name(self, lang): return self.get_language_name(lang)
    def gl_add_languages(self, ob):
        for l in self.gl_get_languages_mapping():
            ob.add_language(l['code'])
            if l['default']: ob.manage_changeDefaultLang(l['code'])
    def gl_changeLanguage(self, old_lang, REQUEST=None):
        """ """
        self.getLocalizer().changeLanguage(old_lang)
        if REQUEST: REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    #layer over NyEpozToolbox
    def getUploadedImages(self): return self.getImagesFolder().objectValues(['Image'])

    security.declareProtected(view, 'process_image_upload')
    def process_image_upload(self, file='', REQUEST=None):
        """ """
        if file != '':
            if hasattr(file, 'filename'):
                if file.filename != '':
                    manage_addImage(self.getImagesFolder(), '', file)
        if REQUEST:
            REQUEST.RESPONSE.redirect('%s/toolbox_html' % self.absolute_url())

    security.declareProtected(view, 'process_file_upload')
    def process_file_upload(self, file='', REQUEST=None):
        """ """
        if file != '':
            if hasattr(file, 'filename'):
                if file.filename != '':
                    manage_addFile(self.getImagesFolder(), '', file)
        if REQUEST:
            REQUEST.RESPONSE.redirect('%s/toolbox_html' % self.absolute_url())

    security.declareProtected(view, 'process_delete')
    def process_delete(self, ids=[], REQUEST=None):
        """ """
        try: self.getImagesFolder().manage_delObjects(self.utConvertToList(ids))
        except: pass
        if REQUEST:
            REQUEST.RESPONSE.redirect('%s/toolbox_html' % self.absolute_url())

    #site map stuff
    def getSiteMap(self, expand=[], root=None, showitems=0):
        #returns a list of objects with additional information
        #in order to draw the site map
        if root is None: root = self
        return self.__getSiteMap(root, showitems, expand, 0)

    def getSiteMapTrail(self, expand, tree):
        #given a list with all tree nodes, returns a string with all relatives urls
        if expand == 'all': return ','.join([node[0].absolute_url(1) for node in tree])
        else: return expand

    def __getSiteMap(self, root, showitems, expand, depth):
        #site map core
        l_tree = []
        if root is self: l_folders = root.getMainFolders()
        else: l_folders = root.getPublishedFolders()
        for l_folder in l_folders:
            if (len(l_folder.objectValues(METATYPE_FOLDER)) > 0) or ((len(l_folder.getObjects()) > 0) and showitems==1):
                if l_folder.absolute_url(1) in expand or 'all' in expand:
                    l_tree.append((l_folder, 0, depth))
                    if showitems:
                        for l_item in l_folder.getPublishedObjects():
                            l_tree.append((l_item, -1, depth+1))
                    l_tree.extend(self.__getSiteMap(l_folder, showitems, expand, depth+1))
                else:
                    l_tree.append((l_folder, 1, depth))
            else:
                l_tree.append((l_folder, -1, depth))
        return l_tree

    def processExpand(self, expand, node):
        #process a click in the site map tree on an expand button
        return self.joinToList(self.addToList(expand, str(node)))

    def processCollapse(self, expand, node):
        #process a click in the site map tree on a collapse button
        return self.joinToList(self.removeFromList(expand, str(node)))

    #site actions
    security.declareProtected(view, 'processFeedbackForm')
    def processFeedbackForm(self, username='', email='', comments='', REQUEST=None):
        """ """
        self.sendFeedbackEmail(self.administrator_email, username, email, comments)
        if REQUEST:
            REQUEST.RESPONSE.redirect('%s/note_html' % self.absolute_url())

    security.declareProtected(view, 'processChangeCredentials')
    def processChangeCredentials(self, password='', confirm='', firstname='', lastname='', email='', REQUEST=None):
        """ """
        auth_user = REQUEST.AUTHENTICATED_USER.getUserName()
        user = self.getAuthenticationTool().getUser(auth_user)
        err = []
        err = self.getAuthenticationTool().manage_changeUser(auth_user, password, confirm, user.roles, user.domains, firstname, lastname, email)
        if err is not None:
            if REQUEST:
                self.setSessionErrors(err)
                self.setUserSession(auth_user, user.roles, user.domains, firstname, lastname, email, password)
                return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)
        if REQUEST: return REQUEST.RESPONSE.redirect('changecredentials_html')

    security.declareProtected(view, 'processRequestRoleForm')
    def processRequestRoleForm(self, username='', password='', confirm='', firstname='', lastname='', email='', organisation='', location='', comments='', REQUEST=None):
        """ """
        location_path = 'unspecified'
        location_title = 'unspecified'
        if location == '':
            location_path = ''
            location_title = self.site_title
            location_maintainer_email = self.administrator_email
        else:
            obj = self.getFolderByPath(location)
            if obj is not None:
                location_path = obj.absolute_url(1)
                location_title = obj.title
                location_maintainer_email = self.getMaintainersEmails(obj)
        #create an account without role
        errors = []
        err = self.getAuthenticationTool().manage_addUser(username, password, confirm, [], [], firstname, lastname, email, strict=1)
        if err:
            if REQUEST:
                self.setSessionErrors(err)
                self.setUserSession(username, '', '', firstname, lastname, email, '', organisation, comments, location)
                return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)
        if not err:
            self.sendRequestRoleEmail(location_maintainer_email, firstname + ' ' + lastname, email, organisation, username, location_path, location_title, comments)
        if REQUEST:
            REQUEST.RESPONSE.redirect('%s/note_html' % self.absolute_url())

    security.declareProtected(view, 'processNotifyOnErrors')
    def processNotifyOnErrors(self, error_type, error_value, REQUEST):
        """ """
        if self.notify_on_errors:
            error_url = REQUEST.get('URL', '')
            error_ip = self.utGetRefererIp(REQUEST)
            error_user = REQUEST.AUTHENTICATED_USER.getUserName()
            error_time = self.utGetTodayDate()
            if self.portal_url != '': mail_from = 'error@%s' % self.portal_url
            else: mail_from = 'error@%s' % REQUEST.SERVER_NAME
            self.notifyOnErrorsEmail(self.administrator_email, mail_from, error_url, error_ip, error_type, error_value, error_user, error_time)

    security.declareProtected(view, 'externalSearch')
    def externalSearch(self, servers=[], query='', sort_expr='', order='', page_search_start=''):
        """ """
        list_results = []
        try:    page_search_start = int(page_search_start)
        except: page_search_start = 0
        if query.strip() != '':
            query = self.utStrEscapeForSearch(query)
            servers = self.utConvertToList(servers)
            results = self.external_ew_search(servers, query)
            if len(results) > 1:
                filter(list_results.extend, results)
            else:
                list_results = results[0]
        else:
            list_results = []
        batch_obj = batch_utils(self.numberresultsperpage, len(list_results), page_search_start)
        if sort_expr!='' and order=='ascending':
            self.utSortListOfDictionariesByKey(list_results, sort_expr, 0)   # sort ascending
        elif sort_expr!='' and order=='descending':
            self.utSortListOfDictionariesByKey(list_results, sort_expr, 1)    #sort descending
        if len(list_results) > 0:
            paging_informations = batch_obj.butGetPagingInformations()
        else:
            paging_informations = (-1, 0, 0, -1, -1, 0, self.numberresultsperpage, [0])
        return (paging_informations, list_results[paging_informations[0]:paging_informations[1]])

    security.declarePublic('external_search')
    def external_search(self, search_param=''):
        """ """
        curr_lang = self.gl_get_selected_language()
        #transtab = string.maketrans('/','_')
        #unused='\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf'
        list_res=[]
        results = self.searchCatalog(search_param, '', curr_lang)
        for result in results:
            if hasattr(result,'description') and result.description!='':
                #result_desc=unicode(string.translate(result.getDescription(curr_lang),transtab,unused), 'latin-1').encode('utf-8')
                result_desc=result.description.encode('utf-8')
            else:
                result_desc='No description available'
            if hasattr(result,'title') and result.title!='':
                #result_title=unicode(string.translate(result.getTitle(curr_lang),transtab,unused), 'latin-1').encode('utf-8')
                result_title=result.title.encode('utf-8')
            else:
                result_title='Untitled'
            try:
                time=unicode(str(result.bobobase_modification_time()), 'latin-1').encode('utf-8')
                if result.absolute_url(0) not in list_res:
                    list_res.append({'url':result.absolute_url(0), 'description':result_desc[:100], 'title':result_title,'icon':self.REQUEST.SERVER_URL+'/'+result.icon,'meta_type':result.meta_type, 'time':time})
            except:
                pass
        return list_res

    security.declareProtected(view, 'internalSearch')
    def internalSearch(self, query='', sort_expr='', order='', page_search_start='', where='all'):
        """ """
        lang = self.gl_get_selected_language()
        try: page_search_start = int(page_search_start)
        except: page_search_start = 0
        if query:
            if where == 'all':
                path = ''
            else:
                path = where
            if type(query) == type(''):
                query = self.utStrEscapeForSearch(query)
            results = self.searchCatalog(query, path, lang)
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

    #paging stuff
    def process_querystring(self, p_querystring):
        #eliminates empty values and the 'start' key
        if p_querystring:
            l_qsparts = p_querystring.split('&')
            for i in range(len(l_qsparts)):
                if l_qsparts[i] != '':
                    l_qsparts_tuple = l_qsparts[i].split('=', 1)
                    l_key = self.utUnquote(l_qsparts_tuple[0])
                    l_value = self.utUnquote(l_qsparts_tuple[1])
                    if l_value == '' or l_key in ['start', 'skey', 'rkey']:
                        l_qsparts[i] = ''
            return '&'.join(filter(None, l_qsparts))
        else:
            return ''

    def page_something(self, p_result, p_start, p_perpage=10):
        #Returns results with paging information
        l_paging_information = (0, 0, 0, -1, -1, 0, p_perpage, [0])
        try: p_start = abs(int(p_start))
        except: p_start = 0
        if len(p_result) > 0:
            l_paging_information = batch_utils(p_perpage, len(p_result), p_start).butGetPagingInformations()
        if len(p_result) > 0:
            return (l_paging_information, p_result[l_paging_information[0]:l_paging_information[1]])
        else:
            return (l_paging_information, [])

    #rdf files
    security.declareProtected(view, 'latestuploads_rdf')
    def latestuploads_rdf(self):
        """ """
        return self.getSyndicationTool().syndicateSomething(self.absolute_url(), self.getLatestUploads())

    security.declareProtected(view, 'localchannels_rdf')
    def localchannels_rdf(self):
        """ """
        syndication_tool = self.getSyndicationTool()
        return syndication_tool.syndicateSomething(self.absolute_url(), syndication_tool.get_local_channels())

    #administration actions
    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_metadata')
    def admin_metadata(self, site_title='', site_subtitle='', description='', publisher='',
        contributor='', creator='', rights='', lang=None, REQUEST=None):
        """ """
        if lang is None: lang = self.gl_get_selected_language()
        self._setLocalPropValue('title', lang, site_title)
        self._setLocalPropValue('site_title', lang, site_title)
        self._setLocalPropValue('site_subtitle', lang, site_subtitle)
        self._setLocalPropValue('description', lang, description)
        self._setLocalPropValue('publisher', lang, publisher)
        self._setLocalPropValue('contributor', lang, contributor)
        self._setLocalPropValue('creator', lang, creator)
        self._setLocalPropValue('rights', lang, rights)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_metadata_html?lang=%s' % (self.absolute_url(), lang))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_logos')
    def admin_logos(self, logo='', logobis='', REQUEST=None):
        """ """
        if logo != '':
            if hasattr(logo, 'filename'):
                if logo.filename != '':
                    content = logo.read()
                    if content != '':
                        image_ob = self.getLayoutTool()._getOb('logo.gif')
                        image_ob.update_data(data=content)
                        image_ob._p_changed=1
        if logobis != '':
            if hasattr(logobis, 'filename'):
                if logobis.filename != '':
                    content = logobis.read()
                    if content != '':
                        image_ob = self.getLayoutTool()._getOb('logobis.gif')
                        image_ob.update_data(data=content)
                        image_ob._p_changed=1
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_logos_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_properties')
    def admin_properties(self, number_latest_uploads='', number_announcements='', http_proxy='',
        repository_url='', keywords_glossary='', coverage_glossary='', portal_url='', REQUEST=None):
        """ """
        try: number_latest_uploads = int(number_latest_uploads)
        except: number_latest_uploads = self.number_latest_uploads
        try: number_announcements = int(number_announcements)
        except: number_announcements = self.number_announcements
        if keywords_glossary == '': keywords_glossary = None
        if coverage_glossary == '': coverage_glossary = None
        self.number_latest_uploads = number_latest_uploads
        self.number_announcements = number_announcements
        self.http_proxy = http_proxy
        self.repository_url = repository_url
        self.keywords_glossary = keywords_glossary
        self.coverage_glossary = coverage_glossary
        self.portal_url = portal_url
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_properties_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_layout')
    def admin_layout(self, theMasterList='', theSlaveList='', REQUEST=None):
        """ """
        self.getLayoutTool().manageLayout(theMasterList, theSlaveList)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_layout_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_deleteusers')
    def admin_deleteusers(self, names=[], REQUEST=None):
        """ """
        self.getAuthenticationTool().manage_delUsers(names)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_users_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_adduser')
    def admin_adduser(self, firstname='', lastname='', email='', name='', password='',
        confirm='', REQUEST=None):
        """ """
        msg = err = ''
        try:
            self.getAuthenticationTool().manage_addUser(name, password, confirm, [], [], firstname,
                lastname, email)
        except Exception, error:
            err = error
        else:
            msg = MESSAGE_SAVEDCHANGES % self.utGetTodayDate()
        if REQUEST:
            if err != '':
                self.setSessionErrors([err])
                self.setUserSession(name, [], [], firstname, lastname, email, '')
                REQUEST.RESPONSE.redirect('%s/admin_adduser_html' % self.absolute_url())
            if msg != '':
                self.setSessionInfo([msg])
                REQUEST.RESPONSE.redirect('%s/admin_users_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_edituser')
    def admin_edituser(self, firstname='', lastname='', email='', name='', password='',
        confirm='', REQUEST=None):
        """ """
        msg = err = ''
        try:
            self.getAuthenticationTool().manage_changeUser(name, password, confirm, [], [], firstname,
                lastname, email)
        except Exception, error:
            err = error
        else:
            msg = MESSAGE_SAVEDCHANGES % self.utGetTodayDate()
        if REQUEST:
            if err != '':
                self.setSessionErrors([err])
                self.setUserSession(name, [], [], firstname, lastname, email, '')
            if msg != '':
                self.setSessionInfo([msg])
            REQUEST.RESPONSE.redirect('%s/admin_edituser_html?name=%s' % (self.absolute_url(), name))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_revokeroles')
    def admin_revokeroles(self, roles=[], REQUEST=None):
        """ """
        self.getAuthenticationTool().manage_revokeUsersRoles(roles)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_roles_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addroles')
    def admin_addroles(self, name='', roles=[], loc='allsite', location='', REQUEST=None):
        """ """
        msg = err = ''
        try:
            self.getAuthenticationTool().manage_addUsersRoles(name, roles, location)
        except Exception, error:
            err = error
        else:
            msg = MESSAGE_SAVEDCHANGES % self.utGetTodayDate()
        if REQUEST:
            if err != '': self.setSessionErrors([err])
            if msg != '': self.setSessionInfo([msg])
            REQUEST.RESPONSE.redirect('%s/admin_roles_html' % self.absolute_url())

    security.declareProtected(PERMISSION_TRANSLATE_PAGES, 'admin_editmessage')
    def admin_editmessage(self, message, language, translation, skey, rkey, query, REQUEST=None):
        """ """
        ob = self.getPortalTranslations()
        message_encoded = message
        message = ob.message_decode(message_encoded)
        ob.message_edit(message, language, translation, '')
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_messages_html?msg=%s&skey=%s&rkey=%s&query=%s' % (self.absolute_url(), quote(message_encoded), skey, rkey, query))

    security.declareProtected(PERMISSION_TRANSLATE_PAGES, 'admin_exportmessages')
    def admin_exportmessages(self, x, REQUEST=None, RESPONSE=None):
        """ """
        return self.getPortalTranslations().manage_export(x, REQUEST, RESPONSE)

    security.declareProtected(PERMISSION_TRANSLATE_PAGES, 'admin_importmessages')
    def admin_importmessages(self, lang, file, REQUEST=None):
        """ """
        self.getPortalTranslations().manage_import(lang, file)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_translations_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_deletelinkslist')
    def admin_deletelinkslist(self, ids=[], REQUEST=None):
        """ """
        self.getPortletsTool().manage_delObjects(self.utConvertToList(ids))
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_linkslists_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addlinkslist')
    def admin_addlinkslist(self, id='', title='', portlet='', REQUEST=None):
        """ """
        self.getPortletsTool().manage_addLinksList(id, title, portlet)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_linkslists_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_editlinkslist')
    def admin_editlinkslist(self, id='', title='', REQUEST=None):
        """ """
        ob = self.getPortletsTool().getLinksListById(id)
        if ob is not None:
            ob.manageProperties(title)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_linkslist_html?id=%s' % (self.absolute_url(), id))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_deletelinks')
    def admin_deletelinks(self, id='', ids=[], REQUEST=None):
        """ """
        ob = self.getPortletsTool().getLinksListById(id)
        if ob is not None:
            ob.manage_delete_links(self.utConvertToList(ids))
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_linkslist_html?id=%s' % (self.absolute_url(), id))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addlink')
    def admin_addlink(self, id='', title='', description='', url='', relative='', permission='', order='', REQUEST=None):
        """ """
        ob = self.getPortletsTool().getLinksListById(id)
        if ob is not None:
            ob.manage_add_link_item('', title, description, url, relative, permission, order)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_linkslist_html?id=%s' % (self.absolute_url(), id))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_editlink')
    def admin_editlink(self, id='', item='', title='', description='', url='', relative='', permission='', order='', REQUEST=None):
        """ """
        ob = self.getPortletsTool().getLinksListById(id)
        if ob is not None:
            ob.manage_update_link_item(item, title, description, url, relative, permission, order)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_linkslist_html?id=%s' % (self.absolute_url(), id))

    security.declareProtected(PERMISSION_ADMINISTRATE, 'admin_discardversion')
    def admin_discardversion(self, url=None, REQUEST=None):
        """ """
        ob = self.utGetObject(url)
        if ob is not None:
            ob.discardVersion()
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_versioncontrol_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addmaintopics')
    def admin_addmaintopics(self, title='', REQUEST=None):
        """ """
        id = PREFIX_FOLDER + self.utGenRandomId(6)
        addNyFolder(self, id=id, title=title)
        self.maintopics.append(id)
        self._p_changed = 1
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_maintopics_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_ordermaintopics')
    def admin_ordermaintopics(self, positions=None, REQUEST=None):
        """ """
        if positions is not None:
            sortorder = 0
            for x in positions.split('|'):
                try:
                    ob = self._getOb(x)
                    ob.sortorder = sortorder
                    ob._p_changed = 1
                    sortorder = sortorder + 1
                except:
                    pass
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_maintopics_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_deletemaintopics')
    def admin_deletemaintopics(self, ids=None, REQUEST=None):
        """ """
        if ids is not None: ids = self.utConvertToList(ids)
        else: ids = []
        for id in ids:
            try: self.maintopics.remove(id)
            except: pass
        self._p_changed = 1
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_maintopics_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addremotechannel')
    def admin_addremotechannel(self, title='', url='', numbershownitems='', portlet='', REQUEST=None):
        """ """
        self.getSyndicationTool().manage_addRemoteChannel('', title, url, numbershownitems, portlet)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_remotechannels_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_editremotechannel')
    def admin_editremotechannel(self, id='', title='', url='', numbershownitems='', REQUEST=None):
        """ """
        self.getSyndicationTool().get_channel(id).manageProperties(title, url, numbershownitems)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_remotechannels_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_updateremotechannel')
    def admin_updateremotechannel(self, id='', REQUEST=None):
        """ """
        res = self.getSyndicationTool().get_channel(id).updateChannel()
        if REQUEST:
            if res == '':
                self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            else:
                self.setSessionErrors([res])
            REQUEST.RESPONSE.redirect('%s/admin_remotechannels_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_deleteremotechannel')
    def admin_deleteremotechannel(self, ids=[], REQUEST=None):
        """ """
        self.getSyndicationTool().manage_delObjects(self.utConvertToList(ids))
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_remotechannels_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addlocalchannel')
    def admin_addlocalchannel(self, title='', description='', language=None, type=None, objmetatype=[], numberofitems='', portlet='', REQUEST=None):
        """ """
        self.getSyndicationTool().manage_addLocalChannel('', title, description, language, type, objmetatype, numberofitems, portlet)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_localchannels_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_editlocalchannel')
    def admin_editlocalchannel(self, id='', title='', description='', language=None, type=None, objmetatype=[], numberofitems='', portlet='', REQUEST=None):
        """ """
        self.getSyndicationTool().get_channel(id).manageProperties(title, description, language, type, objmetatype, numberofitems, portlet)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_localchannels_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_deletelocalchannel')
    def admin_deletelocalchannel(self, ids=[], REQUEST=None):
        """ """
        self.getSyndicationTool().manage_delObjects(self.utConvertToList(ids))
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_localchannels_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_leftportlets')
    def admin_leftportlets(self, portlets=[], REQUEST=None):
        """ """
        self.set_left_portlets_ids(self.utConvertToList(portlets))
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_leftportlets_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_frontportlets')
    def admin_frontportlets(self, portlets=[], REQUEST=None):
        """ """
        self.set_center_portlets_ids(self.utConvertToList(portlets))
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_frontportlets_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_rightportlets')
    def admin_rightportlets(self, folder='', portlets=[], REQUEST=None):
        """ """
        self.set_right_portlets_locations(folder, self.utConvertToList(portlets))
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_rightportlets_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_deleterightportlets')
    def admin_deleterightportlets(self, portlets=[], REQUEST=None):
        """ """
        for pair in self.utConvertToList(portlets):
            location, id = pair.split('||')
            self.delete_right_portlets_locations(location, id)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_rightportlets_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_deleteremotechportlet')
    def admin_deleteremotechportlet(self, ids=[], REQUEST=None):
        """ """
        self.getPortletsTool().manage_delObjects(self.utConvertToList(ids))
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_remotechportlets_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addremotechportlet')
    def admin_addremotechportlet(self, id='', REQUEST=None):
        """ """
        ob = self.getSyndicationTool().get_channel(id)
        if ob is not None: self.create_portlet_for_remotechannel(ob)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_remotechportlets_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_deletelocalchportlet')
    def admin_deletelocalchportlet(self, ids=[], REQUEST=None):
        """ """
        self.getPortletsTool().manage_delObjects(self.utConvertToList(ids))
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_localchportlets_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addlocalchportlet')
    def admin_addlocalchportlet(self, id='', REQUEST=None):
        """ """
        ob = self.getSyndicationTool().get_channel(id)
        if ob is not None: self.create_portlet_for_localchannel(ob)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_localchportlets_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_deletefolderportlet')
    def admin_deletefolderportlet(self, ids=[], REQUEST=None):
        """ """
        self.getPortletsTool().manage_delObjects(self.utConvertToList(ids))
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_folderportlets_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addfolderportlet')
    def admin_addfolderportlet(self, folder='', REQUEST=None):
        """ """
        if folder != '':
            ob = self.getFolderByPath(folder)
            if ob is not None:
                if not self.exists_portlet_for_object(ob):
                    self.create_portlet_for_folder(ob)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_folderportlets_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_deletelinksportlet')
    def admin_deletelinksportlet(self, ids=[], REQUEST=None):
        """ """
        self.getPortletsTool().manage_delObjects(self.utConvertToList(ids))
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_linksportlets_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addlinksportlet')
    def admin_addlinksportlet(self, id='', REQUEST=None):
        """ """
        ob = self.getPortletsTool().getLinksListById(id)
        if ob is not None: self.create_portlet_for_linkslist(ob)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_linksportlets_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addhtmlportlet')
    def admin_addhtmlportlet(self, REQUEST=None):
        """ """
        id = PREFIX_PORTLET + self.utGenRandomId(6)
        self.getPortletsTool().addHTMLPortlet(id=id, title='New portlet')
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_htmlportlets_html?id=%s' % (self.absolute_url(), id))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_edithtmlportlet')
    def admin_edithtmlportlet(self, id='', title='', body='', lang=None, REQUEST=None):
        """ """
        ob = self.getPortletsTool().getPortletById(id)
        if ob is not None:
            ob.manage_properties(title, body, lang)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_htmlportlets_html?id=%s' % (self.absolute_url(), id))


    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_deletehtmlportlet')
    def admin_deletehtmlportlet(self, ids=[], REQUEST=None):
        """ """
        self.getPortletsTool().manage_delObjects(self.utConvertToList(ids))
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_htmlportlets_html' % self.absolute_url())

    #administration pages
    security.declareProtected(PERMISSION_ADMINISTRATE, 'admin_centre_html')
    def admin_centre_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_centre')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_metadata_html')
    def admin_metadata_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_metadata')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_logos_html')
    def admin_logos_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_logos')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_properties_html')
    def admin_properties_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_properties')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_layout_html')
    def admin_layout_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_layout')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_users_html')
    def admin_users_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_users')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_adduser_html')
    def admin_adduser_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_adduser')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_edituser_html')
    def admin_edituser_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_edituser')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_roles_html')
    def admin_roles_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_roles')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_sources_html')
    def admin_sources_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_sources')

    security.declareProtected(PERMISSION_TRANSLATE_PAGES, 'admin_translations_html')
    def admin_translations_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_translations')

    security.declareProtected(PERMISSION_TRANSLATE_PAGES, 'admin_messages_html')
    def admin_messages_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_messages')

    security.declareProtected(PERMISSION_TRANSLATE_PAGES, 'admin_importexport_html')
    def admin_importexport_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_importexport')

    security.declareProtected(PERMISSION_TRANSLATE_PAGES, 'admin_linkslists_html')
    def admin_linkslists_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_linkslists')

    security.declareProtected(PERMISSION_TRANSLATE_PAGES, 'admin_linkslist_html')
    def admin_linkslist_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_linkslist')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_basket_html')
    def admin_basket_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_basket')

    security.declareProtected(PERMISSION_VALIDATE_OBJECTS, 'admin_validation_html')
    def admin_validation_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_validation')

    security.declareProtected(PERMISSION_VALIDATE_OBJECTS, 'admin_validation_tree_html')
    def admin_validation_tree_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_validation_tree')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_versioncontrol_html')
    def admin_versioncontrol_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_versioncontrol')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_maintopics_html')
    def admin_maintopics_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_maintopics')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_localchannels_html')
    def admin_localchannels_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_localchannels')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_remotechannels_html')
    def admin_remotechannels_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_remotechannels')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_leftportlets_html')
    def admin_leftportlets_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_leftportlets')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_frontportlets_html')
    def admin_frontportlets_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_frontportlets')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_rightportlets_html')
    def admin_rightportlets_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_rightportlets')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_specialportlets_html')
    def admin_specialportlets_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_specialportlets')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_remotechportlets_html')
    def admin_remotechportlets_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_remotechportlets')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_localchportlets_html')
    def admin_localchportlets_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_localchportlets')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_folderportlets_html')
    def admin_folderportlets_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_folderportlets')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_linksportlets_html')
    def admin_linksportlets_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_linksportlets')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_htmlportlets_html')
    def admin_htmlportlets_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_htmlportlets')

    #others
    def get_localch_noportlet(self):
        return [x for x in self.getSyndicationTool().get_local_channels() if not self.exists_portlet_for_object(x)]

    def get_remotech_noportlet(self):
        return [x for x in self.getSyndicationTool().get_remote_channels() if not x.exists_portlet_for_object(x)]

    def get_linkslists_noportlet(self):
        return [x for x in self.getPortletsTool().getLinksLists() if not x.exists_portlet_for_object(x)]

    def getRemoteServers(self):
        #get remote servers
        return self.get_repository_sites(self.repository_url)

    def checkPermissionForLink(self, name, context):
        #checks the given group of permissions in the given context
        if name != '': return self.getAuthenticationTool().checkGroupPermission(name, context)
        else: return 1

    def updateRemoteChannels(self, uid):
        """ used by cron tools to update the remote channels. The key provided is the uid of the site"""
        if uid == self.get_site_uid():
            for l_channel in self.getRemoteChannels():
                l_channel.updateChannel()
            return "Update Remote Channels ended successfully on site %s" % self.absolute_url()

    def list_glossaries(self):
        #this method *must* be overwritten
        return []

    def get_keywords_glossary(self):
        try: return self._getOb(self.keywords_glossary)
        except: return None

    def get_coverage_glossary(self):
        try: return self._getOb(self.coverage_glossary)
        except: return None

    def import_object(self, node, object):
        #import an object
        zope_obj = node._getOb(object.id, None)
        if zope_obj is None:
            print 'create zope_ob'
        for obj in object.objects:
            print obj.id, obj.meta_type
            self.import_object(zope_obj, obj)

    #sending emails
    def sendFeedbackEmail(self, p_to, p_username, p_email, p_comments):
        #sends a feedback email
        email_template = self.getEmailTool()._getOb('email_feedback')
        l_subject = email_template.title
        l_content = email_template.body
        l_content = l_content.replace('@@USERNAME@@', p_username)
        l_content = l_content.replace('@@COMMENTS@@', p_comments)
        l_content = l_content.replace('@@TIMEOFPOST@@', str(self.utGetTodayDate()))
        self.getEmailTool().sendEmail(l_content, p_to, p_email, l_subject)

    def notifyOnErrorsEmail(self, p_to, p_from, p_error_url, p_error_ip, p_error_type, p_error_value, p_error_user, p_error_time):
        #notify on errors email
        email_template = self.getEmailTool()._getOb('email_notifyonerrors')
        l_subject = email_template.title
        l_content = email_template.body
        l_content = l_content.replace('@@URL@@', p_error_url)
        l_content = l_content.replace('@@ERRORTYPE@@', p_error_type)
        l_content = l_content.replace('@@ERRORVALUE@@', p_error_value)
        l_content = l_content.replace('@@IPADDRESS@@', p_error_ip)
        l_content = l_content.replace('@@USER@@', p_error_user)
        l_content = l_content.replace('@@TIMEOFREQUEST@@', str(p_error_time))
        self.getEmailTool().sendEmail(l_content, p_to, p_from, l_subject)

    def sendRequestRoleEmail(self, p_to, p_name, p_email, p_organisation, p_username, p_location_path, p_location_title, p_comments):
        #sends a request role email
        email_template = self.getEmailTool()._getOb('email_requestrole')
        l_subject = email_template.title
        l_content = email_template.body
        l_content = l_content.replace('@@NAME@@', p_name)
        l_content = l_content.replace('@@EMAIL@@', p_email)
        l_content = l_content.replace('@@ORGANISATION@@', p_organisation)
        l_content = l_content.replace('@@USERNAME@@', p_username)
        l_content = l_content.replace('@@LOCATIONPATH@@', p_location_path)
        if p_location_path:
            l_content = l_content.replace('@@LOCATION@@', "the %s folder (%s/%s)" % (p_location_title, self.portal_url, p_location_path))
        else:
            l_content = l_content.replace('@@LOCATION@@', 'entire portal')
        l_content = l_content.replace('@@COMMENTS@@', p_comments)
        l_content = l_content.replace('@@PORTAL_URL@@', self.portal_url)
        l_content = l_content.replace('@@PORTAL_TITLE@@', self.site_title)
        l_content = l_content.replace('@@TIMEOFPOST@@', str(self.utGetTodayDate()))
        self.getEmailTool().sendEmail(l_content, p_to, p_email, l_subject)

    def notifyMaintainerEmail(self, p_to, p_from, p_itemid, p_container_path, p_container_basketpath):
        #notify folder maintainer when a new upload is done
        email_template = self.getEmailTool()._getOb('email_notifyonupload')
        l_subject = email_template.title
        l_content = email_template.body
        l_content = l_content.replace('@@ITEMID@@', p_itemid)
        l_content = l_content.replace('@@CONTAINERPATH@@', p_container_path)
        l_content = l_content.replace('@@UPLOADTIME@@', str(self.utGetTodayDate()))
        l_content = l_content.replace('@@CONTAINERBASKETPATH@@', p_container_basketpath)
        self.getEmailTool().sendEmail(l_content, p_to, p_from, l_subject)

    #pluggable content
    def get_pluggable_content(self):
        #information about the available types
        return get_pluggable_content()

    def get_pluggable_metatypes(self):
        return get_pluggable_content().keys()

    def get_pluggable_metatypes_validation(self):
        #returns a list with all meta_types for validation process
        return [x['meta_type'] for x in get_pluggable_content().values() if x['validation'] == 1]

    def get_pluggable_item(self, meta_type):
        return get_pluggable_content().get(meta_type, None)

    def get_pluggable_installed_meta_types(self):
        return self.__pluggable_installed_content.keys()

    def is_pluggable_item_installed(self, meta_type):
        return self.__pluggable_installed_content.has_key(meta_type)

    security.declareProtected(view_management_screens, 'manage_install_pluggableitem')
    def manage_install_pluggableitem(self, meta_type=None, REQUEST=None):
        """ """
        if meta_type is not None:
            pitem = self.get_pluggable_item(meta_type)
            #load pluggable item's data
            formstool_ob = self.getFormsTool()
            for frm in pitem['forms']:
                content = self.futRead(join(NAAYACONTENT_PRODUCT_PATH, pitem['module'], 'zpt', '%s.zpt' % frm), 'r')
                formstool_ob.manage_addTemplate(id=frm, title='', file='')
                formstool_ob._getOb(frm).pt_edit(text=content, content_type='text/html')
            #remember that this meta_type was installed
            self.__pluggable_installed_content[meta_type] = 1
            self._p_changed = 1
        if REQUEST: REQUEST.RESPONSE.redirect('%s/manage_controlpanel_html' % self.absolute_url())

    security.declareProtected(view_management_screens, 'manage_uninstall_pluggableitem')
    def manage_uninstall_pluggableitem(self, meta_type=None, REQUEST=None):
        """ """
        if meta_type is not None:
            pitem = self.get_pluggable_item(meta_type)
            #remove pluggable item's data
            try: self.getFormsTool().manage_delObjects(copy(pitem['forms']))
            except: pass
            #remember that this meta_type was removed
            del(self.__pluggable_installed_content[meta_type])
            self._p_changed = 1
        if REQUEST: REQUEST.RESPONSE.redirect('%s/manage_controlpanel_html' % self.absolute_url())

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_controlpanel_html')
    manage_controlpanel_html = PageTemplateFile('zpt/site_manage_controlpanel', globals())

    security.declareProtected(view_management_screens, 'macro_manage_add')
    macro_manage_add = PageTemplateFile('zpt/site_macro_manage_add', globals())

    security.declareProtected(view_management_screens, 'macro_manage_edit')
    macro_manage_edit= PageTemplateFile('zpt/site_macro_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'standard_html_header')
    def standard_html_header(self, REQUEST=None, RESPONSE=None):
        """ """
        context = self.unrestrictedTraverse(self.REQUEST.PATH_INFO)
        context = self.REQUEST.PARENTS[0]
        return self.getLayoutTool().getContent({'here': context}, 'standard_html_headerfooter').split('<!--STANDARD_HEADERFOOTER_MARKER-->')[0]

    security.declareProtected(view, 'standard_html_footer')
    def standard_html_footer(self, REQUEST=None, RESPONSE=None):
        """ """
        context = self.unrestrictedTraverse(self.REQUEST.PATH_INFO)
        context = self.REQUEST.PARENTS[0]
        return self.getLayoutTool().getContent({'here': context}, 'standard_html_headerfooter').split('<!--STANDARD_HEADERFOOTER_MARKER-->')[1]

    security.declareProtected(view, 'standard_error_message')
    def standard_error_message(self, client=None, REQUEST=None, **kwargs):
        """ """
        context = self.unrestrictedTraverse(self.REQUEST.PATH_INFO)
        context = self.REQUEST.PARENTS[0]
        kwargs['here'] = context
        return self.getFormsTool().getContent(kwargs, 'standard_error_message')

    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_index')

    security.declareProtected(view, 'messages_box')
    def messages_box(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'messages_box')

    security.declareProtected(view, 'languages_box')
    def languages_box(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'languages_box')

    security.declareProtected(view, 'login_html')
    def login_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_login')

    security.declareProtected(view, 'logout_html')
    def logout_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_logout')

    security.declareProtected(view, 'unauthorized_html')
    def unauthorized_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_unauthorized')

    security.declareProtected(view, 'search_html')
    def search_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_search')

    security.declareProtected(view, 'external_search_html')
    def external_search_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_external_search')

    security.declareProtected(view, 'sitemap_html')
    def sitemap_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_sitemap')

    security.declareProtected(view, 'feedback_html')
    def feedback_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_feedback')

    security.declareProtected(view, 'note_html')
    def note_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_note')

    security.declareProtected(view, 'requestrole_html')
    def requestrole_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self.REQUEST.PARENTS[0]}, 'site_requestrole')

InitializeClass(NySite)
