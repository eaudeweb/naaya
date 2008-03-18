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
from Products.NaayaSurvey.SurveyTool import SurveyTool

class CustomContentUpdater(NaayaContentUpdater):
    """Update Naaya Survey Tool"""

    meta_type = "Naaya Survey Tool Updater"

    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Update Naaya Survey Tool'
        self.description = '''Update Naaya Survey Tool.'''
        self.update_meta_type = SurveyTool.meta_type

    def _update(self):
        for update in self._list_updates():
            update.manage_configureSite()
            logger.debug('Updated %s' % (update.absolute_url(1),))

def register(uid):
    return CustomContentUpdater(uid)
