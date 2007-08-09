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
# Agency (EEA). Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alec Ghica, Eau de Web
# Cornel Nitu, Eau de Web

#Python imports
from os.path import join, isfile
import os
from OFS.History import html_diff
import copy

from OFS.Folder import Folder
import Globals
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl.Permissions import view_management_screens
from AccessControl import ClassSecurityInfo

from Products.Naaya.managers.skel_parser import skel_parser
from Products.naayaUpdater.utils import *
from Products.NaayaContent.constants import NAAYACONTENT_PRODUCT_PATH

UPDATERID = 'naaya_updates'
UPDATERTITLE = 'Update scripts for Naaya'
NAAYAUPDATER_PRODUCT_PATH = Globals.package_home(globals())

class NaayaUpdater(Folder):
    """NaayaUpdater class"""

    meta_type = 'Naaya Updater'
    icon = 'misc_/naayaUpdater/updater.jpg'

    def manage_options(self):
        """ """
        l_options = (Folder.manage_options[0],)
        l_options += ({'label': 'View', 'action': 'index_html'},) + Folder.manage_options[3:8]
        return l_options

    security = ClassSecurityInfo()

    def __init__(self, id):
        """constructor"""
        self.id = id
        self.title = UPDATERTITLE


    ###
    #General stuff
    ######
    security.declareProtected(view_management_screens, 'index_html')
    index_html = PageTemplateFile('zpt/updater_index', globals())

    security.declareProtected(view_management_screens, 'getRootNaayaSites')
    def getRootNaayaSites(self, context, meta_types):
        """ """
        res = []
        [res.append(portal) for portal in context.objectValues(meta_types)]
        return res

    security.declareProtected(view_management_screens, 'getNaayaSites')
    def getNaayaSites(self, context, meta_types):
        """ """
        res = []
        for portal in context.objectValues(meta_types):
            res.append(portal)
            if len(portal.objectValues(meta_types)) > 0:
                res.extend(self.getNaayaSites(portal, meta_types))
        return res


    ###
    #See all modified forms
    ######
    security.declareProtected(view_management_screens, 'show_alldiff_html')
    show_alldiff_html = PageTemplateFile('zpt/show_alldiff', globals())

    security.declareProtected(view_management_screens, 'getAllModified')
    def getAllModified(self, meta_types, nonrecursive=True, forms=True, contentype_forms=False, portlets=False, layout=False):
        """ """
        root = self.getPhysicalRoot()
        meta_types = convertToList(meta_types)
        out_modified = []
        out_unmodified = []
        out_diff = 0

        if nonrecursive:
            for portal in self.getRootNaayaSites(root, meta_types):
                modified, unmodified, list_diff = self.get_modified_forms(portal)
                out_modified.extend(modified)
                out_unmodified.extend(unmodified)
                out_diff += list_diff
        else:
            portals_list = self.getNaayaSites(root, meta_types)
            for portal in portals_list:
                modified, unmodified, list_diff = self.get_modified_forms(portal)
                out_modified.extend(modified)
                out_unmodified.extend(unmodified)
                out_diff += list_diff
        return out_modified, out_unmodified, out_diff


    ###
    #Reinstall Naaya content types
    ######
    security.declareProtected(view_management_screens, 'reinstall_contenttypes_html')
    reinstall_contenttypes_html = PageTemplateFile('zpt/reinstall_contenttypes', globals())

    security.declareProtected(view_management_screens, 'reloadMetaTypesForms')
    def reloadMetaTypesForms(self, portal):
        """ reload Naaya portal forms"""
        for meta_type in portal.get_pluggable_metatypes():
            item = portal.get_pluggable_item(meta_type)
            #chech if the meta_type is installed
            if portal.is_pluggable_item_installed(meta_type):
                portal.manage_uninstall_pluggableitem(meta_type)  #uninstall
                portal.manage_install_pluggableitem(meta_type)    #install

    security.declareProtected(view_management_screens, 'reinstallMetaTypes')
    def reinstallMetaTypes(self, meta_types='Naaya Site', nonrecursive=True, modified=True, exclude='', REQUEST=None):
        """ reinstall active metatypes for Naaya portals"""
        root = self.getPhysicalRoot()
        meta_types = convertToList(meta_types)

        #TODO: to implement MODIFIED parameter
        if nonrecursive:
            for portal in self.getRootNaayaSites(root, meta_types):
                self.reloadMetaTypesForms(portal)
        else:
            portals_list = self.getNaayaSites(root, meta_types)
            for portal in portals_list:
                self.reloadMetaTypesForms(portal)

        #TODO: to create/show the report
        return ''


    ###
    #Overwritte Naaya forms
    ######
    security.declareProtected(view_management_screens, 'overwritte_forms_html')
    overwritte_forms_html = PageTemplateFile('zpt/overwritte_forms', globals())

    security.declareProtected(view_management_screens, 'diff_forms_html')
    diff_forms_html = PageTemplateFile('zpt/diff_forms', globals())

