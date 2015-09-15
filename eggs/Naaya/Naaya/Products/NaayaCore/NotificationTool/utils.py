from DateTime import DateTime
from Products.NaayaCore.EmailTool.EmailSender import build_email
from containers import AccountSubscription, AnonymousSubscription
from datetime import timedelta
from interfaces import ISubscriptionContainer
import constants
import logging
import warnings


notif_logger = logging.getLogger('naaya.core.notif')


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
        for subscription in sc:
            yield subscription
    except TypeError:
        pass

    if inherit:
        if hasattr(obj, 'aq_parent'):
            for subscription in fetch_subscriptions(obj.aq_parent,
                                                    inherit=True):
                yield subscription


def walk_subscriptions(obj, cutoff_level=None):
    """
    Get subscriptions on `obj` and all of its children. Returns a
    generator that yields tuples in the form `(obj, n, subscription)`.

    If `cutoff_level` is set to an integer x, than at most x levels
    will be walked, first included.

    """
    if cutoff_level == 0:
        return
    elif cutoff_level is not None:
        cutoff_level -= 1
    try:
        sc = ISubscriptionContainer(obj)
    except TypeError:
        # we reached an object that does not support subscription
        return

    for n, subscription in sc.list_with_keys():
        yield (obj, n, subscription)

    for child_obj in obj.objectValues():
        for item in walk_subscriptions(child_obj, cutoff_level):
            yield item


def list_modified_objects(site, when_start, when_end):
    warnings.warn("Use `get_modified_objects` instead", DeprecationWarning)
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


def get_modified_objects(site, when_start, when_end, log_type=None):
    """ Search through action log entries given ``when_start``, ``when_end``
    and ``log_type``. Yield objects based on paths from action log entries.
    Also make sure each object is returned one time.

    """

    action_logger = site.getActionLogger()
    if log_type is not None:
        log_types = [log_type]
    else:
        log_types = constants.LOG_TYPES.values()

    DT_when_start = DateTime_from_datetime(when_start)
    DT_when_end = DateTime_from_datetime(when_end)

    visited_paths = []
    for entry_id, log_entry in action_logger.items():
        if (log_entry.type in log_types):
            if log_entry.path in visited_paths:  # Return objects just once
                continue
            visited_paths.append(log_entry.path)

            if (DT_when_start.lessThanEqualTo(log_entry.created_datetime) and
                    DT_when_end.greaterThanEqualTo(
                    log_entry.created_datetime)):
                try:
                    yield (log_entry.type,
                           site.unrestrictedTraverse(log_entry.path))
                except KeyError:
                    notif_logger.error('Found nonexistent path: %r',
                                       log_entry.path)


def _send_notification(email_tool, addr_from, addr_to, subject, body):
    build_email(addr_from, addr_to, subject, body)
    # TODO: send using the EmailSender
    email_tool.sendEmail(body, addr_to, addr_from, subject)


def _mock_send_notification(email_tool, addr_from, addr_to, subject, body):
    mock_saved.append((addr_from, addr_to, subject, body))


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


def match_account_subscription(subs, user_id, notif_type, lang,
                               content_types=None):
    for n, subscription in subs.list_with_keys():
        if not isinstance(subscription, AccountSubscription):
            continue
        if (subscription.user_id == user_id and
            subscription.notif_type == notif_type and
            subscription.lang == lang and
            (content_types is None or
             getattr(subscription, 'content_types', None) == content_types)):
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
        # TODO exclude disabled users
        if email is None:
            continue
        content_types = getattr(subscription, 'content_types', [])
        if content_types and ob.meta_type not in content_types:
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
