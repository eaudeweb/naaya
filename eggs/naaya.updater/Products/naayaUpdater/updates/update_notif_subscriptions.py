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
# Alex Morega, Eau de Web


#Python imports

#Zope imports
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from Products.NaayaCore.NotificationTool.interfaces import \
    ISubscriptionContainer
from Products.NaayaCore.NotificationTool.NotificationTool import \
    AccountSubscription

class UpdateNotifSubscriptions(UpdateScript):
    """ Migrates from central notifications index to annotations """
    title = 'Migrate storage of notification subscriptions'
    creation_date = 'Feb 25, 2010'
    authors = ['Alex Morega']
    description = "Migrates from central notifications index to annotations."
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        notif_tool = portal.getNotificationTool()
        repr(notif_tool) # force loading from database
        if 'subscriptions' not in notif_tool.__dict__:
            self.log.debug('Portal already up-to-date')
            return True

        for old_subscription in notif_tool.subscriptions:
            convert_subscription(old_subscription, portal, self.log)

        self.log.info('Removing old `subscriptions` list')
        del notif_tool.subscriptions

        return True

def convert_subscription(old_subscription, portal, log):
    location = old_subscription.location
    user_id = old_subscription.user_id
    notif_type = old_subscription.notif_type
    lang = old_subscription.lang

    log.info('Updating (location=%r, user_id=%r, notif_type=%r, lang=%r)',
             location, user_id, notif_type, lang)

    try:
        obj = portal.unrestrictedTraverse(location)
        sc = ISubscriptionContainer(obj)
        new_subscription = AccountSubscription(user_id, notif_type, lang)
        sc.add(new_subscription)
    except:
        log.exception('Failed to update subscription')
