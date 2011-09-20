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
# Andrei Laza, Eau de Web


#Python imports

#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from OFS.Folder import Folder

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from Products.Naaya.adapters import FolderMetaTypes

class UpdateAddForum(UpdateScript):
    """ Update add forum script  """
    title = 'Update add forum to all folders'
    creation_date = 'Sep 17, 2009'
    authors = ['Andrei Laza']
    description = 'Adds the Naaya forum as subobject to all folders and subsequent added folders.'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        to_add = "Naaya Forum"

        filter_out_folders = ['news', 'events', 'stories']
        filter_out_folders_cap = [f.capitalize() for f in filter_out_folders]
        filter_out_folders.extend(filter_out_folders_cap)
        self.log.debug('Filtering out folders: %s', filter_out_folders)

        prop_tool = portal.getPropertiesTool()
        ny_subobjects = [item for item in prop_tool.getProductsMetaTypes() if item in prop_tool.adt_meta_types]
        subobjects = [item for item in prop_tool.get_meta_types(1) if item in prop_tool.adt_meta_types]
        self.log.debug('Found ny_subobjects: %s and subobjects: %s' % (ny_subobjects, subobjects))

        if to_add not in ny_subobjects:
            self.log.debug('Adding %s to ny_subobjects' % to_add)
            ny_subobjects.append(to_add)
            prop_tool.manageSubobjects(subobjects, ny_subobjects)

        ny_folders = [folder for folder in portal.getCatalogedObjectsCheckView(meta_type="Naaya Folder")]
        filtered_folders = []
        for folder in ny_folders:
            f_splits = folder.absolute_url(1).split('/')
            for fs in f_splits:
                if fs in filter_out_folders:
                    break
            else:
                filtered_folders.append(folder)
        ny_folders = filtered_folders

        i, j = 0, 0
        for folder in ny_folders:
            meta_types = FolderMetaTypes(folder)
            f_mt = meta_types.get_values()
            if to_add not in f_mt:
                meta_types.add(to_add)
                i+=1
                self.log.debug('Updated folder %s' % folder.absolute_url(1))
            else:
                j+=1
                self.log.debug('Skipped folder %s' % folder.absolute_url(1))

        self.log.debug('Updated %s folders | Skipped %s folders | Total %s folders' % (i, j, i+j))

        return True


