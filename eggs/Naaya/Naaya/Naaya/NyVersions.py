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
# Dragos Chirila, Finsiel Romania

#Python imports

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens

#Product imports
from constants import *

class NyVersions:
    """
    Class for upgrading from one version to another.
    """

    security = ClassSecurityInfo()

    security.declareProtected(view_management_screens, 'upgrade_submitted')
    def upgrade_submitted(self):
        """
        Add 'submitted' property for all objects and recatalog them.
        """
        catalog_tool = self.getCatalogTool()
        for b in self.getCatalogedBrains():
            x = catalog_tool.getobject(b.data_record_id_)
            x.submitThis()
            self.recatalogNyObject(x)
        return "Upgrading OK: 'submitted' property added for all objects."

    security.declareProtected(view_management_screens, 'upgrade_mailfrom')
    def upgrade_mailfrom(self):
        """
        Add 'mail_address_from' property for Naaya sites
        """
        self.mail_address_from = ''
        self._p_changed = 1
        return "Upgraded OK: created email from property for portal"

    security.declareProtected(view_management_screens, 'upgrade_others')
    def upgrade_others(self):
        """
        Upgrade other stuff.
        """
        self.show_releasedate = 1
        self.submit_unapproved = 1
        self._p_changed = 1
        return "Upgraded OK: show_releasedate and submit_unapproved"

    security.declareProtected(view_management_screens, 'upgrade_photoarchive')
    def upgrade_photoarchive(self):
        """
        Upgrade other stuff.
        """
        self.PhotoArchive.submitted = 1
        self._p_changed = 1
        return "Upgraded OK: submitted for PhotoArchive"

    security.declareProtected(view_management_screens, 'upgrade_netregistry')
    def upgrade_netregistry(self):
        """
        Upgrade other stuff.
        """
        self.net_repository.submitted = 1
        self._p_changed = 1
        for site in self.net_repository.get_netsites():
            site.submitted = 1
            site._p_changed = 1
            self.recatalogNyObject(site)
            for channel in site.get_netchannels():
                channel.submitted = 1
                channel._p_changed = 1
                self.recatalogNyObject(channel)
        return "Upgraded OK: submitted for NetRepository"
            

    security.declareProtected(view_management_screens, 'set_contributor')
    def set_contributor(self, new_contributor, folder_name):
        """
        set contributor for objects with an empty string as contributor.
        """
        naaya_site = self.getSite()
        for i in naaya_site.objectValues('Naaya Folder')
            if i.id==folder_name:
                if x.contributor=="":
                    x.setContributor(new_contributor)
        return "Contributor set up."


InitializeClass(NyVersions)
