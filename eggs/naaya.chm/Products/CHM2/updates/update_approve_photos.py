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
from Products.NaayaCore.EditorTool.EditorTool import manage_addEditorTool

class CustomContentUpdater(NaayaContentUpdater):
    """ """

    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Update Naaya Photo Folders / Photos'
        self.description = 'Approve/Submit Naaya Photo Folders/Naaya Photos'
        self.update_meta_type = ['Naaya Photo Gallery', 'Naaya Photo Folder']

    def _verify_doc(self, doc):
        """ See super"""
        if not (getattr(doc, 'submitted', 0) and getattr(doc, 'approved', 0)):
            return doc
        for photo in doc.objectValues('Naaya Photo'):
            if not (getattr(photo, 'submitted', 0) and getattr(photo, 'approved', 0)):
                return doc
        return None

    def _update_photo(self, photo):
        photo.submitted = 1
        photo.approved = 1

    def _update(self):
        updates = self._list_updates()
        for update in updates:
            update.submitted = 1
            update.approved = 1
            logger.debug('%-70s [UPDATED]', update.absolute_url(1))
            for photo in update.objectValues('Naaya Photo'):
                self._update_photo(photo)
                logger.debug('%-70s [UPDATED]', photo.absolute_url(1))

def register(uid):
    return CustomContentUpdater(uid)
