import urllib
try:
    import json
except ImportError:
    import simplejson as json
from os.path import join
from urllib import quote
from zipfile import ZipFile
from datetime import datetime, timedelta
from urlparse import urlparse
import logging
import time
import os
import operator

import zLOG
from OFS.Folder import Folder
from OFS.Image import manage_addImage
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate import manage_addPageTemplate
from AccessControl import ClassSecurityInfo, Unauthorized
from AccessControl.Permission import Permission
from AccessControl.Permissions import view_management_screens, view
from AccessControl.Permissions import change_permissions
from ZPublisher import BeforeTraverse
from Products.SiteErrorLog.SiteErrorLog import manage_addErrorLog
from Globals import DTMLFile
from zope.interface import implements
from App.ImageFile import ImageFile
from zope import component
import transaction
from zope.deprecation import deprecate
from zope.app.component.site import LocalSiteManager, SiteManagerContainer
from App.config import getConfiguration
import pytz
from zope.event import notify

from interfaces import INySite, IActionLogger
from action_logger import ActionLogger
from constants import *
from Products.NaayaBase.constants import *
from Products.NaayaCore.constants import *
import naaya.content.base
from naaya.content.base.meta import get_schema_name
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
from Products.NaayaCore.LayoutTool.DiskFile import manage_addDiskFile
from Products.NaayaCore.LayoutTool.DiskTemplate import manage_addDiskTemplate
from Products.NaayaCore.NotificationTool.NotificationTool import manage_addNotificationTool
from Products.NaayaCore.EditorTool.EditorTool import manage_addEditorTool
from Products.NaayaCore.GeoMapTool.GeoMapTool import manage_addGeoMapTool
from Products.NaayaCore.SchemaTool.SchemaTool import manage_addSchemaTool
from Products.NaayaCore.GoogleDataTool.AnalyticsTool import manage_addAnalyticsTool

from Products.NaayaBase.NyBase import NyBase
from Products.NaayaBase.NyImportExport import NyImportExport
from Products.NaayaBase.NyPermissions import NyPermissions
from Products.NaayaBase.NyImageContainer import NyImageContainer
from Products.NaayaBase.NyCommonView import NyCommonView
from Products.NaayaCore.managers.utils import utils, list_utils, batch_utils, file_utils
from Products.NaayaCore.managers.catalog_tool import catalog_tool
from Products.NaayaCore.managers.urlgrab_tool import urlgrab_tool
from Products.NaayaCore.managers.search_tool import search_tool
from Products.NaayaCore.managers.session_manager import session_manager
from Products.NaayaCore.managers.xmlrpc_tool import XMLRPCConnector
from Products.NaayaCore.managers.utils import vcard_file
from Products.NaayaCore.managers.import_export import (CSVImportTool,
                                                       ExportTool, UnicodeReader)
from Products.NaayaCore.managers.zip_import_export import ZipImportTool, ZipExportTool
from Products.NaayaCore.managers.rdf_calendar_utils import rdf_cataloged_items
from Products.NaayaCore.PropertiesTool.managers.contenttypes_tool import contenttypes_tool
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from Products.Localizer.Localizer import manage_addLocalizer
from Products.Localizer.LocalPropertyManager import LocalPropertyManager, LocalProperty
from managers.skel_parser import skel_parser
from managers.networkportals_manager import networkportals_manager
from Products.NaayaBase.managers.import_parser import import_parser
from NyVersions import NyVersions
from NyFolder import folder_add_html, addNyFolder, importNyFolder
from Products.NaayaBase.gtranslate import translate, translate_url
from NyFolderBase import NyFolderBase
from naaya.core.utils import call_method, cooldown, is_ajax
from naaya.core.zope2util import path_in_site, ofs_path
from naaya.core.zope2util import permission_add_role
from naaya.core.zope2util import redirect_to
from naaya.core.exceptions import ValidationError
from Products.NaayaBase.NyRoleManager import NyRoleManager

from naaya.core.StaticServe import StaticServeFromZip, StaticServeFromFolder
from naaya.component import bundles

from events import NyPluggableItemInstalled

log = logging.getLogger(__name__)

MAINTOPICS_SETTINGS = {
    'expanded': True,
    'persistent': True,
    'expand_levels': 1,
    'max_levels': 1
}

# Other modules can alter these 2 lists. E.g.: CHMSite appends METATYPE_CHMSITE
CONTAINERS_METATYPES = \
    [METATYPE_NYSITE, METATYPE_FOLDER, 'Folder', 'Naaya Photo Gallery',
     'Naaya Photo Folder', 'Naaya Forum', 'Naaya Forum Topic',
     'Naaya Consultation', 'Naaya Simple Consultation',
     'Naaya TalkBack Consultation', 'Naaya Survey Questionnaire']

NAAYA_CONTAINERS_METATYPES = \
    [METATYPE_NYSITE, METATYPE_FOLDER, 'Naaya Photo Gallery',
     'Naaya Photo Folder', 'Naaya Forum', 'Naaya Forum Topic',
     'Naaya Consultation', 'Naaya Simple Consultation',
     'Naaya TalkBack Consultation', 'Naaya Survey Questionnaire']

