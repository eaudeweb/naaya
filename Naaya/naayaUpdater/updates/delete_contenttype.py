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
from Products.naayaUpdater.NaayaContentUpdater import NaayaContentUpdater

class CustomContentUpdater(NaayaContentUpdater):
    """ """
    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Delete content_type property from files'
        self.description = 'Delete content_type property from files as there is a method with the same name'
        self.update_meta_type = ['Naaya Extended File', 'Naaya File']

    def _verify_doc(self, doc):
        """ """
        if doc.meta_type == 'Naaya Extended File':
            for lang, fileitem in doc.getFileItems():
                if 'content_type' in fileitem.__dict__.keys():
                    return doc
        else:
            if 'content_type' in doc.__dict__.keys():
                return doc
        return None

    def _update_file_doc(self, doc):
        try:
            delattr(doc, 'content_type')
        except AttributeError:
            pass

    def _update_doc(self, doc):
        if doc.meta_type == 'Naaya File':
            return self._update_file_doc(doc)
        for lang, fileitem in doc.getFileItems():
            self._update_file_doc(fileitem)

    def _update(self):
        """ """
        updates = self._list_updates()
        for update in updates:
            logger.debug('Updated %s', update.absolute_url(1))
            self._update_doc(update)

def register(uid):
    return CustomContentUpdater(uid)
