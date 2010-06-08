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
from Products.ExtFile.ExtFile import ExtFile

class CustomContentUpdater(NaayaContentUpdater):
    """ Make NyExFile folderish """
    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Make Naaya Extended Files folderish'
        self.description = 'Update Naaya Extended Files to work on Zope 2.8+'
        self.update_meta_type = 'Naaya Extended File'

    def _verify_doc(self, doc):
        """ """
        if not getattr(doc, 'getFileItems', None):
            logger.debug("Invalid NyExFile: %s" % doc)
            return None

        if doc._get_old_files():
            return doc

        if doc.hasVersion() and doc.version._get_old_files():
            return doc

        logger.debug('%-20s %s ', 'Skip NyExFile', doc.absolute_url(1))
        return None

    def _update_doc(self, doc):
        """ """
        old_files = doc._get_old_files()
        logger.debug('Update NyExFile %s', doc.absolute_url(1))
        for lang, fileitem in old_files.items():
            if lang in doc.objectIds():
                doc.manage_delObjects([lang])
            doc._setObject(lang, fileitem)
        setattr(doc, '_exfile_item__files', {})
        doc._p_changed = 1

    def _update_doc_version(self, doc):
        """ """
        if 'version' in doc.__dict__.keys() and doc.version:
            logger.debug('Update NyExFile version %s', doc.absolute_url(1))
            self._update_doc(doc.version)
            doc._setObject('new_version', doc.version)
            delattr(doc, 'version')
            doc.manage_renameObjects(['new_version'], ['version'])
            

    def _update(self):
        """ """
        updates = self._list_updates()
        for update in updates:
            self._update_doc(update)
            self._update_doc_version(update)

def register(uid):
    return CustomContentUpdater(uid)
