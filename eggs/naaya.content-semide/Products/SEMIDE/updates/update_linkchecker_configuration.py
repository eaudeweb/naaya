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
    """ Update a site property"""
    
    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Update Naaya LinkChecker '
        self.description = 'Configure Naaya LinkChecker ObjectMetaType'
    
    def _verify_doc(self, doc):
        """ Verify if site property is up-to-date"""
        return doc.objectValues('Naaya LinkChecker')
    
    def _list_updates(self):
        """ Return all portals that need to be updated """
        utool = self.naaya_updates
        portals = utool.getPortals()
        for portal in portals:
            for doc in self._verify_doc(portal):
                yield doc
    
    def _update(self):
        """ Update all objects returned by _list_updates"""
        updates = self._list_updates()
        for linkchecker_ob in updates:
            meta_types = linkchecker_ob.getObjectMetaTypes()
            logger.debug('Deleting objectMetaTypes for Naaya LinkChecker %s', linkchecker_ob.absolute_url())
            linkchecker_ob.manage_delMetaType(objectMetaType=meta_types)
            logger.debug('Update objectMetaTypes for Naaya LinkChecker %s', linkchecker_ob.absolute_url())
            linkchecker_ob.getSite()._configure_linkchecker(linkchecker_ob)

def register(uid):
    return CustomContentUpdater(uid)
