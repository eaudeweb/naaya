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
import re

#PATTERN = 'ewindows.eu.org'
#REPLACEMENT = 'ew.eea.europa.eu'

PATTERN = 'experts.'

class CustomContentUpdater(NaayaContentUpdater):
    """ search """
    bulk_update = False
    
    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Search Naaya objects where attributes match given PATTERN: %s' % PATTERN
        self.description = ""
        self.update_meta_type = ['Naaya Report Chapter', 'Naaya Report Questionnaire', 'Naaya Report Comment', 'Naaya Study', 'Naaya SMAP Project', \
                                 'Naaya Contact', 'Naaya Report', 'Naaya News', 'Naaya Story', 'Naaya Report Answer', 'Naaya Report Question', 'Naaya Extended File', \
                                 'Naaya Document', 'Naaya Pointer', 'Naaya URL', 'Naaya SMAP Expert', 'Naaya Report Reference', 'Naaya Media File', 'Naaya Event', \
                                 'Naaya Report Section', 'Naaya File', 'Naaya Folder', 'Naaya GeoPoint', 'Naaya Blog Entry']

    def _get_languages(self, doc):
        """ get the list of available languages """
        return list(doc.getSite().gl_get_languages())

    def _verify_doc(self, doc):
        # Verify ZODB storage
        for lang in self._get_languages(doc):
            if doc.getLocalProperty('title', lang).find(PATTERN) != -1:
                return doc
            if doc.getLocalProperty('description', lang).find(PATTERN) != -1:
                return doc
            if doc.getLocalProperty('details', lang).find(PATTERN) != -1:
                return doc
            if doc.getLocalProperty('body', lang).find(PATTERN) != -1:
                return doc
            if doc.getLocalProperty('locator', lang).find(PATTERN) != -1:
                return doc
        if getattr(doc, 'pointer', '').find(PATTERN) != -1:
            return doc
        if getattr(doc, 'resourceurl', '').find(PATTERN) != -1:
            return doc
        return None

    def _update(self):
        pass

def register(uid):
    return CustomContentUpdater(uid)
