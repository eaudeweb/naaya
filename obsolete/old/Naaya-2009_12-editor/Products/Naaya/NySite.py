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
# The Original Code is Naaya version 1.0
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
# Alin Voinea, Eau de Web


#Python imports
import urllib
from os.path import join, isfile
from urllib import quote
from copy import copy
from cStringIO import StringIO
from zipfile import ZipFile
from datetime import datetime, timedelta

#Zope imports
import zLOG
from OFS.Folder import Folder, manage_addFolder
from OFS.Image import manage_addImage
from OFS.DTMLMethod import addDTMLMethod
from OFS.DTMLDocument import addDTMLDocument
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate import manage_addPageTemplate
from AccessControl import ClassSecurityInfo, Unauthorized
from AccessControl.Permissions import view_management_screens, view
from ZPublisher import BeforeTraverse
from Products.SiteErrorLog.SiteErrorLog import manage_addErrorLog
from Globals import DTMLFile
import Products
from zope.interface import implements
from App.ImageFile import ImageFile
from zope import component, interface

#Product imports
from interfaces import INySite, IHeartbeat
from constants import *
from Products.NaayaBase.constants import *
from Products.NaayaCore.constants import *
import naaya.content.base
from naaya.content.base.constants import *
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
from Products.NaayaCore.NotificationTool.NotificationTool import manage_addNotificationTool
from Products.NaayaCore.ProfilesTool.ProfilesTool import manage_addProfilesTool
from Products.NaayaCore.EditorTool.EditorTool import manage_addEditorTool
from Products.NaayaCore.GeoMapTool.GeoMapTool import manage_addGeoMapTool
from Products.NaayaCore.SchemaTool.SchemaTool import manage_addSchemaTool
from Products.NaayaBase.NyBase import NyBase
from Products.NaayaBase.NyImportExport import NyImportExport
from Products.NaayaBase.NyPermissions import NyPermissions
from Products.NaayaBase.NyImageContainer import NyImageContainer
from Products.NaayaCore.managers.utils import utils, list_utils, batch_utils, file_utils
from Products.NaayaCore.managers.catalog_tool import catalog_tool
from Products.NaayaCore.managers.captcha_tool import captcha_tool
from Products.NaayaCore.managers.urlgrab_tool import urlgrab_tool
from Products.NaayaCore.managers.search_tool import search_tool
from Products.NaayaCore.managers.session_manager import session_manager
from Products.NaayaCore.managers.xmlrpc_tool import XMLRPCConnector
from Products.NaayaCore.managers.utils import vcard_file
from Products.NaayaCore.managers.csv_import_export import CSVImportTool, CSVExportTool
from Products.NaayaCore.PropertiesTool.managers.contenttypes_tool import contenttypes_tool
from Products.Localizer.Localizer import manage_addLocalizer
from Products.Localizer.MessageCatalog import manage_addMessageCatalog
from Products.Localizer.LocalPropertyManager import LocalPropertyManager, LocalProperty
from managers.skel_parser import skel_parser
from managers.networkportals_manager import networkportals_manager
from Products.NaayaBase.managers.import_parser import import_parser
from NyVersions import NyVersions
from NyFolder import NyFolder, folder_add_html, addNyFolder, importNyFolder
from Products.NaayaCore.NotificationTool.Subscriber import Subscriber
from Products.NaayaBase.gtranslate import translate, translate_url
from NyFolderBase import NyFolderBase
from naaya.core.utils import call_method

#reCaptcha
from Products.NaayaCore.managers import recaptcha_utils

from naaya.core.template_helper import NaayaTemplateHelper

streamlined_updates = [
    '2009_05-zope_210_baseline',
    '2009_05-schema_tool',
]

from naaya.z2util import redirect_to


