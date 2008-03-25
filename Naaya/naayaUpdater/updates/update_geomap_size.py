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
# Alin Voinea, Eau de Web
from Products.naayaUpdater.updates import nyUpdateLogger as logger
from Products.naayaUpdater.NaayaContentUpdater import NaayaContentUpdater

class CustomContentUpdater(NaayaContentUpdater):
    """ Add size-related attributes to Naaya GeoMap Tool"""
    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Update Naaya GeoMap Tool properties'
        self.description = 'Add size-related attributes.'
        self.update_meta_type = 'Naaya GeoMap Tool'

    def _verify_doc(self, doc):
        # Verify ZODB storage
        if not hasattr(doc, 'map_width'):
            return doc
        logger.debug('%-15s %s', 'Skip Naaya GeoMap Tool', doc.absolute_url(1))
        return None

    def _list_updates(self):
        """ Return all objects that need update"""
        utool = self.aq_inner.aq_parent
        portals = utool.getPortals()
        for portal in portals:
            doc = portal.getGeoMapTool()
            if doc is None:
                continue
            if not self._verify_doc(doc):
                continue
            yield doc

    def _update(self):
        updates = self._list_updates()
        for update in updates:
            logger.debug('%-15s %s', 'Update Naaya GeoMap Tool', update.absolute_url(1))
            setattr(update, 'map_width', 600)
            setattr(update, 'map_height', 300)
            setattr(update, 'detailed_map_width', 400)
            setattr(update, 'detailed_map_height', 400)

def register(uid):
    return CustomContentUpdater(uid)
