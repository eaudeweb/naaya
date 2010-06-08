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
from Products.ExtFile.ExtFile import ExtFile

class CustomContentUpdater(NaayaContentUpdater):
    """ """
    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Delete downloadfilename property from files'
        self.description = 'Delete downloadfilename property from files'
        self.update_meta_type = ['Naaya Extended File', 'Naaya File']

    def _verify_doc(self, doc):
        """ """
        
        if 'downloadfilename' in doc.__dict__.keys():
            return doc

    def _update(self):
        """ """
        updates = self._list_updates()
        for update in updates:
            logger.debug('Updated %s', update.absolute_url(1))
            delattr(update, 'downloadfilename')

def register(uid):
    return CustomContentUpdater(uid)
