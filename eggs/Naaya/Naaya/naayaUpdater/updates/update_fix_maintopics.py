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

from Products.NaayaBase.NyImageContainer import NyImageContainer

class CustomContentUpdater(NaayaContentUpdater):
    """ Update"""
    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Update Naaya Site attributes'
        self.description = 'Update Naaya Site maintopics attribute'
        self.update_meta_type = ''

    def _verify_doc(self, doc):
        # Verify ZODB storage
        doc_id = doc.getId()
        maintopics = getattr(doc, 'maintopics', [])
        for maintopic in maintopics:
            if maintopic.startswith("%s/" % doc_id):
                return doc
        logger.debug("Skip portal - %s", doc.absolute_url())
        return None
    
    def _list_updates(self):
        """ Return all portals that need update"""
        utool = self.aq_inner.aq_parent
        portals = utool.getPortals()
        for portal in portals:
            if not self._verify_doc(portal):
                continue
            yield portal

    def _update(self):
        updates = self._list_updates()
        for update in updates:
            update_id = update.getId()
            update.maintopics = [x.replace("%s/" % update_id, "", 1) for x in update.maintopics]
            logger.debug('Update portal - %s', update.absolute_url())
        self._p_changed = 1

def register(uid):
    return CustomContentUpdater(uid)
