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
from os.path import join
from Products.naayaUpdater.updates import nyUpdateLogger as logger
from Products.naayaUpdater.NaayaContentUpdater import NaayaContentUpdater
from Products.Naaya.constants import NAAYA_PRODUCT_PATH

class CustomContentUpdater(NaayaContentUpdater):
    """Add email_notifyoncomment template to portal_email if missing"""

    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Update email_notifyoncomment template'
        self.description = 'Add email_notifyoncomment template to portal_email if missing.'
    
    def _verify_doc(self, doc):
        """ See super"""
        etool = getattr(doc, 'portal_email', None)
        if not etool:
            logger.debug('Skip site %s, missing portal_email tool.', doc.absolute_url())
            return None
        if getattr(etool, 'email_notifyoncomment', None) is not None:
            logger.debug('Skip site %s, already up-to-date.', doc.absolute_url())
            return None
        return etool
    
    def _list_updates(self):
        """ Return all portals that need update"""
        portals = self.getPortals()
        for portal in portals:
            update = self._verify_doc(portal)
            if not update:
                continue
            yield update
    
    def _update(self):
        updates = self._list_updates()
        for update in updates:
            logger.debug('Update object %s', update.absolute_url())
            data_path = join(NAAYA_PRODUCT_PATH, 'skel', 'emails', 'email_notifyoncomment.txt')
            template_data = update.futRead(data_path, 'r')
            update.manage_addEmailTemplate('email_notifyoncomment', 'Comment notification', template_data)

def register(uid):
    return CustomContentUpdater(uid)
