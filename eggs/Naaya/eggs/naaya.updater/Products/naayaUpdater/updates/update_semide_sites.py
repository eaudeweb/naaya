#Python imports
import os
from copy import deepcopy

#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.StandardCacheManagers.RAMCacheManager import RAMCacheManager
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from OFS.Folder import Folder
from ZODB.broken import rebuild
import transaction

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from Products.SEMIDE.SEMIDESite import SEMIDESite
import Products.SEMIDE
from Products.Naaya import NySite as NySite_module
from Products.Naaya.NyFolder import addNyFolder

from Products.NaayaPhotoArchive.NyPhotoGallery import manage_addNyPhotoGallery
from Products.NaayaPhotoArchive.NyPhotoFolder import manage_addNyPhotoFolder
from Products.NaayaPhotoArchive.NyPhoto import NyPhoto, addNyPhoto

from Products.NaayaCore.NotificationTool.NotificationTool import manage_addNotificationTool
from Products.NaayaCore.SchemaTool.SchemaTool import manage_addSchemaTool
from Products.NaayaCore.GoogleDataTool.AnalyticsTool import manage_addAnalyticsTool

from Products.Naaya.managers.skel_parser import skel_parser
from Products.naayaUpdater.utils import (convertLinesToList, convertToList,
    get_template_content, normalize_template, html_diff, readFile)


# Content Types to be fixed
from naaya.content.semide.document.semdocument_item import NySemDocument
from Products.NaayaCore.LayoutTool.Template import Template

SEMIDE_PRODUCT_PATH = os.path.dirname(Products.SEMIDE.__file__)