#constructor
manage_addNySite_html = PageTemplateFile('zpt/site_manage_add', globals())
def manage_addNySite(self, id='', title='', lang=None, default_content=True, REQUEST=None):
    """ """
    ut = utils()
    id = ut.utCleanupId(id)
    if not id: id = PREFIX_SITE + ut.utGenRandomId(6)
    portal_uid = '%s_%s' % (PREFIX_SITE, ut.utGenerateUID())
    self._setObject(id, NySite(id, portal_uid, title, lang))
    ob = self._getOb(id)
    ob.createPortalTools()
    if default_content:
        ob.loadDefaultData()
    manage_addSchemaTool(ob) # we add SchemaTool here because we need site languages to be loaded
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class NySite(CookieCrumbler, LocalPropertyManager, Folder,
    NyBase, NyPermissions, NyImportExport, NyVersions,
    utils, list_utils, file_utils,
    catalog_tool,
    search_tool,
    contenttypes_tool,
    session_manager,
    portlets_manager,
    networkportals_manager,
    NyFolderBase):
    """ """

    implements(INySite)

    meta_type = METATYPE_NYSITE
    icon = 'misc_/Naaya/Site.gif'

    manage_options = (
        Folder.manage_options
        +
        (
            {'label': 'Control Panel', 'action': 'manage_controlpanel_html'},
        )
        +
        NyImportExport.manage_options
    )

    product_paths = [NAAYA_PRODUCT_PATH]

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    title = LocalProperty('title')
    site_title = LocalProperty('site_title')
    site_subtitle = LocalProperty('site_subtitle')
    description = LocalProperty('description')
    publisher = LocalProperty('publisher')
    contributor = LocalProperty('contributor')
    creator = LocalProperty('creator')
    rights = LocalProperty('rights')
    display_contributor = "on"
    display_subobject_count = ""
    default_logo = ''

    def __init__(self, id, portal_uid, title, lang):
        """ """
        self.id = id
        self.__portal_uid = portal_uid
        self._auto_updates_reg = set(streamlined_updates)
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('site_title', lang, title)
        self._setLocalPropValue('site_subtitle', lang, u'')
        self._setLocalPropValue('description', lang, u'')
        self._setLocalPropValue('publisher', lang, u'')
        self._setLocalPropValue('contributor', lang, u'')
        self._setLocalPropValue('creator', lang, u'')
        self._setLocalPropValue('rights', lang, u'')
        self.adt_meta_types = []
        self.search_age = 12
        self.searchable_content = []
        self.numberresultsperpage = 10
        self.notify_on_errors = 1
        self.http_proxy = ''
        self.repository_url = ''
        self.mail_server_name = DEFAULT_MAILSERVERNAME
        self.mail_server_port = DEFAULT_MAILSERVERPORT
        self.recaptcha_public_key = ''
        self.recaptcha_private_key = ''
        # The email address (must exist) from which the email tool sends mails
        self.mail_address_from = ''
        self.administrator_email = ''
        #holds info about customized folder's contact us page
        self.rdf_max_items = 10
        self.folder_customized_feedback = {}
        self.portal_url = ''
        self.maintopics = []
        self.keywords_glossary = None
        self.coverage_glossary = None
        self.__pluggable_installed_content = {}
        self.show_releasedate = 1
        self.submit_unapproved = 0
        self.rename_id = 0
        self.nyexp_schema = NYEXP_SCHEMA_LOCATION
        # Allow users to move current language content to another language.
        self.switch_language = 0
        # Choose whether or not the contributor should be displayed
        self.display_contributor = "on"
        self.display_subobject_count = ""
        self.default_logo = ''
        contenttypes_tool.__dict__['__init__'](self)
        CookieCrumbler.__dict__['__init__'](self)
        catalog_tool.__dict__['__init__'](self)
        search_tool.__dict__['__init__'](self)
        portlets_manager.__dict__['__init__'](self)
        networkportals_manager.__dict__['__init__'](self)

    security.declarePrivate('createPortalTools')
    def createPortalTools(self):
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
        manage_addNotificationTool(self)
        manage_addProfilesTool(self)
        manage_addEditorTool(self)
        manage_addGeoMapTool(self)
        manage_addErrorLog(self)

    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self):
        """ """
        #load default skeleton
        self.loadSkeleton(NAAYA_PRODUCT_PATH)
        #set default main topics
        self.getPropertiesTool().manageMainTopics(['info'])
        self.imageContainer = NyImageContainer(self.getImagesFolder(), False)

    security.declarePrivate('get_skel_handler')
    def get_skel_handler(self, product_path):
        skel_path = join(product_path, 'skel')
        skel_content = self.futRead(join(skel_path, 'skel.xml'), 'r')
        skel_handler, error = skel_parser().parse(skel_content)
        if error:
            zLOG.LOG('NySite.loadSkeleton', zLOG.ERROR, error)
            raise ValueError('error parsing skel.xml')
        skel_handler.skel_path = skel_path
        return skel_handler

    security.declarePrivate('get_all_skel_handlers')
    def get_all_skel_handlers(self):
        handlers = []
        for product_path in self.product_paths:
            handlers.append(self.get_skel_handler(product_path))
        return handlers

    security.declarePrivate('loadSkeleton')
    def loadSkeleton(self, product_path):
        """ """
        #load site skeleton - configuration
        skel_handler = self.get_skel_handler(product_path)
        skel_path = skel_handler.skel_path
        if skel_handler is not None:
            properties_tool = self.getPropertiesTool()
            formstool_ob = self.getFormsTool()
            layouttool_ob = self.getLayoutTool()
            syndicationtool_ob = self.getSyndicationTool()
            portletstool_ob = self.getPortletsTool()
            emailtool_ob = self.getEmailTool()
            authenticationtool_ob = self.getAuthenticationTool()
            notificationtool_ob = self.getNotificationTool()
            #load security permissions and roles
            if skel_handler.root.security is not None:
                for permission in skel_handler.root.security.grouppermissions:
                    authenticationtool_ob.addPermission(permission.name, permission.description, permission.permissions)
                for role in skel_handler.root.security.roles:
                    try: authenticationtool_ob.addRole(role.name, role.grouppermissions)
                    except: pass
                    #set the grouppermissions
                    authenticationtool_ob.editRole(role.name, role.grouppermissions)
                    #set individual permissions
                    b = [x['name'] for x in self.permissionsOfRole(role.name) if x['selected']=='SELECTED']
                    b.extend(role.permissions)
                    self.manage_role(role.name, b)
            #load pluggable content types
            if skel_handler.root.pluggablecontenttypes is not None:
                for pluggablecontenttype in skel_handler.root.pluggablecontenttypes.pluggablecontenttypes:
                    try: action = abs(int(pluggablecontenttype.action))
                    except: action = 1
                    if action == 0:
                        self.manage_uninstall_pluggableitem(meta_type=pluggablecontenttype.meta_type)
                    else:
                        self.manage_install_pluggableitem(meta_type=pluggablecontenttype.meta_type)
            #load properties
            if skel_handler.root.properties is not None:
                for language in skel_handler.root.properties.languages:
                    properties_tool.manage_addLanguage(language.code)
                for contenttype in skel_handler.root.properties.contenttypes:
                    content = self.futRead(join(skel_path, 'contenttypes', contenttype.picture), 'rb')
                    self.createContentType(contenttype.id, contenttype.title, content)
            #forms are loaded from disk at runtime; they can be customized in portal_forms.
            #load skins
            if skel_handler.root.layout is not None:
                for skin in skel_handler.root.layout.skins:
                    if not layouttool_ob._getOb(skin.id, None):
                        layouttool_ob.manage_addSkin(id=skin.id, title=skin.title)
                    skin_ob = layouttool_ob._getOb(skin.id)
                    for template in skin.templates:
                        content = self.futRead(join(skel_path, 'layout', skin.id, '%s.zpt' % template.id), 'r')
                        if not skin_ob._getOb(template.id, None):
                            skin_ob.manage_addTemplate(id=template.id, title=template.title, file='')
                        skin_ob._getOb(template.id).pt_edit(text=content, content_type='')
                    for scheme in skin.schemes:
                        if skin_ob._getOb(scheme.id, None):
                            skin_ob.manage_delObjects([scheme.id])
                        skin_ob.manage_addScheme(id=scheme.id, title=scheme.title)
                        scheme_ob = skin_ob._getOb(scheme.id)
                        for style in scheme.styles:
                            content = self.futRead(join(skel_path, 'layout', skin.id, scheme.id, '%s.css' % style.id), 'r')
                            if scheme_ob._getOb(style.id, None):
                                scheme_ob.manage_delObjects([style.id])
                            scheme_ob.manage_addStyle(id=style.id, title=style.title, file=content)
                        for image in scheme.images:
                            content = self.futRead(join(skel_path, 'layout', skin.id, scheme.id, image.id), 'rb')
                            if not scheme_ob._getOb(image.id, None):
                                scheme_ob.manage_addImage(id=image.id, file='', title=image.title)
                            image_ob = scheme_ob._getOb(image.id)
                            image_ob.update_data(data=content)
                            image_ob._p_changed=1
                if skel_handler.root.layout.default_skin_id and skel_handler.root.layout.default_scheme_id:
                    layouttool_ob.manageLayout(skel_handler.root.layout.default_skin_id, skel_handler.root.layout.default_scheme_id)
                #load logos
                try:
                    content = self.futRead(join(skel_path, 'layout', 'logo.gif'), 'rb')
                except IOError, err:
                    zLOG.LOG('NySite.loadSkeleton', zLOG.ERROR, err)
                else:
                    image_ob = layouttool_ob._getOb('logo.gif', None)
                    if image_ob is None:
                        layouttool_ob.manage_addImage(id='logo.gif', file='', title='Site logo')
                        image_ob = layouttool_ob._getOb('logo.gif')
                    image_ob.update_data(data=content)
                    image_ob._p_changed=1
                try:
                    content = self.futRead(join(skel_path, 'layout', 'logobis.gif'), 'rb')
                except IOError, err:
                    zLOG.LOG('NySite.loadSkeleton', zLOG.ERROR, err)
                else:
                    image_ob = layouttool_ob._getOb('logobis.gif', None)
                    if image_ob is None:
                        layouttool_ob.manage_addImage(id='logobis.gif', file='', title='Site secondary logo')
                        image_ob = layouttool_ob._getOb('logobis.gif')
                    image_ob.update_data(data=content)
                    image_ob._p_changed=1
            #load syndication
            if skel_handler.root.syndication is not None:
                for namespace in skel_handler.root.syndication.namespaces:
                    syndicationtool_ob.createNamespaceItem(namespace.id, namespace.prefix, namespace.value)
                for channeltype in skel_handler.root.syndication.channeltypes:
                    syndicationtool_ob.add_channeltype_item(channeltype.id, channeltype.title)
                for channel in skel_handler.root.syndication.scriptchannels:
                    language = self.utEmptyToNone(channel.language)
                    type = self.utEmptyToNone(channel.type)
                    body = self.futRead(join(skel_path, 'syndication', '%s.py' % channel.id), 'r')
                    channel_ob = syndicationtool_ob._getOb(channel.id, None)
                    if channel_ob is None:
                        syndicationtool_ob.manage_addScriptChannel(channel.id, channel.title, channel.description, language, type, body, channel.numberofitems, channel.portlet)
                        channel_ob = syndicationtool_ob._getOb(channel.id)
                    else:
                        channel_ob.write(body)
                    if channel.portlet:
                        content = self.futRead(join(skel_path, 'syndication', '%s.zpt' % channel.id), 'r')
                        portletstool_ob._getOb('%s%s' % (PREFIX_PORTLET, channel.id)).pt_edit(text=content, content_type='')
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
                for reflist in skel_handler.root.portlets.reflists:
                    reflist_ob = portletstool_ob._getOb(reflist.id, None)
                    if reflist_ob is None:
                        portletstool_ob.manage_addRefList(reflist.id, reflist.title, reflist.description)
                        reflist_ob = portletstool_ob._getOb(reflist.id)
                    else:
                        reflist_ob.manage_delete_items(reflist_ob.get_collection().keys())
                    for item in reflist.items:
                        reflist_ob.add_item(item.id, item.title)
                for reftree in skel_handler.root.portlets.reftrees:
                    reftree_ob = portletstool_ob._getOb(reftree.id, None)
                    if reftree_ob is None:
                        portletstool_ob.manage_addRefTree(reftree.id)
                        reftree_ob = portletstool_ob._getOb(reftree.id)
                        for property, langs in reftree.properties.items():
                            for lang in langs:
                                reftree_ob._setLocalPropValue(property, lang, langs[lang])
                    else:
                        reftree_ob.manage_delObjects(reftree_ob.objectIds())
                    for node in reftree.nodes:
                        reftree_ob.manage_addRefTreeNode(node.id, '', node.parent, node.pickable)
                        node_ob = reftree_ob._getOb(node.id)
                        for property, langs in node.properties.items():
                            for lang in langs:
                                node_ob._setLocalPropValue(property, lang, langs[lang])
                if skel_handler.root.portlets.left:
                    for portlet_id in portletstool_ob.get_portlet_ids_for('', 'left'):
                        portletstool_ob.unassign_portlet('', 'left', portlet_id)
                    for portlet_id in skel_handler.root.portlets.left.split(','):
                        portletstool_ob.assign_portlet('', "left", portlet_id, True)
                if skel_handler.root.portlets.center:
                    for portlet_id in portletstool_ob.get_portlet_ids_for('', 'center'):
                        portletstool_ob.unassign_portlet('', 'center', portlet_id)
                    for portlet_id in skel_handler.root.portlets.center.split(','):
                        portletstool_ob.assign_portlet('', "center", portlet_id, False)
            #load email templates
            if skel_handler.root.emails is not None:
                for emailtemplate in skel_handler.root.emails.emailtemplates:
                    content = self.futRead(join(skel_path, 'emails', '%s.txt' % emailtemplate.id), 'r')
                    email_ob = emailtool_ob._getOb(emailtemplate.id, None)
                    if email_ob is None:
                        emailtool_ob.manage_addEmailTemplate(emailtemplate.id, emailtemplate.title, content)
                    else:
                        email_ob.manageProperties(title=email_ob.title, body=content)
            #set subobjects for folders
            self.getPropertiesTool().manageSubobjects(subobjects=None, ny_subobjects=self.get_meta_types(1))
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
                if skel_handler.root.others.sitemap_xml is not None:
                    content = self.futRead(join(skel_path, 'others', 'sitemap_xml'), 'r')
                    file_ob = self._getOb('sitemap_xml', None)
                    if file_ob is None:
                        self.manage_addProduct['PythonScripts'].manage_addPythonScript(id='sitemap_xml')
                        file_ob = self._getOb('sitemap_xml')
                    file_ob.ZPythonScript_edit(params='', body=content)
                    file_ob._p_changed=1
                if skel_handler.root.others.favicon is not None:
                    content = self.futRead(join(skel_path, 'others', 'favicon.ico'), 'rb')
                    image_ob = self._getOb('favicon.ico', None)
                    if image_ob is None:
                        self.manage_addImage(id='favicon.ico', file='', title='')
                        image_ob = self._getOb('favicon.ico')
                    image_ob.update_data(data=content)
                    image_ob._p_changed=1
                if skel_handler.root.others.nyexp_schema is not None:
                    self.nyexp_schema = skel_handler.root.others.nyexp_schema.url
                if skel_handler.root.others.images is not None:
                    self.manage_addFolder(ID_IMAGESFOLDER, 'Images')
                if skel_handler.root.others.submit_unapproved is not None:
                    self.submit_unapproved = 1
                    self._p_changed = 1
        self.setDefaultSearchableContent()
        #load site skeleton - default content
        import_handler, error = import_parser().parse(self.futRead(join(skel_path, 'skel.nyexp'), 'r'))
        if import_handler is not None:
            for object in import_handler.root.objects:
                self.import_data(object)
        else:
            raise Exception, EXCEPTION_PARSINGFILE % (join(skel_path, 'skel.nyexp'), error)

    def updatePath(self):
        """@DEPRECATED"""
        handle = self.meta_type + '/' + self.getId()
        nc = BeforeTraverse.NameCaller(self.getId())
        BeforeTraverse.registerBeforeTraverse(self, nc, handle)

    #hooks
    def hook_after_approve(self, ob):
        """
        This method is called after an object is approved. Can be overwritten.
        @param ob: the object
        @type ob: naaya object instance
        """
        pass

    def hook_after_unapprove(self, ob):
        """
        This method is called after an object is unapproved. Can be overwritte.
        @param ob: the object
        @type ob: naaya object instance
        """
        pass

    def get_archive_listing(self, p_objects):
        """ """
        results = []
        select_all, delete_all, flag = 0, 0, 0
        for x in p_objects:
            del_permission = x.checkPermissionDeleteObject()
            edit_permission = x.checkPermissionEditObject()
            if del_permission and flag == 0:
                select_all, delete_all, flag = 1, 1, 1
            if edit_permission and flag == 0:
                flag, select_all = 1, 1
            if ((del_permission or edit_permission) and not x.approved) or x.approved:
                results.append((del_permission, edit_permission, x))
        return (select_all, delete_all, results)

    security.declareProtected(view, 'getArchiveListing')
    def getArchiveListing(self, p_archive, p_attr='releasedate', p_desc=1):
        """ Returns a list of objects sorted by an attribute such as the 'releasedate'
            Used by custom folder indexes
        """
        p_objects = p_archive.getObjects()
        p_objects = self.utSortObjsListByAttr(p_objects, p_attr, p_desc)
        return self.get_archive_listing(p_objects)

    security.declarePrivate('setSearchableContent')
    def setSearchableContent(self, p_meta_types):
        """
        Set the meta types to be considered in searches.
        """
        self.searchable_content = self.utConvertToList(p_meta_types)
        self._p_changed = 1

    security.declarePrivate('setDefaultSearchableContent')
    def setDefaultSearchableContent(self):
        """
        Set the default meta types to be considered in searches.
        """
        l = self.get_pluggable_installed_meta_types()
        l.append(METATYPE_FOLDER)
        self.setSearchableContent(l)

    #import/export
    def exportdata_custom(self):
        #exports all the Naaya content in XML format from the portal
        r = []
        ra = r.append
        for x in self.getSite().get_containers():
            ra(x.export_this())
        return ''.join(r)

    def import_data(self, object):
        #import an object
        if object.meta_type == METATYPE_FOLDER:
            importNyFolder(self, object.param, object.id, object.attrs, object.content,
                object.properties, object.discussion, object.objects)
        else:
            self.import_data_custom(self, object)

    def import_data_custom(self, node, object):
        #import some special type of object
        if object.meta_type == 'Image':
            id = object.attrs['id'].encode('utf-8')
            node.manage_addImage(id=id, file='')
            image_ob = node._getOb(id)
            image_ob.update_data(data=self.utBase64Decode(object.attrs['content'].encode('utf-8')))
            image_ob._p_changed=1
        elif object.meta_type == 'File':
            id = object.attrs['id'].encode('utf-8')
            node.manage_addFile(id=id, file='')
            file_ob = node._getOb(id)
            file_ob.update_data(data=self.utBase64Decode(object.attrs['content'].encode('utf-8')))
            file_ob._p_changed=1
        elif object.meta_type == 'Page Template':
            id = object.attrs['id'].encode('utf-8')
            title = object.attrs['title'].encode('utf-8')
            manage_addPageTemplate(node, id=id, title=title, text='')
            pt_obj = node._getOb(id)
            pt_obj.pt_edit(text=object.content, content_type='')
        else:
            print 'Import an object of type [%s]' % object.meta_type

    #api
    security.declarePublic('get_site_uid')
    def get_site_uid(self): return self.__portal_uid

    security.declarePublic('get_constant')
    def get_constant(self, c): return naaya.content.base.discover.get_constant(c)

    security.declarePublic('get_meta_types')
    def get_meta_types(self, folder=0):
        #returns a list with objects metatypes
        res = []
        if folder==1:
            res.append(METATYPE_FOLDER)
        # Add Naaya Forum to subobjects list
        try:
            from Products.NaayaForum.constants import METATYPE_NYFORUM
        except ImportError:
            pass
        else:
            res.append(METATYPE_NYFORUM)
        res.extend(self.get_pluggable_installed_meta_types())
        return res

    security.declarePublic('get_label_for_meta_type')
    def get_label_for_meta_type(self, meta_type):
        #returns the label associated with the given meta_type
        #it can be a Naaya Folder or a pluggable content type
        if meta_type == METATYPE_FOLDER:
            return LABEL_NYFOLDER
        else:
            try: return self.getSchemaTool().getSchemaForMetatype(meta_type).title_or_id()
            except: return meta_type

    security.declarePublic('getProductsMetaTypes')
    def getProductsMetaTypes(self):
        #returns a list with all meta types
        return [x['name'] for x in self.filtered_meta_types()]

    def get_data_path(self):
        """
        Returns the path to the data directory.
        All classes that extends I{NySite} B{must} overwrite
        this method.
        """
        return NAAYA_PRODUCT_PATH

    #not used anymore
    security.declarePublic('isArabicLanguage')
    def isArabicLanguage(self, lang=None):
        """ test if lang is a RTL language """
        return self.isRTL(lang)

    security.declarePublic('isRTL')
    def isRTL(self, lang=None):
        """ test if lang is a RTL language """
        #Arabic          [AR]
        #Azerbaijani     [AZ]
        #Persian         [FA]
        #Javanese        [JV]
        #Kashmiri        [KS]
        #Kazakh          [KK]
        #Kurdish         [KU]
        #Malay           [MS]
        #Malayalam       [ML]
        #Pashto          [PS]
        #Punjabi         [PA]
        #Sindhi          [SD]
        #Somali          [SO]
        #Turkmen         [TK]
        #Hebrew          [HE]
        #Yiddish         [YI]
        #Urdu            [UR]
        if not lang: lang = self.gl_get_selected_language()
        return lang in ['ar', 'az', 'fa', 'jv', 'ks', 'kk', 'ku', 'ms', 'ml',\
                        'ps', 'pa', 'sd', 'so', 'tk', 'he', 'yi', 'ur']


    #objects getters
    security.declarePublic('getSite')
    def getSite(self): return self

    security.declarePublic('getPropertiesTool')
    def getPropertiesTool(self): return self._getOb(ID_PROPERTIESTOOL)

    security.declarePublic('getPortletsTool')
    def getPortletsTool(self): return self._getOb(ID_PORTLETSTOOL)

    security.declarePublic('getAuthenticationTool')
    def getAuthenticationTool(self): return self._getOb(ID_AUTHENTICATIONTOOL)

    security.declarePublic('getDynamicPropertiesTool')
    def getDynamicPropertiesTool(self): return self._getOb(ID_DYNAMICPROPERTIESTOOL)

    security.declarePublic('getCatalogTool')
    def getCatalogTool(self): return self._getOb(ID_CATALOGTOOL)

    security.declarePublic('getLayoutTool')
    def getLayoutTool(self): return self._getOb(ID_LAYOUTTOOL)

    security.declarePublic('getSyndicationTool')
    def getSyndicationTool(self): return self._getOb(ID_SYNDICATIONTOOL)

    security.declarePublic('getEmailTool')
    def getEmailTool(self): return self._getOb(ID_EMAILTOOL)

    security.declarePublic('getFormsTool')
    def getFormsTool(self): return self._getOb(ID_FORMSTOOL)

    security.declarePublic('getSchemaTool')
    def getSchemaTool(self): return self._getOb(ID_SCHEMATOOL)

    security.declarePublic('getLocalizer')
    def getLocalizer(self): return self._getOb('Localizer')

    security.declarePublic('getPortalTranslations')
    def getPortalTranslations(self): return self._getOb(ID_TRANSLATIONSTOOL)

    security.declarePublic('getImagesFolder')
    def getImagesFolder(self): return self._getOb(ID_IMAGESFOLDER)

    security.declarePublic('getProfilesTool')
    def getProfilesTool(self): return self._getOb(ID_PROFILESTOOL)

    security.declarePublic('getNotificationTool')
    def getNotificationTool(self): return self._getOb(ID_NOTIFICATIONTOOL)

    security.declarePublic('getProfilesTool')
    def getProfilesTool(self): return self._getOb(ID_PROFILESTOOL)

    security.declarePublic('getEditorTool')
    def getEditorTool(self): return self._getOb(ID_EDITORTOOL)

    security.declarePublic('getGeoMapTool')
    def getGeoMapTool(self): return self._getOb(ID_GEOMAPTOOL, None)

    #objects absolute/relative path getters
    security.declarePublic('getSitePath')
    def getSitePath(self, p=0): return self.absolute_url(p)
    security.declarePublic('getPropertiesToolPath')
    def getPropertiesToolPath(self, p=0): return self._getOb(ID_PROPERTIESTOOL).absolute_url(p)
    security.declarePublic('getPortletsToolPath')
    def getPortletsToolPath(self, p=0): return self._getOb(ID_PORTLETSTOOL).absolute_url(p)
    security.declarePublic('getPortalTranslationsPath')
    def getPortalTranslationsPath(self, p=0): return self._getOb(ID_TRANSLATIONSTOOL).absolute_url(p)
    security.declarePublic('getAuthenticationToolPath')
    def getAuthenticationToolPath(self, p=0): return self._getOb(ID_AUTHENTICATIONTOOL).absolute_url(p)
    security.declarePublic('getDynamicPropertiesToolPath')
    def getDynamicPropertiesToolPath(self, p=0): return self._getOb(ID_DYNAMICPROPERTIESTOOL).absolute_url(p)
    security.declarePublic('getCatalogToolPath')
    def getCatalogToolPath(self, p=0): return self._getOb(ID_CATALOGTOOL).absolute_url(p)
    security.declarePublic('getLayoutToolPath')
    def getLayoutToolPath(self, p=0): return self._getOb(ID_LAYOUTTOOL).absolute_url(p)
    security.declarePublic('getSyndicationToolPath')
    def getSyndicationToolPath(self, p=0): return self._getOb(ID_SYNDICATIONTOOL).absolute_url(p)
    security.declarePublic('getEmailToolPath')
    def getEmailToolPath(self, p=0): return self._getOb(ID_EMAILTOOL).absolute_url(p)
    security.declarePublic('getFormsToolPath')
    def getFormsToolPath(self, p=0): return self._getOb(ID_FORMSTOOL).absolute_url(p)
    security.declarePublic('getFolderByPath')
    def getFolderByPath(self, p_folderpath): return self.unrestrictedTraverse(p_folderpath, None)

    security.declarePublic('getProfilesToolPath')
    def getProfilesToolPath(self, p=0): return self._getOb(ID_PROFILESTOOL).absolute_url(p)

    security.declarePublic('getNotificationToolPath')
    def getNotificationToolPath(self, p=0): return self._getOb(ID_NOTIFICATIONTOOL).absolute_url(p)
    security.declarePublic('getProfilesToolPath')
    def getProfilesToolPath(self, p=0): return self._getOb(ID_PROFILESTOOL).absolute_url(p)

    security.declarePublic('getGeoMapToolPath')
    def getGeoMapToolPath(self, p=0): return self._getOb(ID_GEOMAPTOOL).absolute_url(p)

    def getFolderMetaType(self): return METATYPE_FOLDER
    security.declarePublic('getFolderMainParent')
    def getFolderMainParent(self, p_folder):
        """
        Returns the main parent of the given folder.
        @param p_folder: a folder object
        @type p_folder: NyFolder
        @return: a NyFolder object
        """
        l_parent = p_folder
        while l_parent.getParentNode().meta_type != self.meta_type:
            l_parent = l_parent.getParentNode()
        return l_parent

    security.declarePublic('getAllParents')
    def getAllParents(self, p_folder):
        """
        Returns all parents of a folder, without aquisition.
        @param p_folder: a folder object
        @type p_folder: NyFolder
        @return: a list of NyFolder objects
        """
        l_parent = p_folder
        l_result = [l_parent]
        while l_parent.getParentNode().meta_type != self.meta_type:
            l_parent = l_parent.getParentNode()
            l_result.append(l_parent)
        l_result.reverse()
        return l_result

    security.declarePublic('get_containers')
    def get_containers(self):
        #this method returns all container type that can be used in an export operation
        return [x for x in self.objectValues(METATYPE_FOLDER) if x.submitted==1]

    security.declarePublic('getObjectById')
    def getObjectById(self, p_id):
        """
        Returns an object inside this one with the given id.
        @param p_id: object id
        @type p_id: string
        @return:
            - the object is exists
            - None otherwise
        """
        try: return self._getOb(p_id)
        except: return None

    security.declarePublic('get_containers_metatypes')
    def get_containers_metatypes(self):
        #this method is used to display local roles, called from getUserRoles methods
        return [METATYPE_FOLDER, 'Folder', 'Naaya Photo Gallery', 'Naaya Photo Folder', 'Naaya Forum', 'Naaya Forum Topic', 'Naaya Consultation', 'Naaya Simple Consultation', 'Naaya TalkBack Consultation', 'Naaya Survey Questionnaire']

    security.declarePublic('get_naaya_containers_metatypes')
    def get_naaya_containers_metatypes(self):
        """ this method is used to display local roles, called from getUserRoles methods """
        return [METATYPE_FOLDER, 'Naaya Photo Gallery', 'Naaya Photo Folder', 'Naaya Forum', 'Naaya Forum Topic', 'Naaya Consultation', 'Naaya Simple Consultation', 'Naaya TalkBack Consultation', 'Naaya Survey Questionnaire']

    #layer over selection lists
    security.declarePublic('getEventTypesList')
    def getEventTypesList(self):
        """
        Return the selection list for event types.
        """
        return self.getPortletsTool().getRefListById('event_types').get_list()

    def getEventTypeTitle(self, id):
        """
        Return the title of an item for the selection list for event types.
        """
        try:
            return self.getPortletsTool().getRefListById('event_types').get_item(id).title
        except:
            return ''

    #api
    security.declarePublic('process_releasedate')
    def process_releasedate(self, p_string='', p_date=None):
        """
        Process a value for an object's release date.

        @param p_string: represents a date like 'dd/mm/yyyy' or 'yyyy/mm/dd'
        @type lang: string
        @param p_date: represents a date
        @type p_date: DateTime
        @return: a DateTime value
        """
        releasedate = self.utConvertStringToDateTimeObj(p_string)
        if releasedate is None:
            if p_date is None: releasedate = self.utGetTodayDate()
            else: releasedate = p_date
        else:
            if p_date is not None:
                #check if the day was changed: if no then restore release date
                if (p_date.year() == releasedate.year()) and \
                    (p_date.month() == releasedate.month()) and \
                    (p_date.day() == releasedate.day()):
                    releasedate = p_date
        return releasedate

    security.declarePublic('getMainFolders')
    def getMainFolders(self):
        """
        Returns a list with all folders objects at the first level
        that are approved and sorted by 'order' property
        """
        return self.utSortObjsListByAttr([x for x in self.objectValues(METATYPE_FOLDER) if x.approved==1 and x.submitted==1], 'sortorder', 0)

    security.declarePublic('getMainTopics')
    def getMainTopics(self):
        """
        Returns the list of main topic folders
        sorted by 'order' property
        """
        return self.utSortObjsListByAttr(filter(lambda x: x is not None, map(lambda f, x: f(x, None), (self.utGetObject,)*len(self.maintopics), self.maintopics)), 'sortorder', 0)

    security.declarePublic('getMainTopicByURL')
    def getMainTopicByURL(self, url):
        """
        Returns the main topic folder object
        given the URL
        """
        return self.utGetObject(url)

    security.declarePublic('getFoldersWithPendingItems')
    def getFoldersWithPendingItems(self):
        """ returns a list with all folders that contain pending(draft) objects """
        d = {}
        for x in self.getCatalogedObjects(METATYPE_FOLDER):
            c = len(x.getPendingContent())
            if c > 0: #this folder has pending content
                p = self.getFolderMainParent(x)
                url = p.absolute_url(1)
                if not d.has_key(url): d[url] = [p, []]
                d[url][1].append((x, c))
        return d

    security.declarePublic('getFoldersWithUntranslatedContent')
    def getFoldersWithTranslatableContent(self, lang):
        """
        returns a list with all folders that contain objects that
        have not yet been translated in the specified language
        """
        translatable = {}
        for folder in self.getCatalogedObjects(METATYPE_FOLDER):
            main_parent = self.getFolderMainParent(folder)
            main_parent_url = main_parent.absolute_url(1)
            translatable.setdefault(main_parent_url, {})
            translatable[main_parent_url]['obj'] = main_parent
            translatable[main_parent_url].setdefault('content', [])
            translatable[main_parent_url]['content'].extend(folder.getTranslatableContent(lang))
        #if there are no un-translated items for the given language, return an empty dictionary
        if not [object for object in translatable.values() if object['content']]:
            return {}
        return translatable

    security.declarePublic('getLatestUploads')
    def getLatestUploads(self, howmany=None):
        """
        Returns a list with the latest published items in the portal
        """
        if howmany is None: howmany = 50
        return self.getCatalogedObjects(meta_type=self.get_meta_types(), approved=1, howmany=howmany, path=['/'.join(x.getPhysicalPath()) for x in self.getMainTopics()])

    security.declarePublic('getCheckedOutObjects')
    def getCheckedOutObjects(self):
        """ Returns a list with all checked out objects in the portal (open versions) """
        return self.getCatalogCheckedOutObjects()

    security.declarePublic('getBreadCrumbTrail')
    def getBreadCrumbTrail(self, REQUEST):
        """ generates the breadcrumb trail """
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
        auth_tool = self.getAuthenticationTool()
        if node is self: return l_emails
        else:
            while 1:
                if node == self:
                    l_emails.extend(node.administrator_email.split(','))
                    break
                if hasattr(node, 'maintainer_email'):
                    if node.maintainer_email != '' and node.maintainer_email not in l_emails:
                        l_emails.extend(node.maintainer_email.split(','))
                admins = self.get_administrator(node)

                l_emails.extend(auth_tool.getUsersEmails(admins))
                node = node.getParentNode()
        return l_emails

    def admin_getuser_fullnames(self, usernames):
        auth_tool = self.getAuthenticationTool()
        return auth_tool.getUsersFullNames(usernames)

    def getFolderMaintainersEmails(self, node):
        #returns a list of emails for given folder until the site object
        l_emails = []
        auth_tool = self.getAuthenticationTool()
        if node is self: return l_emails
        else:
            while 1:
                if node == self:
                    if len(l_emails) == 0:
                        l_emails.append(node.administrator_email)
                    break
                if hasattr(node, 'maintainer_email'):
                    if node.maintainer_email != '' and node.maintainer_email not in l_emails:
                        l_emails.append(node.maintainer_email)
                admins = self.get_administrator(node)
                l_emails.extend(auth_tool.getUsersEmails(admins))
                node = node.getParentNode()
        return l_emails

    security.declarePrivate('get_administrators')
    def get_administrator(self, node):
        l_users = []
        for roles_tuple in node.get_local_roles():
            roles = roles_tuple[1]
            user = roles_tuple[0]
            if ('Administrator' in list(roles) or 'Manager' in list(roles)) and user not in l_users:
                l_users.append(user)
        return l_users

    def get_portal_domain(self):
        if not self.portal_url.startswith('http://'):
            return 'http://%s' % self.portal_url
        else:
            return self.portal_url

    # deprecated
    def get_portal_mail_address(self):
        return self.getEmailTool()._get_from_address()

    def notifyFolderMaintainer(self, p_folder, p_object, **kwargs):
        """
        Process and notify by email that B{p_object} has been
        uploaded into the B{p_folder}.
        """
        if (hasattr(p_object, 'submitted') and p_object.submitted==1) or not hasattr(p_object, 'submitted'):
            l_emails = self.getMaintainersEmails(p_folder)
            if len(l_emails) > 0:
                #old way gets mails rejected
                #mail_from = self.get_portal_mail_address()
                mail_from = self.getEmailTool()._get_from_address()
                self.notifyMaintainerEmail(l_emails, mail_from, p_object, p_folder.absolute_url(), '%s/basketofapprovals_html' % p_folder.absolute_url(), **kwargs)

    def processDynamicProperties(self, meta_type, REQUEST=None, keywords={}):
        """ """
        for l_prop in self.getDynamicPropertiesTool().getDynamicProperties(meta_type):
            try: keywords[l_prop.id] = REQUEST.get(l_prop.id, '')
            except: keywords[l_prop.id] = ''

        return keywords

    def getItemsAge(self): return self.search_age
    def setItemsAge(self, age): self.search_age = age
    def getNumberOfResults(self): return self.numberresultsperpage
    def setNumberOfResults(self, results_number): self.numberresultsperpage = results_number

    #layer over the Localizer and MessageCatalog
    #the scope is to centralize the list of available languages
    security.declarePublic('gl_get_all_languages')
    def gl_get_all_languages(self): return self.get_all_languages()

    security.declarePublic('gl_get_languages')
    def gl_get_languages(self): return self.get_languages()

    security.declarePublic('gl_get_languages_mapping')
    def gl_get_languages_mapping(self): return self.get_languages_mapping()

    security.declarePublic('gl_get_default_language')
    def gl_get_default_language(self): return self.get_default_language()

    security.declarePublic('gl_get_selected_language')
    def gl_get_selected_language(self): return self.get_selected_language()

    security.declarePublic('gl_get_languages_map')
    def gl_get_languages_map(self):
        lang, langs, r = self.gl_get_selected_language(), self.get_available_languages(), []
        for x in langs:
            r.append({'id': x, 'title': self.gl_get_language_name(x), 'selected': x==lang})
        return r

    security.declarePublic('gl_get_language_name')
    def gl_get_language_name(self, lang): return self.get_language_name(lang)

    def gl_add_languages(self, ob):
        for l in self.gl_get_languages_mapping():
            ob.add_language(l['code'])
            if l['default']: ob.manage_changeDefaultLang(l['code'])
    def gl_changeLanguage(self, old_lang, REQUEST=None):
        """ """
        self.getLocalizer().changeLanguage(old_lang)
        if REQUEST: REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    def gl_add_site_language(self, language):
        #this is called when a new language is added for the portal
        catalog_tool = self.getCatalogTool()
        self.add_language(language)
        self.getLocalizer().add_language(language)
        self.getPortalTranslations().add_language(language)
        catalog_tool.add_indexes_for_lang(language)
        for b in self.getCatalogedBrains():
            x = catalog_tool.getobject(b.data_record_id_)
            try: x.add_language(language)
            except: pass
        for x in self.getPortletsTool().get_html_portlets():
            try: x.add_language(language)
            except: pass
        self.gl_add_site_language_custom(language)
        # Custom update site children languages
        for x in self.objectValues():
            object_add_meth = getattr(x, 'custom_object_add_language', None)
            if not object_add_meth:
                continue
            try:
                object_add_meth(language)
            except Exception, exc_error:
                zLOG.LOG('NySite', zLOG.DEBUG, 'Could not add language %s for object %s: %s' % (language, x.absolute_url(1), exc_error))
                continue

    def gl_add_site_language_custom(self, language):
        #this is called to handle other types of multilanguage objects
        pass

    def gl_del_site_languages(self, languages):
        #this is called when one or more languages are deleted from the portal
        catalog_tool = self.getCatalogTool()
        for language in languages:
            self.del_language(language)
            self.getLocalizer().del_language(language)
            self.getPortalTranslations().del_language(language)
            catalog_tool.del_indexes_for_lang(language)
        for b in self.getCatalogedBrains():
            x = catalog_tool.getobject(b.data_record_id_)
            for language in languages:
                try: x.del_language(language)
                except: pass
        for x in self.getPortletsTool().get_html_portlets():
            for language in languages:
                try: x.del_language(language)
                except: pass
        self.gl_del_site_languages_custom(languages)
        # Custom update site children languages
        for x in self.objectValues():
            object_del_meth = getattr(x, 'custom_object_del_language', None)
            if not object_del_meth:
                continue
            for language in languages:
                try:
                    object_del_meth(language)
                except Exception, exc_error:
                    zLOG.LOG('NySite', zLOG.DEBUG, 'Could not delete language %s for object %s: %s' % (language, x.getId(), exc_error))
                    continue

    def gl_del_site_languages_custom(self, languages):
        #this is called to handle other types of multilanguage objects
        pass

    def gl_change_site_defaultlang(self, language):
        #this is called when site default language is changed
        catalog_tool = self.getCatalogTool()
        self.manage_changeDefaultLang(language)
        self.getLocalizer().manage_changeDefaultLang(language)
        self.getPortalTranslations().manage_changeDefaultLang(language)
        for b in self.getCatalogedBrains():
            x = catalog_tool.getobject(b.data_record_id_)
            try: x.manage_changeDefaultLang(language)
            except: pass
        for x in self.getPortletsTool().get_html_portlets():
            try: x.manage_changeDefaultLang(language)
            except: pass
        self.gl_change_site_defaultlang_custom(language)

    def gl_change_site_defaultlang_custom(self, language):
        #this is called to handle other types of multilanguage objects
        pass

    security.declareProtected(view_management_screens, 'gl_clean_objects_translations')
    def gl_clean_objects_translations(self, prop, lang):
        """
        Method that cleans all empty translations of the I{title}
        property in the given language.
        """
        catalog_tool = self.getCatalogTool()
        for b in self.getCatalogedBrains():
            ob = catalog_tool.getobject(b.data_record_id_)
            p = ob._local_properties.get(prop, None)
            if p:
                t = p.get(lang, None)
                if t:
                    if len(t[0])==0:
                        del ob._local_properties[prop][lang]
                        self.recatalogNyObject(ob)
        return 'gl_clean_objects_translations OK.'

    #layer over NyEpozToolbox XXX
    def getUploadedImages(self): return self.getImagesFolder().objectValues(['Image'])

    security.declareProtected(view, 'process_image_upload')
    def process_image_upload(self, file='', REQUEST=None):
        """ """
        if file != '':
            if hasattr(file, 'filename'):
                if file.filename != '':
                    manage_addImage(self.getImagesFolder(), '', file)
        if REQUEST:
            REQUEST.RESPONSE.redirect('%s?doc_url=%s' % \
                                        (REQUEST['HTTP_REFERER'],
                                         self.utUrlEncode(self.absolute_url()))) # TODO update URL

    security.declareProtected(view, 'process_file_upload')
    def process_file_upload(self, file='', REQUEST=None):
        """ """
        if file != '':
            if hasattr(file, 'filename'):
                if file.filename != '':
                    pos = max(file.filename.rfind('/'), file.filename.rfind('\\'), file.filename.rfind(':'))+1
                    id = file.filename[pos:]
                    ph = file.filename[:pos]
                    while True:
                        try:
                            manage_addFile(self.getImagesFolder(), '', file)
                            break
                        except:
                            rand_id = utils().utGenRandomId(6)
                            file.filename = '%s%s_%s' % (ph, rand_id , id)
        if REQUEST: REQUEST.RESPONSE.redirect('%s' % self.absolute_url()) # TODO update URL

    security.declareProtected(view, 'process_delete')
    def process_delete(self, ids=[], REQUEST=None):
        """ """
        try: self.getImagesFolder().manage_delObjects(self.utConvertToList(ids))
        except: pass
        if REQUEST:
            REQUEST.RESPONSE.redirect('%s' % self.absolute_url()) # TODO update URL

    #site map stuff
    security.declareProtected(view, 'getNavigationSiteMap')
    def getNavigationSiteMap(self, REQUEST=None, **kwargs):
        """ Returns site map in order to be used with extjs library"""
        node = REQUEST.form.get('node', '')
        if not node or node == '__root':
            node = ''

        items = self.getFolderPublishedContent(node)
        folders = items[0]
        documents = items[1]
        res = []
        for folder in folders:
            iconCls = 'custom-%s' % folder.meta_type.replace(' ', '-')
            title = ''
            folder_localized = getattr(folder.aq_base, 'getLocalProperty', None)
            if folder_localized:
                title = folder_localized('title')
            title = title or folder.title_or_id()
            title = self.utStrEscapeHTMLTags(title)
            title = title.replace('"', "'").replace('\r', '').replace('\n', ' ')
            title = self.utToUtf8(title)
            title = self.utJsEncode(title)
            res.append("""{
                "id": "%(id)s",
                "text": "%(title)s",
                "leaf": false,
                "href": "%(href)s",
                "iconCls": "%(iconCls)s"
                }""" % {
                    "id": folder.absolute_url(1),
                    "title": title,
                    "href": '',
                    "iconCls": iconCls,
                })
        for document in documents:
            icon = getattr(document, 'icon', '')
            icon = icon and '/'.join((self.absolute_url(), icon))
            title = ''
            document_localized = getattr(document.aq_base, "getLocalProperty", None)
            if document_localized:
                title = document_localized('title')
            title = title or document.title_or_id()
            title = self.utStrEscapeHTMLTags(title)
            title = title.replace('"', "'").replace('\r', '').replace('\n', ' ')
            title = self.utToUtf8(title)
            title = self.utJsEncode(title)
            res.append("""{
                "id": "%(id)s",
                "text": "%(title)s",
                "leaf": true,
                "href": "%(href)s",
                "icon": "%(icon)s"
                }""" % {
                    "id": document.absolute_url(1),
                    "title": title,
                    "href": '',
                    "icon": icon,
                })
        res = ', '.join(res)
        return '[%s]' % res

    security.declareProtected(view, 'getCompleteNavigationSiteMap')
    def getCompleteNavigationSiteMap(self, REQUEST=None, **kwargs):
        """ Returns site map including unapproved items,
        in order to be used with extjs library"""

        node = REQUEST.form.get('node', '')
        if not node or node == '__root':
            node = ''

        items = self.getFolderContent(node)
        folders = items[0]
        documents = items[1]
        res = []
        for folder in folders:
            iconCls = 'custom-%s' % folder.meta_type.replace(' ', '-')
            if not folder.approved: iconCls += '-marked'
            title = ''
            folder_localized = getattr(folder.aq_base, 'getLocalProperty', None)
            if folder_localized:
                title = folder_localized('title')
            title = title or folder.title_or_id()
            title = self.utStrEscapeHTMLTags(title)
            title = title.replace('"', "'").replace('\r', '').replace('\n', ' ')
            res.append("""{
                "id": "%(id)s",
                "text": "%(title)s",
                "leaf": false,
                "href": "%(href)s",
                "iconCls": "%(iconCls)s"
                }""" % {
                    "id": folder.absolute_url(1),
                    "title": title,
                    "href": '',
                    "iconCls": iconCls,
                })
        for document in documents:
            if document.approved: icon = getattr(document, 'icon', '')
            else: icon = getattr(document, 'icon_marked', '')
            icon = icon and '/'.join((self.absolute_url(), icon))
            title = ''
            document_localized = getattr(document.aq_base, "getLocalProperty", None)
            if document_localized:
                title = document_localized('title')
            title = title or document.title_or_id()
            title = self.utStrEscapeHTMLTags(title)
            title = title.replace('"', "'").replace('\r', '').replace('\n', ' ')
            res.append("""{
                "id": "%(id)s",
                "text": "%(title)s",
                "leaf": true,
                "href": "%(href)s",
                "icon": "%(icon)s"
                }""" % {
                    "id": document.absolute_url(1),
                    "title": title,
                    "href": '',
                    "icon": icon,
                })
        res = ', '.join(res)
        return '[%s]' % res.encode('utf-8')

    security.declareProtected(view, 'getNavigationPhotos')
    def getNavigationPhotos(self, REQUEST=None, **kwargs):
        """ Returns site map with photos only in order to be used with extjs library"""
        node = REQUEST.form.get('node', '')
        if not node or node == '__root':
            node = ''

        items = self.getFolderPublishedContent(node)
        folders = items[0]
        documents = [x for x in items[1] if x.meta_type == 'Naaya Photo']
        res = []
        for folder in folders:
            iconCls = 'custom-%s' % folder.meta_type.replace(' ', '-')
            title = ''
            folder_localized = getattr(folder.aq_base, 'getLocalProperty', None)
            if folder_localized:
                title = folder_localized('title')
            title = title or folder.title_or_id()
            title = self.utStrEscapeHTMLTags(title)
            title = title.replace('"', "'").replace('\r', '').replace('\n', ' ')
            res.append("""{
                "id": "%(id)s",
                "text": "%(title)s",
                "leaf": false,
                "href": "%(href)s",
                "iconCls": "%(iconCls)s"
                }""" % {
                    "id": folder.absolute_url(1),
                    "title": title,
                    "href": '',
                    "iconCls": iconCls,
                })
        for document in documents:
            icon = getattr(document, 'icon', '')
            icon = icon and '/'.join((self.absolute_url(), icon))
            title = ''
            document_localized = getattr(document.aq_base, "getLocalProperty", None)
            if document_localized:
                title = document_localized('title')
            title = title or document.title_or_id()
            title = self.utStrEscapeHTMLTags(title)
            title = title.replace('"', "'").replace('\r', '').replace('\n', ' ')
            res.append("""{
                "id": "%(id)s",
                "text": "%(title)s",
                "leaf": true,
                "href": "%(href)s",
                "icon": "%(icon)s"
                }""" % {
                    "id": document.absolute_url(1),
                    "title": title,
                    "href": '',
                    "icon": icon,
                })
        res = ', '.join(res)
        return '[%s]' % res.encode('utf-8')

    def getSiteMap(self, expand=[], root=None, showitems=0, sort_order=1):
        #returns a list of objects with additional information
        #in order to draw the site map
        if root is None: root = self
        return self.__getSiteMap(root, showitems, expand, 0, sort_order)

    def getSiteMapTrail(self, expand, tree):
        #given a list with all tree nodes, returns a string with all relatives urls
        if expand == 'all': return ','.join([node[0].absolute_url(1) for node in tree])
        else: return expand

    def getFolderPublishedContent(self, folder_path):
        """ return the published content of a folder """
        if folder_path:
            folder_ob = self.restrictedTraverse(folder_path)
            parent = folder_ob.getParentNode()
            if parent == self:
                ppath = ''
            else:
                ppath = parent.absolute_url(1)
            pub_folders = call_method(folder_ob, 'getPublishedFolders', [])
            pub_objects = call_method(folder_ob, 'getPublishedObjects', [])
            return pub_folders, pub_objects, ppath

        objects = []
        for ob in self.objectValues(self.get_naaya_containers_metatypes()):
            if not getattr(ob, 'approved', 0):
                continue
            elif not getattr(ob, 'submitted', 0):
                continue
            else:
                objects.append(ob)

        return objects, [], ''

    def getFolderContent(self, folder_path):
        """ return the content of a folder """
        if folder_path:
            folder_ob = self.restrictedTraverse(folder_path)
            parent = folder_ob.getParentNode()
            if parent == self:
                ppath = ''
            else:
                ppath = parent.absolute_url(1)
            return folder_ob.getFolders(), folder_ob.getObjects(), ppath
        return [x for x in self.objectValues(self.get_naaya_containers_metatypes()) if x.submitted==1], [], ''

    def __getSiteMap(self, root, showitems, expand, depth, sort_order=1):
        #site map core
        l_tree = []
        if root is self: l_folders = [x for x in root.objectValues(self.get_naaya_containers_metatypes()) if x.approved == 1 and x.submitted==1]
        else: l_folders = call_method(root, 'getPublishedFolders', [])
        l_folders = self.utSortObjsListByAttr(l_folders, 'sortorder', sort_order)
        for l_folder in l_folders:
            if (len(l_folder.objectValues(self.get_naaya_containers_metatypes())) > 0) or ((len(l_folder.getObjects()) > 0) and showitems==1):
                if l_folder.absolute_url(1) in expand or 'all' in expand:
                    l_tree.append((l_folder, 0, depth))
                    if showitems:
                        for l_item in call_method(l_folder, 'getPublishedObjects', []):
                            l_tree.append((l_item, -1, depth+1))
                    l_tree.extend(self.__getSiteMap(l_folder, showitems, expand, depth+1, sort_order))
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
    def processFeedbackForm(self, username='', email='', comments='', contact_word='', REQUEST=None):
        """ """
        err = []
        if not self.checkPermissionPublishDirect():
            if contact_word=='' or contact_word!=self.getSession('captcha', None):
                err.append('The word you typed does not match with the one shown in the image. Please try again.')
        if username.strip() == '':
            err.append('The full name is required')
        if email.strip() == '':
            err.append('The email is required')
        if comments.strip() == '':
            err.append('The comments are required')
        if err:
            if REQUEST:
                self.setSessionErrors(err)
                self.setFeedbackSession(username, email, comments)
                return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)
        else:
            self.sendFeedbackEmail(self.administrator_email, username, email, comments)
        if REQUEST:
            self.setSession('title', 'Thank you for your feedback')
            self.setSession('body', 'The administrator will process your comments and get back to you.')
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())

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

    security.declareProtected(view, 'confirm_user')
    def confirm_user(self, key='', REQUEST=None):
        """ Confirm user by string
        """
        try:
            res = self.getAuthenticationTool().manage_confirmUser(key)
        except Exception, err:
            title = err
            body = 'Please make sure that you clicked on the \
            correct link for activating your account as \
            specified in the confirmation email. if the \
            problem persists, try copying the link and \
            pasteing it in the address bar.'
        else:
            title = 'Thank you for registering'
            body = 'An account has been created for you. \
            The administrator will be informed of your request \
            and may or may not grant your account with the \
            approriate role.'
            self.sendCreateAccountEmail(
                p_to=self.administrator_email,
                p_name=res.get('firstname', '') + ' ' + res.get('lastname', ''),
                p_email=res.get('email', ''),
                p_organisation=res.get('organisation', ''),
                p_username=res.get('name', ''),
                p_location_path=self.absolute_url(1),
                p_location_title=self.site_title,
                p_comments=res.get('comments', ''),
                p_template = 'email_requestrole'
            )
        self.setSession('title', title)
        self.setSession('body', body)
        REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())

    security.declareProtected(view, 'processRequestRoleForm')
    def processRequestRoleForm(self, username='', password='', confirm='',
                               firstname='', lastname='', email='',
                               organisation='', location='',
                               comments='', apply_role='contributor', REQUEST=None):
        """
        Sends notification email(s) to the administrators when people apply
        for a role. If the role is requested at portal level, the addresses
        from the 'administrator_email' property get it. If the role is
        requested at folder level, all 'maintainer_email' of the parent folders
        get it and eventually the portal 'administrator_email' gets it if there
        is no 'maintainer_email'
        """
        location_path = 'unspecified'
        location_title = 'unspecified'
        acl_tool = self.getAuthenticationTool()
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
        #if given role is 'contributor', proceed with default behaviour
        if apply_role == 'contributor':
            #create an account without role
            try:
                userinfo = acl_tool.manage_addUser(name=username, password=password,
                           confirm=confirm, roles=[], domains=[], firstname=firstname,
                           lastname=lastname, email=email, strict=0)
            except Exception, error:
                err = error
            else:
                err = ''
            if err:
                if not REQUEST:
                    return err
                self.setSessionErrors(err)
                self.setRequestRoleSession(username, firstname, lastname, email,
                                           password, organisation, comments,
                                           location)
                return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

            if acl_tool.emailConfirmationEnabled():
                self.sendConfirmationEmail(firstname + ' ' + lastname, userinfo, email)
                message_body = 'Plase follow the link in your email in order to complete registration.'
            else:
                self.sendCreateAccountEmail(
                    p_to=location_maintainer_email,
                    p_name=firstname + ' ' + lastname,
                    p_email=email,
                    p_organisation=organisation,
                    p_username=username,
                    p_location_path=location_path,
                    p_location_title=location_title,
                    p_comments=comments,
                    role=apply_role)
                message_body = 'An account has been created for you. \
                The administrator will be informed of your request and may \
                or may not grant your account with the approriate role.'
            if not REQUEST:
                return message_body

        #if given role differs from 'contributor'
        #proceed with customised behaviour
        elif apply_role != 'contributor':
            #get data from user object
            user = acl_tool.getUser(username)
            firstname = acl_tool.getUserFirstName(user)
            lastname = acl_tool.getUserLastName(user)
            email = acl_tool.getUserEmail(user)

            #send administrator email
            self.sendCreateAccountEmail(
                p_to=location_maintainer_email,
                p_name=firstname + ' ' + lastname,
                p_email=email,
                p_organisation=organisation,
                p_username=username,
                p_location_path=location_path,
                p_location_title=location_title,
                p_comments=comments,
                role=apply_role)
            message_body = 'The administrator will be informed of your request '
            'and may or may not grant your account with the approriate role.'
        if not REQUEST:
            return message_body

        self.setSession('title', 'Thank you for registering')
        self.setSession('body', message_body)
        return REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())

    security.declareProtected(view, 'processNotifyOnErrors')
    def processNotifyOnErrors(self, error_type, error_value, REQUEST):
        """ """
        if self.notify_on_errors:
            error_value = str(error_value)
            error_type = str(error_type)
            error_url = REQUEST.get('URL', '')
            error_ip = self.utGetRefererIp(REQUEST)
            error_user = REQUEST.AUTHENTICATED_USER.getUserName()
            error_time = self.utGetTodayDate()
            if self.portal_url != '':
                domain_name = self.portal_url.replace('http://', '').replace('https://','')
                mail_from = 'error@%s' % domain_name
            else: mail_from = 'error@%s' % REQUEST.SERVER_NAME
            self.notifyOnErrorsEmail(self.administrator_email, mail_from,
                                     error_url, error_ip, error_type,
                                     error_value, error_user, error_time)

    #external search
    security.declarePublic('external_search_capabilities')
    def external_search_capabilities(self):
        """
        Returns info about the searches that can be performed.
        """
        return [x['id'] for x in self.gl_get_languages_map()]

    security.declareProtected(view, 'get_remote_servers')
    def get_remote_servers(self):
        #get remote servers
        xconn = XMLRPCConnector(self.http_proxy)
        res = xconn(self.repository_url, 'get_sites')
        if res is None: return {}
        else: return res

    def getNetworkPortals(self):
        #returns the list of user defined network portals
        return self.__network_portals

    security.declareProtected(view, 'getDataForExternalSearch')
    def getDataForExternalSearch(self):
        """
        Returns two lists:
        - a list of languages ids
        - a list of tuples: (url, title) from two lists:
        portals in your network and remote servers. Duplicates
        portal/server urls are removed.
        """
        l, d = {}, {}
        for x in self.get_networkportals_list():
            url, langs = x.url, x.langs
            if url.endswith('/'): url = url[:-1]
            d[url] = {'url': url, 'title': x.title}
            for lang in langs:
                l[lang] = self.gl_get_language_name(lang)
        for x in self.get_remote_servers():
            url, langs = x['url'], x['langs']
            if url.endswith('/'): url = url[:-1]
            d[url] = {'url': url, 'title': x['title']}
            for lang in langs:
                l[lang] = self.gl_get_language_name(lang)
        return l.items(), d.values()

    security.declarePublic('handle_external_search')
    def handle_external_search(self, query, langs, max_items=250):
        """
        Handle an external call: performs the search in the given languages.
        """
        if isinstance(query, unicode): query = query.encode('utf-8')
        r = []
        ra = r.append
        index = 0
        for lang in langs:
            for ob in self.query_objects_ex(q=query, lang=lang):
                if index >= max_items:
                    break
                item = {
                    'url': ob.absolute_url(),
                    'icon': '%s/%s' % (self.REQUEST.SERVER_URL, ob.icon),
                    'meta_type': ob.meta_type,
                    'lang': lang,
                    'title': None,
                    'description': None
                }
                try:
                    description = ob.getLocalProperty('description', lang)
                    if description:
                        #strip all HTML tags from the description and take just
                        #the first 200 characters
                        desc = self.utStripAllHtmlTags(description.encode('utf-8', 'ignore'))[:200]
                        desc = self.utStripMSWordUTF8(desc)
                        # Remove non-ascii unknown chars
                        desc = desc.decode('utf-8', 'ignore').encode('utf-8', 'ignore')
                        item['description'] = desc
                except:
                    pass
                try:
                    title = ob.getLocalProperty('title', lang)
                    if not title:
                        #get title; if it is empty return the id instead
                        title = title.encode('utf-8')
                        if len(title) == 0: title = ob.getId()
                    title = self.utStripMSWordUTF8(title)
                    item['title'] = title
                except:
                    #save id as title
                    item['title'] = ob.getId()
                t = unicode(str(ob.bobobase_modification_time()), 'latin-1').encode('utf-8')
                item['time'] = t
                ra(item)
                index += 1
        return r

    security.declarePublic('external_search')
    def external_search(self, portal_url, query, langs):
        """
        Perform an XMLRPC call to handle this external search
        for the specified portal.
        """
        xconn = XMLRPCConnector(self.http_proxy)
        res = xconn(portal_url, 'handle_external_search', query, langs)
        if res is None: return []
        else: return res

    security.declareProtected(view, 'externalSearch')
    def externalSearch(self, servers=[], langs=[], query='', skey='', rkey='', start=0):
        """ """
        r = []
        rex = r.extend
        try: start = abs(int(start))
        except: start = 0
        if len(query.strip()):
            query = self.utStrEscapeForSearch(query)
            temp = self.utRemoveDuplicates(servers)
            #search in portals in your network
            for portal in self.get_networkportals_list():
                if portal.url in temp:
                    m = self.utListIntersection(portal.langs, langs)
                    if len(m):
                        rex(self.external_search(portal.url, query, m))
                        temp.remove(portal.url)
            #search in repository's portals
            for portal in self.get_remote_servers():
                if portal['url'] in temp:
                    m = self.utListIntersection(portal['langs'], langs)
                    if len(m):
                        rex(self.external_search(portal['url'], query, m))
                        temp.remove(portal['url'])
        batch_obj = batch_utils(self.numberresultsperpage, len(r), start)
        if skey in ['meta_type', 'title', 'lang', 'time']:
            self.utSortListOfDictionariesByKey(r, skey, rkey)
        if len(r):
            paging_informations = batch_obj.butGetPagingInformations()
        else:
            paging_informations = (-1, 0, 0, -1, -1, 0, self.numberresultsperpage, [0])
        return (paging_informations, r[paging_informations[0]:paging_informations[1]])

    security.declareProtected(view, 'internalSearch')
    def internalSearch(self, query='', langs=None, releasedate=None, releasedate_range=None, meta_types=[], skey='', rkey='', start='', path=''):
        """ """
        r = []
        rex = r.extend
        if langs is None: langs = [self.gl_get_selected_language()]
        try: start = int(start)
        except: start = 0
        releasedate = self.utConvertStringToDateTimeObj(releasedate)
        if releasedate_range not in ['min', 'max']: releasedate_range = None
        if releasedate is None: releasedate_range = None
        if len(query.strip()):
            #search in each language
            for lang in langs:
                rex(self.query_objects_ex(meta_types, query, lang, path, releasedate=releasedate, releasedate_range=releasedate_range))
            r = self.utEliminateDuplicatesByURL(r)
            res = [k for k in r if k.can_be_seen()]
            batch_obj = batch_utils(self.numberresultsperpage, len(res), start)
            if skey in ['meta_type', 'title', 'bobobase_modification_time']:
                if skey == 'bobobase_modification_time':
                    res = self.utSortObjsListByMethod(res, skey, rkey)
                else:
                    res = self.utSortObjsListByAttr(res, skey, rkey)
            if len(r):
                paging_informations = batch_obj.butGetPagingInformations()
            else:
                paging_informations = (-1, 0, 0, -1, -1, 0, self.numberresultsperpage, [0])
        return (paging_informations, res[paging_informations[0]:paging_informations[1]])

    security.declareProtected(view, 'process_profile')
    def process_profile(self, firstname='', lastname='', email='', name='', old_pass='', password='',
        confirm='', REQUEST=None):
        """ """
        msg = err = ''
        auth_user = REQUEST.AUTHENTICATED_USER.getUserName()
        user = self.getAuthenticationTool().getUser(auth_user)
        if password == '': password = confirm = old_pass
        if user._getPassword() == old_pass:
            try:
                self.getAuthenticationTool().manage_changeUser(name, password, confirm, [], [], firstname,              lastname, email)
                self.credentialsChanged(name, password)
                #keep authentication
            except Exception, error:
                err = error
            else:
                msg = MESSAGE_SAVEDCHANGES % self.utGetTodayDate()
        else:
            err = WRONG_PASSWORD
        if REQUEST:
            if err != '':self.setSessionErrors([err])
            if msg != '': self.setSessionInfo([msg])
            REQUEST.RESPONSE.redirect('%s/profile_html' % self.absolute_url())

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
    security.declareProtected(view, 'localchannels_rdf')
    def localchannels_rdf(self):
        """
        Returns a RDF feed with all local channels.
        """
        syndication_tool = self.getSyndicationTool()
        r = syndication_tool.get_script_channels()
        r.extend(syndication_tool.get_local_channels())
        return syndication_tool.syndicateSomething(self.absolute_url(), r)

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

    security.declarePublic('hasLeftLogo')
    def hasLeftLogo(self, lang=''):
        """ Returns true if the left logo image from the portal_layout tool is not empty
            and therefore telling if this image should be displayed in the standard header.
            Since older versions of Naaya used 'logo' as the image ID, this is the second choice
        """
        layout_tool = self.getLayoutTool()
        if not lang: lang = self.gl_get_selected_language()
        logo = layout_tool._getOb('logo_%s.gif' % lang, None)
        if logo and logo.size:
            return True
        return False

    security.declarePublic('leftLogo')
    def leftLogo(self, lang='', REQUEST=None):
        """Returns the left logo corresponding to the site language"""
        layout_tool = self.getLayoutTool()
        if not lang: lang = self.gl_get_selected_language()
        logo = layout_tool._getOb('logo_%s.gif' % lang, None)
        if REQUEST:
            REQUEST.RESPONSE.redirect(logo.absolute_url())
        return logo

    security.declarePublic('leftLogo')
    def leftLogoUrl(self, lang=''):
        """Returns the left logo url corresponding to the site language"""
        layout_tool = self.getLayoutTool()
        if not lang: lang = self.gl_get_selected_language()
        logo = layout_tool._getOb('logo_%s.gif' % lang, None)
        if logo and logo.size:
            return logo.absolute_url()

    security.declarePublic('hasRightLogo')
    def hasRightLogo(self, lang=''):
        """ Returns true if the right logo image from the portal_layout tool is not empty
            and therefore telling if this image should be displayed in the standard header.
            Since older versions of Naaya used 'logobis' as the image ID, this is the second choice
        """
        layout_tool = self.getLayoutTool()
        if not lang: lang = self.gl_get_selected_language()
        logo = layout_tool._getOb('logobis_%s.gif' % lang, None)
        if logo and logo.size:
            return True
        return False

    security.declarePublic('rightLogo')
    def rightLogo(self, lang='', REQUEST=None):
        """Returns the right logo corresponding to the site language"""
        layout_tool = self.getLayoutTool()
        if not lang: lang = self.gl_get_selected_language()
        logo = layout_tool._getOb('logobis_%s.gif' % lang, None)
        if REQUEST:
            REQUEST.RESPONSE.redirect(logo.absolute_url())
        return logo

    security.declarePublic('leftLogo')
    def rightLogoUrl(self, lang=''):
        """Returns the right logo url corresponding to the site language"""
        layout_tool = self.getLayoutTool()
        if not lang: lang = self.gl_get_selected_language()
        logo = layout_tool._getOb('logobis_%s.gif' % lang, None)
        if logo and logo.size:
            return logo.absolute_url()

    security.declarePublic('defaultLeftLogoUrl')
    def defaultLeftLogoUrl(self):
        """Returns the url corresponding to the default left site logo"""
        default_logo = self.leftLogoUrl(lang=self.default_logo)
        if not default_logo:
            logo = self.getLayoutTool()._getOb('logo.gif', None)
            if logo is None:
                logo = self.getLayoutTool()._getOb('logo', None)
            if logo and logo.size:
                return logo.absolute_url()
        else:
            return default_logo

    security.declarePublic('defaultRightLogoUrl')
    def defaultRightLogoUrl(self):
        """Returns the url corresponding to the default right site logo"""
        default_logo = self.rightLogoUrl(lang=self.default_logo)
        if not default_logo:
            logo = self.getLayoutTool()._getOb('logobis.gif', None)
            if logo is None:
                logo = self.getLayoutTool()._getOb('logobis', None)
            if logo and logo.size:
                return logo.absolute_url()
        else:
            return default_logo

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_logos')
    def admin_logos(self, logo='', logobis='', del_leftlogo='', del_rightlogo='', default_lang='', lang='', REQUEST=None):
        """ Allows changing and deleting the left and right logos for a Naaya site.
            Left and right logos are independent of the layout chosen and are images called
            'logo.gif' and 'logobis.gif' (or, for older versions of Naaya, 'logo' and 'logobis'
        """
        layouttool = self.getLayoutTool()
        if not lang: lang = self.gl_get_selected_language()

        left_logo_id = 'logo_%s.gif' % lang
        left_logo = layouttool._getOb(left_logo_id, None)
        if left_logo is None:
            layouttool.manage_addImage(id=left_logo_id, file='', title='Site logo')
            left_logo = layouttool._getOb(left_logo_id)
        if logo != '' and hasattr(logo, 'filename') and logo.filename != '':
            content = logo.read()
            if content != '':
                left_logo.update_data(data=content)
                left_logo._p_changed = 1
        if del_leftlogo:
            left_logo.update_data(data='')
            left_logo._p_changed = 1

        right_logo_id = 'logobis_%s.gif' % lang
        right_logo = layouttool._getOb(right_logo_id, None)
        if right_logo is None:
            layouttool.manage_addImage(id=right_logo_id, file='', title='Site logo (right side)')
            right_logo = layouttool._getOb(right_logo_id)
        if logobis != '' and hasattr(logobis, 'filename') and logobis.filename != '':
            content = logobis.read()
            if content != '':
                right_logo.update_data(data=content)
                right_logo._p_changed = 1
        if del_rightlogo:
            right_logo.update_data(data='')
            right_logo._p_changed = 1

        if default_lang:
            self.default_logo = default_lang

        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_logos_html' % self.absolute_url())

    #administration actions
    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_properties')
    def admin_properties(self, REQUEST=None, **kwargs):
        """ Update portal properties.

        The following properties are accepted:
        - show_releasedate: bool;
        - rename_id: bool;
        - submit_unapproved: bool;
        - keywords_glossary: string;
        - coverage_glossary: string;
        - repository_url: string;
        - portal_url: string;
        - http_proxy: string;
        - rdf_max_items: int;
        - switch_language: int;
        """
        if REQUEST:
            kwargs.update(getattr(REQUEST, 'form', {}))

        # Update portal properties
        self.rdf_max_items          = kwargs.get('rdf_max_items', 10)
        self.show_releasedate       = kwargs.get('show_releasedate', 0) and 1 or 0
        self.rename_id              = kwargs.get('rename_id', 0) and 1 or 0
        self.submit_unapproved      = kwargs.get('submit_unapproved', '') and 1 or 0
        self.repository_url         = kwargs.get('repository_url', '')
        self.portal_url             = kwargs.get('portal_url', '')
        self.http_proxy             = kwargs.get('http_proxy', '')
        self.recaptcha_public_key   = kwargs.get('recaptcha_public_key', '')
        self.recaptcha_private_key  = kwargs.get('recaptcha_private_key', '')
        self.switch_language        = kwargs.get('switch_language', 0)
        self.display_contributor    = kwargs.get('display_contributor', '')
        self.display_subobject_count= kwargs.get('display_subobject_count', '')

        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_properties_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_email')
    def admin_email(self, mail_server_name='', mail_server_port='', administrator_email='', mail_address_from='', notify_on_errors='', REQUEST=None):
        """ """
        self.getEmailTool().manageSettings(mail_server_name, mail_server_port, administrator_email, mail_address_from, notify_on_errors)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_email_html' % self.absolute_url())

    #security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'get_maintopics_children')
    def get_maintopics_children(self, first_level='0', foldermetatypes=[METATYPE_FOLDER]):
        """returns a list of tuples, with maintopics and their children, used in notification sitemap form
        (first_level_folder, [the list of children])
        first_level can be one of:
        0 --> only the maintopics will be parsed
        1 --> all firstlevel NaayaFolders will be parsed (approved & not approved)
        2 --> all firstlevel Folders & NaayaFolders will be parsed
        2 --> approved firstlevel Naaya Folders will be parsed
        """
        first_folders_children=[]
        first_level_folders=[]
        if first_level == '0': first_level_folders = self.getMainTopics()
        elif first_level == '1': first_level_folders = self.objectValues(METATYPE_FOLDER)
        elif first_level == '2': first_level_folders = self.objectValues(self.get_containers_metatypes())
        else:
            for x in self.objectValues(foldermetatypes):
                if x.approved: first_level_folders.append(x)
        for x in first_level_folders:
            children = x.objectValues(foldermetatypes)
            first_folders_children.append((x,children))
        return first_folders_children

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_layout')
    def admin_layout(self, theMasterList='', theSlaveList='', REQUEST=None):
        """ """
        if theMasterList == '' or theSlaveList == '':
            pass
        else:
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
        confirm='', strict=0, REQUEST=None):
        """
        Create a user with the specified information
        """
        msg = err = ''
        try:
            userinfo = self.getAuthenticationTool().manage_addUser(name,
                            password, confirm, [], [], firstname, lastname,
                            email, strict)
        except Exception, error:
            err = error
        else:
            msg = MESSAGE_SAVEDCHANGES % self.utGetTodayDate()
        if not REQUEST:
            return userinfo

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
        """
        Update the specified user's information
        """
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

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addrole')
    def admin_addrole(self, role='', permissions=[], REQUEST=None):
        """
        Create a role, with the specified permissions
        """
        msg = err = ''
        try:
            self.getAuthenticationTool().addRole(role, permissions)
        except Exception, error:
            err = error
        else:
            msg = MESSAGE_SAVEDCHANGES % self.utGetTodayDate()
        if REQUEST:
            if err != '':
                self.setSessionErrors([err])
                return REQUEST.RESPONSE.redirect('%s/admin_addrole_html' % self.absolute_url())
            if msg != '':
                self.setSessionInfo([msg])
                return REQUEST.RESPONSE.redirect('%s/admin_users_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_revokeroles')
    def admin_revokeroles(self, roles=[], REQUEST=None):
        """ """
        self.getAuthenticationTool().manage_revokeUsersRoles(roles)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_roles_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addroles')
    def admin_addroles(self, names=[], roles=[], loc='allsite', location='', send_mail='', REQUEST=None):
        """
        Assign the given list of roles to the given list of users at the
        specified location
        """
        msg = err = ''
        names = self.utConvertToList(names)
        if len(names)<=0:
            err = 'An username must be specified'
        else:
            try:
                for name in names:
                    self.getAuthenticationTool().manage_addUsersRoles(name, roles, loc, location)
            except Exception, error:
                err = error
            else:
                msg = MESSAGE_SAVEDCHANGES % self.utGetTodayDate()
            if not err and send_mail:
                auth_tool = self.getAuthenticationTool()
                for name in names:
                    try:
                        email = auth_tool.getUsersEmails([name])[0]
                        fullname = auth_tool.getUsersFullNames([name])[0]
                        self.sendAccountModifiedEmail(email, roles, loc, location)
                    except:
                        err = 'Could not send confirmation mail.'
        if REQUEST:
            if err != '': self.setSessionErrors([err])
            if msg != '': self.setSessionInfo([msg])
            REQUEST.RESPONSE.redirect('%s/admin_roles_html' % self.absolute_url())

    security.declareProtected(view, 'admin_welcome_page')
    def admin_welcome_page(self, REQUEST=None):
        """
        Redirect to welcome page, in this case is the login_html page
        where user's roles in the portal are displayed.
        """
        REQUEST.RESPONSE.redirect('%s/login_html' % self.absolute_url())

    security.declareProtected(PERMISSION_TRANSLATE_PAGES, 'admin_editmessage')
    def admin_editmessage(self, message, language, translation, start, skey, rkey, query, REQUEST=None):
        """ """
        ob = self.getPortalTranslations()
        message_encoded = ob.message_encode(message)
        ob.message_edit(message, language, translation, '')
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_messages_html?msg=%s&start=%s&skey=%s&rkey=%s&query=%s' % \
                (self.absolute_url(), quote(message_encoded), start, skey, rkey, query))

    security.declareProtected(PERMISSION_TRANSLATE_PAGES, 'admin_exportmessages')
    def admin_exportmessages(self, x, REQUEST=None, RESPONSE=None):
        """ """
        return self.getPortalTranslations().manage_export(x, REQUEST, RESPONSE)

    security.declareProtected(PERMISSION_TRANSLATE_PAGES, 'admin_importmessages')
    def admin_importmessages(self, lang, file, REQUEST=None):
        """ """
        if REQUEST:
            if not file:
                self.setSessionErrors(['You must select a file to import.'])
                return REQUEST.RESPONSE.redirect('%s/admin_importexport_html' % self.absolute_url())
            else:
                self.getPortalTranslations().manage_import(lang, file)
                self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
                return REQUEST.RESPONSE.redirect('%s/admin_translations_html' % self.absolute_url())

    security.declareProtected(PERMISSION_TRANSLATE_PAGES, 'admin_exportxliff')
    def admin_exportxliff(self, x, export_all=1, REQUEST=None, RESPONSE=None):
        """ """
        return self.getPortalTranslations().xliff_export(x, export_all, REQUEST, RESPONSE)

    security.declareProtected(PERMISSION_TRANSLATE_PAGES, 'admin_importxliff')
    def admin_importxliff(self, file, REQUEST=None):
        """ """
        if REQUEST:
            if not file:
                self.setSessionErrors(['You must select a file to import.'])
                return REQUEST.RESPONSE.redirect('%s/admin_importexport_html' % self.absolute_url())
            else:
                self.getPortalTranslations().xliff_import(file)
                self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
                return REQUEST.RESPONSE.redirect('%s/admin_translations_html' % self.absolute_url())


    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_deletereflist')
    def admin_deletereflist(self, ids=[], REQUEST=None):
        """ """
        self.getPortletsTool().manage_delObjects(self.utConvertToList(ids))
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_reflists_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addreflist')
    def admin_addreflist(self, id='', title='', description='', REQUEST=None):
        """ """
        self.getPortletsTool().manage_addRefList(id, title, description)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_reflists_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_editreflist')
    def admin_editreflist(self, id='', title='', description='', REQUEST=None):
        """ """
        ob = self.getPortletsTool().getRefListById(id)
        if ob is not None:
            ob.manageProperties(title, description)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_reflist_html?id=%s' % (self.absolute_url(), id))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_deleteitems')
    def admin_deleteitems(self, id='', ids=[], REQUEST=None):
        """ """
        ob = self.getPortletsTool().getRefListById(id)
        if ob is not None:
            ob.manage_delete_items(self.utConvertToList(ids))
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_reflist_html?id=%s' % (self.absolute_url(), id))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_additem')
    def admin_additem(self, id='', item='', title='', REQUEST=None):
        """ """
        ob = self.getPortletsTool().getRefListById(id)
        if ob is not None:
            ob.manage_add_item(item, title)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_reflist_html?id=%s' % (self.absolute_url(), id))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_edititem')
    def admin_edititem(self, id='', item='', title='', REQUEST=None):
        """ """
        ob = self.getPortletsTool().getRefListById(id)
        if ob is not None:
            ob.manage_update_item(item, title)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_reflist_html?id=%s' % (self.absolute_url(), id))

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

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addnetworkportal')
    def admin_addnetworkportal(self, title='', url='', REQUEST=None):
        """ """
        msg, err, res = '', '', None
        xconn = XMLRPCConnector(self.http_proxy)
        if url.endswith('/'): url = url[:-1]
        res = xconn(url, 'external_search_capabilities')
        if res is None:
            err = 'Cannot connect to the given URL.'
        else:
            self.add_networkportal_item(url, title, url, res)
            msg = MESSAGE_SAVEDCHANGES % self.utGetTodayDate()
        if REQUEST:
            if err != '': self.setSessionErrors([err])
            if msg != '': self.setSessionInfo([msg])
            REQUEST.RESPONSE.redirect('%s/admin_network_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_updatenetworkportal')
    def admin_updatenetworkportal(self, id='', REQUEST=None):
        """ """
        msg, err, res = '', '', None
        networkportal = self.get_networkportal_item(id)
        if networkportal:
            xconn = XMLRPCConnector(self.http_proxy)
            res = xconn(networkportal.url, 'external_search_capabilities')
            if res is None:
                err = 'Cannot connect to the given URL.'
            else:
                self.edit_networkportal_item(id, networkportal.title, networkportal.url, res)
                msg = MESSAGE_SAVEDCHANGES % self.utGetTodayDate()
        else:
            err = 'Invalid network portal.'
        if REQUEST:
            if err != '': self.setSessionErrors([err])
            if msg != '': self.setSessionInfo([msg])
            REQUEST.RESPONSE.redirect('%s/admin_network_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_deletenetworkportal')
    def admin_deletenetworkportal(self, ids=[], REQUEST=None):
        """ """
        self.delete_networkportal_item(self.utConvertToList(ids))
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_network_html' % self.absolute_url())

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
    def admin_addmaintopics(self, title='', lang=None, REQUEST=None):
        """ """
        folder_id = addNyFolder(self, title=title, lang=lang)
        folder_ob = self.utGetObject(folder_id)
        folder_ob.approveThis()
        self.maintopics.append(folder_ob.absolute_url(1))
        self._p_changed = 1
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_maintopics_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_updatemaintopics')
    def admin_updatemaintopics(self, folder_url='', REQUEST=None):
        """ """
        if folder_url and folder_url not in self.maintopics:
            self.maintopics.append(folder_url)
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
                    ob = self.getMainTopicByURL(x)
                    ob.sortorder = sortorder
                    ob._p_changed = 1
                    sortorder = sortorder + 1
                except:
                    pass
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_maintopics_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_deletemaintopics')
    def admin_deletemaintopics(self, ids=None, delref=None, REQUEST=None):
        """ """
        if ids is not None: ids = self.utConvertToList(ids)
        else: ids = []
        for id in ids:
            try: self.maintopics.remove(id)
            except: self.log_current_error()

            if not delref: continue
            doc = self.unrestrictedTraverse(id)
            if not doc: continue

            parent = doc.aq_inner.aq_parent
            if not parent: continue
            try: parent.manage_delObjects([doc.getId(),])
            except: self.log_current_error()

        self._p_changed = 1
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_maintopics_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addremotechannel')
    def admin_addremotechannel(self, title='', url='', numbershownitems='', portlet='',
        saveit='', providername='', location='', obtype='', filter_by_language='',
        automatic_translation_portlet='', REQUEST=None):
        """ """
        if saveit:
            self.getSyndicationTool().manage_addRemoteChannelFacade('', title, url, providername,
                location, obtype, numbershownitems, portlet)
        else:
            self.getSyndicationTool().manage_addRemoteChannel('', title, url, numbershownitems, portlet,
                    filter_by_language, automatic_translation_portlet)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_remotechannels_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_editremotechannel')
    def admin_editremotechannel(self, id='', title='', url='', numbershownitems='', filter_by_language='', REQUEST=None):
        """ """
        self.getSyndicationTool().get_channel(id).manageProperties(title, url, numbershownitems, filter_by_language)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_remotechannels_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_editremotechannelfacade')
    def admin_editremotechannelfacade(self, id='', title='', url='', numbershownitems='',
        providername='', location='', obtype='news', REQUEST=None):
        """ """
        self.getSyndicationTool().get_channel(id).manageProperties(title, url,
            providername, location, obtype, numbershownitems)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_remotechannels_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_updateremotechannel')
    def admin_updateremotechannel(self, id='', REQUEST=None):
        """ """
        res = self.getSyndicationTool().get_channel(id).updateChannel(self.get_site_uid())
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

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addremotechannels_aggregator')
    def admin_addremotechannels_aggregator(self, title='', channels=[], portlet='', description='', REQUEST=None):
        """ """
        self.getSyndicationTool().manage_addChannelAggregator('', title, channels, portlet, description)

        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_remotechannels_aggregators_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_editremotechannels_aggregator')
    def admin_editremotechannels_aggregator(self, id='', title='', channels=[], description='', REQUEST=None):
        """ """
        self.getSyndicationTool().get_channel(id).manageProperties(title, channels, description)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_remotechannels_aggregators_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_deleteremotechannel')
    def admin_deleteremotechannels_aggregator(self, ids=[], REQUEST=None):
        """ """
        self.getSyndicationTool().manage_delObjects(self.utConvertToList(ids))
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_remotechannels_aggregators_html' % self.absolute_url())

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
        if ob is not None:
            if ob.meta_type == METATYPE_REMOTECHANNEL:
                self.create_portlet_for_remotechannel(ob)
            elif ob.meta_type == METATYPE_REMOTECHANNELFACADE:
                self.create_portlet_for_remotechannelfacade(ob)
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

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_email_html')
    def admin_email_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_email')

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

    security.declareProtected('View', 'admin_documentation_html')
    def admin_documentation_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_documentation')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_users_html')
    def admin_users_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_users')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_adduser_html')
    def admin_adduser_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_adduser')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_edituser_html')
    def admin_edituser_html(self, REQUEST=None, RESPONSE=None, **kwargs):
        """ """
        kwargs['here'] = self
        return self.getFormsTool().getContent(kwargs, 'site_admin_edituser')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addrole_html')
    def admin_addrole_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_addrole')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_roles_html')
    def admin_roles_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_roles')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_sources_html')
    def admin_sources_html(self, REQUEST=None, RESPONSE=None):
        """ """
        if REQUEST is not None:
            came_from = REQUEST.get('came_from', None)
            if came_from is not None:
                return REQUEST.RESPONSE.redirect(came_from)
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

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_linkslists_html')
    def admin_linkslists_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_linkslists')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_linkslist_html')
    def admin_linkslist_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_linkslist')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_reflists_html')
    def admin_reflists_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_reflists')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_reflist_html')
    def admin_reflist_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_reflist')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_network_html')
    def admin_network_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_network')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_basket_html')
    def admin_basket_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_basket')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_basket_translations_html')
    def admin_basket_translations_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return PageTemplateFile('skel/forms/site_admin_basket_translations', globals()).__of__(self)()

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

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_remotechannels_aggregators_html')
    def admin_remotechannels_aggregators_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_remotechannels_aggregators')
    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_leftportlets_html_old')
    def admin_leftportlets_html_old(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_leftportlets')
    admin_leftportlets_html = redirect_to(
            '%(self_url)s/portal_portlets/admin_layout')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_frontportlets_html_old')
    def admin_frontportlets_html_old(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_frontportlets')
    admin_rightportlets_html = redirect_to(
            '%(self_url)s/portal_portlets/admin_layout')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_rightportlets_html_old')
    def admin_rightportlets_html_old(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_rightportlets')

    admin_leftportlets_html = redirect_to(
            '%(self_url)s/portal_portlets/admin_layout')

    admin_rightportlets_html = redirect_to(
            '%(self_url)s/portal_portlets/admin_layout')

    admin_frontportlets_html = redirect_to(
            '%(self_url)s/portal_portlets/admin_layout')

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

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_notifications_html')
    def admin_notifications_html(self, REQUEST):
        """ redirect to new notifications admin page """
        notification_tool_url = self.getNotificationTool().absolute_url()
        return REQUEST.RESPONSE.redirect(notification_tool_url + '/admin_html')

    #others
    def get_localch_noportlet(self):
        return [x for x in self.getSyndicationTool().get_local_channels() if not self.exists_portlet_for_object(x)]

    def get_remotech_noportlet(self):
        syndicationtool_ob = self.getSyndicationTool()
        l = syndicationtool_ob.get_remote_channels()
        l.extend(syndicationtool_ob.get_remote_channels_facade())
        return [x for x in l if not x.exists_portlet_for_object(x)]

    def get_linkslists_noportlet(self):
        return [x for x in self.getPortletsTool().getLinksLists() if not x.exists_portlet_for_object(x)]

    def checkPermissionForLink(self, name, context):
        #checks the given group of permissions in the given context
        if name != '': return self.getAuthenticationTool().checkGroupPermission(name, context)
        else: return 1

    def checkPermissionAddFolders(self, context):
        """
        Check for adding folders permission in the given context.
        """
        return context.checkPermission(PERMISSION_ADD_FOLDER)

    def list_glossaries(self):
        #this method can be overwritten
        return self.objectValues(['Naaya Glossary', 'Naaya Thesaurus'])

    def get_keywords_glossary(self):
        # TODO: deprecate and remove this
        try: return self._getOb(self.keywords_glossary)
        except: return None

    def get_coverage_glossary(self):
        # TODO: deprecate and remove this
        try: return self._getOb(self.coverage_glossary)
        except: return None

    security.declareProtected(PERMISSION_PUBLISH_DIRECT, 'publish_direct')
    def publish_direct(self):
        raise NotImplemented

    security.declareProtected(view, 'getCaptcha')
    def getCaptcha(self):
        """ generate a Captcha image """
        g = captcha_tool()
        g.defaultSize = (100, 20)
        i = g.render()
        newimg = StringIO()
        i.save(newimg, "JPEG")
        newimg.seek(0)
        #set the word on session
        self.setSession('captcha', g.solutions[0])
        return newimg.getvalue()

    #sending emails
    def sendConfirmationEmail(self, name, confirm_key, mto):
        # Send confirmation email
        param = urllib.urlencode({'key': confirm_key})
        portal_url = self.portal_url or self.absolute_url()
        link = portal_url + '/confirm_user?' + param
        info = {'NAME': name,
                'PORTAL_TITLE': self.site_title,
                'PORTAL_URL': portal_url,
                'LINK': link,
                'SENDER_NAME': self.site_title + ' team',
            }
        etool = self.getEmailTool()
        template = etool._getOb('email_confirmuser')
        msubj = template.title
        mbody = template.body % info
        mfrom = self.mail_address_from or self.administrator_email or \
              'no-reply@' + portal_url.replace('http:', '', 1
                            ).replace('/', '').replace('www.', '')
        etool.sendEmail(mbody, mto, mfrom, msubj)

    def sendAccountCreatedEmail(self, p_name, p_email, p_username, REQUEST, p_roles=[]):
        #sends a confirmation email to the newlly created account's owner
        email_template = self.getEmailTool()._getOb('email_createaccount')
        l_subject = email_template.title
        l_content = email_template.body
        l_content = l_content.replace('@@PORTAL_URL@@', self.portal_url)
        l_content = l_content.replace('@@PORTAL_TITLE@@', self.site_title)
        l_content = l_content.replace('@@NAME@@', p_name)
        l_content = l_content.replace('@@USERNAME@@', p_username)
        l_content = l_content.replace('@@EMAIL@@', p_email)
        l_content = l_content.replace('@@TIMEOFPOST@@', str(self.utGetTodayDate()))
        mail_from = self.mail_address_from
        self.getEmailTool().sendEmail(l_content, p_email, mail_from, l_subject)

    def sendAccountModifiedEmail(self, email, roles, loc, location):
        #sends an email informing the user about the modifications to its account
        emailtool_ob = self.getEmailTool()
        email_template = emailtool_ob._getOb('email_modifyaccount', None)
        #if the needed email template doesn't exist, create it from the filesystem
        if not email_template:
            try:
                content = self.futRead(join(NAAYA_PRODUCT_PATH, 'skel', 'emails', 'email_modifyaccount.txt'), 'r')
                emailtool_ob.manage_addEmailTemplate('email_modifyaccount', 'Account modified notification', content)
            except: return
        email_template = emailtool_ob._getOb('email_modifyaccount', None)

        #make sure roles is a list
        if type(roles) != type([]): roles = [roles]
        roles = ', '.join(roles)
        #append roles location
        if loc == "other" and location:
            roles = "%s locally in %s." % (roles, location.absolute_url(1))
        else:
            roles = "%s for the entire portal." % roles

        #construct mail
        subject = email_template.title
        content = email_template.body
        content = content.replace('@@PORTAL_TITLE@@', self.site_title)
        content = content.replace('@@PORTAL_URL@@', self.portal_url)
        content = content.replace('@@ROLES@@', roles)

        #send mail
        mail_from = self.mail_address_from
        self.getEmailTool().sendEmail(content, email, mail_from, subject)

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

    def sendCreateAccountEmail(self, p_to, p_name, p_email, p_organisation,
                            p_username, p_location_path,
                            p_location_title, p_comments, **kwargs):

        role = kwargs.get('role')
        #sends a request role email
        email_template = self.getEmailTool()._getOb('email_requestrole')
        l_subject = email_template.title
        l_content = email_template.body
        l_content = l_content.replace('@@NAME@@', p_name)
        l_content = l_content.replace('@@EMAIL@@', p_email)
        l_content = l_content.replace('@@ORGANISATION@@', p_organisation)
        l_content = l_content.replace('@@USERNAME@@', p_username)
        l_content = l_content.replace('@@LOCATIONPATH@@', p_location_path)
        l_content = l_content.replace('@@ROLE@@', role)
        if p_location_path:
            l_content = l_content.replace('@@LOCATION@@', "the %s folder (%s/%s)" % (p_location_title, self.portal_url, p_location_path))
        else:
            l_content = l_content.replace('@@LOCATION@@', 'entire portal')
        l_content = l_content.replace('@@COMMENTS@@', p_comments)
        l_content = l_content.replace('@@PORTAL_URL@@', self.portal_url)
        l_content = l_content.replace('@@PORTAL_TITLE@@', self.site_title)
        l_content = l_content.replace('@@TIMEOFPOST@@', str(self.utGetTodayDate()))
        self.getEmailTool().sendEmail(l_content, p_to, p_email, l_subject)

    def notifyMaintainerEmail(self, p_to, p_from, p_item, p_container_path, p_container_basketpath, p_template='email_notifyonupload', **kwargs):
        #notify folder maintainer when a new upload is done
        user = self.REQUEST.AUTHENTICATED_USER
        user_name = user.getUserName()
        atool = self.getAuthenticationTool()
        try:
            user_email = atool.getUserEmail(user)
        except:
            user_email = ''
        email_template = self.getEmailTool()._getOb(p_template)
        l_subject = email_template.title
        l_content = email_template.body
        l_content = l_content.replace('@@USERNAME@@', user_name)
        l_content = l_content.replace('@@USEREMAIL@@', user_email)
        l_content = l_content.replace('@@ITEMTITLEORID@@', p_item.title_or_id())
        l_content = l_content.replace('@@CONTAINERPATH@@', p_container_path)
        l_content = l_content.replace('@@UPLOADTIME@@', str(self.utShowFullDateTime(self.utGetTodayDate())))
        if (hasattr(p_item, 'approved') and p_item.approved == 0):
            l_content = l_content.replace('@@CONTAINERBASKETPATH@@', p_container_basketpath)
        else:
            l_content = self.utRemoveLineInString('@@CONTAINERBASKETPATH@@', l_content)
        self.getEmailTool().sendEmail(l_content, p_to, p_from, l_subject)

    def log_current_error(self):
        """ Log the current error (from sys.exc_info) into the site's error_log """
        import sys
        self.error_log.raising(sys.exc_info())

    #pluggable content
    def get_pluggable_content(self):
        #information about the available types
        return naaya.content.base.discover.get_pluggable_content()

    def get_pluggable_metatypes(self):
        return self.get_pluggable_content().keys()

    def get_pluggable_metatypes_validation(self):
        #returns a list with all meta_types for validation process
        return [x['meta_type'] for x in self.get_pluggable_content().values() if x['validation'] == 1]

    def get_pluggable_item(self, meta_type):
        return self.get_pluggable_content().get(meta_type, None)

    def get_pluggable_installed_meta_types(self):
        return self.__pluggable_installed_content.keys()

    def is_pluggable_item_installed(self, meta_type):
        return self.__pluggable_installed_content.has_key(meta_type)

    #pluggable meta types properties
    def get_pluggable_item_properties_ids(self, meta_type):
        if meta_type in ('Naaya Folder',):
            #XXX: Hardcoded
            return ['title', 'description', 'coverage', 'keywords', 'sortorder',
                    'releasedate', 'maintainer_email']
        if self.is_pluggable_item_installed(meta_type):
            return self.get_pluggable_content().get(meta_type, None)['properties'].keys()
        return []

    def get_pluggable_item_properties_item(self, meta_type, prop):
        return self.get_pluggable_content().get(meta_type, None)['properties'][prop]

    def get_pluggable_item_property_mandatory(self, meta_type, prop):
        if self.is_pluggable_item_installed(meta_type):
            return self.get_pluggable_content().get(meta_type, None)['properties'][prop][0]
        return 0

    def check_pluggable_item_properties(self, meta_type, **args):
        l = []
        la = l.append
        translate = self.getPortalTranslations().translate
        for k, v in self.get_pluggable_content().get(meta_type, None)['properties'].items():
            if v[0] == 1 or v[1]:   #this property is mandatory
                if args.has_key(k):    #property found in parameters list
                    value = args.get(k)
                    if v[1] == MUST_BE_NONEMPTY:
                        if self.utIsEmptyString(value): la(translate('', v[2]))
                    elif v[1] == MUST_BE_DATETIME:
                        if not self.utIsValidDateTime(value): la(translate('', v[2]))
                    elif v[1] == MUST_BE_DATETIME_STRICT:
                        if self.utIsEmptyString(value) or not self.utIsValidDateTime(value):
                            la(translate('', v[2]))
                    elif v[1] == MUST_BE_POSITIV_INT:
                        if not self.utIsAbsInteger(value): la(translate('', v[2]))
                    elif v[1] == MUST_BE_POSITIV_FLOAT:
                        if not value or not self.utIsFloat(value, positive=0): la(translate('', v[2]))
                    elif v[1] == MUST_BE_CAPTCHA:
                        if value != self.getSession('captcha', '') and not self.checkPermissionPublishDirect(): la(translate('', v[2]))
                    elif v[1] == MUST_BE_FLVFILE:
                        if not (value and value.headers.get("content-type", "") in [
                            "application/x-flash-video", "video/x-flv"]):
                            la(translate('', v[2]))
                    elif v[1] == MUST_BE_VIDEOFILE:
                        # TODO: Handle this
                        pass
        return l

    def set_pluggable_item_session(self, meta_type, **args):
        for l_prop in self.get_pluggable_item_properties_ids(meta_type):
            self.setSession(l_prop, args.get(l_prop, ''))

    def del_pluggable_item_session(self, meta_type):
        for l_prop in self.get_pluggable_item_properties_ids(meta_type):
            self.delSession(l_prop)

    security.declareProtected(view_management_screens, 'manage_install_pluggableitem')
    def manage_install_pluggableitem(self, meta_type=None, REQUEST=None):
        """
        Makes the content with the given meta_type available for usage in the portal.
        Raises ValueError if content does not exist.
        If the content specifies an `on_install` function in it's `config`
        this method will call `[on_install](self)`
        """
        data_path = join(self.get_data_path(), 'skel', 'forms')
        if meta_type is not None:
            pitem = self.get_pluggable_item(meta_type)
            if pitem == None:
                raise ValueError('Missing pluggable content type "%s"' % meta_type)

            #create Schema for this content type, if there is none
            if ID_SCHEMATOOL in self.objectIds():
                # if the site is just being created, there's no schema tool yet; move on, the
                # schemas will be created later.
                schema_tool = self._getOb(ID_SCHEMATOOL)
                if pitem['module'] not in schema_tool.objectIds() and pitem['default_schema']:
                    schema_tool.addSchema(pitem['module'], title=pitem['label'], defaults=pitem['default_schema'])

            #add content's permission to `Add content` permission group
            acl = self.getAuthenticationTool()
            acl.manage_group_permission('Add content', pitem['permission'], 'add')

            #run `on_install` function if defined in content's `config`
            if 'on_install' in pitem:
                pitem['on_install'](self)

            #remember that this meta_type was installed
            self.__pluggable_installed_content[meta_type] = 1
            self.searchable_content.append(meta_type)
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
            self.searchable_content = [x for x in self.searchable_content if x != meta_type]
            #remove content's permission from `Add content` permission group
            acl = self.getAuthenticationTool()
            acl.manage_group_permission('Add content', pitem['permission'], 'remove')
            self._p_changed = 1
        if REQUEST: REQUEST.RESPONSE.redirect('%s/manage_controlpanel_html' % self.absolute_url())

    def is_logged(self, REQUEST=None):
        """ """
        if not REQUEST:
            REQUEST = self.REQUEST
        return REQUEST.AUTHENTICATED_USER.getUserName() != 'Anonymous User'

    #methods to be runned by OS scheduler - crond
    def updateRemoteChannels(self, uid):
        """
        Used by cron tools to update the remote channels.

        @param uid: site uid
        @type uid: string
        """
        if uid==self.get_site_uid():
            syndicationtool_ob = self.getSyndicationTool()
            for c in syndicationtool_ob.get_remote_channels():
                c.updateChannel(uid)
            for c in syndicationtool_ob.get_remote_channels_facade():
                c.updateChannel(uid)
            return "Update Remote Channels ended successfully on site %s" % self.absolute_url()

    def cleanupUnsubmittedObjects(self, uid):
        """
        Used by cron tools to clean up unsubmitted objects older than 1 day.

        @param uid: site uid
        @type uid: string
        """
        if uid==self.get_site_uid():
            today = self.utGetTodayDate()
            catalog_tool = self.getCatalogTool()
            for x in self.getCatalogedUnsubmittedObjects():
                if x.bobobase_modification_time() + 1 < today:
                    #delete only unsubmitted objects older than 1 day
                    x.getParentNode().manage_delObjects([x.id])
            return "Clean up unsubmitted objects ended successfully on site %s" % self.absolute_url()

    #xxx delete messages // for internal administration
    security.declareProtected(PERMISSION_TRANSLATE_PAGES, 'admin_delmsg')
    def admin_delmsg(self, messages=[], REQUEST=None):
        """ """
        ob = self.getPortalTranslations()
        messages = self.utConvertToList(messages)
        for message in messages:
            ob.message_del(message)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_delmesg_html' % self.absolute_url())

    security.declareProtected(PERMISSION_TRANSLATE_PAGES, 'admin_delmesg_html')
    def admin_delmesg_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_delmessages')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'send_mail_to_roles')
    def send_mail_to_roles(self, mail_subject, mail_body, mails, REQUEST=None):
        """
        Sends bulk mail with the specified subject and body to
        all email addresses in 'mails'
        """
        for mail in mails:
            self.getEmailTool().sendEmail(mail_body, mail, self.mail_address_from, mail_subject)

        if REQUEST:
            self.setSessionInfo(['Mail sent. (%s)' % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_bulk_mail_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'export_contacts_vcard')
    def export_contacts_vcard(self, REQUEST=None):
        """ Exports all portal contacts in vCard format contained in a zip file """
        contacts = self.getCatalogedObjects(meta_type=['Naaya Contact'])
        files = [vcard_file(contact.id, contact.export_vcard()) for contact in contacts]
        if REQUEST:
            return self.utGenerateZip('%s-contacts.zip' % self.id, files, self.REQUEST.RESPONSE)
        else: return files

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'import_contacts_vcard')
    def import_contacts_vcard(self, vcard_zipfile, location, REQUEST=None):
        """ Import contacts in vCard format from a zip file """
        from naaya.content.contact.contact_item import addNyContact, parse_vcard_data
        container = self.restrictedTraverse(location)
        errors = []
        infos = []
        objects_created = 0
        vcard_zip = ZipFile(vcard_zipfile)
        for filename in vcard_zip.namelist():
            data = vcard_zip.read(filename)
            try:
                contact_data = parse_vcard_data(data)
            except:
                errors.append('Error parsing "%s"' % filename)
            else:
                objects_created += 1
                contact_data['title'] = '%s %s' % (
                    contact_data['firstname'], contact_data['lastname'])
                addNyContact(container, **contact_data)

        if objects_created:
            import transaction
            transaction.get().note('Imported %d Naaya Contact objects' % objects_created)
            infos.append('Imported %d contact objects' % objects_created)

        if REQUEST is not None:
            self.setSessionErrors(errors)
            self.setSessionInfo(infos)
            return REQUEST.RESPONSE.redirect('%s/admin_contacts_html' % self.absolute_url())

    security.declareProtected(view, 'recaptcha_is_present')
    def recaptcha_is_present(self):
        return self.recaptcha_private_key and self.recaptcha_public_key

    security.declareProtected(view, 'show_recaptcha')
    def show_recaptcha(self, context):
        """ Returns HTML code for reCAPTCHA """
        return recaptcha_utils.render_captcha(context)

    security.declareProtected(view, 'is_valid_recaptcha')
    def is_valid_recaptcha(self, context, REQUEST):
        """ Test if reCaptcha is valid. """
        return recaptcha_utils.is_valid_captcha(context, REQUEST)

    security.declareProtected(view, 'validateCaptcha')
    def validateCaptcha(self, contact_word, REQUEST):
        """ Validates captcha or recaptcha, returns errors if invalid """

        if self.recaptcha_is_present():
            if not self.is_valid_recaptcha(self, REQUEST):
                return ['Verification words do not match the ones in the picture.']
        else:
            if contact_word != self.getSession('captcha', ''):
                self.delSession('captcha')
                return ['The word you typed does not match with the one shown in the image. Please try again.']

    security.declareProtected(view, 'HEAD')
    def HEAD(self, REQUEST=None):
        """ """
        modified = self.bobobase_modification_time()
        return self.REQUEST.RESPONSE.setHeader('Last-Modified', modified)

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_controlpanel_html')
    manage_controlpanel_html = PageTemplateFile('zpt/site_manage_controlpanel', globals())

    security.declareProtected(view, 'macro_manage_add')
    macro_manage_add = PageTemplateFile('zpt/site_macro_manage_add', globals())

    security.declareProtected(view, 'macro_manage_edit')
    macro_manage_edit= PageTemplateFile('zpt/site_macro_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'standard_html_header')
    def standard_html_header(self, REQUEST=None, RESPONSE=None):
        """ """
        context = self.REQUEST.PARENTS[0]
        return self.getLayoutTool().getContent({'here': context}, 'site_header').split('<!--SITE_HEADERFOOTER_MARKER-->')[0]

    security.declareProtected(view, 'standard_html_footer')
    def standard_html_footer(self, REQUEST=None, RESPONSE=None):
        """ """
        context = self.REQUEST.PARENTS[0]
        return self.getLayoutTool().getContent({'here': context}, 'site_footer').split('<!--SITE_HEADERFOOTER_MARKER-->')[1]

    security.declareProtected(view, 'standard_error_message')
    def standard_error_message(self, client=None, REQUEST=None, **kwargs):
        """ """
        context = self.REQUEST.PARENTS[0]
        kwargs['here'] = context
        return self.getFormsTool().getContent(kwargs, 'standard_error_message')

    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_index')

    security.declareProtected(view, 'messages_html')
    def messages_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_messages')

    security.declareProtected(view, 'messages_box')
    def messages_box(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'messages_box')

    security.declareProtected(view, 'languages_box')
    def languages_box(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'languages_box')

    security.declareProtected(view, 'form_languages_box')
    def form_languages_box(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'form_languages_box')

    security.declarePublic('login_html')
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

    security.declareProtected(view, 'sitemap_add_html')
    def sitemap_add_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'sitemap_add')

    security.declareProtected(view, 'feedback_html')
    def feedback_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_feedback')

    security.declareProtected(view, 'requestrole_html')
    def requestrole_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self.REQUEST.PARENTS[0]}, 'site_requestrole')

    security.declareProtected(view, 'profile_html')
    def profile_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_userprofile')

    security.declareProtected(view, 'channel_details_html')
    def channel_details_html(self, REQUEST=None, RESPONSE=None, **kwargs):
        """ """
        kwargs['here'] = self
        return self.getFormsTool().getContent(kwargs, 'channel_details')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_bulk_mail_html')
    def admin_bulk_mail_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return PageTemplateFile('skel/forms/admin_bulk_mail', globals()).__of__(self)()

    #calendar widget
    security.declareProtected(view, 'calendar_js')
    calendar_js = DTMLFile('zpt/calendar/calendar_js', globals())

    security.declareProtected(view, 'core_js')
    core_js = DTMLFile('zpt/calendar/core_js', globals())

    security.declareProtected(view, 'datetime_js')
    datetime_js = DTMLFile('zpt/calendar/datetime_js', globals())

    #common javascript
    security.declareProtected(view, 'common_js')
    common_js = DTMLFile('zpt/common_js', globals())
    #
    # Macro libs
    #
    security.declareProtected(view, 'folder_lib_toolbar_buttons')
    folder_lib_toolbar_buttons = PageTemplateFile(
        'zpt/folder_lib_toolbar_buttons', globals())

    security.declareProtected(view, 'folder_listing')
    folder_listing = PageTemplateFile(
        'zpt/folder_listing', globals())

    security.declareProtected(PERMISSION_ADD_FOLDER, 'folder_add_html')
    folder_add_html = folder_add_html
    security.declareProtected(PERMISSION_ADD_FOLDER, 'addNyFolder')
    addNyFolder = addNyFolder

    security.declareProtected(view, 'macro_utils')
    macro_utils = PageTemplateFile('zpt/site_macro_utils', globals())

    csv_import = CSVImportTool('csv_import')
    csv_export = CSVExportTool('csv_export')

    #--------------------------------------------------------------------------------------------------
    security.declareProtected(view_management_screens, 'update_portal_forms')
    def update_portal_forms(self):
        """ """
        skel_path = join(NAAYA_PRODUCT_PATH, 'skel')
        formstool_ob = self.getFormsTool()
        portal_forms = {'site_admin_users': 'Portal administration - users'}
        for k, v in portal_forms.items():
            content = self.futRead(join(skel_path, 'forms', '%s.zpt' % k), 'r')
            form_ob = formstool_ob._getOb(k, None)
            if form_ob is None:
                continue
            form_ob.pt_edit(text=content, content_type='')
        return 'done'

    common_css = ImageFile('www/common.css', globals())
    print_css = ImageFile('www/print.css', globals())
    style_css = ImageFile('www/style.css', globals())

    def additional_style_css(self, REQUEST):
        """ """
        REQUEST.RESPONSE.setHeader('Content-Type', 'text/css')
        return self.getLayoutTool().getNaayaContentStyles()

    notifications_subscribe = Subscriber('notifications_subscribe')

    def heartbeat_work(self, REQUEST=None):
        """ does a heartbeat work on this site """
        if REQUEST is not None:
            raise Unauthorized

        hb = Heartbeat()
        component.handle(self, hb)

    def heartbeat(self):
        """ if cooldown has passed does a heartbeat """

        path = '/'.join(self.getPhysicalPath())
        if heartbeat_cooldown.has_key(path) and\
            datetime.now() < heartbeat_cooldown[path]:
                return

        heartbeat_cooldown[path] = datetime.now() + timedelta(minutes=10)
        self.heartbeat_work()

    def manage_check_heartbeat(self):
        """ return the time of the last heartbeat """

        path = '/'.join(self.getPhysicalPath())
        if heartbeat_cooldown.has_key(path):
            last_heartbeat = heartbeat_cooldown[path] - timedelta(minutes=10)
            time_ever_since = datetime.now() - last_heartbeat
            minutes_ever_since = int(time_ever_since.seconds / 60)
            seconds_ever_since = time_ever_since.seconds % 60
            last_heartbeat = last_heartbeat.strftime('%d %B %Y %H:%M:%S')
            return 'Time of last heartbeat: %s (%s minutes and %s seconds ago)'\
                % (last_heartbeat, minutes_ever_since, seconds_ever_since)
        return 'The heart did not beat since last system restart.'

    # functions for translation
    def translate(self, *args):
        return translate(*args)

    def translate_url(self, *args):
        return translate_url(*args)

    def get_helper(self):
        return NaayaTemplateHelper(ny_site=self)

    @property
    def helper(self):
        return NaayaTemplateHelper(ny_site=self)

    helper = NaayaTemplateHelper()

InitializeClass(NySite)

heartbeat_cooldown = {}

class Heartbeat(object):
    interface.implements(IHeartbeat)
    def __init__(self):
        self.when = datetime.now()

