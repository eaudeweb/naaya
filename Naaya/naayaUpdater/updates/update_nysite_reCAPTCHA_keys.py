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
# Cristian Ciupitu, Eau de Web
from Products.naayaUpdater.updates import nyUpdateLogger as logger
from Products.naayaUpdater.NaayaContentUpdater import NaayaContentUpdater

class CustomContentUpdater(NaayaContentUpdater):
    """Add reCAPTCHA keys to Naaya Site if necessarily"""
    _properties=({'id':'recaptcha_public_key', 'type': 'string','mode':'w'},
                 {'id':'recaptcha_private_key', 'type': 'string','mode':'w'},)

    def manage_options(self):
        """ ZMI tabs """
        return ({'label':'Properties', 'action':'manage_propertiesForm'},) + \
                NaayaContentUpdater.manage_options(self)

    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Update Naaya Site properties'
        self.description = 'Add reCAPTCHA keys if necessarily'
        self.recaptcha_public_key = ''
        self.recaptcha_private_key = ''

    def _verify_doc(self, doc):
        """See super"""
        for i in self._properties:
            key = i['id']
            if not getattr(doc, key, ''):
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
        updates = self._list_updates()
        for update in updates:
            for i in self._properties:
                key = i['id']
                key_val = getattr(self, key)
                logger.debug('Updated %s: set %s to %s' % (update.absolute_url(1), key, key_val))
                setattr(update, key, key_val)

def register(uid):
    return CustomContentUpdater(uid)
