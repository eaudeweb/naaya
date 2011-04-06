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
from Products.naayaUpdater.updates import nyUpdateLogger as logger
from Products.naayaUpdater.utils import get_portals

from Products.naayaUpdater.NaayaContentUpdater import NaayaContentUpdater
from Products.NaayaSurvey.SurveyTool import SurveyTool, manage_addSurveyTool

class CustomContentUpdater(NaayaContentUpdater):
    """Add Survey Tool to Naaya Site if necessarily"""

    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Add Survey Tool to Naaya Site'
        self.description = 'Add Survey Tool if necessarily'

    def _verify_doc(self, doc):
        """See super"""
        if not doc.__dict__.get(SurveyTool.portal_id, None):
            return doc

    def _list_updates(self):
        """ Return all portals that need update """
        utool = self.aq_inner.aq_parent
        portals = get_portals(self)
        for portal in portals:
            if not self._verify_doc(portal):
                continue
            yield portal

    def _update(self):
        updates = self._list_updates()
        for update in updates:
            logger.debug('Added survey tool to %s' % (update.absolute_url(1),))
            manage_addSurveyTool(update)

def register(uid):
    return CustomContentUpdater(uid)
