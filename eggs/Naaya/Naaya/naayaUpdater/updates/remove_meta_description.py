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
# Cristian Ciupitu, Eau de Web

# Python imports
import re

# Zope imports
from zLOG import LOG, DEBUG

# Naaya imports
from Products.naayaUpdater.updates import nyUpdateLogger as logger
from Products.naayaUpdater.NaayaContentUpdater import NaayaContentUpdater

class CustomContentUpdater(NaayaContentUpdater):
    """Remove meta description from site_header"""

    meta_description_regex = re.compile(r'''^\s*<\s*meta[^>]*\s+name=(["'])description\1[^>]*/>\s*$''', re.MULTILINE)

    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Remove meta description from site_header'
        self.description = '''Remove the "<meta name="description" .../> tag from the site_header
                              of the current skin.
                              The only purpose of the script is to remove the name clash between
                              the meta with name "description" and other HTML elements that have
                              the same name or id. TinyMCE is affected by this issue (when using
                              Internet Explorer).'''
        self.update_meta_type = "Naaya Template"

    def _verify_doc(self, doc):
        """See super"""
        LOG('naayaUpdater.updates.remove_meta_description.CustomContentUpdater', DEBUG, '_verify_doc(%s)' % (doc.absolute_url(1)))
        if self.meta_description_regex.search(doc._text):
            return doc
        return None

    def _list_updates(self):
        """ Return all portals that need update """
        utool = self.aq_inner.aq_parent
        for portal in utool.getPortals():
            LOG('naayaUpdater.updates.remove_meta_description.CustomContentUpdater', DEBUG, 'checking portal %s' % (portal.absolute_url(1)))
            ltool = portal.getLayoutTool()
            ob = getattr(ltool.getCurrentSkin(), 'site_header', None)
            if ob is None:
                continue
            if self._verify_doc(ob):
                yield ob

    def _update(self):
        for update in self._list_updates():
            update._text = self.meta_description_regex.sub('', update._text)
            logger.info('Updated %s' % (update.absolute_url(1),))

def register(uid):
    return CustomContentUpdater(uid)
