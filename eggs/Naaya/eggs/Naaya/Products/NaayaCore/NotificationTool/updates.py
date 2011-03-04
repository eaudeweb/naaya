from persistent.list import PersistentList
from Products.naayaUpdater.updates import UpdateScript

from interfaces import ISubscriptionContainer
from containers import SubscriptionContainer, AccountSubscription

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
