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

META_CHANNELS = ['Naaya Script Channel', 'Naaya Local Channel']
META_TOOL = 'Naaya Syndication Tool'
CACHE_NAME = 'cache_syndication'

class MigrateCatalog(NaayaContentUpdater):
    """ Add a cache manager for portal_syndication tool in every site and
    associate it to Local Channels and Script Channels
    """
    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Cache syndication channels'
        self.description = 'Cache script and local channels'
        self.update_meta_type = ''

    def _verify_doc(self, doc):
        """ """
        stool = doc.getSyndicationTool()
        channels = stool.objectValues(META_CHANNELS)
        for channel in channels:
            if not channel.ZCacheable_getManager():
                yield channel

    def _list_updates(self):
        """ """
        utool = self.naaya_updates
        portals = utool.getPortals()
        for portal in portals:
            docs = self._verify_doc(portal)
            for doc in docs:
                yield doc
    
    def _update_channel_cache_manager(self, doc):
        stool = doc.getSyndicationTool()
        if not stool.objectIds('RAM Cache Manager'):
            logger.debug('Add RAM Cache Manager to %s', stool.absolute_url(1))
            manage_addRAMCacheManager(stool, CACHE_NAME)
        
        logger.debug('Set Cache manager for channel %s -> %s',
                     doc.absolute_url(1), CACHE_NAME)
        doc.ZCacheable_setManagerId(CACHE_NAME)

    def _update(self):
        """ Apply updates """
        updates = self._list_updates()
        for update in updates:
            self._update_channel_cache_manager(update)

def register(uid):
    return MigrateCatalog(uid)
