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
    """ Move NyExFiles from ZODB to local disk"""
    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Update Naaya Extended Files storage type'
        self.description = 'Move files from ZODB to disk.'
        self.update_meta_type = 'Naaya Extended File'

    def _verify_lang_doc(self, doc):
        """ Verify single file item """
        # Verify ZODB storage
        if doc.data:
            return doc
        # Verify working version ZODB storage
        if hasattr(doc, 'version'):
            if getattr(doc.version, 'data', ''):
                return doc
        # Verify old versions ZODB storage
        versions = doc.getVersions()
        for version_id in versions.keys():
            version_data = doc.getVersion(version_id)[0]
            if not isinstance(version_data, ExtFile):
                return doc
        return None

    def _verify_doc(self, doc):
        """ Check for ZODB storage """
        if not getattr(doc, 'getFileItems', None):
            logger.debug("Invalid NyExFile: %s" % doc)
            return None

        fileitems = doc.getFileItems()
        for lang, ob in fileitems:
            if self._verify_lang_doc(ob):
                return doc

        logger.debug('%-20s %s ', 'Skip NyExFile', doc.absolute_url(1))
        return None

    def _update_lang_doc(self, doc):
        """ Move doc data from ZODB to disk """
        if not getattr(doc, 'getFileItems', None):
            logger.debug("Invalid NyExFile: %s" % doc)
            return None

        fileitems = doc.getFileItems()
        logger.debug('%-20s %s', 'Update NyExFile', doc.absolute_url(1))
        for lang, ob in fileitems:
            ob.update_data(ob.data)
            self._update_lang_doc_versions(ob)
            self._update_lang_doc_working_version(ob)

    def _update_lang_doc_versions(self, doc):
        """ Move doc versions data from ZODB to disk """
        versions = doc.getVersions()
        new_versions = {}
        for vid, value in versions.items():
            vdata, vtype = doc.getVersion(vid)
            doc_id = getattr(doc, '__name__', 'data.fs')
            doc_title = getattr(doc, 'title', '')
            doc.__ext_file = ExtFile(doc_id, doc_title)
            doc.__ext_file.manage_upload(vdata)
            vdata = doc.__ext_file
            new_versions[vid] = (value[0], value[1], (vdata, vtype))
        if hasattr(doc, '__ext_file'):
            delattr(doc, '__ext_file')
        doc.setVersions(new_versions)

    def _update_lang_doc_working_version(self, doc):
        """ Move doc version data from ZODB to disk """
        if not getattr(doc, 'version', None):
            return
        if not getattr(doc.version, 'data', ''):
            return
        doc.version.update_data(doc.version.data)

    def _update(self):
        """ Find files stored in ZODB and move them to disk """
        updates = self._list_updates()
        for update in updates:
            self._update_lang_doc(update)

def register(uid):
    return CustomContentUpdater(uid)
