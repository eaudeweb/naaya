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

from datetime import time, datetime, timedelta
from itertools import ifilter

#Zope imports
from DateTime import DateTime
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from persistent.dict import PersistentDict
from BTrees.OIBTree import OISet as PersistentTreeSet
from zope import component

#Product imports
from Products.NaayaCore.constants import *
from Products.NaayaBase.constants import PERMISSION_PUBLISH_OBJECTS
from Products.NaayaCore.EmailTool.EmailPageTemplate import manage_addEmailPageTemplate
from Products.NaayaCore.EmailTool.EmailTool import build_email
from Products.Naaya.interfaces import INySite, IHeartbeat

def manage_addNotificationTool(self, REQUEST=None):
    """ """
    ob = NotificationTool(ID_NOTIFICATIONTOOL, TITLE_NOTIFICATIONTOOL)
    self._setObject(ID_NOTIFICATIONTOOL, ob)
    load_default_templates(ob)

    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

def load_default_templates(notification_tool):
    from skel import default_email_templates
    for name, contents in default_email_templates.iteritems():
        manage_addEmailPageTemplate(notification_tool,
            id='%s_template' % name, text=contents)

Subscription = namedtuple('Subscription', 'user_id location notif_type lang')

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
        self.subscriptions = PersistentTreeSet()
        self.config = PersistentDict({
            'admin_on_error': True,
            'admin_on_edit': True,
            'enable_instant': False,
            'enable_daily': False,
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

    def get_config(self, key):
        return self.config[key]


    def get_location_link(self, location):
        if location:
            return self.restrictedTraverse(location, self.getSite()).absolute_url()
        else:
            return self.getSite().absolute_url()

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_add_subscription')
    def admin_add_subscription(self, user_id, location, notif_type, REQUEST):
        """ """
        if location == '__root': location = ''
        location = ('/').join(location.split('/')[1:])
        try:
            self.add_subscription(user_id, location, notif_type, 'en')
        except ValueError, msg:
            self.setSessionErrors(msg)
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/admin_html')


    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_remove_subscription')
    def admin_remove_subscription(self, user_id, location, notif_type, lang, REQUEST):
        """ """
        self.remove_subscription(user_id, location, notif_type, lang)
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/admin_html')

    security.declarePrivate('add_subscription')
    def add_subscription(self, user_id, location, notif_type, lang):
        """ Subscribe the user `user_id` """
        if notif_type not in ('instant', 'daily', 'weekly', 'monthly'):
            raise ValueError('Unknown notification type "%s"' % notif_type)
        if self.config['enable_%s' % notif_type] is False:
            raise ValueError('Notifications of type "%s" not allowed' % notif_type)
        if notif_type not in self.available_notif_types(location):
            raise ValueError('Subscribing to notifications in "%s" not allowed' % location)

        subscription = Subscription(user_id, location, notif_type, lang)
        if self.subscriptions.has_key(subscription):
            raise ValueError('Subscription already exists')

        self.subscriptions.insert(subscription)

    security.declarePrivate('remove_subscription')
    def remove_subscription(self, user_id, location, notif_type, lang):
        subscription = Subscription(user_id, location, notif_type, lang)
        try:
            self.subscriptions.remove(subscription)
        except KeyError:
            raise ValueError('Subscription not found')

    def list_subscriptions(self, user_id=None, notif_type=None,
            location=None, inherit_location=False):
        """ iterate over all existing subscriptions """
        output = self.subscriptions.__iter__()

        if user_id is not None:
            f = lambda s: s.user_id == user_id
            output = ifilter(f, output)

        if notif_type is not None:
            f = lambda s: s.notif_type == notif_type
            output = ifilter(f, output)

        if location is not None:
            if inherit_location:
                f = lambda s: is_subpath(location, s.location)
            else:
                f = lambda s: s.location == location
            output = ifilter(f, output)

        return output

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
    def notify_instant(self, ob, user_id):
        """ send instant notifications because object `ob` was changed """
        if not self.config['enable_instant']:
            return
        ob_path = ob.get_path_in_site()
        messages_by_user = {}
        for subscription in self.list_subscriptions(notif_type='instant'):
            if not is_subpath(ob_path, subscription.location):
                continue
            messages_by_user[subscription.user_id] = {'ob': ob, 'person': user_id}

        template = self._get_template('instant')
        self._send_notifications(messages_by_user, template)

    def _list_modified_objects(self, when_start, when_end):
        DT_when_start = DateTime_from_datetime(when_start)
        DT_when_end = DateTime_from_datetime(when_end)
        catalog = self.getSite().getCatalogTool()
        brains = catalog(bobobase_modification_time={
            'query': (DT_when_start, DT_when_end), 'range': 'min:max'})
        for brain in brains:
            yield brain.getObject()

    def _get_template(self, name):
        template = self._getOb('%s_template' % name, None)
        if template is None:
            raise ValueError('template for "%s" not found' % name)
        return template.render_email

    def _get_email_tool(self):
        return self.getSite().getEmailTool()

    def _send_notifications(self, messages_by_user, template):
        """ send the notifications described in the `messages_by_user` data structure """
        email_tool = self._get_email_tool()
        addr_from = email_tool._get_from_address()
        for user_id, kwargs in messages_by_user.iteritems():
            addr_to = self._get_user_info(user_id)['email']
            mail_data = template(**kwargs)
            send_notification(email_tool, addr_from, addr_to,
                mail_data['subject'], mail_data['body_text'])

    def _get_user_info(self, user_id):
        # First look for the user in Nayaa's acl_users
        auth_tool = self.getAuthenticationTool()
        user_obj = auth_tool.getUser(user_id)
        if user_obj is not None:
            return {
                'user_id': user_id,
                'full_name': '%s %s' % (
                        auth_tool.getUserFirstName(user_obj),
                        auth_tool.getUserLastName(user_obj)),
                'email': auth_tool.getUserEmail(user_obj),
            }

        # The user is not in Naaya's acl_users, so let's look deeper
        parent_acl_users = self.restrictedTraverse('/').acl_users
        if parent_acl_users.meta_type == 'LDAPUserFolder':
            # TODO: what if parent_acl_users is not an LDAPUserFolder?
            # Note: EIONET LDAP data is encoded with latin-1
            ldap_user_data = parent_acl_users.getUserById(user_id)
            if ldap_user_data:
                return {
                    'user_id': ldap_user_data.uid,
                    'full_name': ldap_user_data.cn,
                        # taken from DAPUserFolder's cache,
                        # already utf-8
                    'email': ldap_user_data.mail,
                }

        # Didn't find the user anywhere; return a placeholder
        return {
            'user_id': user_id,
            'full_name': '[missing user]',
            'email': None,
        }

    def _send_newsletter(self, notif_type, when_start, when_end):
        """
        Send notifications for the period between `when_start` and `when_end`
        using the `notif_type` template
        """
        objects_by_user = {}
        for ob in self._list_modified_objects(when_start, when_end):
            ob_path = ob.get_path_in_site()
            for subscription in self.list_subscriptions(notif_type=notif_type):
                if not is_subpath(ob_path, subscription.location):
                    continue
                msgs_for_user = objects_by_user.setdefault(subscription.user_id, [])
                msgs_for_user.append({'ob': ob})

        messages_by_user = {}
        for user_id, objs in objects_by_user.iteritems():
            messages_by_user[user_id] = {'items': objs}

        template = self._get_template(notif_type)
        self._send_notifications(messages_by_user, template)

    def _cron_heartbeat(self, when):

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

    def index_html(self, REQUEST):
        """ redirect to admin page """
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/admin_html')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_html')
    admin_html = PageTemplateFile('zpt/admin', globals())

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
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/admin_html')

InitializeClass(NotificationTool)

def _send_notification(email_tool, addr_from, addr_to, subject, body):
    mail = build_email(addr_from, addr_to, subject, body)
    #TODO: send using the EmailSender
    email_tool.sendEmail(body, addr_to, addr_from, subject)

def _mock_send_notification(email_tool, addr_from, addr_to, subject, body):
    mock_saved.append( (addr_from, addr_to, subject, body) )

def set_testing_mode(testing, save_to=[]):
    global send_notification
    global mock_saved

    if testing:
        send_notification = _mock_send_notification
        mock_saved = save_to

    else:
        send_notification = _send_notification

set_testing_mode(False)

def norm_folder_path(p):
    if p == '':
        return '/'
    else:
        return '/' + p + '/'

def is_subpath(path1, path2):
    """ check whether `path1` is inside the folder `path2` """
    path1 = norm_folder_path(path1)
    path2 = norm_folder_path(path2)

    return path1.startswith(path2)

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

@component.adapter(INySite, IHeartbeat)
def notifSubscriber(site, hb):
    # notifications are delayed by 1 minute to allow for non-committed
    # transactions (otherwise there's a remote chance that objects added
    # or changed when heartbeat runs would be missed)
    when = hb.when - timedelta(minutes=1)
    site.getNotificationTool()._cron_heartbeat(when)
component.provideHandler(notifSubscriber)

