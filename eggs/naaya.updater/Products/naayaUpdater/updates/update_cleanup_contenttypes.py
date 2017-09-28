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
# Cornel Nitu, Eau de Web

from Products.naayaUpdater.updates import UpdateScript

class UpdateContentType(UpdateScript):
    """
    Generic script to clean up obsolete content-types in Naaya sites. This script must
    ALWAYS be safe to run on ANY site.
    """

    title = 'Cleanup contenttypes'
    authors = ['Cornel Nitu']
    creation_date = 'Feb 11, 2010'
    description = 'Cleans portal contenttypes.'

    def _update(self, portal):
        self.cleanContentTypes(portal)
        return True

    def cleanContentTypes(self, portal):
        """ Cleans portal contenttypes """
        broken_meta_types = set()
        for meta_type in portal.get_pluggable_installed_meta_types():
            if meta_type not in portal.get_pluggable_metatypes():
                self.log.debug(meta_type)
                broken_meta_types.add(meta_type)
        for meta_type in broken_meta_types:
            portal.manage_uninstall_pluggableitem(meta_type)
