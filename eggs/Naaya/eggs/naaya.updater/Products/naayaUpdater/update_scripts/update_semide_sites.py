#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
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
# The Initial Owner of the Original Code is EMWIS/SEMIDE.
# Code created by Finsiel Romania are
# Copyright (C) EMWIS/SEMIDE. All Rights Reserved.
#
# Authors:
#
# Alexandru Plugaru, Eau de Web

#Python imports
import os
from copy import deepcopy

#Zope imports
from DateTime import DateTime
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.StandardCacheManagers.RAMCacheManager import RAMCacheManager
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from OFS.Folder import Folder
from transaction import commit
from ZODB.broken import rebuild

#Naaya imports
from Products.naayaUpdater.update_scripts import UpdateScript, PRIORITY
from Products.SEMIDE.SEMIDESite import SEMIDESite
from Products.Naaya import NySite as NySite_module

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

class UpdateSemideSites(UpdateScript):
    """ Update Semide Sites  """
    id = 'update_semide_sites'
    title = 'Update Semide Sites'
    #meta_type = 'Naaya Update Script'
    creation_date = DateTime('Mar 31, 2010')
    authors = ['Alexandru Plugaru']
    #priority = PRIORITY['LOW']
    description = 'Updates all semide sites for compatibility with Naaya trunk version'
    #dependencies = []
    #categories = []

    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):

        #This should only be enabled on the development version
        
        self.log.debug('Disabling administrator e-mails')
        portal.administrator_email = ''
        portal.notify_on_errors = 0
        
        self.log.debug('Removing RAMCacheManager(s)')
        self.removeRamCacheManagers(portal)
           
        self.removeAddTools(portal)
        
        self.log.debug('Adding jQuery to site header')
        self.addJquery(portal)
        
        self.log.debug('Removing custom forms from FormsTool')
        #self.deleteForms(portal, ['country_custom_footer', 'country_custom_header']) # Completly deletes
        self.removeForms(portal, [ # Sets to FS Template
            'semdocument_add', 'semdocument_edit', 'semdocument_index',
            'country_add', 'country_edit', 'country_editportlet', 'country_index',
            'semevent_add', 'semdevent_edit', 'semevent_index',
            'semnews_add', 'semnews_edit', 'semnews_index',
            'semfieldsite_add', 'semfieldsite_edit',
            'semfunding_add', 'semfunding_edit',
            'semorganisation_add', 'semorganisation_edit',
            'semproject_add', 'semproject_edit', 'semproject_index', 
            'semtextlaws_add', 'semtextlaws_edit', 'semtextlaws_index',
            'site_macro_add', 'site_macro_edit',
        ])
        
        self._unused_meta_types = ('Naaya Entry', 'Naaya EntryPress', )
        self.remove_unused_meta_types(portal)
        
        self.log.debug('Updating some old portlets')
        self.updatePortlets(portal)
        #
        self.log.debug('Migrating photo galleries')
        self.migratePhotoGallery(portal)
        
        #self.log.debug('Switching from site_header + site_footer to standard_template')
        #self.updateLayout(portal)
        
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
        
    def removeForms(self, portal, forms):
        """ Delete *customized* forms from ZMI and use those from disc """
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
        try:
            ltool = portal.getLayoutTool()
            site_header = ltool.get_current_skin().site_header
            site_footer = ltool.get_current_skin().site_footer
            
            site_header_content = site_header.read().split('<!--SITE_HEADERFOOTER_MARKER-->')[0]
            site_footer_content = site_footer.read().split('<!--SITE_HEADERFOOTER_MARKER-->')[1]
            template_content = site_header_content + "\n<!--SITE_HEADERFOOTER_MARKER-->\n" + site_footer_content
            standard_template = Template('standard_template', 'Portal standard template', template_content.encode('utf-8'), '')
            ltool.get_current_skin().manage_delObjects([site_header.id, site_footer.id,])
            ltool.get_current_skin()._setObject(standard_template.id, standard_template)
        except AttributeError:
            pass
        
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

        if portal.id == 'medaquaministerial2008':
            portal.manage_renameObjects(['photos', ], ['photos_old', ])
            photo_gallery_folder = portal.photos_old
            manage_addNyPhotoGallery(portal, id='photos', title=photo_gallery_folder.title)
            new_gallery = portal.photos
            
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
        
        if portal.id == 'medaquaministerial2008': #Delete old gallery folder
            portal.manage_delObjects([photo_gallery_folder.id])

