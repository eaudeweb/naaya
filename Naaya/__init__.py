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
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alex Morega, Eau de Web

import sys

from Products.Naaya.NySite import NySite
from Products.Naaya.NyFolder import NyFolder
import NotificationList
from constants import *

def notifyInterestGroups(site, obj, upload_user):
    # walk down the tree towards the NySite instance
    folder = obj
    while True:
        folder = folder.getParentNode()

        if NOTIFICATION_LIST_DEFAULT_ID in folder.objectIds(spec=METATYPE_NOTIFICATION_LIST):
            # we found a subscriber list; notify the subscribers
            folder._getOb(NOTIFICATION_LIST_DEFAULT_ID).notify_subscribers(obj, upload_user)

        if folder == site:
            # we've reached the site level; bail out
            return

# patch notifyFolderMaintainer method of NySite
old_notifyFolderMaintainer = NySite.notifyFolderMaintainer
def new_notifyFolderMaintainer(self, folder, obj, **kwargs):
    old_notifyFolderMaintainer(self, folder, obj, **kwargs)

    try:
       notifyInterestGroups(self, obj, self.REQUEST.AUTHENTICATED_USER)
    except:
        # we catch the error and log it ourselves; we don't want our patch
        # to bring down any innocent site because of some bug
        self.error_log.raising(sys.exc_info())
NySite.notifyFolderMaintainer = new_notifyFolderMaintainer

def initialize(context):
    # register NotificationList
    context.registerClass(
        NotificationList.NotificationList,
        constructors=(NotificationList.manage_addNotificationList_html,
                       NotificationList.manage_addNotificationList),
        icon='www/notification_list.gif',
    )

# TODO: manage_addNotificationList should not be manually injected (should work by itself)
NyFolder.manage_addNotificationList = NotificationList.manage_addNotificationList
