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
# David Batranu, Eau de Web
from Products.naayaUpdater.updates import nyUpdateLogger as logger
from Products.naayaUpdater.utils import get_portals
from Products.naayaUpdater.NaayaContentUpdater import NaayaContentUpdater

class CustomContentUpdater(NaayaContentUpdater):
    """ Add 'allow_overtime' property to the Naaya Survey """
    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Update Naaya Survey properties'
        self.description = 'Add allow_overtime property'
        self.update_meta_type = 'Naaya Mega Survey'

    def _verify_doc(self, doc):
        # Verify ZODB storage
        if not hasattr(doc, 'allow_overtime'):
            return doc
        logger.debug('%-15s %s', 'Skip Survey', doc.absolute_url())
        return None

    def _list_updates(self):
        """ Return all objects that need update"""
        utool = self.aq_inner.aq_parent
        portals = get_portals(self)
        for portal in portals:
            for survey in portal.getCatalogedObjects(meta_type='Naaya Mega Survey'):
                if not self._verify_doc(survey):
                    continue
                yield survey

    def _update(self):
        updates = self._list_updates()
        for update in updates:
            logger.debug('%-15s %s', 'Update Survey', update.absolute_url())
            setattr(update, 'allow_overtime', 0)

def register(uid):
    return CustomContentUpdater(uid)
