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
    """Update attached pdf files with ksh extension"""
    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Update Naaya Files and Naaya Extended Files'
        self.description = 'Fix PDF objects that have .ksh extension'
        self.update_meta_type = ['Naaya File', 'Naaya Extended File']

    def _verify_doc(self, doc):
        # Verify ZODB storage
        if not getattr(doc, 'get_data', None):
            return None
        data = doc.get_data(as_string=False)
        filename = getattr(data, 'filename', None)
        if not filename:
            return None
        if not filename[2].endswith('.ksh'):
            return None
        if not 'pdf' in doc.getContentType():
            return None
        return doc

    def _update(self):
        updates = self._list_updates()
        for update in updates:
            logger.debug('%-15s %s', 'Update PDF file', update.absolute_url(1))
            update.update_data(data=update.get_data(), content_type=update.getContentType())

def register(uid):
    return CustomContentUpdater(uid)