portlets = {
            'portlet_country_left':
"""<tal:block metal:use-macro="python:here.getLayoutTool().getCurrentSkin().getTemplateById(portlet_macro).macros['portlet']">
<tal:block metal:fill-slot="portlet_title">
    <div tal:content="here/get_country_object_title" />
</tal:block>
<tal:block metal:fill-slot="portlet_content">
<ul class="main_menu_ul" tal:define="has_nfp_url python:here.utLinkValue(here.getLocalAttribute('nfp_url')); has_links here/hasLinksValues">
    <li class="main_menu_li" tal:condition="python:has_nfp_url or has_links">
        <a tal:condition="has_nfp_url"
            tal:attributes="href python: here.getLocalAttribute('nfp_url');" title="NFP URL" i18n:attributes="title"
            tal:content="python: here.getLocalAttribute('nfp_label')" />
        <ul class="left_submenu" tal:condition="has_links">
            <li tal:condition="python:here.utLinkValue(here.getLocalAttribute('link_ins'))">
                <a class="inactive_link" tal:attributes="href python: here.getLocalAttribute('link_ins')"
                    title="Institutions" target="_blank" i18n:attributes="title" i18n:translate="">Institutions</a></li>
            <li tal:condition="python:here.utLinkValue(here.getLocalAttribute('link_doc'))">
                <a class="inactive_link" tal:attributes="href python: here.getLocalAttribute('link_doc')"
                    title="Documentation" target="_blank" i18n:attributes="title" i18n:translate="">Documentation</a></li>
            <li tal:condition="python:here.utLinkValue(here.getLocalAttribute('link_train'))">
                <a class="inactive_link" tal:attributes="href python: here.getLocalAttribute('link_train')"
                    title="Training" target="_blank" i18n:attributes="title" i18n:translate="">Training</a></li>
            <li tal:condition="python:here.utLinkValue(here.getLocalAttribute('link_rd'))">
                <a class="inactive_link" tal:attributes="href python: here.getLocalAttribute('link_rd')"
                    title="Research &amp; Development" target="_blank" i18n:attributes="title" i18n:translate="">R&amp;D</a></li>
            <li tal:condition="python:here.utLinkValue(here.getLocalAttribute('link_data'))">
                <a class="inactive_link" tal:attributes="href python: here.getLocalAttribute('link_data')"
                    title="Data management" target="_blank" i18n:attributes="title" i18n:translate="">Data management</a></li>
        </ul>
    </li>
    <li class="main_menu_li" tal:define="item here/contacts">
        <a tal:attributes="class python:test(here.inCountryTopic(item, here), 'active_link', 'inactive_link'); href string:${item/absolute_url}/; title item/tooltip"
            tal:content="item/title_or_id" />
    </li>
    <li class="main_menu_li" tal:define="item here/national_program">
        <a tal:attributes="class python:test(here.inCountryTopic(item, here), 'active_link', 'inactive_link'); href string:${item/absolute_url}/; title item/title_or_id"
            tal:content="item/title_or_id" />
    </li>
    <li class="main_menu_li" tal:define="item here/legislation_water">
        <a tal:attributes="class python:test(here.inCountryTopic(item, here), 'active_link', 'inactive_link'); href string:${item/absolute_url}/; title item/tooltip"
            tal:content="item/title_or_id" />
    </li>
    <li class="main_menu_li" tal:define="item here/project_water">
        <a tal:attributes="class python:test(here.inCountryTopic(item, here), 'active_link', 'inactive_link'); href string:${item/absolute_url}/; title item/tooltip"
            tal:content="item/title_or_id" />
    </li>
    <li class="main_menu_li" tal:define="item here/data_statistics">
        <a tal:attributes="class python:test(here.inCountryTopic(item, here), 'active_link', 'inactive_link'); href string:${item/absolute_url}/; title item/tooltip"
            tal:content="item/title_or_id" />
    </li>
    <li class="main_menu_li" tal:define="item here/links">
        <a tal:attributes="class python:test(here.inCountryTopic(item, here), 'active_link', 'inactive_link'); href string:${item/absolute_url}/; title item/tooltip"
            tal:content="item/title_or_id" />
    </li>
</ul>
</tal:block>
</tal:block>
"""
}