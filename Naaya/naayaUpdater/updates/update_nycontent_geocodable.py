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
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# David Batranu, Eau de Web
from Products.naayaUpdater.updates import nyUpdateLogger as logger
from Products.naayaUpdater.NaayaContentUpdater import NaayaContentUpdater

class CustomContentUpdater(NaayaContentUpdater):
    """ Add new properties to Naaya content types to allow geocoding """
    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Update Naaya content types with geocoding properties'
        self.description = 'Step 3 - Add geocoding properties'
        self.update_meta_type = 'Naaya Content'
        self.props = ['longitude', 'latitude', 'address', 'url', 'geo_type']

    def _verify_doc(self, doc):
        # Verify ZODB storage

        for prop in self.props:
            if not hasattr(doc, prop):
                return doc
            logger.debug('%-15s %s', 'Content has property %s' % prop, doc.absolute_url())
        return None

    def _list_updates(self):
        """ Return all objects that need update"""
        utool = self.aq_inner.aq_parent
        portals = utool.getPortals()
        for portal in portals:
            content_types = portal.get_pluggable_installed_meta_types()
            objects = portal.getCatalogedObjects(meta_type=content_types)
            for ny_content in objects:
                if not self._verify_doc(ny_content):
                    continue
                yield ny_content

    def _update(self):
        updates = self._list_updates()
        for update in updates:
            logger.debug('%-15s %s', 'Update content', update.absolute_url())
            for prop in self.props:
                setattr(update, prop, '')

def register(uid):
    return CustomContentUpdater(uid)
