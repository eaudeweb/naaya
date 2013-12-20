from AccessControl import ClassSecurityInfo
from persistent.list import PersistentList

from interfaces import ISubscriptionContainer
from containers import SubscriptionContainer, AccountSubscription

from Products.naayaUpdater.updates import UpdateScript
from naaya.core.zope2util import path_in_site, relative_object_path
from utils import match_account_subscription

class RemoveNotifUseridSpaces(UpdateScript):
    title = 'Remove spaces from notification subscription user_ids'
    authors = ['Alex Morega']
    creation_date = 'Oct 08, 2010'

    def _update(self, portal):
        def fix_subscriptions(obj):
            try:
                sc = ISubscriptionContainer(obj)
            except TypeError:
                pass # object does not support subscription
            else:
                assert isinstance(sc, SubscriptionContainer)
                for sub_id, sub in sc.subscriptions.items():
                    if not isinstance(sub, AccountSubscription):
                        continue
                    user_id = sub.user_id
                    if user_id != user_id.strip():
                        self.log.info('fixing user_id %r', user_id)
                        sub.user_id = user_id.strip()
                        # AccountSubscription is not Persistent, so we must
                        # invalidate its container.
                        sc.subscriptions._p_changed = True

            for child_obj in obj.objectValues():
                fix_subscriptions(child_obj)

        fix_subscriptions(portal)
        return True

class AddPendingSubscriptionsContainer(UpdateScript):
    title = 'Add pending subscriptions container'
    authors = ['Alexandru Plugaru']
    creation_date = 'Dec 8, 2010'

    def _update(self, portal):
        notif_tool = portal.getNotificationTool()
        if not hasattr(notif_tool, 'pending_anonymous_subscriptions'):
            notif_tool.pending_anonymous_subscriptions = PersistentList()
        if 'enable_anonymous' not in notif_tool.config:
            notif_tool.config['enable_anonymous'] = False
        self.log.info("Added `pending_anonymous_subscriptions` to "
                      "notification tool")
        return True

class SubscribeAdministrativeNotifications(UpdateScript):
    """ Subscribe all users with local administrator role to the
    approval notifications (the notifications that previously went
    automatically to all local administrators) """
    title = 'Subscribe local administratos to administrative notifications'
    creation_date = 'Jul 05, 2013'
    authors = ['Valentin Dumitru']
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        notif_tool = portal.getNotificationTool()
        auth_tool = portal.getAuthenticationTool()
        admins = auth_tool.search_users('', role='Administrator',
                        rkey=0, skey='name', all_users=True, location='_all_')
        self.log.debug('Started update in %s' % portal.getId())
        for admin in admins:
            for role in admin.roles:
                if 'Administrator' in role[0]:
                    user_id = admin.user_id
                    own_site_location = path_in_site(role[1])
                    this_site_location = relative_object_path(role[1], portal)
                    if own_site_location != this_site_location:
                        self.log.debug('Location %s is probably in a subportal'
                        % own_site_location)
                        continue
                    obj = portal.restrictedTraverse(this_site_location)
                    if match_account_subscription(
                    ISubscriptionContainer(obj), user_id, 'administrative', 'en'):
                        self.log.debug('Subscription for user %s already present '
                        'in location %s' %(user_id, this_site_location or '/'))
                    else:
                        notif_tool.add_account_subscription(user_id,
                            this_site_location, 'administrative', 'en', [])
                        self.log.debug('Subscription added for user %s in location %s'
                            %(user_id, this_site_location or '/'))
        return True
