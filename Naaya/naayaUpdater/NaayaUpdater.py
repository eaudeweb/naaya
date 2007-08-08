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
from os.path import join
import os

from OFS.Folder import Folder
import Globals
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl.Permissions import view_management_screens
from AccessControl import ClassSecurityInfo


from Products.naayaUpdater.utils import *

UPDATERID = 'naaya_updates'
UPDATERTITLE = 'Update scripts for Naaya'

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

    security.declareProtected(view_management_screens, 'index_html')
    index_html = PageTemplateFile('zpt/updater_index', globals())

    ###
    #Reinstall Naaya content types
    ######
    security.declareProtected(view_management_screens, 'reinstall_contenttypes_html')
    reinstall_contenttypes_html = PageTemplateFile('zpt/reinstall_contenttypes', globals())

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

    security.declareProtected(view_management_screens, 'reloadNaayaSiteForms')
    def reloadNaayaSiteForms(self, portal):
        """ reload Naaya portal forms"""
        for meta_type in portal.get_pluggable_metatypes():
            item = portal.get_pluggable_item(meta_type)
            #chech if the meta_type is installed
            if portal.is_pluggable_item_installed(meta_type):
                portal.manage_uninstall_pluggableitem(meta_type)  #uninstall
                portal.manage_install_pluggableitem(meta_type)    #install

    security.declareProtected(view_management_screens, 'reinstallMetaTypes')
    def reinstallMetaTypes(self, meta_types='Naaya Site', nonrecursive=True, modified=True, REQUEST=None):
        """ reinstall active metatypes for Naaya portals"""
        root = self.getPhysicalRoot()
        meta_types = convertToList(meta_types)

        #TODO: to implement MODIFIED parameter
        if nonrecursive:
            for portal in self.getRootNaayaSites(root, meta_types):
                self.reloadNaayaSiteForms(portal)
        else:
            portals_list = self.getNaayaSites(root, meta_types)
            for portal in portals_list:
                self.reloadNaayaSiteForms(portal)

        #TODO: to create/show the report
        return ''

    ###
    #Overwritte Naaya forms
    ######
    security.declareProtected(view_management_screens, 'overwritte_forms_html')
    overwritte_forms_html = PageTemplateFile('zpt/overwritte_forms', globals())

    security.declareProtected(view_management_screens, 'findModifiedForms')
    def getPortalCreationDate(self, portal):
        """ """
        creation_date = portal.error_log.bobobase_modification_time()
        for form in portal.getFormsTool().objectValues("Naaya Template"):
            creation_date = minDate(form.bobobase_modification_time(), creation_date)
        return creation_date

    security.declareProtected(view_management_screens, 'findModifiedForms')
    def findModifiedForms(self, portal):
        """ """
        forms_list = []
        add_form = forms_list.append
        tmp_date = ''

        forms_date = [(form.bobobase_modification_time(), form) for form in portal.getFormsTool().objectValues("Naaya Template")]
        forms_date.sort()
        last_date = forms_date[0][0]

        if forms_date[0][0] != forms_date[-1][0]:
            for form in portal.getFormsTool().objectValues("Naaya Template"):
                if form.id not in ["site_admin_comments", "site_admin_network", "site_external_search", "site_admin_properties"] and "old" not in str(form.id):
                    creation_date = form.bobobase_modification_time()
                    if creation_date > last_date:
                        add_form(form.id)
        return forms_list

    def getPath(self, metatype='EnviroWindows Site'):
        """ """
        res = []
        my_path = Globals.package_home(globals())
        res.extend(my_path.split(os.sep)[:-1])
        res.append(metatype.split(' ')[0])
        return '%s'.join(res) % os.sep

    security.declareProtected(view_management_screens, 'reinstallMetaTypes')
    def overwritteForms(self, meta_types='Naaya Site', nonrecursive=True, modified=True, REQUEST=None):
        """ overwritte Naaya portal forms """
        root = self.getPhysicalRoot()
        meta_types = convertToList(meta_types)

        #TODO: to implement MODIFIED parameter
        if nonrecursive:
            for portal in self.getRootNaayaSites(root, meta_types):
                if modified:
                    for k in self.findModifiedForms(portal):
                        print '%s/portal_forms/%s' % (portal.absolute_url(), k)
        else:
            portals_list = self.getNaayaSites(root, meta_types)
            for portal in portals_list:
                if modified:
                    for k in self.findModifiedForms(portal):
                        print k

        #TODO: to create/show the report
        return ''

Globals.InitializeClass(NaayaUpdater)