#    security.declareProtected(view_management_screens, 'getPortalCreationDate')
#    def getPortalCreationDate(self, portal):
#        """ """
#        creation_date = portal.error_log.bobobase_modification_time()
#        for form in portal.getFormsTool().objectValues("Naaya Template"):
#            creation_date = minDate(form.bobobase_modification_time(), creation_date)
#        return creation_date

    security.declarePrivate('get_modified_forms')
    def get_modified_forms(self, portal):
        """ return the list of modified forms inside this portal"""

        EXCLUSION_FORMS_LIST = ['site_admin_comments', 'site_admin_network', 'site_external_search', 'site_admin_properties']
        modified = []   #modified forms list
        unmodified = [] #unmodified forms list

        forms_date_list = [(f.bobobase_modification_time(), f) for f in portal.getFormsTool().objectValues("Naaya Template")]
        forms_date_list.sort()

        if forms_date_list[0][0] != forms_date_list[-1][0]:
            for fdate in forms_date_list:
                f = fdate[1]    #get form object
                if f.id not in EXCLUSION_FORMS_LIST and f.id.find('_old') == -1:
                    if f.bobobase_modification_time() > forms_date_list[0][0]:
                        modified.append(f)
                    else:
                        unmodified.append(f)

        list_diff = len(forms_date_list) - len(modified)    #number of unmodified forms
        return modified, unmodified, list_diff

    security.declarePrivate('_get_path')
    def _get_path(self, metatype):
        """ return the product path """
        portal_path = NAAYAUPDATER_PRODUCT_PATH.split(os.sep)[:-1]
        product_name = metatype.split(' ')[0]
        if product_name.lower() == 'chm': product_name = 'CHM2'
        portal_path.append(product_name)
        return str(os.sep).join(portal_path)

    security.declarePrivate('_list_forms')
    def _list_forms(self, metatype=''):
        portal_product_path = self._get_path(metatype)
        skel_handler, error = skel_parser().parse(readFile(join(portal_product_path, 'skel', 'skel.xml'), 'r'))
        if skel_handler.root.forms is not None:
            return [f.id for f in skel_handler.root.forms.forms]

    security.declarePrivate('_get_contenttypes_form')
    def _get_contenttypes_form(self, idform, portal):
        portal_product_path = self._get_path(portal.meta_type)
        data_path = join(portal_product_path, 'skel', 'forms')

        for meta_type in portal.get_pluggable_metatypes():
            if portal.is_pluggable_item_installed(meta_type):
                pitem = portal.get_pluggable_item(meta_type)
                #load pluggable item's data
                for frm in pitem['forms']:
                    if idform == frm:
                        frm_name = '%s.zpt' % frm
                        if isfile(join(data_path, frm_name)):
                            #load form from the 'forms' directory because it si customized
                            content = readFile(join(data_path, frm_name), 'r')
                        else:
                            #load form from the pluggable meta type folder
                            content = readFile(join(NAAYACONTENT_PRODUCT_PATH, pitem['module'], 'zpt', frm_name), 'r')
                        break
        return content

    security.declarePrivate('_get_form')
    def _get_form(self, idform, metatype=''):
        portal_product_path = self._get_path(metatype)
        skel_handler, error = skel_parser().parse(readFile(join(portal_product_path, 'skel', 'skel.xml'), 'r'))
        if skel_handler.root.forms is not None:
            return readFile(join(portal_product_path, 'skel', 'forms', '%s.zpt' % idform), 'r')

    security.declarePrivate('getFSForm')
    def getFSForm(self, idform, pathportal):
        """ return the content of the filesystem template """
        NAAYA_METATYPE = 'Naaya Site'
        root = self.getPhysicalRoot()
        portal = root.unrestrictedTraverse(pathportal)

        if idform in self._list_forms(portal.meta_type):
            content = self._get_form(idform, portal.meta_type)   #get filesystem template content
        elif idform in self._list_forms(NAAYA_METATYPE):
            content = self._get_form(idform, NAAYA_METATYPE)   #get filesystem template content
        else:
            #is pluggable content type
            content = self._get_contenttypes_form(idform, portal)
        return content

    security.declarePrivate('getZMIForm')
    def getZMIForm(self, pathform):
        """ return the content of the ZMI template """
        root = self.getPhysicalRoot()
        return root.unrestrictedTraverse(pathform)

    security.declareProtected(view_management_screens, 'diffTemplate')
    def diffTemplate(self, idform, pathform, pathportal):
        """ """
        fs_content = self.getFSForm(idform, pathportal)
        zmi_content = self.getZMIForm(pathform)
        return html_diff(fs_content, zmi_content._text)

    security.declareProtected(view_management_screens, 'getReportModifiedForms')
    def getReportModifiedForms(self, meta_types='Naaya Site', nonrecursive=True, modified=True, REQUEST=None):
        """ overwritte Naaya portal forms """
        if REQUEST.has_key('show_report'):
            root = self.getPhysicalRoot()
            meta_types = convertToList(meta_types)

            if nonrecursive:
                portals_list = self.getRootNaayaSites(root, meta_types)
            else:
                portals_list = self.getNaayaSites(root, meta_types)

            out_modified = []
            out_diff = 0
            for portal in portals_list:
                if modified:
                    modified, unmodified, list_diff = self.get_modified_forms(portal)
                    #final check
                    buf = copy.copy(modified)
                    for m in buf:
                        zmi = self.getFSForm(m.id, portal.absolute_url(1))
                        if create_signature(m._text) == create_signature(zmi):
                            modified.remove(m)
                    #check for unmodified
                    out_modified.append((modified, portal))
                    out_diff += list_diff
            return out_modified, out_diff

    security.declareProtected(view_management_screens, 'reloadPortalForms')
    def reloadPortalForms(self, fmod, REQUEST=None):
        """ reload portal forms """
        fmods = convertToList(fmod)
        for f in fmods:
            form_ob = self.getZMIForm(f)
            site = form_ob.getSite() #use the acquisition to obtain the site object
            fs_content = self.getFSForm(form_ob.id, site.absolute_url(1))
            try:
                form_ob.pt_edit(text=fs_content, content_type='')
            except Exception, error:
                print error
        return REQUEST.RESPONSE.redirect('%s/overwritte_forms_html?u=1' % self.absolute_url())


Globals.InitializeClass(NaayaUpdater)