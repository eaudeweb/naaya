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

from StringIO import StringIO
#  cStringIO doesn't work! Need to see why
__version__ = '0.0.1'

class CustomContentUpdater(NaayaContentUpdater):
    """ Move NyPhotos from ZODB to local disk"""
    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Update Naaya Photo Archive to version 2.0'
        self.description = 'Step 3 - Generate listing display'
        self.update_meta_type = 'Naaya Photo'

    def _verify_doc(self, doc):
        """  """
        if doc.is_generated('Album'):
            return None
        return doc

    def _update(self):
        """ Update """
        updates = self._list_updates()
        for update in updates:
            logger.debug('Generate album display for image: %s', update.absolute_url(1))
            update._getDisplay('Album')

def register(uid):
    return CustomContentUpdater(uid)
