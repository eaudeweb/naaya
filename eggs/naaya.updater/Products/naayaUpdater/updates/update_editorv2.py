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
# David Batranu, Eau de Web


#Python imports

#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from OFS.Folder import Folder

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from Products.NaayaCore.EditorTool.EditorTool import manage_addEditorTool


class UpdateExample(UpdateScript):
    """ Update portal editor to version 2"""
    title = 'Update NaayaEditorTool.v2'
    creation_date = 'Dec 16, 2009'
    authors = ['David Batranu']
    description = 'Updates Naaya Editor Tool to latest version. Removes and adds portal_editor. Catalogs Naaya Photo Folder objects.'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        self.remove_and_add(portal)
        self.update_catalog(portal)
        return True

    def update_catalog(self, portal):
        catalog = portal.getCatalogTool()
        self.walk_folders(portal, catalog)

    def walk_folders(self, folder, catalog):
        for ob in folder.objectValues():
            if not isinstance(ob, (Folder)):
                continue

            if ob.meta_type in ["Naaya Photo Folder"]:
                try:
                    catalog.catalog_object(ob)
                    self.log.debug("Cataloged object %s" % ob.absolute_url(1))
                except Exception, err:
                    self.log.debug("Error occurred while cataloging %s (%s)" % (ob.absolute_url(1), err))

            if isinstance(ob, Folder):
                self.walk_folders(ob, catalog)

    def remove_and_add(self, portal):
        if hasattr(portal.aq_base, 'portal_editor'):
            try:
                portal.manage_delObjects(['portal_editor'])
                self.log.debug("Removed editor tool.")
            except Exception, err:
                self.log.debug("Error occurred while trying to delete editor tool. (%s)" % err)
        try:
            manage_addEditorTool(portal)
            self.log.debug("Added editor tool.")
        except Exception, err:
                self.log.debug('Error occurred while trying to add editor tool. (%s)' % err)
