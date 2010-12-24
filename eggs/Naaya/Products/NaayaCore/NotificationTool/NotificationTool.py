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

#Python imports
try: from collections import namedtuple
except ImportError: from Products.NaayaCore.backport import namedtuple
from operator import attrgetter
import random
try:
    from hashlib.sha1 import new as sha
except:
    from sha import sha

from datetime import time, datetime, timedelta
from itertools import ifilter
import logging

import simplejson as json

#Zope imports
from DateTime import DateTime
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, Unauthorized
from AccessControl.Permissions import view_management_screens, view
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from persistent import Persistent
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from zope import interface
from zope import component
from zope import annotation
import transaction

#Product imports
from Products.NaayaCore.constants import *
from Products.NaayaBase.constants import PERMISSION_PUBLISH_OBJECTS
from Products.NaayaCore.EmailTool.EmailPageTemplate import (
    manage_addEmailPageTemplate, EmailPageTemplateFile)
from Products.NaayaCore.EmailTool.EmailTool import build_email
from Products.Naaya.interfaces import INySite, IHeartbeat
from Products.NaayaCore.PortletsTool.interfaces import INyPortlet
from naaya.content.base.interfaces import INyContentObject
from naaya.core.utils import path_in_site
from naaya.core.utils import relative_object_path
from naaya.core.utils import force_to_unicode
from naaya.core.utils import ofs_path
from naaya.core.zope2util import folder_manage_main_plus
from naaya.core.paginator import DiggPaginator, EmptyPage, InvalidPage
from naaya.core.exceptions import i18n_exception
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from Products.NaayaCore.managers.utils import is_valid_email

from interfaces import ISubscriptionContainer
from interfaces import ISubscription
from interfaces import ISubscriptionTarget

notif_logger = logging.getLogger('naaya.core.notif')

email_templates = {
    'instant': EmailPageTemplateFile('emailpt/instant.zpt', globals()),
    'daily': EmailPageTemplateFile('emailpt/daily.zpt', globals()),
    'weekly': EmailPageTemplateFile('emailpt/weekly.zpt', globals()),
    'monthly': EmailPageTemplateFile('emailpt/monthly.zpt', globals()),
}

def manage_addNotificationTool(self, REQUEST=None):
    """ """
    ob = NotificationTool(ID_NOTIFICATIONTOOL, TITLE_NOTIFICATIONTOOL)
    self._setObject(ID_NOTIFICATIONTOOL, ob)

    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

# TODO: remove `Subscription` after all sites have been updated
Subscription = namedtuple('Subscription', 'user_id location notif_type lang')

def match_account_subscription(subs, user_id, notif_type, lang):
    for n, subscription in subs.list_with_keys():
        if not isinstance(subscription, AccountSubscription):
            continue
        if (subscription.user_id == user_id and
            subscription.notif_type == notif_type and
            subscription.lang == lang):
            return n

