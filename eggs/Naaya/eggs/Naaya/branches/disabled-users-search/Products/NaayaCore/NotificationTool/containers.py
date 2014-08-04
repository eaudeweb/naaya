import logging
from datetime import datetime
from time import time
import random
try:
    from hashlib.sha1 import new as sha
except ImportError:
    from sha import sha

from AccessControl.Permissions import view
from zope import interface, annotation, component
from persistent import Persistent
from persistent.dict import PersistentDict


from naaya.core.utils import force_to_unicode

from interfaces import ISubscriptionContainer
from interfaces import ISubscription
from interfaces import ISubscriptionTarget

notif_logger = logging.getLogger('naaya.core.notif')

class SubscriptionContainer(Persistent):
    """ Holds anonymous and authenticated notifications """
    interface.implements(ISubscriptionContainer)
    component.adapts(ISubscriptionTarget)

    def __init__(self):
        self.subscriptions = PersistentDict()
        self._next_id = 1

    def add(self, subscription):
        self.subscriptions[self._next_id] = subscription
        self._next_id += 1

    def remove(self, n):
        del self.subscriptions[n]

    def list_with_keys(self):
        for n, subscription in self.subscriptions.iteritems():
            yield n, subscription

    def __iter__(self):
        for subscription in self.subscriptions.itervalues():
            yield subscription

class AccountSubscription(object):
    interface.implements(ISubscription)

    def __init__(self, user_id, notif_type, lang, content_types=[]):
        self.user_id = user_id
        self.lang = lang
        self.notif_type = notif_type
        self.content_types = content_types

    def check_permission(self, obj):
        acl_users = obj.getSite().getAuthenticationTool()
        user = acl_users.get_user_with_userid(self.user_id)

        if user is None:
            return False
        elif user.has_permission(view, obj):
            return True
        else:
            return False

    def _name_and_email(self, obj):
        # First look for the user in Nayaa's acl_users
        site = obj.getSite()
        auth_tool = site.getAuthenticationTool()
        user_obj = auth_tool.getUser(self.user_id)
        if user_obj is not None:
            try:
                full_name = u'%s %s' % (
                    auth_tool.getUserFirstName(user_obj).decode('utf-8'),
                    auth_tool.getUserLastName(user_obj).decode('utf-8'))
            except UnicodeEncodeError:
                full_name = u'%s %s' % (
                    auth_tool.getUserFirstName(user_obj),
                    auth_tool.getUserLastName(user_obj))
            email = auth_tool.getUserEmail(user_obj)
            return (full_name, email)

        # The user is not in Naaya's acl_users, so let's look deeper
        parent_acl_users = site.restrictedTraverse('/').acl_users
        if parent_acl_users.meta_type == 'LDAPUserFolder':
            # TODO: what if parent_acl_users is not an LDAPUserFolder?
            # Note: EIONET LDAP data is encoded with latin-1
            ldap_user_data = parent_acl_users.getUserById(self.user_id)
            if ldap_user_data:
                full_name = ldap_user_data.cn
                email = ldap_user_data.mail
                return (force_to_unicode(full_name), email)

        # Didn't find the user anywhere; return a placeholder
        notif_logger.warn('Could not find email for user %r (context: %r)',
                          self.user_id, obj)
        return (u'[not found]', None)

    def get_email(self, obj):
        return self._name_and_email(obj)[1]

    def to_string(self, obj):
        name, email = self._name_and_email(obj)
        if name:
            return u'%s (%s)' % (name, email)
        else:
            return u'%s' % email

class AnonymousSubscription(object):
    """
    Non authentificated user subscriptions
    """
    interface.implements(ISubscription)

    first_name = None
    last_name = None
    organisation = None
    country = None

    def __init__(self, **kw):
        """
        @todo: Make a heartbeat to clean-up temporary subscribtions
        """
        self.email = kw.pop('email')
        self.first_name = kw.get('first_name')
        self.last_name = kw.get('last_name')
        self.organisation = kw.get('organisation')
        self.country = kw.get('country')
        self.notif_type = kw.pop('notif_type')
        self.lang = kw.pop('lang')
        self.content_types = kw.pop('content_types')
        self.location = kw.pop('location')
        self.key = sha("%s%s" % (time(),
                                     random.randrange(1, 10000))).hexdigest()
        self.__dict__.update(kw)
        self.datetime = datetime.now()

    def check_permission(self, obj):
        user = obj.unrestrictedTraverse('/acl_users')._nobody
        return bool(user.has_permission(view, obj))

    def get_email(self, obj):
        return self.email

    def to_string(self, obj):
        if getattr(self, 'organisation', ''):
            return u'%s (%s)' % (self.organisation, self.email)
        else:
            return u'%s' % self.email

#The key is the old location of the class
subscription_container_factory = annotation.factory(SubscriptionContainer,
"Products.NaayaCore.NotificationTool.NotificationTool.SubscriptionContainer")
