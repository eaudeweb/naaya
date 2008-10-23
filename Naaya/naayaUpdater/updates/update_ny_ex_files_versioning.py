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
from OFS.Folder import Folder
from Products.naayaUpdater.updates import nyUpdateLogger as logger
from Products.naayaUpdater.NaayaContentUpdater import NaayaContentUpdater

class CustomContentUpdater(NaayaContentUpdater):
    """ Make NyExFile folderish """
    update_ctypes = False

    _properties= NaayaContentUpdater._properties + (
        {'id':'update_ctypes', 'type': 'boolean','mode':'w',
         'label': 'Reinstall NyFile, NyExFile content-types ?'},
    )

    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Update Naaya Files and Naaya Extended Files Versioning'
        self.description = 'Move versions from dictionary to tree structure. (See Properties tab for aditional parameters)'
        self.update_meta_type = ['Naaya Extended File', 'Naaya File']

    def _verify_doc(self, doc):
        """ """
        if doc.meta_type == 'Naaya File':
            if getattr(doc, '_NyVersioning__versions', None):
                return doc
            if not getattr(doc, 'versions', None):
                return doc
        elif doc.meta_type == 'Naaya Extended File':
            for lang, fileitem in doc.getFileItems():
                if getattr(fileitem, '_NyVersioning__versions', None):
                    return doc
                if not getattr(fileitem, 'versions', None):
                    return doc
        return None

    def _update_file_doc(self, doc):
        if not getattr(doc, 'versions', None):
            doc.versions = Folder('versions')
        versions = doc.versions

        old_versions = getattr(doc, '_NyVersioning__versions', {})
        for key, value in old_versions.items():
            # Skip current version
            if key == getattr(doc, '_NyVersioning__current_version_uid', ''):
                continue

            data = value[2][0]
            if isinstance(data, str):
                # Ohh boy !
                logger.debug('WARNING: OLD data string found in version: %s, doc: %s',
                             key, doc.absolute_url(1))
                from Products.ExtFile.ExtFile import manage_addExtFile
                data_id = doc.get_data(as_string=False).getId()
                data_ctype = value[2][1]
                while data_id in versions.objectIds():
                    data_id = '.' + data_id
                data_id = manage_addExtFile(versions, data_id)
                version = versions._getOb(data_id)
                version.manage_upload(data, data_ctype)
            else:
                ext_id = data.getId()
                if ext_id not in versions.objectIds():
                    versions._setObject(ext_id, data)
                version = versions._getOb(ext_id)
            setattr(version, 'modification_time', value[0])
            setattr(version, 'username', value[1])

        if hasattr(doc, '_NyVersioning__versions'):
            delattr(doc, '_NyVersioning__versions')
        if hasattr(doc, '_NyVersioning__current_version_uid'):
            delattr(doc, '_NyVersioning__current_version_uid')

    def _update_doc(self, doc):
        if doc.meta_type == 'Naaya File':
            return self._update_file_doc(doc)
        for lang, fileitem in doc.getFileItems():
            self._update_file_doc(fileitem)

    def _update(self):
        """ """
        updates = self._list_updates()
        for update in updates:
            logger.debug('Update %s versioning', update.absolute_url(1))
            self._update_doc(update)
        # Reinstall naaya file and naaya extended file content types
        if self.update_ctypes:
            logger.debug('Reinstall NyFile, NyExFile content-types')
            self.reinstallMetaTypes(all=True, ct_action='ict',
                contenttypes='Naaya File,Naaya Extended File')

def register(uid):
    return CustomContentUpdater(uid)
