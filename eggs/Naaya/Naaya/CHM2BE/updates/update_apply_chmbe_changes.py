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

import os
from Products.PageTemplates.ZopePageTemplate import manage_addPageTemplate
from Products.naayaUpdater.updates import nyUpdateLogger as logger
from Products.naayaUpdater.NaayaContentUpdater import NaayaContentUpdater
from Products.CHM2BE.constants import CHM2BE_PRODUCT_PATH
from Products.CHM2.constants import CHM2_PRODUCT_PATH

class CustomContentUpdater(NaayaContentUpdater):
    """ """
    _properties=({'id':'version', 'type': 'float','mode':'w'},)
    
    version = 1.0
    
    def manage_options(self):
        """ ZMI tabs """
        return NaayaContentUpdater.manage_options(self) + (
            {'label':'Properties', 'action':'manage_propertiesForm'},)

    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Apply CHM-BE changes'
        self.description = 'Import custom chm-be skel.xml'
    
    def _verify_doc(self, doc):
        """ See super"""
        version = getattr(doc, 'version', None)
        if version is None:
            return doc
        if float(version) < float(self.version):
            return doc
        
        logger.debug('Skip site %s version: %s self.version: %s',
                     doc.absolute_url(1), version, self.version)
        return None
    
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
            update.loadSkeleton(os.path.join(CHM2BE_PRODUCT_PATH, 'skel'))
            update.version = self.version
            self._update_map_index(update)
            
            logger.debug('%-70s [UPDATED]', update.absolute_url(1))

    #
    # Custom updates
    #
    def _update_map_index(self, portal):
        custom_map_index = portal.futRead(
            os.path.join(CHM2_PRODUCT_PATH, 'skel', 'others', 'map_index.zpt'))
        portal_map = portal.getGeoMapTool()
        if not portal_map._getOb('map_index', None):
            manage_addPageTemplate(portal_map, id='map_index', title='', text='')
        map_index = portal_map._getOb('map_index')
        map_index.pt_edit(text=custom_map_index, content_type='')
        return map_index.getId()

def register(uid):
    return CustomContentUpdater(uid)
