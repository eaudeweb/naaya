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
import re

#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from OFS.Folder import Folder

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript, PRIORITY


mapping = {'METATYPE_NYNEWS': "'Naaya News'",
           'METATYPE_NYEVENT': "'Naaya Event'",
           'METATYPE_NYSTORY': "'Naaya Story'",
           'METATYPE_FOLDER': "'Naaya Folder'",
           }

match = r"\w*\.get_constant\('(\w*)'\)"


class UpdateMigrateToEggs(UpdateScript):
    """ Migrates existing portals to eggs """
    title = 'Migrate portals to eggs'
    creation_date = 'Oct 14, 2009'
    authors = ['David Batranu']
    description = 'Migrates existing portals to eggs. Currently it replaces get_constant with the actual meta_type'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        # replace get_constant with the actual meta_type
        self.update_channels(portal)
        self.update_site_headers(portal)
        return True

    def update_site_headers(self, portal):
        for skin in portal['portal_layout'].objectValues('Naaya Skin'):
            skin_content = skin['site_header'].read()
            updated_content = self.replace_constant(skin_content, skin.absolute_url(1))
            if updated_content:
                skin['site_header'].pt_edit(text=updated_content, content_type='text/html')


    def update_channels(self, portal):
        for channel in portal['portal_syndication'].objectValues('Naaya Script Channel'):
            channel_content = channel.read()
            updated_content = self.replace_constant(channel_content, channel.absolute_url(1))
            if updated_content:
                channel.write(updated_content)

    def replace_constant(self, content, obj_url):
        updated_content = ''
        if 'get_constant' in content:
            try:
                found = re.search(match, content).group(1)
            except AttributeError:
                self.log.debug("Could not properly identify 'get_constant' in %s" % obj_url)
            replacement = mapping.get(found, '')
            if replacement:
                updated_content = re.sub(match, replacement, content)
                self.log.debug("Replaced '%s' with '%s' in %s" % (found, replacement, obj_url))
            else:
                self.log.debug("No replacement is defined for %s" % found)
        return updated_content
