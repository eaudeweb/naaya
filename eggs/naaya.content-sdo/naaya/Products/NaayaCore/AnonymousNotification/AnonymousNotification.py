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
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alexandru Plugaru, Eau de Web

try:
    from hashlib import sha1 as sha
except ImportError:
    import sha # 2.4

import re
import random
import time
#from datetime import datetime

from zope import interface
from zope import component
from zope import annotation

from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view

from persistent import Persistent
from persistent.dict import PersistentDict
from persistent.list import PersistentList

from Products.NaayaCore.NotificationTool.interfaces import ISubscription, ISubscriptionContainer, ISubscriptionTarget

from Products.NaayaCore.EmailTool.EmailPageTemplate import EmailPageTemplateFile
from Products.NaayaCore.EmailTool.EmailTool import build_email

from Products.NaayaCore.managers.utils import is_valid_email

class AnonymousSubscription(object):
    """ 
    Non authentificated user subscription to events
    """
    interface.implements(ISubscription)
    
    def __init__(self, email, organisation, sector, country, notif_type, lang):
        """
        @todo: Make a heartbeat to clean-up temporary subscribtions
        """
        self.email = email
        self.organisation = organisation
        self.sector = sector
        self.country = country
        self.notif_type = notif_type
        self.lang = lang
        self.key = sha.new("%s%s" % (time.time(), random.randrange(1, 10000))).hexdigest()
        #self.datetime = datetime.now()
    
    def check_permission(self, obj):
        user = obj.restrictedTraverse('/acl_users')._nobody
        if user.has_permission(view, obj):
            return True
        else:
            return False
        
    def get_email(self, obj):
        return self.email

    def to_string(self, obj):
        return u'%s (%s)' % (self.organisation, self.email)

class AnonymousNotification(SimpleItem):
    meta_type = "Anonymous Notification"
    security = ClassSecurityInfo()
    
    def __init__(self, id):
        self.id = id
        self.subscriptions_temp = PersistentList()
    
    security.declarePrivate('add_account_subscription')
    def add_email_subscription(self, email, organisation, sector, country, notif_type, lang, confirm_url=""):
        """ 
        Add to e-mail subscription to a temporary list.
        If the user confirms the e-mail then move it to ISubscriptionContainer
        """
        portal_notification = self.getSite().getNotificationTool()
        if not is_valid_email(email):
            raise ValueError('You email address does not appear to be valid.')
        if not organisation:
            raise ValueError('Your organization cannot be empty.')
        if notif_type not in ('instant', 'daily', 'weekly', 'monthly'):
            raise ValueError('Unknown notification type "%s"' % notif_type)
        if portal_notification.config['enable_%s' % notif_type] is False:
            raise ValueError('Notifications of type "%s" not allowed' % notif_type)
        
        subscription_container = ISubscriptionContainer(self.getSite())
        
        # Check if subscription exists
        for id, subscription in subscription_container.list_with_keys():
            if (subscription.email == email and
                subscription.notif_type == notif_type and
                subscription.lang == lang):
                    raise ValueError('Subscription already exists')
        subscription = AnonymousSubscription(email, organisation, sector, country, notif_type, lang)
        self.subscriptions_temp.append(subscription)
        
        #Send email
        email_tool = self.getSite().getEmailTool()
        
        email_from = email_tool._get_from_address()
        email_data = EmailPageTemplateFile('emailpt/email_notify_confirm_email.zpt', globals()).render_email(**{'key': subscription.key, 'url': confirm_url})
        email_to = subscription.email
        email_tool.sendEmail(email_data['body_text'], email_to, email_from, email_data['subject'])
    
    security.declarePrivate('add_account_subscription')
    def import_email_subscription(self, email, organisation, sector, country, notif_type, lang):
        """Import e-mail subscription into the subscriptions container."""
        portal_notification = self.getSite().getNotificationTool()
        subscription_container = ISubscriptionContainer(self.getSite())
        
        subscription = AnonymousSubscription(email, organisation, sector, country, notif_type, lang)
        subscription_container.add(subscription)
    
    security.declarePrivate('remove_account_subscription')
    def remove_account_subscription(self, email, location='', notif_type='', lang=''):
        if not is_valid_email(email):
            raise ValueError('You email address does not appear to be valid.')
        subscription_container = ISubscriptionContainer(self.getSite())
        for id, subscription in subscription_container.list_with_keys():
            if subscription.email == email:
                subscription_container.remove(id)
                return
        raise ValueError('Subscription not found')
    
InitializeClass(AnonymousNotification)