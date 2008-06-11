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
    """ Add frontpicture attribute to Naaya Documents"""
    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Update Naaya Semide Document properties'
        self.description = 'Add imageContainer attribute.'
        self.update_meta_type = 'Naaya Semide Document'

    def _verify_doc(self, doc):
        # Verify ZODB storage
        if not hasattr(doc, 'imageContainer'):
            return doc
        logger.debug('%-15s %s', 'Skip NySemDocument', doc.absolute_url(1))
        return None

    def _update(self):
        updates = self._list_updates()
        for update in updates:
            logger.debug('%-15s %s', 'Update NySemDocument', update.absolute_url(1))
            setattr(update, 'imageContainer', NyImageContainer(update, True))

def register(uid):
    return CustomContentUpdater(uid)