#constructor
manage_addNySite_html = PageTemplateFile('zpt/site_manage_add', globals())
def manage_addNySite(self, id='', title='', lang=None, default_content=True, REQUEST=None):
    """ """
    ut = utils()
    id = ut.utSlugify(id)
    if not id: id = PREFIX_SITE + ut.utGenRandomId(6)
    self._setObject(id, NySite(id, title, lang))
    ob = self._getOb(id)
    ob.createPortalTools()
    if default_content:
        ob.loadDefaultData()
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class NySite(NyRoleManager, NyCommonView, CookieCrumbler, LocalPropertyManager,
             Folder, NyBase, NyPermissions, NyImportExport, NyVersions, utils,
             list_utils, file_utils, catalog_tool, search_tool,
             contenttypes_tool, session_manager, portlets_manager,
             networkportals_manager, NyFolderBase):
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
    display_subobject_count_for_admins = ""
    default_logo = ''
    content_versioning_enabled = True
    notify_on_errors_email = ''

    _Delete_objects_Permission = ['Administrator']

    www = StaticServeFromFolder("www", globals())

    def __init__(self, id, title='', lang=None):
        """ """
        self.id = id

        #Set local site manager
        sm = LocalSiteManager(self)

        #This was done because Zope2 setSiteManager does not set the ISite
        #interface which is needed to do component lookup in site managers.
        SiteManagerContainer.setSiteManager.im_func(self, sm)
        self.setSiteManager(sm)

        #Set up a default bundle for this site
        bundle = bundles.get('Naaya')
        self.set_bundle(bundle)

        self.__portal_uid = '%s_%s' % (PREFIX_SITE, self.utGenerateUID())
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
        self.notify_on_errors_email = ''
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
        self.maintopics_settings = MAINTOPICS_SETTINGS
        self.keywords_glossary = None
        self.coverage_glossary = None
        self.__pluggable_installed_content = {}
        self.show_releasedate = 1
        self.rename_id = 0
        self.nyexp_schema = NYEXP_SCHEMA_LOCATION
        # Allow users to move current language content to another language.
        self.switch_language = 0
        # Choose whether or not the contributor should be displayed
        self.display_contributor = "on"
        self.display_subobject_count = ""
        self.display_subobject_count_for_admins = ""
        self.default_logo = ''
        contenttypes_tool.__dict__['__init__'](self)
        CookieCrumbler.__dict__['__init__'](self)
        catalog_tool.__dict__['__init__'](self)
        search_tool.__dict__['__init__'](self)
        portlets_manager.__dict__['__init__'](self)
        networkportals_manager.__dict__['__init__'](self)

    security.declarePrivate('get_bundle')
    def get_bundle(self):
        """ Get current Naaya bundle"""
        return self.getSiteManager().__bases__[0]

    security.declarePrivate('set_bundle')
    def set_bundle(self, bundle):
        """ Setup a bundle for this site. This tells the site manager that
        it's parent is the bundle. Without the bundle the resolution of
        components will be like this::

            Local Site Manager -> Global Site Manager

        Using bundles the resolution looks like this::

            Local Site Manager -> Naaya Bundle -> Global Site Manager

        """
        self.getSiteManager().__bases__ = (bundle,)

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
        manage_addEditorTool(self)
        manage_addGeoMapTool(self)
        manage_addAnalyticsTool(self)
        manage_addErrorLog(self)
        manage_addSchemaTool(self)

    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self):
        """ """

        sm = self.getSiteManager()
        #Register Action Logger utility
        sm.registerUtility(ActionLogger(), IActionLogger)

        # initially, nobody can skip approval process
        self._set_submit_unapproved(True)

        #load default skeleton
        self.loadSkeleton(NAAYA_PRODUCT_PATH)
        #set default main topics
        self.getPropertiesTool().manageMainTopics(['info'])
        self.imageContainer = NyImageContainer(self.getImagesFolder(), False)

    skel_handler_cache = {}

    security.declarePrivate('get_skel_handler')
    def get_skel_handler(self, product_path, enable_cache=True):
        if enable_cache and product_path in self.skel_handler_cache:
            return self.skel_handler_cache[product_path]

        skel_path = join(product_path, 'skel')
        skel_content = self.futRead(join(skel_path, 'skel.xml'), 'r')
        skel_handler, error = skel_parser().parse(skel_content)
        if error:
            zLOG.LOG('NySite.loadSkeleton', zLOG.ERROR, error)
            raise ValueError('error parsing skel.xml')

        skel_handler.skel_path = skel_path

        self.skel_handler_cache[product_path] = skel_handler
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

            #load pluggable content types
            if skel_handler.root.pluggablecontenttypes is not None:
                for pluggablecontenttype in skel_handler.root.pluggablecontenttypes.pluggablecontenttypes:
                    try: action = abs(int(pluggablecontenttype.action))
                    except: action = 1
                    meta_type = pluggablecontenttype.meta_type
                    if self.get_pluggable_item(meta_type) is None:
                        log.info("Skipping pluggable content type %r "
                                 "because it's not available", meta_type)
                        continue
                    if action == 0:
                        self.manage_uninstall_pluggableitem(meta_type=meta_type)
                    else:
                        self.manage_install_pluggableitem(meta_type=meta_type)

            #load security permissions and roles
            if skel_handler.root.security is not None:
                for role in skel_handler.root.security.roles:
                    if role.name not in self.__ac_roles__:
                        authenticationtool_ob.addRole(role.name)
                    for permission in role.permissions:
                        permission_add_role(self, permission.name, role.name)

            #load properties
            if skel_handler.root.properties is not None:
                for language in skel_handler.root.properties.languages:
                    properties_tool.manage_addLanguage(language.code)
                for contenttype in skel_handler.root.properties.contenttypes:
                    content = self.futRead(join(skel_path, 'contenttypes', contenttype.picture), 'rb')
                    self.createContentType(contenttype.id, contenttype.title, content)
            #forms are loaded from disk at runtime; they can be customized in portal_forms.
            #load skins
            layout = skel_handler.root.layout
            if layout is not None:
                def layout_diskpath_prefix():
                    assert layout.diskpath_prefix is not None, ("Please set a "
                            "`diskpath_prefix` attribute on the <layout> tag")
                    return layout.diskpath_prefix

                for skin in skel_handler.root.layout.skins:
                    if not layouttool_ob._getOb(skin.id, None):
                        layouttool_ob.manage_addSkin(id=skin.id, title=skin.title)
                    skin_ob = layouttool_ob._getOb(skin.id)
                    for template in skin.templates:
                        content = self.futRead(join(skel_path, 'layout', skin.id, '%s.zpt' % template.id), 'r')
                        if not skin_ob._getOb(template.id, None):
                            skin_ob.manage_addTemplate(id=template.id, title=template.title, file='')
                        skin_ob._getOb(template.id).pt_edit(text=content, content_type='')
                    for style in skin.styles:
                        content = self.futRead(join(skel_path, 'layout', skin.id, '%s.css' % style.id), 'r')
                        if skin_ob._getOb(style.id, None):
                            skin_ob.manage_delObjects([style.id])
                        skin_ob.manage_addStyle(id=style.id, title=style.title, file=content)
                    if skin.images:
                        if not skin_ob._getOb('images', None):
                            skin_ob.manage_addFolder(id='images', title='Images common to all schemes contained in this skin.')
                        images_folder = skin_ob._getOb('images')
                        for image in skin.images:
                            content = self.futRead(join(skel_path, 'layout', skin.id, 'images', image.id), 'rb')
                            if not images_folder._getOb(image.id, None):
                                images_folder.manage_addImage(id=image.id, file='', title=image.title)
                            image_ob = images_folder._getOb(image.id)
                            image_ob.update_data(data=content)
                            image_ob._p_changed=1

                    for diskfile in skin.diskfiles:
                        manage_addDiskFile(skin_ob, pathspec='/'.join([
                            layout_diskpath_prefix(),
                            'layout',
                            skin.id,
                            diskfile.path ]), id=(diskfile.id or ''))

                    for disktemplate in skin.disktemplates:
                        manage_addDiskTemplate(skin_ob, pathspec='/'.join([
                            layout_diskpath_prefix(),
                            'layout',
                            skin.id,
                            disktemplate.path ]), id=(disktemplate.id or ''))

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

                        for file in scheme.files:
                            content = self.futRead(join(skel_path, 'layout', skin.id, scheme.id, file.id), 'rb')
                            if not scheme_ob._getOb(file.id, None):
                                scheme_ob.manage_addFile(id=file.id, file='', title=file.title)
                            file_ob = scheme_ob._getOb(file.id)
                            file_ob.update_data(data=content)
                            file_ob._p_changed=1

                        for diskfile in scheme.diskfiles:
                            manage_addDiskFile(scheme_ob, pathspec='/'.join([
                                layout_diskpath_prefix(),
                                'layout',
                                skin.id,
                                scheme.id,
                                diskfile.path ]), id=(diskfile.id or ''))

                        for disktemplate in scheme.disktemplates:
                            manage_addDiskTemplate(scheme_ob, pathspec='/'.join([
                                layout_diskpath_prefix(),
                                'layout',
                                skin.id,
                                scheme.id,
                                disktemplate.path ]), id=(disktemplate.id or ''))

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
                    ch_type = self.utEmptyToNone(channel.type)
                    body = self.futRead(join(skel_path, 'syndication', '%s.py' % channel.id), 'r')
                    channel_ob = syndicationtool_ob._getOb(channel.id, None)
                    if channel_ob is None:
                        syndicationtool_ob.manage_addScriptChannel(channel.id, channel.title, channel.description, language, ch_type, body, channel.numberofitems, channel.portlet)
                        channel_ob = syndicationtool_ob._getOb(channel.id)
                    else:
                        channel_ob.write(body)
                    if channel.portlet:
                        content = self.futRead(join(skel_path, 'syndication', '%s.zpt' % channel.id), 'r')
                        portletstool_ob._getOb('%s%s' % (PREFIX_PORTLET, channel.id)).pt_edit(text=content, content_type='')
                for channel in skel_handler.root.syndication.localchannels:
                    language = self.utEmptyToNone(channel.language)
                    ch_type = self.utEmptyToNone(channel.type)
                    syndicationtool_ob.manage_addLocalChannel(channel.id, channel.title, channel.description, language, ch_type, channel.objmetatype.split(','), channel.numberofitems, 1)
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
                        portletstool_ob.manage_addRefTree(reflist.id, reflist.title, reflist.description)
                        reflist_ob = portletstool_ob._getOb(reflist.id)
                    else:
                        reflist_ob.manage_delObjects(reflist_ob.objectIds())
                    for item in reflist.items:
                        reflist_ob.manage_addRefTreeNode(item.id, item.title)
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

                if skel_handler.root.portlets.inherit:
                    # this can have 'left', 'right', 'center' and also portlet_ids
                    inherit_portlets = set(skel_handler.root.portlets.inherit.split(','))
                else:
                    # default inherit just left portlets (as it was before)
                    inherit_portlets = set(['left'])
                if skel_handler.root.portlets.left:
                    for portlet_id in portletstool_ob.get_portlet_ids_for('', 'left'):
                        portletstool_ob.unassign_portlet('', 'left', portlet_id)
                    for portlet_id in skel_handler.root.portlets.left.split(','):
                        inherit = (('left' in inherit_portlets)
                                or (portlet_id in inherit_portlets))
                        portletstool_ob.assign_portlet('', "left", portlet_id, inherit)
                if skel_handler.root.portlets.center:
                    for portlet_id in portletstool_ob.get_portlet_ids_for('', 'center'):
                        portletstool_ob.unassign_portlet('', 'center', portlet_id)
                    for portlet_id in skel_handler.root.portlets.center.split(','):
                        inherit = (('center' in inherit_portlets)
                                or (portlet_id in inherit_portlets))
                        portletstool_ob.assign_portlet('', "center", portlet_id, inherit)
                if skel_handler.root.portlets.right:
                    for portlet_id in portletstool_ob.get_portlet_ids_for('', 'right'):
                        portletstool_ob.unassign_portlet('', 'right', portlet_id)
                    for portlet_id in skel_handler.root.portlets.right.split(','):
                        inherit = (('right' in inherit_portlets)
                                or (portlet_id in inherit_portlets))
                        portletstool_ob.assign_portlet('', "right", portlet_id, inherit)
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

    security.declareProtected(view, 'getActionLogger')
    def getActionLogger(self):
        return component.getUtility(IActionLogger, context=self)

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

    security.declarePublic('get_label_for_meta_type')
    def get_label_for_meta_type(self, meta_type):
        """Returns the label associated with the given meta_type
        it can be a Naaya Folder or a pluggable content type

        .. warning::
            This function should not be used in new code.
            Please use Products.Naaya.NyFolderBase.get_meta_type_label
            instead.

        """
        if meta_type == METATYPE_FOLDER:
            return LABEL_NYFOLDER
        else:
            try: return self.getSchemaTool().getSchemaForMetatype(meta_type).title_or_id()
            except: return meta_type

    security.declarePublic('getProductsMetaTypes')
    def getProductsMetaTypes(self):
        """returns a list with all meta types"""

        return [x['name'] for x in self.filtered_meta_types()]

    def get_data_path(self):
        """
        Returns the path to the data directory.
        All classes that extends I{NySite} B{must} overwrite
        this method.
        """
        return NAAYA_PRODUCT_PATH

    security.declarePublic('get_timezone')
    def get_timezone(self):
        """
        Returns a string representing portal timezone. For example::

            'Europe/Copenhagen', 'CET'

        Try, in order:
            1. zope-conf-additional in buildout
            2. os.environ
            3. time.tzname

        """
        conf = getConfiguration()
        if conf.environment.has_key('TZ') and conf.environment['TZ']:
            return conf.environment['TZ']
        elif os.environ.has_key('TZ') and os.environ['TZ']:
                return os.environ['TZ']
        elif len(time.tzname):
            return time.tzname[0]
        else:
            # Fallback
            return 'Europe/Copenhagen'

    security.declarePublic('get_tzinfo')
    def get_tzinfo(self):
        return pytz.timezone(self.get_timezone())

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
    @deprecate('DynamicPropertiesTool is deprecated. Use SchemaTool instead.')
    def getDynamicPropertiesTool(self):
        return self._getOb(ID_DYNAMICPROPERTIESTOOL)

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

    security.declarePublic('getNotificationTool')
    def getNotificationTool(self): return self._getOb(ID_NOTIFICATIONTOOL)

    security.declarePublic('getEditorTool')
    def getEditorTool(self): return self._getOb(ID_EDITORTOOL)

    security.declarePublic('getAnalyticsTool')
    def getAnalyticsTool(self): return self._getOb(ID_ANALYTICSTOOL)

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
    security.declarePublic('getNotificationToolPath')
    def getNotificationToolPath(self, p=0): return self._getOb(ID_NOTIFICATIONTOOL).absolute_url(p)
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
        l_result = []
        while l_parent.meta_type != self.meta_type:
            l_result.append(l_parent)
            l_parent = l_parent.getParentNode()
        l_result.reverse()
        return l_result

    security.declarePublic('get_containers')
    def get_containers(self):
        #this method returns all container type that can be used in an export operation
        return [x for x in self.objectValues(METATYPE_FOLDER) if x.submitted==1]

    security.declarePublic('getObjectById')
    def getObjectById(self, p_id):
        """ Get an object with a given `p_id` from `self` container"""
        return self._getOb(p_id, None)

    security.declarePublic('get_containers_metatypes')
    def get_containers_metatypes(self):
        """
        Get meta_type-s which are containers.
        List defined in :mod:`Products.Naaya.NySite`.

        """
        return list(CONTAINERS_METATYPES)

    security.declarePublic('get_naaya_containers_metatypes')
    def get_naaya_containers_metatypes(self):
        """
        Get meta_type-s which are containers (Naaya content types only).
        List defined in :mod:`Products.Naaya.NySite`.

        """
        return list(NAAYA_CONTAINERS_METATYPES)

    #layer over selection lists
    def get_list_nodes(self, list_id):
        """ Return a list with the items of the selection
        list, first try RefLists then try RefTrees"""
        ptool = self.getPortletsTool()
        try:
            return ptool.getRefListById(list_id).get_list()
        except:
            try:
                tree_thread = ptool.getRefTreeById(list_id).get_tree_thread()
                return [x['ob'] for x in tree_thread]
            except:
                return []

    def get_node_title(self, list_id, node_id):
        ptool = self.getPortletsTool()
        try:
            return ptool.getRefListById(list_id).get_item(node_id).title
        except:
            try:
                return ptool.getRefTreeById(list_id)[node_id].title
            except:
                return ''

    security.declarePublic('getEventTypesList')
    def getEventTypesList(self):
        """
        Return the selection list for event types.
        """
        return self.get_list_nodes('event_types')

    def getEventTypeTitle(self, id):
        """
        Return the title of an item for the selection list for event types.
        """
        return self.get_node_title('event_types', id)

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
        Returns the list of main topic folder objects
        """
        return filter(lambda ob: ob is not None,
                      (self.utGetObject(path) for path in self.maintopics))

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
        return self.getEmailTool().get_addr_from()

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
                mail_from = self.getEmailTool().get_addr_from()
                self.notifyMaintainerEmail(l_emails, mail_from, p_object, p_folder.absolute_url(), '%s/basketofapprovals_html' % p_folder.absolute_url(), **kwargs)

    def processDynamicProperties(self, meta_type, REQUEST=None, keywords={}):
        """ """
        output = {}
        for l_prop in self.getDynamicPropertiesTool().getDynamicProperties(meta_type):
            try: output[l_prop.id] = REQUEST.get(l_prop.id, keywords.get(l_prop.id, ''))
            except: output[l_prop.id] = ''

        return output

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

    # Generating AjaxTree sitemap
    security.declareProtected(view, 'getNavigationSiteMap')
    def getNavigationSiteMap(self, REQUEST=None, all=False, only_folders=False,
                             **kwargs):
        """
        Return JSON tree of the sitemap
        Used with javascript tree libraries
        """
        node = REQUEST.form.get('node', '')
        if not node or node == '/':
            node = ''

        def recurse(items, level=0, stop_level=2):
            """ Create a dict with node properties and children """
            res = []
            for item in items:
                if (only_folders is not False and
                    item.meta_type != METATYPE_FOLDER):
                    continue
                children_items = []
                if level != stop_level:
                    node = path_in_site(item)
                    if all: items = self.getFolderContent(node)
                    else: items = self.getFolderPublishedContent(node)
                    children_items = recurse(
                        items[0]+items[1],
                        level+1,
                        stop_level
                    )
                res.append(dict(
                    data = dict(
                        title=self.utStrEscapeHTMLTags(self.utToUtf8(item.title_or_id())),
                        icon=item.approved and item.icon or item.icon_marked
                    ),
                    attributes=dict(
                        title=path_in_site(item)
                    ),
                    children = children_items
                ))
            return res

        if all: items = self.getFolderContent(node)
        else: items = self.getFolderPublishedContent(node)
        ret = recurse(items[0]+items[1])

        #Adding the portal if we are in root
        if not node or node == '/':
            ret = {
                'attributes': {
                    'title': '/'
                },
                'data': {
                    'icon': self.icon,
                    'title': self.title
                },
                'children': ret
            }
        return json.dumps(ret)

    security.declareProtected(view, 'getCompleteNavigationSiteMap')
    def getCompleteNavigationSiteMap(self, REQUEST=None, **kwargs):
        """ Returns site map including unapproved items,
        in order to be used to display a tree"""
        self.getNavigationSiteMap(REQUEST=REQUEST, all=True, **kwargs)

    security.declareProtected(view, 'getNavigationPhotos')
    def getNavigationPhotos(self, REQUEST=None, **kwargs):
        """
        XXX: Not used in Naaya.. should be removed
        Returns site map with photos only in order to be used with extjs library
        """
        node = REQUEST.form.get('node', '')
        if not node or node == '/':
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
        l_folders = self.utSortObjsListByAttr(l_folders, 'title', sort_order)
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

    def getSiteMapTree(self, obj, showitems, expand, sort_order=1):
        """ return the tree of obj's children
            (with levels expanded according to parameters """
        output = {'ob': obj, 'has_children': False}
        if obj.meta_type == 'Naaya Folder':
            objects_list = obj.getFolders()
            if showitems:
                objects_list += obj.getObjects()
        elif obj is self or obj.meta_type in self.get_naaya_containers_metatypes():
            objects_list = obj.objectValues(self.get_naaya_containers_metatypes())
        else:
            objects_list = None

        if objects_list:
            output['has_children'] = True
            if expand=='all' or path_in_site(obj) in expand:
                children=[]
                for ob in objects_list:
                    children.append(self.getSiteMapTree(ob, showitems, expand, sort_order=sort_order))
                output['children'] = children

        return output

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
                err.append(('The word you typed does not match with the one shown in the image. Please try again.', ))
        if username.strip() == '':
            err.append('The full name is required')
        if email.strip() == '':
            err.append('The email is required')
        if comments.strip() == '':
            err.append('The comments are required')
        if err:
            if REQUEST:
                self.setSessionErrorsTrans(err)
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
                self.setSessionErrorsTrans(err)
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
                err = unicode(error)
            else:
                err = ''
            if err:
                if not REQUEST:
                    return err
                self.setSessionErrorsTrans(err)
                self.setRequestRoleSession(username, firstname, lastname, email,
                                           password, organisation, comments,
                                           location)
                return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

            if acl_tool.emailConfirmationEnabled():
                self.sendConfirmationEmail(firstname + ' ' + lastname, userinfo, email)
                message_body = 'Please follow the link in your email in order to complete the registration.'
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
            user_info = acl_tool.get_user_info(username)

            #send administrator email
            self.sendCreateAccountEmail(
                p_to=location_maintainer_email,
                p_name=user_info.full_name,
                p_email=user_info.email,
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

    security.declarePublic('processNotifyOnErrors')
    def processNotifyOnErrors(self, error_type, error_value, REQUEST):
        """ """
        ignored_exceptions = self.error_log.getProperties()['ignored_exceptions']
        if error_type not in ignored_exceptions and self.notify_on_errors_email:
            if self.portal_url != '':
                domain_name = self.portal_url.replace('http://', '').replace('https://','')
                mail_from = 'error@%s' % domain_name
            else: mail_from = 'error@%s' % urlparse(REQUEST.SERVER_URL)[1]
            self.notifyOnErrorsEmail(p_to = self.notify_on_errors_email,
                                    p_from = mail_from,
                                    p_error_url = REQUEST.get('URL', ''),
                                    p_error_ip = self.utGetRefererIp(REQUEST),
                                    p_error_type = str(error_type),
                                    p_error_value = str(error_value),
                                    p_error_user = REQUEST.AUTHENTICATED_USER.getUserName(),
                                    p_error_time = self.utGetTodayDate())

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
                        desc = self.html2text(description.encode('utf-8', 'ignore'), trim_length=200)
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
    def internalSearch(self, query='', langs=None, releasedate=None,
                        releasedate_range=None, meta_types=[], skey='', rkey='',
                        path=''):
        """ """
        object_list = []

        if langs is None:
            langs = [self.gl_get_selected_language()]

        releasedate = self.utConvertStringToDateTimeObj(releasedate)
        if releasedate_range not in ['min', 'max']:
            releasedate_range = None
        if releasedate is None:
            releasedate_range = None

        # no query
        if releasedate is None and not query.strip():
            return {'object_list': None, 'error': None}

        if not query.strip():
            query = None # because query_brains_ex expects None for no query

        #search in each language
        brains_list = []
        for lang in langs:
            try:
                lang_brains = self.query_brains_ex(meta_types, query, lang,
                                                   path,
                                                   releasedate=releasedate,
                                                   releasedate_range=releasedate_range)
                brains_list.extend(lang_brains)
            except Exception, e:
                return {'object_list': None, 'error': unicode(e)}
        brains_list = self.utEliminateDuplicateBrains(brains_list)
        object_list = self.safe_getobjects(brains_list)

        # filter results
        object_list = [k for k in object_list if k.can_be_seen()]

        # sort results
        if skey == 'bobobase_modification_time':
            object_list = self.utSortObjsListByMethod(object_list, skey, rkey)
        elif skey in ['meta_type', 'title']:
            object_list = self.utSortObjsListByAttr(object_list, skey, rkey)
        return {'object_list': object_list, 'error': None}

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
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
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
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_logos_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_set_glossary_ids')
    def admin_set_glossary_ids(self, keywords=None, coverage=None, REQUEST=None):
        """ Change glossary widget for all content types """

        self.keywords_glossary = keywords
        self.coverage_glossary = coverage

        for schema in self.getSchemaTool().objectValues():
            for widget in schema.listWidgets():
                prop_name = widget.prop_name()

                if prop_name == 'keywords':
                    widget.glossary_id = keywords
                elif prop_name == 'coverage':
                    widget.glossary_id = coverage
                else:
                    continue

        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_glossaries_html' % self.absolute_url())


    def _set_submit_unapproved(self, submit_unapproved):
        if submit_unapproved:
            # permission will not be acquired and is granted to nobody
            Permission(PERMISSION_SKIP_APPROVAL, (), self).setRoles(())
        else:
            permission_add_role(self, PERMISSION_SKIP_APPROVAL, 'Administrator')
            permission_add_role(self, PERMISSION_SKIP_APPROVAL, 'Manager')

    def get_submit_unapproved(self):
        """ do administrators have the "skip approval" permission? """
        roles = Permission(PERMISSION_SKIP_APPROVAL, (), self).getRoles()
        return bool('Administrator' not in roles)

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
        self._set_submit_unapproved(kwargs.get('submit_unapproved', ''))
        self.repository_url         = kwargs.get('repository_url', '')
        self.portal_url             = kwargs.get('portal_url', '')
        self.http_proxy             = kwargs.get('http_proxy', '')
        self.recaptcha_public_key   = kwargs.get('recaptcha_public_key', '')
        self.recaptcha_private_key  = kwargs.get('recaptcha_private_key', '')
        self.switch_language        = kwargs.get('switch_language', 0)
        self.display_contributor    = kwargs.get('display_contributor', '')
        self.display_subobject_count= kwargs.get('display_subobject_count', '')
        self.display_subobject_count_for_admins= kwargs.get('display_subobject_count_for_admins', '')

        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_properties_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_email')
    def admin_email(self, mail_server_name='', mail_server_port='', administrator_email='', mail_address_from='', notify_on_errors_email='', REQUEST=None):
        """ """
        self.getEmailTool().manageSettings(mail_server_name, mail_server_port, administrator_email, mail_address_from, notify_on_errors_email)
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
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
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_layout_html' % self.absolute_url())

    def get_naaya_permissions_in_site(self):
        """ Return list of permissions relevant to this portal. """
        permission_map = {}
        for pluggable in self.get_pluggable_content().values():
            meta_type = pluggable['meta_type']
            if not self.is_pluggable_item_installed(meta_type):
                continue
            zope_perm = pluggable['permission']
            if '_class' in pluggable:
                meta_label = pluggable['_class'].meta_label
            else:
                meta_label = meta_type
            title = "Submit %s objects" % meta_label
            description = "Create new content items of type \"%s\"" % meta_type
            permission_map[zope_perm] = {
                'title': title,
                'description': description,
                'zope_permission': zope_perm,
            }
        permission_map.update(_naaya_known_permissions)

        return permission_map

    #
    # Admin User management. XXX: Should be moved to AuthenticationTool
    #

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_adduser')
    def admin_adduser(self, firstname='', lastname='', email='', name='',
                      password='', confirm='', strict=0, REQUEST=None):
        """
        Create a user with the specified information. Also check if the
        username is not assigned in some source.
        """
        err = ''
        success = False
        try:
            userinfo = self.getAuthenticationTool().manage_addUser(name,
                            password, confirm, [], [], firstname, lastname,
                            email, strict)
        except ValidationError, error:
            err = error
        else:
            success = True

        if REQUEST is not None:
            if err != '':
                self.setSessionErrorsTrans(err)
                self.setUserSession(name, [], [], firstname, lastname, email,
                                    '')
                REQUEST.RESPONSE.redirect('%s/admin_adduser_html' %
                                          self.absolute_url())
            if success:
                self.setSessionInfoTrans("User added")
                REQUEST.RESPONSE.redirect('%s/admin_local_users_html' %
                                          self.absolute_url())
        else:
            return userinfo

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_edituser')
    def admin_edituser(self, firstname='', lastname='', email='', name='',
                       password='', confirm='', REQUEST=None):
        """
        Update the specified user's information
        """
        err = ''
        success = True
        try:
            self.getAuthenticationTool().manage_changeUser(name, password,
                            confirm, [], [], firstname, lastname, email)
        except ValidationError, error:
            err = error
            success = False

        if REQUEST is not None:
            if err != '':
                self.setSessionErrorsTrans(err)
                self.setUserSession(name, [], [], firstname, lastname, email,
                                    '')
            if success is True:
                self.setSessionInfoTrans("User edited")
            REQUEST.RESPONSE.redirect('%s/admin_edituser_html?name=%s' %
                                      (self.absolute_url(), name))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_deleteusers')
    def admin_deleteusers(self, names=[], REQUEST=None):
        """ """
        if REQUEST is not None:
            redirect_url = REQUEST.environ.get('HTTP_REFERER',
                                '%s/admin_users_html' % self.absolute_url())
        if len(names):
            self.getAuthenticationTool().manage_delUsers(names)
        else:
            if REQUEST is not None:
                self.setSessionErrorsTrans("Please select a user")
                return REQUEST.RESPONSE.redirect(redirect_url)

        if REQUEST is not None:
            self.setSessionInfoTrans("User(s) successfully deleted")
            REQUEST.RESPONSE.redirect(redirect_url)

    #Admin User Roles
    security.declareProtected(change_permissions, 'admin_addrole')
    def admin_addrole(self, role='', REQUEST=None):
        """ Create a role, redirect to edit permissions page """
        err = ''
        success = False
        try:
            self.getAuthenticationTool().addRole(role)
        except ValidationError, error:
            err = error
        else:
            success = True

        if REQUEST:
            if err != '':
                self.setSessionErrorsTrans(err)
                return REQUEST.RESPONSE.redirect('%s/admin_roles_html' %
                                                 self.absolute_url())
            if success:
                self.setSessionInfoTrans("Role added")
                return REQUEST.RESPONSE.redirect('%s/admin_roles_html' %
                                                 self.absolute_url())

    security.declareProtected(change_permissions, 'admin_editrole_html')
    def admin_editrole_html(self, role, REQUEST):
        """ """
        permission_list = self.get_naaya_permissions_in_site().values()
        permission_list.sort(key=operator.itemgetter('title'))

        zope_perm_for_role = {}
        for perm in permission_list:
            zope_perm = perm['zope_permission']
            p = Permission(zope_perm, (), self)
            zope_perm_for_role[zope_perm] = bool(role in p.getRoles())

        tmpl = self.getFormsTool().getForm('site_admin_editrole').__of__(self)
        options = {
            'role': role,
            'permission_list': permission_list,
            'zope_perm_for_role': zope_perm_for_role,
        }
        return tmpl(REQUEST, **options)

    security.declareProtected(change_permissions, 'admin_editrole')
    def admin_editrole(self, role, zope_perm_list=[], REQUEST=None):
        """ Change the permissions of a role """

        for zope_perm in self.get_naaya_permissions_in_site():
            p = Permission(zope_perm, (), self)
            perm_roles = set(p.getRoles())

            if zope_perm in zope_perm_list:
                perm_roles.add(role)
            else:
                perm_roles.discard(role)

            ty = type(p.getRoles())
            p.setRoles(ty(perm_roles))

        if REQUEST is not None:
            self.setSessionInfoTrans("Role edited")
            REQUEST.RESPONSE.redirect('%s/admin_roles_html' %
                                      self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addroles')
    def admin_addroles(self, names=[], roles=[], location='', send_mail='',
                       redirect='', REQUEST=None):
        """
        XXX: Should be assign_roles

        Assign a list of roles to a list of users at the specified location
        optionally sending a notification e-mail

        """
        err = ''
        success = False
        names = self.utConvertToList(names)
        if len(names)<=0:
            err = 'A username must be specified'
        else:
            try:
                for name in names:
                    self.getAuthenticationTool().manage_addUsersRoles(name,
                                                            roles, location)
            except ValidationError, error:
                err = error
            else:
                success = True
            if not err and send_mail:
                auth_tool = self.getAuthenticationTool()
                for name in names:
                    try:
                        email = auth_tool.getUsersEmails([name])[0]
                        fullname = auth_tool.getUsersFullNames([name])[0]
                        if location == "/" or location == '':
                            loc, location = 'all', self.getSite()
                        else:
                            loc, location = 'other', self.unrestrictedTraverse(location, None)
                        self.sendAccountModifiedEmail(email, roles,
                                                      loc, location)
                    except:
                        err = 'Could not send confirmation mail.'

        if REQUEST is not None:
            if redirect != '':
                redirect_url = redirect
            else:
                redirect_url = ('%s/admin_local_users_html' %
                                self.absolute_url())
            if err != '':
                self.setSessionErrorsTrans(err)
                REQUEST.RESPONSE.redirect(
                    REQUEST.environ.get('HTTP_REFERER', redirect_url))
            elif success:
                self.setSessionInfoTrans("Role(s) successfully assigned")
                REQUEST.RESPONSE.redirect(redirect_url)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_revokerole')
    def admin_revokerole(self, user, location, REQUEST=None):
        """ Can be called via normal or ajax request.
        Returns empty string on ajax
        """
        self.getAuthenticationTool().manage_revokeUserRole(user, location)

        if REQUEST is not None:
            if is_ajax(REQUEST):
                return 'SUCCESS'
            else:
                self.setSessionInfoTrans("Role(s) succesfully revoked")
                REQUEST.RESPONSE.redirect(REQUEST.environ.get('HTTP_REFERER',
                            '%s/admin_local_users_html' % self.absolute_url()))
    #
    # END Admin User management. XXX: Should be moved to AuthenticationTool
    #

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
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
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
                self.setSessionErrorsTrans('You must select a file to import.')
                return REQUEST.RESPONSE.redirect('%s/admin_importexport_html' % self.absolute_url())
            else:
                self.getPortalTranslations().manage_import(lang, file)
                self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
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
                self.setSessionErrorsTrans('You must select a file to import.')
                return REQUEST.RESPONSE.redirect('%s/admin_importexport_html' % self.absolute_url())
            else:
                self.getPortalTranslations().xliff_import(file)
                self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
                return REQUEST.RESPONSE.redirect('%s/admin_translations_html' % self.absolute_url())


    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_deletereflist')
    def admin_deletereflist(self, ids=[], REQUEST=None):
        """ """
        self.getPortletsTool().manage_delObjects(self.utConvertToList(ids))
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_reflists_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addreflist')
    def admin_addreflist(self, id='', title='', description='', REQUEST=None):
        """ """
        self.getPortletsTool().manage_addRefList(id, title, description)
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_reflists_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_editreflist')
    def admin_editreflist(self, id='', title='', description='', REQUEST=None):
        """ """
        ob = self.getPortletsTool().getRefListById(id)
        if ob is not None:
            ob.manageProperties(title, description)
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_reflist_html?id=%s' % (self.absolute_url(), id))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_deleteitems')
    def admin_deleteitems(self, id='', ids=[], REQUEST=None):
        """ """
        ob = self.getPortletsTool().getRefListById(id)
        if ob is not None:
            ob.manage_delete_items(self.utConvertToList(ids))
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_reflist_html?id=%s' % (self.absolute_url(), id))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_additem')
    def admin_additem(self, id='', item='', title='', REQUEST=None):
        """ """
        ob = self.getPortletsTool().getRefListById(id)
        if ob is not None:
            ob.manage_add_item(item, title)
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_reflist_html?id=%s' % (self.absolute_url(), id))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_edititem')
    def admin_edititem(self, id='', item='', title='', REQUEST=None):
        """ """
        ob = self.getPortletsTool().getRefListById(id)
        if ob is not None:
            ob.manage_update_item(item, title)
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_reflist_html?id=%s' % (self.absolute_url(), id))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_deletelinkslist')
    def admin_deletelinkslist(self, ids=[], REQUEST=None):
        """ """
        self.getPortletsTool().manage_delObjects(self.utConvertToList(ids))
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_linkslists_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addlinkslist')
    def admin_addlinkslist(self, id='', title='', portlet='', REQUEST=None):
        """ """
        self.getPortletsTool().manage_addLinksList(id, title, portlet)
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_linkslists_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_editlinkslist')
    def admin_editlinkslist(self, id='', title='', REQUEST=None):
        """ """
        ob = self.getPortletsTool().getLinksListById(id)
        if ob is not None:
            ob.manageProperties(title)
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_linkslist_html?id=%s' % (self.absolute_url(), id))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_deletelinks')
    def admin_deletelinks(self, id='', ids=[], REQUEST=None):
        """ """
        ob = self.getPortletsTool().getLinksListById(id)
        if ob is not None:
            ob.manage_delete_links(self.utConvertToList(ids))
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_linkslist_html?id=%s' % (self.absolute_url(), id))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addlink')
    def admin_addlink(self, id='', title='', description='', url='', relative='', permission='', order='', REQUEST=None):
        """ """
        ob = self.getPortletsTool().getLinksListById(id)
        if ob is not None:
            ob.manage_add_link_item('', title, description, url, relative, permission, order)
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_linkslist_html?id=%s' % (self.absolute_url(), id))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_editlink')
    def admin_editlink(self, id='', item='', title='', description='', url='', relative='', permission='', order='', REQUEST=None):
        """ """
        ob = self.getPortletsTool().getLinksListById(id)
        if ob is not None:
            ob.manage_update_link_item(item, title, description, url, relative, permission, order)
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_linkslist_html?id=%s' % (self.absolute_url(), id))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addnetworkportal')
    def admin_addnetworkportal(self, title='', url='', REQUEST=None):
        """ """
        err, res = '', None
        success = False
        xconn = XMLRPCConnector(self.http_proxy)
        if url.endswith('/'): url = url[:-1]
        res = xconn(url, 'external_search_capabilities')
        if res is None:
            err = 'Cannot connect to the given URL.'
        else:
            self.add_networkportal_item(url, title, url, res)
            success = True
        if REQUEST:
            if err != '': self.setSessionErrorsTrans(err)
            if success: self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_network_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_updatenetworkportal')
    def admin_updatenetworkportal(self, id='', REQUEST=None):
        """ """
        err, res = '', None
        success = False
        networkportal = self.get_networkportal_item(id)
        if networkportal:
            xconn = XMLRPCConnector(self.http_proxy)
            res = xconn(networkportal.url, 'external_search_capabilities')
            if res is None:
                err = 'Cannot connect to the given URL.'
            else:
                self.edit_networkportal_item(id, networkportal.title, networkportal.url, res)
                success = True
        else:
            err = 'Invalid network portal.'
        if REQUEST:
            if err != '': self.setSessionErrorsTrans(err)
            if success: self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_network_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_deletenetworkportal')
    def admin_deletenetworkportal(self, ids=[], REQUEST=None):
        """ """
        self.delete_networkportal_item(self.utConvertToList(ids))
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_network_html' % self.absolute_url())

    security.declareProtected(PERMISSION_ADMINISTRATE, 'admin_discardversion')
    def admin_discardversion(self, url=None, REQUEST=None):
        """ """
        ob = self.utGetObject(url)
        if ob is not None:
            ob.discardVersion()
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_versioncontrol_html' % self.absolute_url())

    #Main topics
    security.declareProtected(PERMISSION_PUBLISH_OBJECTS,
                              'admin_addmaintopics')
    def admin_addmaintopics(self, title='', lang=None, REQUEST=None):
        """ """
        folder_id = addNyFolder(self, title=title, lang=lang)
        folder_ob = self.utGetObject(folder_id)
        folder_ob.approveThis()
        self.maintopics.append(path_in_site(folder_ob))
        self._p_changed = True
        if REQUEST is not None:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES,
                                     date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_maintopics_html'
                                      % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS,
                              'admin_updatemaintopics')
    def admin_updatemaintopics(self, folder_url='', REQUEST=None):
        """ """
        try:
            folder_url = path_in_site(self.utGetObject(folder_url))
        except:
            if REQUEST is not None:
                self.setSessionErrorsTrans("Path not found")
                return REQUEST.RESPONSE.redirect('%s/admin_maintopics_html' %
                                                 self.absolute_url())
            else: raise

        if folder_url and folder_url not in self.maintopics:
            self.maintopics.append(folder_url)
            self._p_changed = True

        if REQUEST is not None:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES,
                                     date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_maintopics_html'
                                      % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS,
                              'admin_updatemaintopics_navigation')
    def admin_updatemaintopics_navigation(self, REQUEST=None, **kwargs):
        """ Save navigations settings """
        if REQUEST:
            form_data = dict(REQUEST.form)
        else:
            form_data = dict(kwargs)

        for field, value in form_data.items():
            if field in MAINTOPICS_SETTINGS.keys():
                try:
                    self.maintopics_settings[field] = \
                        type(self.maintopics_settings[field])(value)
                    self._p_changed = True
                except ValueError:
                    if REQUEST is not None:
                        self.setSessionErrorsTrans("Error saving data")
                        return REQUEST.RESPONSE.redirect(
                            '%s/admin_maintopics_html' % self.absolute_url())
                    else: raise
        if REQUEST is not None:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES,
                                     date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_maintopics_html'
                                      % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS,
                              'admin_ordermaintopics')
    def admin_ordermaintopics(self, positions=None, REQUEST=None):
        """ Save sortorder to maintopics by creating a new in the new order """
        if positions:
            new_order = filter(lambda path: path in self.maintopics,
                               positions.split('|'))
            if len(new_order) == len(self.maintopics):
                self.maintopics = new_order
                self._p_changed = True
            else:
                error = "Saving positons failed. \
                        New order list and old list have different length"
                if REQUEST is not None:
                    self.setSessionErrorsTrans(error)
                    return REQUEST.RESPONSE.redirect('%s/admin_maintopics_html'
                                      % self.absolute_url())
                else:
                    raise ValueError(error)
        if REQUEST is not None:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES,
                                     date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_maintopics_html'
                                      % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS,
                              'admin_deletemaintopics')
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
        self._p_changed = True

        if REQUEST is not None:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES,
                                     date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_maintopics_html'
                                      % self.absolute_url())

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
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_remotechannels_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_editremotechannel')
    def admin_editremotechannel(self, id='', title='', url='', numbershownitems='', filter_by_language='', harvester_name='', REQUEST=None):
        """ """
        self.getSyndicationTool().get_channel(id).manageProperties(title, url, numbershownitems, filter_by_language, harvester_name)
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_remotechannels_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_editremotechannelfacade')
    def admin_editremotechannelfacade(self, id='', title='', url='', numbershownitems='',
        providername='', location='', obtype='news', REQUEST=None):
        """ """
        self.getSyndicationTool().get_channel(id).manageProperties(title, url,
            providername, location, obtype, numbershownitems)
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_remotechannels_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_updateremotechannel')
    def admin_updateremotechannel(self, id='', REQUEST=None):
        """ """
        res = self.getSyndicationTool().get_channel(id).updateChannel(self.get_site_uid())
        if REQUEST:
            if res == '':
                self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            else:
                self.setSessionErrorsTrans(res)
            REQUEST.RESPONSE.redirect('%s/admin_remotechannels_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_deleteremotechannel')
    def admin_deleteremotechannel(self, ids=[], REQUEST=None):
        """ """
        self.getSyndicationTool().manage_delObjects(self.utConvertToList(ids))
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_remotechannels_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addremotechannels_aggregator')
    def admin_addremotechannels_aggregator(self, title='', channels=[], portlet='', description='', REQUEST=None):
        """ """
        self.getSyndicationTool().manage_addChannelAggregator('', title, channels, portlet, description)

        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_remotechannels_aggregators_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_editremotechannels_aggregator')
    def admin_editremotechannels_aggregator(self, id='', title='', channels=[], description='', REQUEST=None):
        """ """
        self.getSyndicationTool().get_channel(id).manageProperties(title, channels, description)
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_remotechannels_aggregators_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_deleteremotechannel')
    def admin_deleteremotechannels_aggregator(self, ids=[], REQUEST=None):
        """ """
        self.getSyndicationTool().manage_delObjects(self.utConvertToList(ids))
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_remotechannels_aggregators_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addlocalchannel')
    def admin_addlocalchannel(self, title='', description='', language=None, type=None, objmetatype=[], numberofitems='', portlet='', REQUEST=None):
        """ """
        self.getSyndicationTool().manage_addLocalChannel('', title, description, language, type, objmetatype, numberofitems, portlet)
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_localchannels_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_editlocalchannel')
    def admin_editlocalchannel(self, id='', title='', description='', language=None, type=None, objmetatype=[], numberofitems='', portlet='', REQUEST=None):
        """ """
        self.getSyndicationTool().get_channel(id).manageProperties(title, description, language, type, objmetatype, numberofitems, portlet)
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_localchannels_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_deletelocalchannel')
    def admin_deletelocalchannel(self, ids=[], REQUEST=None):
        """ """
        self.getSyndicationTool().manage_delObjects(self.utConvertToList(ids))
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_localchannels_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_leftportlets')
    def admin_leftportlets(self, portlets=[], REQUEST=None):
        """ """
        self.set_left_portlets_ids(self.utConvertToList(portlets))
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_leftportlets_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_frontportlets')
    def admin_frontportlets(self, portlets=[], REQUEST=None):
        """ """
        self.set_center_portlets_ids(self.utConvertToList(portlets))
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_frontportlets_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_rightportlets')
    def admin_rightportlets(self, folder='', portlets=[], REQUEST=None):
        """ """
        self.set_right_portlets_locations(folder, self.utConvertToList(portlets))
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_rightportlets_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_deleterightportlets')
    def admin_deleterightportlets(self, portlets=[], REQUEST=None):
        """ """
        for pair in self.utConvertToList(portlets):
            location, id = pair.split('||')
            self.delete_right_portlets_locations(location, id)
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_rightportlets_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_deleteremotechportlet')
    def admin_deleteremotechportlet(self, ids=[], REQUEST=None):
        """ """
        self.getPortletsTool().manage_delObjects(self.utConvertToList(ids))
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
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
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_remotechportlets_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_deletelocalchportlet')
    def admin_deletelocalchportlet(self, ids=[], REQUEST=None):
        """ """
        self.getPortletsTool().manage_delObjects(self.utConvertToList(ids))
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_localchportlets_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addlocalchportlet')
    def admin_addlocalchportlet(self, id='', REQUEST=None):
        """ """
        ob = self.getSyndicationTool().get_channel(id)
        if ob is not None: self.create_portlet_for_localchannel(ob)
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_localchportlets_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_deletefolderportlet')
    def admin_deletefolderportlet(self, ids=[], REQUEST=None):
        """ """
        self.getPortletsTool().manage_delObjects(self.utConvertToList(ids))
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
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
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_folderportlets_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_deletelinksportlet')
    def admin_deletelinksportlet(self, ids=[], REQUEST=None):
        """ """
        self.getPortletsTool().manage_delObjects(self.utConvertToList(ids))
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_linksportlets_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addlinksportlet')
    def admin_addlinksportlet(self, id='', REQUEST=None):
        """ """
        ob = self.getPortletsTool().getLinksListById(id)
        if ob is not None: self.create_portlet_for_linkslist(ob)
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_linksportlets_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addhtmlportlet')
    def admin_addhtmlportlet(self, REQUEST=None):
        """ """
        id = PREFIX_PORTLET + self.utGenRandomId(6)
        self.getPortletsTool().addHTMLPortlet(id=id, title='New portlet')
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_htmlportlets_html?id=%s' % (self.absolute_url(), id))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_edithtmlportlet')
    def admin_edithtmlportlet(self, id='', title='', body='', lang=None, REQUEST=None):
        """ """
        ob = self.getPortletsTool().getPortletById(id)
        if ob is not None:
            ob.manage_properties(title, body, lang)
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_htmlportlets_html?id=%s' % (self.absolute_url(), id))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_deletehtmlportlet')
    def admin_deletehtmlportlet(self, ids=[], REQUEST=None):
        """ """
        self.getPortletsTool().manage_delObjects(self.utConvertToList(ids))
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
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
        from zope.sendmail.interfaces import IMailDelivery
        delivery = component.queryUtility(IMailDelivery, 'naaya-mail-delivery')
        queue_enabled = bool(delivery is not None)
        vars = {'here': self, 'queue_enabled': queue_enabled}
        return self.getFormsTool().getContent(vars, 'site_admin_email')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_logos_html')
    def admin_logos_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_logos')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_glossaries_html')
    def admin_glossaries_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_glossaries')

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
    def admin_users_html(self):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_users')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_local_users_html')
    def admin_local_users_html(self):
        """ """
        return self.getFormsTool().getContent({'here': self},
            'site_admin_local_users')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_all_users_html')
    def admin_all_users_html(self):
        """ """
        return self.getFormsTool().getContent({'here': self},
            'site_admin_all_users')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_adduser_html')
    def admin_adduser_html(self):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_adduser')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_importusers_html')
    def admin_importusers_html(self):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_importusers')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_edituser_html')
    def admin_edituser_html(self, **kwargs):
        """ """
        kwargs['here'] = self
        return self.getFormsTool().getContent(kwargs, 'site_admin_edituser')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_assignroles_html')
    def admin_assignroles_html(self, **kwargs):
        """ """
        kwargs['here'] = self
        return self.getFormsTool().getContent(kwargs, 'site_admin_assignroles')

    security.declareProtected(change_permissions, 'admin_roles_html')
    def admin_roles_html(self):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_roles')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_sources_html')
    def admin_sources_html(self, REQUEST=None):
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
        permission_list = self.get_naaya_permissions_in_site().values()
        permission_list.sort(key=operator.itemgetter('title'))

        tmpl = self.getFormsTool().getForm('site_admin_linkslist').__of__(self)
        options = {
            'permission_list': permission_list,
            'permission_titles': dict((p['zope_permission'], p['title'])
                                      for p in permission_list),
        }
        return tmpl(REQUEST, **options)

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

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_folder_subobjects_html')
    def admin_folder_subobjects_html(self, REQUEST):
        """ Admin view for editing global (default) folder subobjects """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_folder_subobjects')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_folder_subobjects_submit')
    def admin_folder_subobjects_submit(self, subobjects=None,
                                       ny_subobjects=None, only_nyobjects=False,
                                       REQUEST=None):
        """ Updating global (default) folder subobjects """
        portal_properties = self.getPropertiesTool()
        portal_properties.manageSubobjects(subobjects, ny_subobjects, only_nyobjects)
        if REQUEST:
            REQUEST.RESPONSE.redirect('admin_folder_subobjects_html?save=ok')

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
        if name != '': return context.checkPermission(name)
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
        mfrom = etool.get_addr_from()
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
        email_tool = self.getEmailTool()
        mail_from = email_tool.get_addr_from()
        email_tool.sendEmail(l_content, p_email, mail_from, l_subject)

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
        email_tool = self.getEmailTool()
        mail_from = email_tool.get_addr_from()
        email_tool.getEmailTool().sendEmail(content, email, mail_from, subject)

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
        self.getEmailTool().sendEmailImmediately(l_content, p_to, p_from, l_subject)

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
        return [x['meta_type'] for x in self.get_pluggable_content().values() if x.get('validation', None) == 1]

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
            return self.get_pluggable_content().get(meta_type, None).get('properties', {}).keys()
        return []

    def get_pluggable_item_properties_item(self, meta_type, prop):
        return self.get_pluggable_content().get(meta_type, None)['properties'][prop]

    def get_pluggable_item_property_mandatory(self, meta_type, prop):
        if self.is_pluggable_item_installed(meta_type):
            config = self.get_pluggable_content().get(meta_type, {})
            entry = config.get('properties', {}).get(prop, [0])
            return entry[0]
        return 0

    def check_pluggable_item_properties(self, meta_type, **args):
        l = []
        la = l.append
        translate = self.getPortalTranslations().translate
        for k, v in self.get_pluggable_content().get(meta_type, None).get('properties', {}).items():
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

            #add content's permission to some roles
            role_names = ('Manager', 'Administrator', 'Contributor')
            self.manage_permission(pitem['permission'], role_names, acquire=1)

            #run `on_install` function if defined in content's `config`
            if 'on_install' in pitem:
                pitem['on_install'](self)

            #send the requisite event
            notify(NyPluggableItemInstalled(self, meta_type))

            #remember that this meta_type was installed
            self.__pluggable_installed_content[meta_type] = 1
            self.searchable_content.append(meta_type)
            self._p_changed = 1

        if REQUEST: REQUEST.RESPONSE.redirect('%s/manage_controlpanel_html' % self.absolute_url())

    security.declareProtected(view_management_screens, 'manage_uninstall_pluggableitem')
    def manage_uninstall_pluggableitem(self, meta_type=None, REQUEST=None):
        """ """
        if meta_type is not None:
            #remember that this meta_type was removed
            del(self.__pluggable_installed_content[meta_type])
            self.searchable_content = [x for x in self.searchable_content if x != meta_type]
            # not removing the permission (why bother?)

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
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
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
        addr_from = self.getEmailTool().get_addr_from()
        for mail in mails:
            self.getEmailTool().sendEmail(mail_body, mail, addr_from, mail_subject)

        if REQUEST:
            self.setSessionInfoTrans('Mail sent. (${date})', date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_bulk_mail_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'export_contacts_vcard')
    def export_contacts_vcard(self, location='', REQUEST=None):
        """ Exports all portal contacts in vCard format contained in a zip file """
        if not location or location == '/':
            loc_obj = self
        else:
            loc_obj = self.unrestrictedTraverse(location)
            site_id = self.getSite().getId()
            if not location.startswith(site_id):
                location = '%s/%s' % (site_id, location)

        contacts = self.getCatalogedObjects(meta_type=['Naaya Contact'], path=location)
        files = [vcard_file(contact.id, contact.export_vcard()) for contact in contacts]
        if REQUEST:
            if not contacts:
                self.setSessionInfoTrans('No contacts found in the selected location.')
                return REQUEST.RESPONSE.redirect('%s/admin_contacts_html?section=vcard' % self.absolute_url())
            return self.utGenerateZip('%s-contacts.zip' % loc_obj.title_or_id(),
                                      files, self.REQUEST.RESPONSE)
        else: return files

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'import_contacts_vcard')
    def import_contacts_vcard(self, vcard_zipfile, location, REQUEST=None):
        """ Import contacts in vCard format from a zip file """
        from naaya.content.contact.contact_item import addNyContact, parse_vcard_data
        container = self.restrictedTraverse(location)
        error = []
        success = False
        objects_created = 0
        vcard_zip = ZipFile(vcard_zipfile)
        for filename in vcard_zip.namelist():
            data = vcard_zip.read(filename)
            try:
                contact_data = parse_vcard_data(data)
            except:
                errors.append(('Error parsing "${filename}"', {'filename': filename}, ))
            else:
                objects_created += 1
                contact_data['title'] = '%s %s' % (
                    contact_data['firstname'], contact_data['lastname'])
                addNyContact(container, **contact_data)

        if objects_created:
            transaction.get().note('Imported %d Naaya Contact objects' % objects_created)
            success = True

        if REQUEST is not None:
            if len(errors): self.setSessionErrorsTrans(errors)
            if success: self.setSessionInfoTrans('Imported ${objects} contact objects', objects=objects_created)
            return REQUEST.RESPONSE.redirect('%s/admin_contacts_html' % self.absolute_url())


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
    @deprecate('standard_html_header is deprecated and will be removed. '
               'Use standard_template_macro instead.')
    def standard_html_header(self, REQUEST=None, RESPONSE=None):
        """ """
        context = self.REQUEST.PARENTS[0]
        ltool = self.getLayoutTool()
        if hasattr(ltool.get_current_skin(), 'site_header'):
            return ltool.getContent({'here': context}, 'site_header').split('<!--SITE_HEADERFOOTER_MARKER-->')[0]
        return ltool.render_standard_template(context).split('<!--SITE_HEADERFOOTER_MARKER-->')[0]

    security.declareProtected(view, 'standard_html_footer')
    @deprecate('standard_html_footer is deprecated and will be removed. '
               'Use standard_template_macro instead.')
    def standard_html_footer(self, REQUEST=None, RESPONSE=None):
        """ """
        context = self.REQUEST.PARENTS[0]
        ltool = self.getLayoutTool()
        if hasattr(ltool.get_current_skin(), 'site_footer'):
            return ltool.getContent({'here': context}, 'site_footer').split('<!--SITE_HEADERFOOTER_MARKER-->')[1]
        return ltool.render_standard_template(context).split('<!--SITE_HEADERFOOTER_MARKER-->')[1]

    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        layout_tool = self.getLayoutTool()
        current_skin = layout_tool.get_current_skin()
        layout_site_index = current_skin._getOb('site_index', None)
        if layout_site_index is not None:
            return layout_site_index.aq_base.__of__(self)()
        return self.getFormsTool().getContent({'here': self}, 'site_index')

    security.declareProtected(view, 'menusubmissions')
    def menusubmissions(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_menusubmissions')

    security.declareProtected(view, 'messages_html')
    def messages_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_messages')

    security.declarePublic('messages_box')
    def messages_box(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'messages_box')

    security.declarePublic('languages_box')
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

    security.declarePublic('logout_html')
    def logout_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_logout')

    security.declarePublic('unauthorized_html')
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

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_bulk_mail_html')
    def admin_bulk_mail_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return PageTemplateFile('skel/forms/site_admin_bulk_mail', globals()).__of__(self)()

    def standard_template_macro(self, macro='page'):
        return self.getLayoutTool().get_standard_template().macros[macro]

    sitemap_xml = NaayaPageTemplateFile('zpt/sitemap_xml', globals(), 'naaya.google.sitemap')

    sitemap_rdf_xml = NaayaPageTemplateFile('zpt/sitemap_rdf_xml', globals(), 'naaya.semanticweb.sitemap')

    #calendar widget
    security.declarePublic('calendar_js')
    calendar_js = DTMLFile('zpt/calendar/calendar_js', globals())

    security.declarePublic('core_js')
    core_js = DTMLFile('zpt/calendar/core_js', globals())

    security.declarePublic('i18n_js')
    def i18n_js(self, lang='en', REQUEST=None):
        """ translations for messages used by JavaScript """
        portal_translations = self.getPortalTranslations()
        translations = dict( (msg, portal_translations(msg, lang=lang))
                                for msg in JS_MESSAGES )

        if REQUEST is not None:
            REQUEST.RESPONSE.setHeader('Content-Type',
                                       'application/javascript')
            REQUEST.RESPONSE.setHeader('Cache-Control', 'public,max-age=60')
        return 'var naaya_i18n_catalog = %s;' % json.dumps(translations)

    security.declarePublic('datetime_js')
    datetime_js = DTMLFile('zpt/calendar/datetime_js', globals())

    #common javascript
    security.declarePublic('common_js')
    common_js = DTMLFile('zpt/common_js', globals())
    #
    # Macro libs
    #
    security.declareProtected(view, 'folder_lib_toolbar_buttons')
    folder_lib_toolbar_buttons = PageTemplateFile(
        'zpt/folder_lib_toolbar_buttons', globals())

    security.declareProtected(PERMISSION_ADD_FOLDER, 'folder_add_html')
    folder_add_html = folder_add_html
    security.declareProtected(PERMISSION_ADD_FOLDER, 'addNyFolder')
    addNyFolder = addNyFolder

    security.declareProtected(view, 'macro_utils')
    macro_utils = PageTemplateFile('zpt/site_macro_utils', globals())

    csv_import = CSVImportTool('csv_import')
    csv_reader = UnicodeReader
    csv_export = ExportTool('csv_export')
    zip_import = ZipImportTool('zip_import')
    zip_export = ZipExportTool('zip_export')
    jstree = StaticServeFromZip('source', 'www/js/jstree.zip', globals())
    jquery_tree_init = ImageFile('www/js/jquery.tree.init.js', globals())

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
    reset_css = ImageFile('www/reset.css', globals())

    def additional_style_css(self, REQUEST):
        """ """
        REQUEST.RESPONSE.setHeader('Content-Type', 'text/css')
        return self.getLayoutTool().getNaayaContentStyles()

    def heartbeat_work(self, REQUEST=None):
        """ does a heartbeat work on this site """
        if REQUEST is not None:
            raise Unauthorized

        transaction.commit() # commit earlier stuff; fresh transaction
        transaction.get().note('cron heartbeat at %s' % ofs_path(self))

        from naaya.core.heartbeat import Heartbeat
        hb = Heartbeat()
        try:
            component.handle(self, hb)
        except:
            self.log_current_error()
            raise
        transaction.commit()

    def heartbeat(self):
        """ if cooldown has passed does a heartbeat """
        if cooldown('site heartbeat %r' % '/'.join(self.getPhysicalPath()),
                    timedelta(minutes=9)):
            return
        self.heartbeat_work()

    def manage_check_heartbeat(self):
        """ return the time of the last heartbeat """

        from naaya.core.utils import _cooldown_map
        name = 'site heartbeat %r' % '/'.join(self.getPhysicalPath())
        if _cooldown_map.has_key(name):
            last_heartbeat = _cooldown_map[name]
            time_ever_since = datetime.now() - last_heartbeat
            minutes_ever_since = int(time_ever_since.seconds / 60)
            seconds_ever_since = time_ever_since.seconds % 60
            last_heartbeat = last_heartbeat.strftime('%d %B %Y %H:%M:%S')
            return 'Time of last heartbeat: %s (%s minutes and %s seconds ago)'\
                % (last_heartbeat, minutes_ever_since, seconds_ever_since)
        return 'The heart did not beat since last system restart.'

    # functions for translation
    def translate(self, text, dest_lang, src_lang=None):
        return translate(text, dest_lang, src_lang)

    def translate_url(self, *args):
        return translate_url(*args)

    rdf_cataloged_items = rdf_cataloged_items

InitializeClass(NySite)

_naaya_known_permissions = {}
def register_naaya_permission(zope_perm, title, description=""):
    """
    Register a permission so that administrators can assign it to roles.
    """
    _naaya_known_permissions[zope_perm] = {
        'title': title,
        'description': description,
        'zope_permission': zope_perm,
    }
import _permissions
_permissions.register_default_permissions()