class NotificationTool(Folder):
    """ """

    meta_type = METATYPE_NOTIFICATIONTOOL
    icon = 'misc_/NaayaCore/NotificationTool.gif'

    meta_types = ()
    all_meta_types = meta_types

    security = ClassSecurityInfo()



    def __init__(self, id, title):
        """ """
        self.id = id
        self.title = title
        self.config = PersistentDict({
            'admin_on_error': True,
            'admin_on_edit': True,
            'enable_instant': False,
            'enable_daily': False,
            'enable_anonymous': False, #Enable anonymous notifications
            'daily_hour': 0,
            'enable_weekly': False,
            'weekly_day': 1, # 1 = monday, 7 = sunday
            'weekly_hour': 0,
            'enable_monthly': False,
            'monthly_day': 1, # 1 = first day of the month
            'monthly_hour': 0,
            'notif_content_types': [],
        })
        self.timestamps = PersistentDict()
        #Confirmations list
        self.pending_anonymous_subscriptions = PersistentList()

    def get_config(self, key):
        return self.config.get(key)

    def get_location_link(self, location):
        if location:
            return self.restrictedTraverse(location, self.getSite()).absolute_url()
        else:
            return self.getSite().absolute_url()

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS,
                              'admin_get_subscriptions')
    def admin_get_subscriptions(self):
        for obj, sub_id, subscription in walk_subscriptions(self.getSite()):
            yield {
                'user': subscription.to_string(obj),
                'location': path_in_site(obj),
                'sub_id': sub_id,
                'lang': subscription.lang,
                'notif_type': subscription.notif_type,
            }

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS,
                              'admin_add_account_subscription')
    def admin_add_account_subscription(self, REQUEST, user_id,
                                       location, notif_type, lang):
        """ """
        if location == '/': location = ''
        ob = self.getSite().unrestrictedTraverse(location)
        location = relative_object_path(ob, self.getSite())
        try:
            self.add_account_subscription(user_id.strip(), location,
                                          notif_type, lang)
        except ValueError, msg:
            self.setSessionErrorsTrans(msg)
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/admin_html')


    security.declareProtected(PERMISSION_PUBLISH_OBJECTS,
                              'admin_remove_account_subscription')
    def admin_remove_account_subscription(self, REQUEST, location, sub_id):
        """ """
        obj = self.getSite().restrictedTraverse(location)
        subscription_container = ISubscriptionContainer(obj)
        subscription_container.remove(sub_id)
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/admin_html')

    def _validate_subscription(self, **kw):
        """ Validate add/edit subscription for authorized and anonymous users

        """
        if kw['notif_type'] not in self.available_notif_types(kw['location']):
            raise i18n_exception(ValueError, 'Subscribing to notifications in '
                        '"${location}" not allowed', location=kw['location'])
        try:
            obj = self.getSite().restrictedTraverse(kw['location'])
        except:
            raise i18n_exception(ValueError,
                                 'This path is invalid or protected')
        try:
            subscription_container = ISubscriptionContainer(obj)
        except:
            raise i18n_exception(ValueError, 'Cannot subscribe to this folder')

        if not kw.get('anonymous', False):
            n = match_account_subscription(subscription_container,
                                           kw['user_id'], kw['notif_type'],
                                           kw['lang'])
            if n is not None:
                raise i18n_exception(ValueError, 'Subscription already exists')
        else: #Check if subscription exists for this anonymous subscriber
            if not is_valid_email(kw.get('email', '')):
                raise i18n_exception(ValueError,
                            'Your e-mail address does not appear to be valid.')
            for id, subscription in subscription_container.list_with_keys():
                #Normal subscriptions don't have e-mail
                if isinstance(subscription, AnonymousSubscription):
                    if (subscription.email == kw['email'] and
                        subscription.notif_type == kw['notif_type'] and
                        subscription.lang == kw['lang']):
                            raise i18n_exception(ValueError,
                                                 'Subscription already exists')

    security.declarePrivate('add_account_subscription')
    def add_account_subscription(self, user_id, location, notif_type, lang):
        """ Subscribe the user `user_id` """
        self._validate_subscription(user_id=user_id, location=location,
                                    notif_type=notif_type, lang=lang)

        obj = self.getSite().restrictedTraverse(location)
        subscription_container = ISubscriptionContainer(obj)
        subscription = AccountSubscription(user_id, notif_type, lang)
        subscription_container.add(subscription)

    security.declarePrivate('add_anonymous_subscription')
    def add_anonymous_subscription(self, **kw):
        """ Handle anonymous users """
        self._validate_subscription(anonymous=True, **kw)
        subscription = AnonymousSubscription(**kw)
        #Add to temporary container
        self.pending_anonymous_subscriptions.append(subscription)

        #Send email
        email_tool = self.getSite().getEmailTool()
        email_from = email_tool._get_from_address()
        email_template = EmailPageTemplateFile(
            'emailpt/confirm.zpt', globals())
        email_data = email_template.render_email(
            **{'key': subscription.key, 'here': self})
        email_to = subscription.email
        email_tool.sendEmail(email_data['body_text'], email_to, email_from,
                             email_data['subject'])

    security.declarePrivate('remove_account_subscription')
    def remove_account_subscription(self, user_id, location, notif_type, lang):
        obj = self.getSite().restrictedTraverse(location)
        subscription_container = ISubscriptionContainer(obj)
        n = match_account_subscription(subscription_container,
                                       user_id, notif_type, lang)
        if n is None:
            raise ValueError('Subscription not found')
        subscription_container.remove(n)

    security.declarePrivate('unsubscribe_links_html')
    unsubscribe_links_html = PageTemplateFile("emailpt/unsubscribe_links.zpt",
                                              globals())
    security.declarePrivate('remove_anonymous_subscription')
    def remove_anonymous_subscription(self, email, location, notif_type, lang):
        try:
            obj = self.getSite().restrictedTraverse(location)
        except:
            raise i18n_exception(ValueError, 'Invalid location')

        try:
            subscription_container = ISubscriptionContainer(obj)
        except:
            raise i18n_exception(ValueError, 'Invalid container')
        anonymous_subscriptions = [(n, s) for n, s in
                                   subscription_container.list_with_keys()
                                   if hasattr(s, 'email')]
        subscriptions = filter(lambda s: (s[1].email == email and
                                          s[1].location == location and
                                          s[1].notif_type == notif_type),
                                          anonymous_subscriptions)
        if len(subscriptions) == 1:
            subscription_container.remove(subscriptions[0][0])
        else:
            raise i18n_exception(ValueError, 'Subscription not found')

    security.declareProtected(view, 'available_notif_types')
    def available_notif_types(self, location=''):
        if self.config['enable_instant']:
            yield 'instant'
        if self.config['enable_daily']:
            yield 'daily'
        if self.config['enable_weekly']:
            yield 'weekly'
        if self.config['enable_monthly']:
            yield 'monthly'

    security.declarePrivate('notify_instant')
    def notify_instant(self, ob, user_id, ob_edited=False):
        """
        send instant notifications because object `ob` was changed by
        the user `user_id`
        """
        notif_logger.info('Instant notifications on %r', ofs_path(ob))
        if not self.config['enable_instant']:
            return
        messages_by_email = {}
        for subscription in fetch_subscriptions(ob, inherit=True):
            if not subscription.check_permission(ob):
                continue
            if subscription.notif_type != 'instant':
                continue
            email = subscription.get_email(ob)
            if email is None:
                continue

            notif_logger.info('.. sending notification to %r', email)
            messages_by_email[email] = {
                'ob': ob,
                'here': self,
                'ob_edited': ob_edited,
                'person': user_id,
                '_lang': subscription.lang,
                'subscription': subscription,
                'anonymous': isinstance(subscription, AnonymousSubscription)
            }

        template = self._get_template('instant')
        self._send_notifications(messages_by_email, template)

    def _get_template(self, name):
        template = self._getOb('emailpt_%s' % name, None)
        if template is not None:
            return template.render_email

        template = email_templates.get(name, None)
        if template is not None:
            return template.render_email

        raise ValueError('template for %r not found' % name)

    def _send_notifications(self, messages_by_email, template):
        """
        Send the notifications described in the `messages_by_email` data
        structure, using the specified EmailTemplate.

        `messages_by_email` should be a dictionary, keyed by email
        address. The values should be dictionaries suitable to be passed
        as kwargs (options) to the template.
        """
        portal = self.getSite()
        email_tool = portal.getEmailTool()
        addr_from = email_tool._get_from_address()
        for addr_to, kwargs in messages_by_email.iteritems():
            translate = self.getSite().getPortalTranslations()
            kwargs.update({'portal': portal, '_translate': translate})
            mail_data = template(**kwargs)
            send_notification(email_tool, addr_from, addr_to,
                mail_data['subject'], mail_data['body_text'])

    def _send_newsletter(self, notif_type, when_start, when_end):
        """
        Send notifications for the period between `when_start` and `when_end`
        using the `notif_type` template
        """
        notif_logger.info('Notifications newsletter on site %r, type %r, '
                          'from %r to %r',
                          ofs_path(self.getSite()), notif_type,
                          when_start, when_end)
        objects_by_email = {}
        langs_by_email = {}
        subscriptions_by_email = {}
        anonymous_users = {}
        for ob in list_modified_objects(self.getSite(), when_start, when_end):
            notif_logger.info('.. modified object: %r', ofs_path(ob))
            for subscription in fetch_subscriptions(ob, inherit=True):
                if subscription.notif_type != notif_type:
                    continue
                if not subscription.check_permission(ob):
                    continue
                email = subscription.get_email(ob)
                if email is None:
                    continue
                notif_logger.info('.. .. sending notification to %r', email)
                objects_by_email.setdefault(email, []).append({'ob': ob})
                langs_by_email[email] = subscription.lang

                subscriptions_by_email[email] = subscription
                anonymous_users[email] = isinstance(subscription,
                                                    AnonymousSubscription)

        messages_by_email = {}
        for email in objects_by_email:
            messages_by_email[email] = {
                'objs': objects_by_email[email],
                '_lang': langs_by_email[email],
                'subscription': subscriptions_by_email[email],
                'here': self,
                'anonymous': anonymous_users[email]
            }

        template = self._get_template(notif_type)
        self._send_notifications(messages_by_email, template)

    def _cron_heartbeat(self, when):
        transaction.commit() # commit earlier stuff; fresh transaction
        transaction.get().note('notifications cron at %s' % ofs_path(self))

        #Clean temporary subscriptions after a week:
        if self.config.get('enable_anonymous', False):
            a_week_ago = when - timedelta(weeks=1)
            for tmp_subscription in self.pending_anonymous_subscriptions[:]:
                if tmp_subscription.datetime <= a_week_ago:
                    self.pending_anonymous_subscriptions.remove(
                        tmp_subscription)

        ### daily newsletter ###
        if self.config['enable_daily']:
            # calculate the most recent daily newsletter time
            daily_time = time(hour=self.config['daily_hour'])
            latest_daily = datetime.combine(when.date(), daily_time)
            if latest_daily > when:
                latest_daily -= timedelta(days=1)

            # check if we should send a daily newsletter
            prev_daily = self.timestamps.get('daily', when - timedelta(days=1))
            if prev_daily < latest_daily < when:
                self._send_newsletter('daily', prev_daily, when)
                self.timestamps['daily'] = when

        ### weekly newsletter ###
        if self.config['enable_weekly']:
            # calculate the most recent weekly newsletter time
            weekly_time = time(hour=self.config['daily_hour'])
            t = datetime.combine(when.date(), weekly_time)
            days_delta = self.config['weekly_day'] - t.isoweekday()
            latest_weekly = t + timedelta(days=days_delta)
            if latest_weekly > when:
                latest_weekly -= timedelta(weeks=1)

            # check if we should send a weekly newsletter
            prev_weekly = self.timestamps.get('weekly', when - timedelta(weeks=1))
            if prev_weekly < latest_weekly < when:
                self._send_newsletter('weekly', prev_weekly, when)
                self.timestamps['weekly'] = when

        ### monthly newsletter ###
        if self.config['enable_monthly']:
            # calculate the most recent monthly newsletter time
            monthly_time = time(hour=self.config['monthly_hour'])
            the_day = set_day_of_month(when.date(), self.config['monthly_day'])
            latest_monthly = datetime.combine(the_day, monthly_time)
            if latest_monthly > when:
                latest_monthly = minus_one_month(latest_monthly)

            # check if we should send a monthly newsletter
            prev_monthly = self.timestamps.get('monthly', minus_one_month(when))
            if prev_monthly < latest_monthly < when:
                self._send_newsletter('monthly', prev_monthly, when)
                self.timestamps['monthly'] = when

        transaction.commit() # make sure our timestamp updates are saved

    def index_html(self, RESPONSE):
        """ redirect to admin page """
        RESPONSE.redirect(self.absolute_url() + '/my_subscriptions_html')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_html')
    admin_html = PageTemplateFile('zpt/admin', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_search_user')
    def admin_search_user(self, REQUEST):
        """ search for user by name (ajax function) """
        query = REQUEST.form['query']
        acl_users = self.getSite().getAuthenticationTool()
        users = acl_users.search_users(query, all_users=True)
        REQUEST.RESPONSE.setHeader('Content-Type', 'application/json')
        return json.dumps([ {'user_id': user.name,
                             'full_name': user.firstname + " " + user.lastname,
                             'email': user.email} for user in users ])

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_html')
    def admin_settings(self, REQUEST):
        """ save settings from the admin page """
        form = REQUEST.form
        self.config['admin_on_error'] = form.get('admin_on_error', False)
        self.config['admin_on_edit'] = form.get('admin_on_edit', False)
        self.config['enable_instant'] = form.get('enable_instant', False)
        self.config['enable_daily'] = form.get('enable_daily', False)
        self.config['daily_hour'] = form.get('daily_hour')
        self.config['enable_weekly'] = form.get('enable_weekly', False)
        self.config['weekly_day'] = form.get('weekly_day')
        self.config['weekly_hour'] = form.get('weekly_hour')
        self.config['enable_monthly'] = form.get('enable_monthly', False)
        self.config['monthly_day'] = form.get('monthly_day')
        self.config['monthly_hour'] = form.get('monthly_hour')
        self.config['notif_content_types'] = form.get('notif_content_types', [])
        self.config['enable_anonymous'] = form.get('enable_anonymous', False)
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/admin_html')

    security.declareProtected(view_management_screens,
                              'manage_customizeTemplate')
    def manage_customizeTemplate(self, name, REQUEST=None):
        """ customize the email template called `name` """
        ob_id = 'emailpt_%s' % name
        manage_addEmailPageTemplate(self, ob_id, email_templates[name]._text)
        ob = self._getOb(ob_id)

        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(ob.absolute_url() + '/manage_workspace')
        else:
            return ob_id

    security.declareProtected(view_management_screens, 'manage_main')
    manage_main = folder_manage_main_plus

    security.declareProtected(view_management_screens, 'ny_after_listing')
    ny_after_listing = PageTemplateFile('zpt/customize_emailpt', globals())
    ny_after_listing.email_templates = email_templates

    security.declareProtected(view, 'my_subscriptions_html')
    my_subscriptions_html = NaayaPageTemplateFile('zpt/index', globals(),
                                'naaya.core.notifications.my_subscriptions')

    security.declareProtected(view, 'list_my_subscriptions')
    def list_my_subscriptions(self, REQUEST):
        out = []
        user_id = REQUEST.AUTHENTICATED_USER.getId()
        if user_id is None and not self.config.get('enable_anonymous', False):
            raise Unauthorized # to force login

        for obj, n, subscription in walk_subscriptions(self.getSite()):
            if not isinstance(subscription, AccountSubscription):
                continue
            if subscription.user_id != user_id:
                continue
            out.append({
                'location': path_in_site(obj),
                'notif_type': subscription.notif_type,
                'lang': subscription.lang,
            })

        return out

    security.declareProtected(view, 'subscribe_me')
    def subscribe_me(self, REQUEST, location, notif_type, lang=None):
        """ add subscription for currently-logged-in user """
        if lang is None:
            lang = self.gl_get_selected_language()
            REQUEST.form['lang'] = lang
        user_id = REQUEST.AUTHENTICATED_USER.getId()
        if user_id is None and not self.config.get('enable_anonymous', False):
            raise Unauthorized # to force login
        try:
            if user_id:
                self.add_account_subscription(user_id, location, notif_type,
                                              lang)
                self.setSessionInfoTrans(
                    'You will receive ${notif_type} notifications'
                    ' for any changes in "${location}".',
                    notif_type=notif_type, location=location)
            else:
                    self.add_anonymous_subscription(**dict(REQUEST.form))
                    self.setSessionInfoTrans(
                    'An activation e-mail has been sent to ${email}. '
                    'Follow the instructions to subscribe to ${notif_type} '
                    'notifications for any changes in "${location}".',
                    notif_type=notif_type, location=location,
                    email=REQUEST.form.get('email'))
        except ValueError, msg:
            self.setSessionErrors([unicode(msg)])
        return REQUEST.RESPONSE.redirect(self.absolute_url() +
                                         '/my_subscriptions_html')

    security.declareProtected(view, 'unsubscribe_me')
    def unsubscribe_me(self, REQUEST, location='', notif_type='', lang='',
                       email=''):
        """ remove subscription of currently-logged-in user """
        user_id = REQUEST.AUTHENTICATED_USER.getId()
        if user_id is None and not self.config.get('enable_anonymous', False):
            raise Unauthorized # to force login
        try:
            if user_id is not None:
                self.remove_account_subscription(user_id, location, notif_type,
                                                 lang)
            else:
                self.remove_anonymous_subscription(email, location, notif_type,
                                                 lang)
            self.setSessionInfoTrans(
                'You will not receive any more ${notif_type} '
                'notifications for changes in "${location}".',
                notif_type=notif_type, location=location)
        except ValueError, msg:
            self.setSessionErrors([unicode(msg)])
        return REQUEST.RESPONSE.redirect(self.absolute_url() +
                                         '/my_subscriptions_html')

    security.declarePublic('confirm')
    def confirm(self, REQUEST=None, key=''):
        """ Verify confirmation key and redirect to success page
        """
        if key:
            subscriptions = ISubscriptionContainer(self.getSite())
            # Check if the key is in the temporary list
            for subscription in self.pending_anonymous_subscriptions:
                if str(key) == subscription.key:
                    #Verify if the email is not already subscribed
                    for existing_subscription in subscriptions:
                        if subscription.email == existing_subscription.email:
                            return REQUEST.RESPONSE.redirect(
                                self.absolute_url() + '/my_subscriptions_html')
                    container = ISubscriptionContainer(
                            self.getSite().restrictedTraverse(
                                subscription.location))
                    container.add(subscription) # Add to subscribed list
                    # Remove from temporary list
                    del self.pending_anonymous_subscriptions[
                        self.pending_anonymous_subscriptions.index(subscription)]
                    if REQUEST is not None:
                        self.setSessionInfoTrans(
                            'You succesfully subscribed to ${notif_type} '
                            'notifications for any changes in "${location}".',
                            notif_type=subscription.notif_type,
                            location=subscription.location)
                    break
            else:
                if REQUEST is not None:
                    self.setSessionErrorsTrans("Confirmation key not found")
                else:
                    raise ValueError("Confirmation key not found")
        else:
            if REQUEST is not None:
                self.setSessionErrorsTrans("Confirmation key is invalid")
            else:
                raise ValueError("Confirmation key is invalid")

        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect(self.absolute_url() +
                                         '/my_subscriptions_html')

InitializeClass(NotificationTool)

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

divert_notifications(False)

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
    return set_day_of_month(the_date.replace(day=1) - timedelta(days=1), the_date.day)


class SubscriptionContainer(Persistent):
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

subscription_container_factory = annotation.factory(SubscriptionContainer)

class AccountSubscription(object):
    interface.implements(ISubscription)

    def __init__(self, user_id, notif_type, lang):
        self.user_id = user_id
        self.lang = lang
        self.notif_type = notif_type

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

    def __init__(self, **kw):
        """
        @todo: Make a heartbeat to clean-up temporary subscribtions
        """
        self.email = kw.pop('email')
        self.notif_type = kw.pop('notif_type')
        self.lang = kw.pop('lang')
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


@component.adapter(INySite, IHeartbeat)
def notifSubscriber(site, hb):
    # notifications are delayed by 1 minute to allow for non-committed
    # transactions (otherwise there's a remote chance that objects added
    # or changed when heartbeat runs would be missed)
    when = hb.when - timedelta(minutes=1)
    site.getNotificationTool()._cron_heartbeat(when)
component.provideHandler(notifSubscriber)

class NotificationsPortlet(object):
    interface.implements(INyPortlet)
    component.adapts(INySite)

    title = 'Subscribe to notifications'

    def __init__(self, site):
        self.site = site

    def __call__(self, context, position):
        notif_tool = self.site.getNotificationTool()
        if not list(notif_tool.available_notif_types()):
            return ''

        macro = self.site.getPortletsTool()._get_macro(position)
        tmpl = self.template.__of__(context)
        return tmpl(macro=macro, notif_tool=notif_tool,
                    location=path_in_site(context))

    template = PageTemplateFile('zpt/portlet', globals())
