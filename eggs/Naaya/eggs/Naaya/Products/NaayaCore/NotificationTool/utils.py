from datetime import timedelta

from interfaces import ISubscriptionContainer
from DateTime import DateTime

from Products.NaayaCore.EmailTool.EmailTool import build_email
from containers import AccountSubscription, AnonymousSubscription

def DateTime_from_datetime(dt):
    DT = DateTime(dt.isoformat())
    zone = DT.localZone(dt.timetuple())
    local_DT = DT.toZone(zone)
    return local_DT

def set_day_of_month(the_date, day):
    while True:
        try:
            return the_date.replace(day=day)
        except ValueError:
            day -= 1
        if not 26 < day < 31:
            raise ValueError(day)

def minus_one_month(the_date):
    return set_day_of_month(the_date.replace(day=1) - timedelta(days=1),
                            the_date.day)

def fetch_subscriptions(obj, inherit):
    """
    Get subscriptions on `obj`. If `inherit` is True then recurse
    into parents, up to site level.
    """
    try:
        sc = ISubscriptionContainer(obj)
    except TypeError:
        # we probably went below site level; bail out.
        return

    for subscription in sc:
        yield subscription

    if inherit:
        for subscription in fetch_subscriptions(obj.aq_parent, inherit=True):
            yield subscription

def walk_subscriptions(obj):
    """
    Get subscriptions on `obj` and all of its children. Returns a
    generator that yields tuples in the form `(obj, n, subscription)`.
    """
    try:
        sc = ISubscriptionContainer(obj)
    except TypeError:
        # we reached an object that does not support subscription
        return

    for n, subscription in sc.list_with_keys():
        yield (obj, n, subscription)

    for child_obj in obj.objectValues():
        for item in walk_subscriptions(child_obj):
            yield item

def list_modified_objects(site, when_start, when_end):
    DT_when_start = DateTime_from_datetime(when_start)
    DT_when_end = DateTime_from_datetime(when_end)
    catalog = site.getCatalogTool()
    brains = catalog(bobobase_modification_time={
        'query': (DT_when_start, DT_when_end), 'range': 'min:max'})
    for brain in brains:
        try:
            yield brain.getObject()
        except:
            notif_logger.error('Found broken brain: %r', brain.getPath())

def _send_notification(email_tool, addr_from, addr_to, subject, body):
    mail = build_email(addr_from, addr_to, subject, body)
    #TODO: send using the EmailSender
    email_tool.sendEmail(body, addr_to, addr_from, subject)

def _mock_send_notification(email_tool, addr_from, addr_to, subject, body):
    mock_saved.append( (addr_from, addr_to, subject, body) )

def divert_notifications(testing, save_to=[]):
    """
    Place the NotificationTool module in testing mode: all notifications will
    be appended to `save_to` instead of being sent via e-mail.
    """
    global send_notification
    global mock_saved

    if testing:
        send_notification = _mock_send_notification
        mock_saved = save_to

    else:
        send_notification = _send_notification

def match_account_subscription(subs, user_id, notif_type, lang):
    for n, subscription in subs.list_with_keys():
        if not isinstance(subscription, AccountSubscription):
            continue
        if (subscription.user_id == user_id and
            subscription.notif_type == notif_type and
            subscription.lang == lang):
            return n

def get_subscribers_data(self, ob, notif_type='instant', **kw):
    """ Return a dict that contains the data of the messages that can be passed
    to the e-mail template """

    data = {}
    for subscription in fetch_subscriptions(ob, inherit=True):
        if not subscription.check_permission(ob):
            continue
        if subscription.notif_type != notif_type:
            continue
        email = subscription.get_email(ob)
        if email is None:
            continue

        data[email] = {
            'ob': ob,
            'here': self,
            '_lang': subscription.lang,
            'subscription': subscription,
            'anonymous': isinstance(subscription, AnonymousSubscription)
        }
        data[email].update(kw)

    return data
