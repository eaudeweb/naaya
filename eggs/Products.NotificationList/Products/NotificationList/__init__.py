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

import NotificationList
from constants import *

def invokeNotificationLists(site, obj, event):
    """ Walk down the object tree and invoke all NotificationList objects """
    folder = obj
    while True:
        try:
            folder = folder.aq_parent
        except:
            # nowhere to go; bail out
            return

        if folder == site:
            # we've reached the site level; bail out
            return

        if NOTIFICATION_LIST_DEFAULT_ID in folder.objectIds(spec=METATYPE_NOTIFICATION_LIST):
            # we found a subscriber list; notify the subscribers
            folder._getOb(NOTIFICATION_LIST_DEFAULT_ID).notify_subscribers(event)

def patch_NySite():
    """ patch notifyFolderMaintainer method of NySite """

    from Products.Naaya.NySite import NySite

    old_notifyFolderMaintainer = NySite.notifyFolderMaintainer
    def new_notifyFolderMaintainer(self, folder, obj, **kwargs):
        old_notifyFolderMaintainer(self, folder, obj, **kwargs)

        try:
            invokeNotificationLists(self, obj, {
                'user': self.REQUEST.AUTHENTICATED_USER,
                'object': obj,
                'type': 'file upload',
            })
        except:
            # we catch the error and log it ourselves; we don't want our patch
            # to bring down any innocent site because of some bug
            self.error_log.raising(sys.exc_info())
    NySite.notifyFolderMaintainer = new_notifyFolderMaintainer

def patch_NyForum():
    """ hook on to events from NyForum """

    try:
        from Products.NaayaForum import NyForumTopic, NyForumMessage
    except ImportError:
        # NaayaForum is not installed; nothing to patch here
        return

    def event_hook(ob):
        try:
            invokeNotificationLists(ob.getSite(), ob, {
                'user': ob.REQUEST.AUTHENTICATED_USER,
                'object': ob,
                'type': 'forum message',
            })
        except:
            # we catch the error and log it ourselves; we don't want our patch
            # to bring down any innocent site because of some bug
            ob.getSite().error_log.raising(sys.exc_info())

    NyForumTopic.NyForumTopic_creation_hooks.append(event_hook)
    NyForumMessage.NyForumMessage_creation_hooks.append(event_hook)

def initialize(context):
    # register NotificationList
    context.registerClass(
        NotificationList.NotificationList,
        constructors=(NotificationList.manage_addNotificationList_html,
                       NotificationList.manage_addNotificationList),
        icon='www/notification_list.gif',
    )

    patch_NyForum()
    patch_NySite()

    # TODO: manage_addNotificationList should not be manually injected (should work by itself)
    from Products.Naaya.NyFolder import NyFolder
    NyFolder.manage_addNotificationList = NotificationList.manage_addNotificationList