class UpdateSemideSites(UpdateScript):
    """ Update Semide Sites  """
    id = 'update_semide_sites'
    title = 'Update Semide Sites'
    creation_date = 'Mar 31, 2010'
    authors = ['Alexandru Plugaru']
    priority = PRIORITY['HIGH']
    description = 'Updates all semide sites for compatibility with Naaya trunk version'
    #dependencies = []
    categories = ['semide']

    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        #This should only be enabled on the development version
        self.log.debug('Disabling administrator e-mails')
        portal.administrator_email = 'alexandru.plugaru@eaudeweb.ro'

        self.log.debug('Removing RAMCacheManager(s)')
        self.removeRamCacheManagers(portal)

        self.removeAddTools(portal)

        self.log.debug('Adding jQuery to site header')
        self.addJquery(portal)

        self.log.debug('Removing custom forms from FormsTool')
        #self.deleteForms(portal, ['country_custom_footer', 'country_custom_header']) # Completly deletes
        self.removeForms(portal)

        self._unused_meta_types = ('Naaya Entry', 'Naaya EntryPress', )
        self.remove_unused_meta_types(portal)

        if self.REQUEST.form['action'] != 'Show report':
            transaction.commit()

        self.log.debug('Updating some old portlets')
        self.updatePortlets(portal)

        self.log.debug('Migrating photo galleries')
        self.migratePhotoGallery(portal)

        if self.REQUEST.form['action'] != 'Show report':
            transaction.commit()

        self.log.debug('Switching from site_header + site_footer to standard_template')
        self.updateLayout(portal)

        self.log.debug('Moving event and news items to year/month folders')
        self.updateEventNews(portal)

        self.log.debug('Update Semide Sites went succesfully.')
        return True

    def removeAddTools(self, portal):
        """ Remove then Add:
        ControlsTool
        NotificationsTool
        SchemaTool
        """
        portal.manage_delObjects(['portal_control', ])

        portal.manage_delObjects([portal.getNotificationTool().id])
        manage_addNotificationTool(portal)
        self.log.debug('Removed/Add NotificationsTool in ' + str(portal.id))

        try:
            manage_addSchemaTool(portal)
            self.log.debug('Added SchemaTool succesfully.')
        except: pass
        try:
            manage_addAnalyticsTool(portal)
            self.log.debug('Added AnalyticsTool succesfully.')
        except: pass


    def remove_unused_meta_types(self, context):
        for child_id, child_ob in context.objectItems():
            child_path = '/'.join(context.getPhysicalPath() + (child_id, ))
            if child_ob.meta_type in self._unused_meta_types:
                self.log.debug('Deleted %s at %s' % (child_ob.meta_type, child_path))
                context.manage_delObjects([child_ob.id])
            elif hasattr(child_ob.aq_inner.aq_self, 'objectItems'):
                self.remove_unused_meta_types(child_ob)

    def removeRamCacheManagers(self, context):
        """ Find all RAMCacheManager objects and remove also remove references to Cache """
        for child_id, child_ob in context.objectItems():
            child_path = '/'.join(context.getPhysicalPath() + (child_id, ))
            if hasattr(child_ob, '_Cacheable__manager_id'):
                child_ob._Cacheable__manager_id = None
                #self.log.debug('RESET  ' + child_path)
            if RAMCacheManager.meta_type == child_ob.meta_type:
                context.manage_delObjects([child_ob.id])
                self.log.debug('DELETED RAMCacheManager ' + child_path)
            elif hasattr(child_ob.aq_inner.aq_self, 'objectItems'):
                self.removeRamCacheManagers(child_ob)

    def addJquery(self, portal):
        """ Adds jQuery to site_header template"""
        site_header = portal.getLayoutTool().get_current_skin().site_header
        site_header._text = site_header.read().replace('</head>', "\n<script type=\"text/javascript\" tal:attributes=\"src string:${site_url}/misc_/Naaya/jquery-1.3.2.min.js\"></script>\n</head>")

    def deleteForms(self, portal, forms):
        """ Completly remove forms from ZMI """
        #portal.getFormsTool().manage_delObjects(forms)
        pass

    def removeForms(self, portal, exclude_forms = []):
        """ Delete *customized* forms from ZMI and use those from disc """
        forms = set(portal.getFormsTool().objectIds())
        if exclude_forms:
            forms = forms - set(exclude_forms)
        for form in forms:
            try:
                portal.getFormsTool().manage_delObjects([form, ])
                self.log.debug('Removed custom form: %s' % form)
            except: pass

    def get_fs_template(self, id, portal):
        """ return a filesystem template object given the id """
        if id in self.list_fs_templates(portal):
            return self.get_fs_template_content(id, portal)
        elif id in self.list_fs_templates(NySite_module):   #fall back to Naaya filesytem templates
            return self.get_fs_template_content(id, NySite_module)
        return self.get_contenttype_content(id, portal) #fall back to Naaya pluggable content types

    def list_fs_templates(self, portal):
        """ return the list of the filesystem templates """
        portal_path = self.get_portal_path(portal)
        skel_handler, error = skel_parser().parse(readFile(os.path.join(portal_path, 'skel', 'skel.xml'), 'r'))
        if skel_handler.root.forms is not None:
            return [f.id for f in skel_handler.root.forms.forms]

    def updateLayout(self, portal):
        """ It's working but a lot of templates then have to be fixed.. """
        skin = portal.getLayoutTool().get_current_skin()

        try: skin.manage_delObjects(['standard_template'])
        except: pass
        try: skin.manage_delObjects(['site_header', ])
        except: pass
        try: skin.manage_delObjects(['site_footer', ])
        except: pass

        if portal.id in ('semide', 'medwip', ): # get from skel FS
            standard_template = file(os.path.join(os.path.dirname(Products.SEMIDE.__file__)) + '/skel/layout/semide/standard_template.zpt', 'r').read()
        else:
            standard_template = standard_template_skel #See at the end of the file

        skin._setObject('standard_template', Template('standard_template', 'Portal standard template', standard_template.encode('utf-8'), ''))

    def updatePortlets(self, portal):
        """ Update some old portlets """
        portlets_tool = portal.getPortletsTool()
        try:
            getattr(portlets_tool, '_portlet_layout')
        except AttributeError:
            portlets_tool._portlet_layout = {}

        for portlet_id, portlet_content in portlets.items():
            portlet_ob = portlets_tool._getOb(portlet_id, None)
            portlet_ob._text = portlet_content
            portlet_ob._p_changed = 1
            self.log.debug("Updated %s" % '/'.join(portlet_ob.getPhysicalPath()))

    def migratePhotoGallery(self, portal):
        """ Switch from SEMIDEPhotoArhive to NaayaPhotoArchive """
        photo_gallery_folder = None

        if portal.id == 'semide':
            portal.thematicdirs.manage_renameObjects(['fol449646', ], ['fol449646_old', ]) #Renaming
            photo_gallery_folder = portal.thematicdirs.fol449646_old
            manage_addNyPhotoGallery(portal.thematicdirs, id='fol449646', title=photo_gallery_folder.title)
            new_gallery = portal.thematicdirs.fol449646
            new_gallery.tooltip = photo_gallery_folder.title

        if portal.id == 'medaquaministerial2008':
            portal.manage_renameObjects(['photos', ], ['photos_old', ])
            photo_gallery_folder = portal.photos_old
            manage_addNyPhotoGallery(portal, id='photos', title=photo_gallery_folder.title)
            new_gallery = portal.photos
            new_gallery.tooltip = photo_gallery_folder.title
            portal.maintopics[portal.maintopics.index('photos_old')] = 'photos'

        if photo_gallery_folder:
            for photo_folder in photo_gallery_folder.objectValues():
                if photo_folder.title: new_folder_title = photo_folder.title
                else: new_folder_title = photo_folder.id

                manage_addNyPhotoFolder(new_gallery, id=photo_folder.id, title=new_folder_title)
                new_photo_folder = new_gallery._getOb(photo_folder.id)
                new_photo_folder.author = u''
                new_photo_folder.source = u''
                new_photo_folder.max_photos = 500
                folder_pics = photo_folder.objectIds()

                for prop, value in photo_folder.__dict__.items():
                    if prop not in folder_pics and prop != '_objects':
                        setattr(new_photo_folder, prop, value)

                for pic in photo_folder.objectValues():
                    if pic.title: new_pic_title = pic.title
                    else: new_pic_title = pic.id

                    new_pic_id = addNyPhoto(new_photo_folder, id=pic.id, title=new_pic_title)
                    new_pic = new_photo_folder._getOb(new_pic_id)

                    for prop, value in pic.__dict__.items():
                        if prop == '__ac_local_roles__':
                            setattr(new_pic, '_owner', (['acl_users'], value.keys()[0]))
                    extfile_original = getattr(pic, '_ext_file', None)
                    if extfile_original:
                        try:
                            extfile = getattr(new_pic, extfile_original.id)
                        except AttributeError:
                            new_pic.manage_delObjects(['find_broken_products', ])
                            extfile = extfile_original
                            extfile.__version__ = '2.0.2'
                        extfile.width = pic.width
                        extfile.height = pic.height
                        extfile.__ac_local_roles__ = new_pic.__ac_local_roles__
                        extfile.filename = extfile_original.filename
                        extfile.descr = extfile_original.descr
                        extfile._p_changed = 1

        if portal.id == 'semide': # Deleting the old folder
            portal.thematicdirs.manage_delObjects([photo_gallery_folder.id])
            portal.thematicdirs.maintopics.append('fol449646')

        if portal.id == 'medaquaministerial2008': #Delete old gallery folder
            portal.manage_delObjects([photo_gallery_folder.id])

    def updateEventNews(self, portal):
        """ This will work just for semide """
        def create_dirs(folder, date, title):
            """ Helper for creating year/month folders """
            date_year = str(date.year())
            date_month = date.mm()

            year_folder = folder._getOb(date_year, None)
            if year_folder is None:
                year_folder = folder._getOb(addNyFolder(folder, date_year,
                    contributor=folder.contributor, title="%s for %s" % (title, date_year)))

            month_folder = year_folder._getOb(date_month, None)
            if month_folder is None:
                month_folder = year_folder._getOb(addNyFolder(year_folder, date_month,
                                contributor=folder.contributor,
                                title="%s for %s/%s" %
                                (title, date_year, date_month)))
            return month_folder

        def move(object, old_dir, move_folder):
            cut_data = old_dir.manage_cutObjects([object.id, ])
            move_folder.manage_pasteObjects(cut_data)
            old_path = object.absolute_url(1)
            new_path = getattr(move_folder, object.id).absolute_url(1)
            paths[old_path] = new_path
            self.log.debug('Moved %s to %s' % (old_path, new_path))

        if portal.id == 'semide':

            news_dir = portal.thematicdirs.news
            events_dir = portal.thematicdirs.events
            paths = {}



            for event in events_dir.objectValues():
                if event.meta_type == 'Naaya Semide Event':
                    move_folder = create_dirs(events_dir, event.start_date, 'Events')
                    if 'Naaya Semide Event' not in move_folder.folder_meta_types:
                        move_folder.folder_meta_types.append('Naaya Semide Event')
                    move(event, events_dir, move_folder)

            events_dir.redirect_paths = paths # Storing move paths for redirection
            paths = {}

            for news_item in news_dir.objectValues():
                if news_item.meta_type == 'Naaya Semide News':
                    move_folder = create_dirs(news_dir, news_item.news_date, 'News')
                    if 'Naaya Semide News' not in move_folder.folder_meta_types:
                        move_folder.folder_meta_types.append('Naaya Semide News')
                    move(news_item, news_dir, move_folder)

            news_dir.redirect_paths = paths


