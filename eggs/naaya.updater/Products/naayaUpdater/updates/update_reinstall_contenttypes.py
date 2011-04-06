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
# Andrei Laza, Eau de Web


#Python imports

#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript
from Products.naayaUpdater.utils import get_portals, get_portal

class UpdateReinstallContenttypes(UpdateScript):
    """ Update reinstall content types script  """
    title = 'Reinstall Naaya content types'
    authors = ['Alec Ghica', 'Cornel Nitu']
    creation_date = 'Jan 01, 2010'

    security = ClassSecurityInfo()

    security.declareProtected(view_management_screens, 'index_html')
    index_html = PageTemplateFile('zpt/reinstall_contenttypes', globals())

    security.declareProtected(view_management_screens, 'reloadMetaTypesForms')
    def reloadMetaTypesForms(self, portal, contenttypes, ct_action):
        """ reload Naaya portal forms"""
        report = []
        ct_list = []
        for ct_id in contenttypes.split(','):
            ct_list.append(ct_id.strip())

        for meta_type in portal.get_pluggable_metatypes():
            item = portal.get_pluggable_item(meta_type)
            #chech if the meta_type is installed
            if portal.is_pluggable_item_installed(meta_type):
                if (ct_action == 'ect' and meta_type not in ct_list) or \
                   (ct_action == 'ict' and meta_type in ct_list):
                    report.append(meta_type)
                    portal.manage_uninstall_pluggableitem(meta_type)  #uninstall
                    portal.manage_install_pluggableitem(meta_type)    #install

        return report

    security.declareProtected(view_management_screens, 'reinstallMetaTypes')
    def reinstallMetaTypes(self, all=False, ppath='', portals='', p_action='ep',
                           contenttypes='', ct_action='ect', REQUEST=None):
        """ reinstall active metatypes for Naaya portals"""
        report = {}
        portals_custom = []
        for portal_id in portals.split(','):
            portals_custom.append(portal_id.strip())

        if all:
            portals_list = get_portals(self, self.pmeta_types)
            for portal in portals_list:
                do_update = False
                if p_action == 'ep':
                    if not portal.id in portals_custom: do_update = True
                else:
                    if portal.id in portals_custom: do_update = True
                if do_update:
                    report[portal.id] = self.reloadMetaTypesForms(portal, contenttypes, ct_action)
        else:
            portal = get_portal(ppath)
            if not portal.id in portals_custom:
                report[portal.id] = self.reloadMetaTypesForms(portal, contenttypes, ct_action)

        if not REQUEST:
            return report

        REQUEST.SESSION.set('report', report)
        return REQUEST.RESPONSE.redirect(self.absolute_url())
