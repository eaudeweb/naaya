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
from Products.StandardCacheManagers.RAMCacheManager import manage_addRAMCacheManager
from Products.Naaya.constants import FOLDER_CACHE_MANAGER

class CustomContentUpdater(NaayaContentUpdater):
    """ Add a cache manager for portal_syndication tool in every site and
    associate it to Local Channels and Script Channels
    """
    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Cache SEMIDE Site folder channels'
        self.description = 'Cache SEMIDE Site search_atom/search_rdf channels'
        self.update_meta_type = ''

    def _verify_doc(self, doc):
        """ """
        if doc.ZCacheable_getManagerId() != FOLDER_CACHE_MANAGER:
            return doc
        logger.debug('Skip %s: Already up-to-date', doc.absolute_url(1))
        return None
    
    def _list_updates(self):
        utool = self.naaya_updates
        portals = utool.getPortals(meta_types='SEMIDE Site')
        for portal in portals:
            if self._verify_doc(portal):
                yield portal

    def _update_doc(self, doc):
        if FOLDER_CACHE_MANAGER not in doc.objectIds('RAM Cache Manager'):
            logger.debug('Add RAM Cache Manager to %s', doc.absolute_url(1))
            manage_addRAMCacheManager(doc, FOLDER_CACHE_MANAGER)
        
        logger.debug('Set Cache manager for channel %s -> %s',
                     doc.absolute_url(1), FOLDER_CACHE_MANAGER)
        doc.ZCacheable_setManagerId(FOLDER_CACHE_MANAGER)

    def _update(self):
        """ Apply updates """
        updates = self._list_updates()
        for update in updates:
            self._update_doc(update)

def register(uid):
    return CustomContentUpdater(uid)
