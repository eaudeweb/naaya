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
    """ """
    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Delete files broken versions'
        self.description = 'Delete NyExFiles, NyFiles broken versions'
        self.update_meta_type = ['Naaya Extended File', 'Naaya File']

    def _verify_doc(self, doc):
        """ """
        return doc
    
    def _update_doc(self, doc):
        """ """
        if doc.meta_type == 'Naaya File':
            versions = doc.getVersions().keys()
            version_id = doc.getCurrentVersionId()
            if len(versions) == 1 and version_id in versions:
                logger.debug('Update NyFile: %s version: %s', doc.absolute_url(), version_id)
                try:
                    version = doc.getVersions()[version_id][2][0]
                except:
                    pass
                else:
                    version.manage_beforeDelete(version, doc)
                doc.setVersions({})
                doc.setCurrentVersionId(None)
        if doc.meta_type == 'Naaya Extended File':
            items = doc.getFileItems()
            for lang, item in items:
                versions = item.getVersions().keys()
                version_id = item.getCurrentVersionId()
                if len(versions) == 1 and version_id in versions:
                    logger.debug('Update NyExFile: %s, lang: %s, version: %s',
                                 doc.absolute_url(1), lang, version_id)
                    try:
                        version = item.getVersions()[version_id][2][0]
                    except:
                        pass
                    else:
                        version.manage_beforeDelete(version, item)
                    item.setVersions({})
                    item.setCurrentVersionId(None)

    def _update(self):
        """ """
        updates = self._list_updates()
        for update in updates:
            self._update_doc(update)

def register(uid):
    return CustomContentUpdater(uid)
