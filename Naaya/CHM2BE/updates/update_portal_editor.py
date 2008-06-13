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
from Products.NaayaCore.EditorTool.EditorTool import manage_addEditorTool

class CustomContentUpdater(NaayaContentUpdater):
    """ """

    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Remove & Add CHM portal_editor'
        self.description = 'Replace obsolete portal_editors with new instances for CHM Sites'
    
    def _verify_doc(self, doc):
        """ See super"""
        return doc
    
    def _list_updates(self):
        """ Return all portals that need update"""
        utool = self.aq_inner.aq_parent
        portals = utool.getPortals(meta_types=['CHM Site'])
        for portal in portals:
            if not self._verify_doc(portal):
                continue
            yield portal
    
    def _update(self):
        updates = self._list_updates()
        for update in updates:
            if getattr(update, 'portal_editor', None):
                update.manage_delObjects(['portal_editor'])
            manage_addEditorTool(update)
            logger.debug('%-70s [UPDATED]', update.absolute_url(1))

def register(uid):
    return CustomContentUpdater(uid)
