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
EMAIL_TEMPLATES = {
    'email_notifyoncomment': 'Comment notification',
    'email_notifyonupload': 'Upload notification',
    'email_confirmuser': 'New user registration confirmation',
}
class CustomContentUpdater(NaayaContentUpdater):
    """Update email templates"""

    _properties = NaayaContentUpdater._properties + (
        {'id':'overwrite', 'type': 'boolean','mode':'w', 'label': 'Overwrite existing templates'},
    )
    
    overwrite = False
    
    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Update email templates'
        self.description = 'Update email templates'
    
    def _verify_doc(self, doc):
        """ See super"""
        etool = getattr(doc, 'portal_email', None)
        if not etool:
            logger.debug('Skip site %s, missing portal_email tool.', doc.absolute_url())
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
            for template, title in EMAIL_TEMPLATES.items():
                data_path = join(NAAYA_PRODUCT_PATH, 'skel', 'emails', template + '.txt')
                template_data = update.futRead(data_path, 'r')
                template_ob = update._getOb(template, None)
                if template_ob:
                    if not self.overwrite:
                        continue
                    update.manage_delObjects([template,])
                logger.debug('Update template %s in %s', template, update.absolute_url())
                update.manage_addEmailTemplate(template, title, template_data)

def register(uid):
    return CustomContentUpdater(uid)
