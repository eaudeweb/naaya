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
    """Adds the islink setting to Naaya LinkChecker"""

    meta_type = "Naaya LinkChecker islink setting Updater"

    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Update Naaya LinkChecker properties'
        self.description = 'Adds the islink setting and sets it to False.'
        self.update_meta_type = 'Naaya LinkChecker'

    def _verify_doc(self, doc):
        """See super"""
        if getattr(doc, 'portal_linkchecker', None) is not None:
            return doc

    def _list_updates(self):
        """ Return all portals that need update """
        utool = self.aq_inner.aq_parent
        portals = utool.getPortals()
        for portal in portals:
            if not self._verify_doc(portal):
                continue
            yield portal.portal_linkchecker

    def _update(self):
        updates = self._list_updates()
        for update in updates:
            #update = update.portal_linkchecker
            logger.debug('Updating %s' % (update.absolute_url(1),))
            for meta_type, properties in update.objectMetaType.iteritems():
                for i, property in enumerate(properties):
                    if len(property) == 3:
                        logger.debug('  - no need to update property "%s" of meta_type "%s"' % (property[0], meta_type))
                        continue
                    property = tuple(property + (False,))
                    properties[i] = property
                    logger.debug('  - added islink=False to property "%s" of meta_type %s' % (property[0], meta_type))
            update._p_changed = 1

def register(uid):
    return CustomContentUpdater(uid)
