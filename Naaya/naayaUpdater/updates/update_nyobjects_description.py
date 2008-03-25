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

PATTERN = 'smap-root.ew.eea.europa.eu'
REPLACEMENT = 'root.ew.eea.europa.eu'

class CustomContentUpdater(NaayaContentUpdater):
    """  replace broken links in the description """
    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Update Naaya objects description'
        self.description = 'Update description attribute.'
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

        logger.debug('%-15s %s', 'Skip object', doc.absolute_url(1))
        return None

    def _update(self):
        updates = self._list_updates()
        for update in updates:
            for lang in self._get_languages(update):
                #title
                title = update.getLocalProperty('title', lang)
                update._setLocalPropValue('title', lang, re.sub(PATTERN, REPLACEMENT, title))
                logger.debug('%-15s %s', 'Update title property of %s' % update.meta_type, update.absolute_url(1))
                #description
                descr = update.getLocalProperty('description', lang)
                update._setLocalPropValue('description', lang, re.sub(PATTERN, REPLACEMENT, descr))
                logger.debug('%-15s %s', 'Update description property of %s' % update.meta_type, update.absolute_url(1))
                #details
                if hasattr(update, 'details'):
                    details = update.getLocalProperty('details', lang)
                    update._setLocalPropValue('details', lang, re.sub(PATTERN, REPLACEMENT, details))
                    logger.debug('%-15s %s', 'Update details property of %s' % update.meta_type, update.absolute_url(1))
                #body
                if hasattr(update, 'body'):
                    body = update.getLocalProperty('body', lang)
                    update._setLocalPropValue('body', lang, re.sub(PATTERN, REPLACEMENT, body))
                    logger.debug('%-15s %s', 'Update body property of %s' % update.meta_type, update.absolute_url(1))
                #locator
                if hasattr(update, 'locator'):
                    locator = update.getLocalProperty('locator', lang)
                    update._setLocalPropValue('locator', lang, re.sub(PATTERN, REPLACEMENT, locator))
                    logger.debug('%-15s %s', 'Update locator property of %s' % update.meta_type, update.absolute_url(1))
            #pointer
            if hasattr(update, 'pointer'):
                update.pointer = re.sub(PATTERN, REPLACEMENT, update.pointer)
                logger.debug('%-15s %s', 'Update pointer property of %s' % update.meta_type, update.absolute_url(1))
                update._p_changed = 1
            #resourceurl
            if hasattr(update, 'resourceurl'):
                update.resourceurl = re.sub(PATTERN, REPLACEMENT, update.resourceurl)
                logger.debug('%-15s %s', 'Update resourceurl property of %s' % update.meta_type, update.absolute_url(1))
                update._p_changed = 1

def register(uid):
    return CustomContentUpdater(uid)
