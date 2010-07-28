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
# David Batranu, Eau de Web


#Python imports

#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from OFS.Folder import Folder
from ZPublisher import BeforeTraverse

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript, PRIORITY

class UpdateExample(UpdateScript):
    """ Fix portals with broken logins because of ChangeNotification """
    title = 'Fix login on portals added with ChangeNotification present'
    creation_date = 'Dec 2, 2009'
    authors = ['David Batranu']
    description = 'Fix portals that have broken logins because of ChangeNotification'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        traversers = portal.__before_traverse__
        for priority, name in traversers.keys():
            if portal.getId() in name:
                self.log.debug('Fix not needed')
                return
        name_caller = BeforeTraverse.NameCaller(portal.getId())
        app_handle = '%s/%s' % (portal.meta_type, portal.getId())
        BeforeTraverse.registerBeforeTraverse(portal, name_caller, app_handle)
        self.log.debug('Fix applied!')
        return True
