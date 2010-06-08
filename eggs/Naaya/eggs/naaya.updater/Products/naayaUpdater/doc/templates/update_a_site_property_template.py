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
        self.title = 'Update Naaya Site properties'
        self.description = '<<Update some property>>'
        self._property_name = '<<site property to update>>'
        self._property_value = '<<property value>>'
    
    def _verify_doc(self, doc):
        """ Verify if site property is up-to-date"""
        if getattr(doc, self._property_name, None) != '<condition>':
            return doc
        return None
    
    def _list_updates(self):
        """ Return all portals that need to be updated """
        utool = self.naaya_updates
        portals = utool.getPortals()
        for portal in portals:
            if not self._verify_doc(portal):
                continue
            yield portal
    
    def _update(self):
        """ Update all objects returned by _list_updates"""
        updates = self._list_updates()
        for update in updates:
            logger.debug('Update site %s with property %s=%s.', 
                         update.absolute_url(), self._property_name, self._property_value)
            setattr(update, self._property_name, self._property_value)

def register(uid):
    return CustomContentUpdater(uid)
