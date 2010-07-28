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
# Agency (EEA). Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Eau de Web


#Python imports

#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from OFS.Folder import Folder

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from Products.NaayaCore.GoogleDataTool.AnalyticsTool import manage_addAnalyticsTool

class AddStatisticsTool(UpdateScript):
    """ Add portal statistics tool """
    title = 'Update portal statistics tool'
    creation_date = 'Dec 10, 2009'
    authors = ['Cornel Nitu']
    description = 'Creates the portal statistics tool'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        try:
            tool = portal.getAnalyticsTool()
            tool.clear_cache()
            self.log.debug('Portal statistics already exists in this portal')
        except:
            manage_addAnalyticsTool(portal)
            self.log.debug('Added the portal statistics to the portal')
        return True


