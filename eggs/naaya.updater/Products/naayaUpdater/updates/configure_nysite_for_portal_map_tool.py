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
# Cristian Ciupitu, Eau de Web
from Products.naayaUpdater.NaayaContentUpdater import NaayaContentUpdater
from Products.naayaUpdater.updates import nyUpdateLogger as logger

from Products.NaayaCore.constants import ID_GEOMAPTOOL
from Products.NaayaCore.GeoMapTool.GeoMapTool import GeoMapTool

class CustomContentUpdater(NaayaContentUpdater):
    """Update Naaya GeoMapTool"""
    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Configure Naaya sites for GeoMapTool'
        self.description = 'Configure catalog etc.'
        self.update_meta_type = GeoMapTool.meta_type

    def _verify_doc(self, doc):
        """See super"""
        if getattr(doc, ID_GEOMAPTOOL, None) is not None:
            return doc

    def _list_updates(self):
        """ Return all portals that need update """
        utool = self.aq_inner.aq_parent
        portals = utool.getPortals()
        for portal in portals:
            if not self._verify_doc(portal):
                continue
            yield getattr(portal, ID_GEOMAPTOOL)

    def _update(self):
        for update in self._list_updates():
            update.manage_configureSite()
            logger.debug('Updated %s' % (update.absolute_url(1),))

def register(uid):
    return CustomContentUpdater(uid)
