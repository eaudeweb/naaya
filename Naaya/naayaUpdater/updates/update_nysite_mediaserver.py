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
    """ """
    bulk_update = False
    _properties=({'id':'media_server', 'type': 'string','mode':'w'},)
    
    def manage_options(self):
        """ ZMI tabs """
        return ({'label':'Properties', 'action':'manage_propertiesForm'},) + \
               NaayaContentUpdater.manage_options(self)
    
    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Update Naaya Site properties'
        self.description = 'Add media_server attribute'
        self.media_server = ''
    
    def _verify_doc(self, doc):
        """ """
        return doc
    
    def _list_updates(self):
        """ Return all portals that need update """
        utool = self.aq_inner.aq_parent
        portals = utool.getPortals()
        for portal in portals:
            if not self._verify_doc(portal):
                continue
            yield portal
    
    def _update(self):
        """ """
        updates = self._list_updates()
        for update in updates:
            if not self.media_server:
                raise RuntimeError, 'Please set media server first in Properties tab.'
            logger.debug('Update site %s with property media_server = %s', 
                         update.absolute_url(1), self.media_server)
            setattr(update, 'media_server', self.media_server)

def register(uid):
    return CustomContentUpdater(uid)