portlets = {
    'portlet_country_left': open(SEMIDE_PRODUCT_PATH + '/skel/portlets/portlet_country_left.zpt', 'r').read(),
    'portlet_initiatives_news': open(SEMIDE_PRODUCT_PATH + '/skel/portlets/portlet_initiatives_news.zpt', 'r').read(),
    'portlet_initiatives_events': open(SEMIDE_PRODUCT_PATH +'/skel/portlets/portlet_initiatives_events.zpt', 'r').read(),
    'portlet_initiatives_projects': open(SEMIDE_PRODUCT_PATH + '/skel/portlets/portlet_initiatives_projects.zpt', 'r').read()
}

standard_template_skel = """<metal:block define-macro="page"><span tal:replace="python:request.RESPONSE.setHeader('content-type','text/html;charset=utf-8')"/>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"
	tal:attributes="xml:lang here/gl_get_selected_language;
        lang here/gl_get_selected_language;
        dir python:test(isArabic, 'rtl', 'ltr')"
	tal:define=" site_url here/getSitePath;
        isArabic here/isArabicLanguage;
        noArabic not:isArabic;">
    <head tal:define="skin_files_path python:here.getLayoutTool().get_skin_files_path();
        css_screen python:test(isArabic, 'style_rtl', 'style');
		css_common python:test(isArabic, 'style_common_rtl', 'style_common');
		css_handheld python:test(isArabic, 'style_handheld_rtl', 'style_handheld');">

        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <metal:block define-slot="title">
            <title tal:content="string:${here/site_title} - ${here/site_subtitle}" />
        </metal:block>
        <link rel="icon" tal:attributes="href string:${site_url}/favicon.ico" type="image/x-icon" />

        <metal:block define-slot="standard-head-links">
            <link rel="stylesheet" type="text/css" media="screen" tal:attributes="href string:${skin_files_path}/${css_screen}" />
            <link rel="stylesheet" type="text/css" media="all" tal:attributes="href string:${skin_files_path}/${css_common}" />
            <link rel="stylesheet" type="text/css" media="print" tal:attributes="href string:${skin_files_path}/style_print" />
            <link rel="stylesheet" type="text/css" media="handheld" tal:attributes="href string:${skin_files_path}/${css_handheld}" />
            <link tal:condition="python:here.meta_type=='Naaya Glossary'" rel="stylesheet" type="text/css" media="all" tal:attributes="href string:${site_url}/glossary_coverage/style_presentation_css" />
            <link tal:condition="python:here.meta_type=='Naaya Thesaurus'" rel="stylesheet" type="text/css" media="all" tal:attributes="href string:${site_url}/portal_thesaurus/thesaurus_css" />
            <link tal:condition="python:here.meta_type=='SEMIDE Site'" rel="stylesheet" type="text/css" tal:attributes="href string:${site_url}/portal_calendar/calendar_style" />
            <!-- RSS feeds -->
            <tal:block repeat="channel python:here.getSite().getSyndicationTool().get_script_channels()">
                <link rel="alternate" type="application/rss+xml" tal:attributes="title channel/title_or_id; href channel/absolute_url" />
            </tal:block>
            <tal:block repeat="channel python:here.getSite().getSyndicationTool().get_local_channels()">
                <link rel="alternate" type="application/rss+xml" tal:attributes="title channel/title_or_id; href channel/absolute_url" />
            </tal:block>

            <link rel="home" tal:attributes="href python:request['BASE0']" title="Home" />
            <!--[if IE]>
			<style type="text/css">
			/*<![CDATA[*/
			body {
				word-wrap: break-word;
			}
			/*]]>*/
			</style>
            <![endif]-->
        </metal:block>
        <metal:block define-slot="standard-head-content">
            <script type="text/javascript" tal:attributes="src string:${site_url}/misc_/Naaya/jquery.js"></script>
            <script type="text/javascript" tal:attributes="src string:${site_url}/misc_/Naaya/jquery-ui.js"></script>
            <script type="text/javascript" tal:attributes="src string:${site_url}/misc_/Naaya/utils.js"></script>
        </metal:block>
        <metal:block define-slot="head"></metal:block>
	</head>
<metal:block define-slot="standard-body">
<body>
<a class="skiplink" href="#contentstart" accesskey="2" i18n:translate="">Skip navigation</a>
<div class="white_backgrounded">
    <div id="nav_upper" tal:define="authenticated_user python:request.AUTHENTICATED_USER.getUserName()">
        <div tal:define="l_list python:here.getPortletsTool().getLinksListById('menunav_links').get_links_list()">

            <div id="nav_upper_log">

                <img tal:attributes="src string:${here/getSkinFilesPath}/ico_login.gif;" align="middle" alt="" />
                <tal:block condition="python: authenticated_user != 'Anonymous User'">
                    <span i18n:translate="" tal:omit-tag="">you are logged in as</span>
                    <strong tal:content="authenticated_user" />
                    <a tal:attributes="href string:${site_url}/login_html" i18n:translate="">logout</a>
                </tal:block>

                <tal:block condition="python: authenticated_user == 'Anonymous User'"
                        define="proc_came_from python:request.get('URL', '');
                            proc_query python:request.get('QUERY_STRING');
                            query python:test(proc_query.startswith('?'), proc_query, '?' + proc_query);
                            came_from python:test(query, proc_came_from + query, proc_came_from)">
                    <span i18n:translate="" tal:omit-tag="">you are not logged in</span>
                    <a tal:attributes="href string:${site_url}/login_html?came_from=${came_from}&disable_cookie_login__=1" i18n:translate="">login</a>
                    <a tal:attributes="href string:${site_url}/requestrole_html" i18n:translate="">create account</a>
                </tal:block>

            </div>
            <span i18n:translate=""><strong>Union for the Mediterranean</strong></span>
            <tal:block tal:repeat="item l_list">
            <span tal:condition="python:here.checkPermissionForLink(item.permission, here)"><a tal:attributes="href python:test(item.relative, '%s%s' % (site_url, item.url), item.url); title item/description" tal:content="item/title" i18n:translate="" i18n:attributes="title">Title</a> </span>
            </tal:block>
        </div>

    </div>
    <div class="clearing_div_top"> &nbsp; </div>
    <!-- top banner -->
    <div id="top_banner">
        <div id="banner_images" tal:define="thumb_list here/getThumbs;
                                            thumb1 python:thumb_list[0];
                                            thumb2 python:thumb_list[1];
                                            thumb3 python:thumb_list[2]">
            <img tal:attributes="src thumb1" alt="" />
            <img tal:attributes="src thumb2" alt="" />
            <img tal:attributes="src thumb3" alt="" />
        </div>
        <div id="site_logo">
            <img tal:attributes="src string:${here/getLayoutToolPath}/logo.gif" alt="" />
        </div>
        <div id="site_title">
            <span tal:content="here/site_title" />
            <div id="site_subtitle" tal:content="here/site_subtitle" />
        </div>
    </div>
    <!--END top banner -->
    <!-- top menu -->
    <div id="nav_main">
        <div id="nav_main_language">
            <tal:block replace="structure here/languages_box" />
        </div>
        <div id="nav_main_links">
        <!-- LIST CONTAINING THE GLOBAL LEVEL -->
            <ul>
                <li tal:repeat="main_categ here/getMainTopics">
                    <a tal:attributes="href string:${main_categ/absolute_url}; title main_categ/title" tal:content="main_categ/title" />
                    <span tal:condition="isArabic">&nbsp;|&nbsp;</span>
                </li>
            </ul>
        <!-- END OF LIST CONTAINING THE GLOBAL LEVEL -->


        </div>
    </div>
    <!--END top menu -->
    <!-- acces-bread-search -->
    <div id="bar_divided">
        <div id="bread_crumb_trail">
                <tal:block repeat="crumb python:here.getBreadCrumbTrail(request)">
                <a tal:condition="python:crumb.meta_type!='SEMIDE Site'"
                   tal:attributes="href string:${crumb/absolute_url}/;
                                   title crumb/title_or_id;"
                   tal:content="crumb/title_or_id" />
                <a tal:condition="python:crumb.meta_type=='SEMIDE Site'" tal:attributes="href site_url"
                   i18n:translate="">
                    Home
                </a>
                <span tal:condition="not:repeat/crumb/end"> &raquo; </span>
                </tal:block>
        </div>
    </div>
</div>
<!--END acces-bread-search -->
<div class="clearing_div"> &nbsp; </div>

<div id="main_structure_ie_fixer">
    <div id="main_structure">
        <!-- LEFT SIDE PORTLETS -->
        <div id="left_port">
            <br />
            <tal:block tal:repeat="item here/get_left_portlets_objects">
                <tal:block tal:replace="structure python:item({'here': here, 'portlet_macro': 'portlet_left_macro'})" />
            </tal:block>
        </div>
        <!-- END OF LEFT SIDE PORTLETS -->
        <tal:block condition="isArabic" replace="structure string:&lt;table width='100%'&gt;&lt;tr&gt;&lt;td&gt;" />
        <div id="middle_right_port">
            <span tal:replace="structure here/messages_box" />
            <a name="contentstart" id="contentstart"></a>
            <metal:block define-slot="body">

            <!--SITE_HEADERFOOTER_MARKER-->

            </metal:block>
            <div class="right_forcer">&nbsp;</div>
                <div id="site_footer">
                    <div id="footer">
                        <div id="site_update">
                            <span i18n:translate="">Page last updated: </span>
                            <span tal:replace="python:here.utShowDateTime(here.bobobase_modification_time())" />
                        </div>

                        <ul tal:define="l_list python:here.getPortletsTool().getLinksListById('footer_links').get_links_list()">
                            <li>
                                <a href="javascript:print()" title="Print"><img style="vertical-align:middle;" src="misc_/SEMIDE/print.gif" alt="Print" /></a> |
                            </li>
                            <tal:block tal:repeat="item l_list">
                            <li tal:condition="python:here.checkPermissionForLink(item.permission, here)">
                                <a tal:attributes="href python:test(item.relative, '%s%s' % (site_url, item.url), item.url); title item/description" tal:content="item/title" i18n:translate="" i18n:attributes="title">Title</a> |
                            </li>
                            </tal:block>
                        </ul>

                        <br />
                        <div class="right_forcer">&nbsp;</div>
                    </div>
                </div>
        </div>
        <tal:block condition="isArabic" replace="structure string:&lt;/td&gt;&lt;/tr&gt;&lt;/table&gt;" />
    </div>
</div>

<!-- Google Analytics -->
<script src="http://www.google-analytics.com/urchin.js" type="text/javascript">
</script>
<script type="text/javascript">
_uacct = "UA-1033835-2";
urchinTracker();
</script>
<!-- Google Analytics-END -->
</body>
</metal:block>
</html>
</metal:block>
"""
