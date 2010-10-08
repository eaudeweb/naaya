from Products.naayaUpdater.updates import UpdateScript
from Products.NaayaCore.NotificationTool.NotificationTool import (
    ISubscriptionContainer, SubscriptionContainer, AccountSubscription)

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
