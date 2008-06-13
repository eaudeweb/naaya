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
from Products.ExtFile.ExtImage import ExtImage

class CustomContentUpdater(NaayaContentUpdater):
    """ Move NyPhotos from ZODB to local disk"""
    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Update Naaya Photos storage type'
        self.description = 'Move files from ZODB to disk.'
        self.update_meta_type = 'Naaya Photo'

    def _verify_doc(self, doc):
        """ Check for ZODB storage """
        # Verify ZODB storage
        if getattr(doc, 'data', ''):
            return doc
        logger.debug('%-23s %s', 'Skip NyPhoto', doc.absolute_url(1))
        return None
    
    def _update_doc_data(self, doc):
        """ Move doc data from ZODB to disk"""
        logger.debug('%-23s %s', 'Update NyPhoto data', doc.absolute_url(1))
        if not hasattr(doc, '_ext_file'):
            doc._ext_file = ExtImage(doc.getId(), doc.title)
        doc.update_data(doc.data)
    
    def _update_doc_displays(self, doc):
        """ Purge doc displays"""
        logger.debug('%-23s %s', 'Purge NyPhoto displays', doc.absolute_url(1))
        doc.managePurgeDisplays()
        
    def _update(self):
        """ Find files stored in ZODB and move them to disk"""
        updates = self._list_updates()
        for update in updates:
            self._update_doc_data(update)
            self._update_doc_displays(update)

def register(uid):
    return CustomContentUpdater(uid)
