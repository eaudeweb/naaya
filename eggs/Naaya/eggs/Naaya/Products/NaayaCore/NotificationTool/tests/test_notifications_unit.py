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

try: from collections import namedtuple
except ImportError: from Products.NaayaCore.backport import namedtuple

from unittest import TestSuite, makeSuite
from datetime import date, time, datetime, timedelta
from operator import attrgetter
import transaction

from Products.NaayaCore.NotificationTool.NotificationTool \
    import divert_notifications
from Products.NaayaCore.NotificationTool.NotificationTool import (
    NotificationTool, walk_subscriptions)
from Products.NaayaCore.NotificationTool import NotificationTool as \
    NotificationTool_module
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.tests.utils import replace, restore_all
from Products.Naaya.NyFolder import addNyFolder
from naaya.content.document.document_item import addNyDocument
from naaya.core.utils import path_in_site

class BaseNotificationsTest(NaayaTestCase):
    def afterSetUp(self):
        notif_tool = self.portal.getNotificationTool()
        self._notif_config = dict(notif_tool.config)
        self._notifications = []
        self._subscriptions_to_remove = []
        divert_notifications(True, save_to=self._notifications)
        addNyFolder(self.portal, 'fol1', contributor='contributor')
        addNyFolder(self.portal, 'fol2', contributor='contributor')

        self.object_timestamps = []
        def testing_list_modified_objects(site, when_start, when_end):
            for ob_path, modif_datetime in self.object_timestamps:
                if when_start < modif_datetime < when_end:
                    yield site.unrestrictedTraverse(ob_path)

        replace(NotificationTool_module,
                'list_modified_objects',
                testing_list_modified_objects)

        def testing_get_template(self, template_name):
            def single_tmpl(ob, person, portal, **kwargs):
                return {'subject': 'notifications',
                        'body_text': 'instant [%s] %s' %
                            (path_in_site(ob), portal.title_or_id())}

            def group_tmpl(portal, objs, **kwargs):
                keyer = lambda item: path_in_site(item['ob'])
                sorted_items = sorted(objs, key=keyer)
                items_str = ''.join('[%s]' % path_in_site(item['ob']) for
                                    item in sorted_items)
                body = '%s %s %s' % (template_name, items_str,
                                     portal.title_or_id())
                return {'subject': 'notifications', 'body_text': body}

            if template_name == 'instant':
                return single_tmpl
            else:
                return group_tmpl

        replace(NotificationTool, '_get_template', testing_get_template)
        transaction.commit()


    def beforeTearDown(self):
        notif_tool = self.portal.getNotificationTool()
        restore_all()
        for args in self._subscriptions_to_remove:
            notif_tool.remove_account_subscription(*args)
        self.portal.manage_delObjects(['fol1', 'fol2'])
        notif_tool.config.update(self._notif_config)
        divert_notifications(False)
        transaction.commit()

    def _fetch_test_notifications(self):
        notifications = list(self._notifications)
        self._notifications[:] = []
        return notifications

    def add_account_subscription(self, *args):
        """
        create a subscription; it will be auto-removed in
        beforeTearDown.
        """
        self.portal.getNotificationTool().add_account_subscription(*args)
        self._subscriptions_to_remove.append(args)

    def walk_site_subscriptions(self):
        return set((sub.user_id, path_in_site(obj),
                    sub.notif_type, sub.lang) for
                        obj, n, sub in walk_subscriptions(self.portal))

class NotificationsUnitTest(BaseNotificationsTest):
    """ unit test for notifications """

    def afterSetUp(self):
        super(NotificationsUnitTest, self).afterSetUp()
        self.portal.getNotificationTool().config.update({
            'enable_instant': True,
            'enable_daily': True,
            'enable_weekly': True,
            'enable_monthly': True,
        })
        transaction.commit()

    def test_add_account_subscription(self):
        notif_tool = self.portal.getNotificationTool()

        self.add_account_subscription('gigel', '', 'instant', 'en')
        self.add_account_subscription('contributor', '', 'instant', 'en')

        subs = self.walk_site_subscriptions()
        self.assertEqual(len(subs), 2)
        self.assertEqual(subs, set([
            ('gigel', '', 'instant', 'en'),
            ('contributor', '', 'instant', 'en'), ]))

    def test_weekly_notification_interval(self):
        notif_tool = self.portal.getNotificationTool()

        self.add_account_subscription('user1', '', 'weekly', 'en')
        self.add_account_subscription('user2', '', 'weekly', 'en')

        addNyDocument(self.portal['fol1'], id='doc_a')
        addNyDocument(self.portal['fol1'], id='doc_b')
        self.object_timestamps = [
            ('fol1/doc_a', datetime(2009, 7, 16)),
            ('fol1/doc_b', datetime(2009, 8, 3)),
        ]

        notif_tool._send_newsletter('weekly',
            datetime(2009, 7, 30), datetime(2009, 8, 5))
        self.assertEqual(set(self._fetch_test_notifications()), set([
            ('from.zope@example.com', 'user1@example.com', 'notifications',
                'weekly [fol1/doc_b] portal'),
            ('from.zope@example.com', 'user2@example.com', 'notifications',
                'weekly [fol1/doc_b] portal'),
        ]))

    def test_notification_type_checking(self):
        notif_tool = self.portal.getNotificationTool()

        self.add_account_subscription('user1', 'fol1', 'instant', 'en')
        self.add_account_subscription('user2', 'fol1', 'daily', 'en')
        self.add_account_subscription('user3', 'fol1', 'weekly', 'en')

        addNyDocument(self.portal['fol1'], id='doc_a')
        addNyDocument(self.portal['fol1'], id='doc_b')
        self.object_timestamps = [
            ('fol1/doc_a', datetime(2009, 7, 16)),
            ('fol1/doc_b', datetime(2009, 8, 3)),
        ]

        notif_tool._send_newsletter('daily',
            datetime(2009, 7, 30), datetime(2009, 8, 5))
        self.assertEqual(set(self._fetch_test_notifications()), set([
            ('from.zope@example.com', 'user2@example.com', 'notifications',
                'daily [fol1/doc_b] portal'),
        ]))

        notif_tool._send_newsletter('weekly',
            datetime(2009, 7, 30), datetime(2009, 8, 5))
        self.assertEqual(set(self._fetch_test_notifications()), set([
            ('from.zope@example.com', 'user3@example.com', 'notifications',
                'weekly [fol1/doc_b] portal'),
        ]))

        notif_tool._send_newsletter('monthly',
            datetime(2009, 7, 30), datetime(2009, 8, 5))
        self.assertEqual(set(self._fetch_test_notifications()), set())

    def test_weekly_notification_paths(self):
        notif_tool = self.portal.getNotificationTool()

        addNyFolder(self.portal['fol1'], 'g', contributor='admin')
        addNyFolder(self.portal['fol1'], 'h', contributor='admin')
        addNyDocument(self.portal['fol1']['g'], id='doc_a')
        addNyDocument(self.portal['fol1']['h'], id='doc_b')
        addNyDocument(self.portal['fol1'], id='doc_c', discussion=0)

        self.add_account_subscription('user1', 'fol1/g', 'weekly', 'en')
        self.add_account_subscription('user2', 'fol1/h', 'weekly', 'en')
        self.add_account_subscription('user3', 'fol1', 'weekly', 'en')

        self.object_timestamps = [
            ('fol1/g/doc_a', datetime(2009, 8, 3)),
            ('fol1/h/doc_b', datetime(2009, 8, 3)),
            ('fol1/doc_c', datetime(2009, 8, 3)),
        ]

        notif_tool._send_newsletter('weekly',
            datetime(2009, 7, 30), datetime(2009, 8, 5))
        self.assertEqual(set(self._fetch_test_notifications()), set([
            ('from.zope@example.com', 'user1@example.com',
                'notifications', 'weekly [fol1/g/doc_a] portal'),
            ('from.zope@example.com', 'user2@example.com',
                'notifications', 'weekly [fol1/h/doc_b] portal'),
            ('from.zope@example.com', 'user3@example.com', 'notifications',
                'weekly [fol1/doc_c][fol1/g/doc_a][fol1/h/doc_b] portal'),
        ]))

    def test_instant_notifications(self):
        notif_tool = self.portal.getNotificationTool()

        self.add_account_subscription('user1', 'fol1', 'instant', 'en')
        self.add_account_subscription('user2', 'fol2', 'instant', 'en')
        self.add_account_subscription('user3', '', 'instant', 'en')

        addNyDocument(self.portal['fol1'], id='doc_a')
        self.object_timestamps = [
            ('fol1/doc_a', datetime(2009, 8, 3)),
        ]
        notif_tool.notify_instant(self.portal['fol1']['doc_a'], 'somebody')
        self.assertEqual(set(self._fetch_test_notifications()), set([
            ('from.zope@example.com', 'user1@example.com', 'notifications',
                'instant [fol1/doc_a] portal'),
            ('from.zope@example.com', 'user3@example.com', 'notifications',
                'instant [fol1/doc_a] portal'),
        ]))

class NotificationsRestrictedUnitTest(BaseNotificationsTest):
    """ unit test for notifications on restricted objects """

    def afterSetUp(self):
        super(NotificationsRestrictedUnitTest, self).afterSetUp()
        self.portal.getNotificationTool().config.update({
            'enable_instant': True,
            'enable_daily': True,
            'enable_weekly': True,
            'enable_monthly': True,
        })
        transaction.commit()

    def test_restricted_instant(self):
        notif_tool = self.portal.getNotificationTool()

        self.add_account_subscription('reviewer', 'fol1', 'instant', 'en')
        self.add_account_subscription('user2', 'fol1', 'instant', 'en')

        addNyDocument(self.portal['fol1'], id='doc_a', contributor='admin')
        addNyDocument(self.portal['fol1'], id='doc_b', contributor='admin')
        self.portal['fol1']['doc_a']._View_Permission = ('Reviewer',)
        self.portal['fol1']['doc_b']._View_Permission = ('Contributor',)

        notif_tool.notify_instant(self.portal['fol1']['doc_a'], 'somebody')
        notif_tool.notify_instant(self.portal['fol1']['doc_b'], 'somebody')

        self.assertEqual(set(self._fetch_test_notifications()), set([
            ('from.zope@example.com', 'reviewer@example.com',
                'notifications', 'instant [fol1/doc_a] portal'),
            ('from.zope@example.com', 'user2@example.com',
                'notifications', 'instant [fol1/doc_b] portal'),
        ]))

    def test_restricted_periodic(self):
        notif_tool = self.portal.getNotificationTool()

        self.add_account_subscription('reviewer', 'fol1', 'weekly', 'en')
        self.add_account_subscription('user2', 'fol1', 'weekly', 'en')

        addNyDocument(self.portal['fol1'], id='doc_a', contributor='admin')
        addNyDocument(self.portal['fol1'], id='doc_b', contributor='admin')
        self.portal['fol1']['doc_a']._View_Permission = ('Reviewer',)
        self.portal['fol1']['doc_b']._View_Permission = ('Contributor',)
        self.object_timestamps = [
            ('fol1/doc_a', datetime(2009, 8, 3)),
            ('fol1/doc_b', datetime(2009, 8, 3)),
        ]

        notif_tool._send_newsletter('weekly',
            datetime(2009, 7, 30), datetime(2009, 8, 5))

        self.assertEqual(set(self._fetch_test_notifications()), set([
            ('from.zope@example.com', 'reviewer@example.com', 'notifications',
                'weekly [fol1/doc_a] portal'),
            ('from.zope@example.com', 'user2@example.com', 'notifications',
                'weekly [fol1/doc_b] portal'),
        ]))

class NotificationsCronUnitTest(BaseNotificationsTest):
    """ unit test for notifications """

    def afterSetUp(self):
        super(NotificationsCronUnitTest, self).afterSetUp()
        notif_tool = self.portal.getNotificationTool()
        notif_tool.config['daily_hour'] = 10
        notif_tool.config['weekly_hour'] = 10
        notif_tool.config['weekly_day'] = 3
        notif_tool.config['monthly_hour'] = 10
        notif_tool.config['monthly_day'] = 17

        self._newsletters = []
        def testing_send_newsletter(self2, notif_type, when_start, when_end):
            self._newsletters.append( (notif_type, when_start, when_end) )

        replace(NotificationTool, '_send_newsletter', testing_send_newsletter)
        transaction.commit()

    def fetch_test_newsletters(self):
        newsletters = set(self._newsletters)
        self._newsletters[:] = []
        return newsletters


    def test_daily(self):
        notif_tool = self.portal.getNotificationTool()

        # daily notifications are disabled; send nothing
        today = date(2009, 8, 3)
        notif_tool._cron_heartbeat(datetime.combine(today, time(7, 15)))
        self.failUnlessEqual(self.fetch_test_newsletters(), set())

        # enable daily notifications
        notif_tool.config['enable_daily'] = True

        # no previous timestamp; should send daily newsletter
        today_7_15 = datetime.combine(today, time(7, 15))
        notif_tool._cron_heartbeat(today_7_15)
        self.failUnlessEqual(self.fetch_test_newsletters(),
            set([ ('daily', today_7_15 - timedelta(days=1), today_7_15) ]))

        # again no previous timestamp, but this time after the designated
        # hour; should still send newsletter
        del notif_tool.timestamps['daily']
        today_15_26 = datetime.combine(today, time(15, 26))
        notif_tool._cron_heartbeat(today_15_26)
        self.failUnlessEqual(self.fetch_test_newsletters(),
            set([ ('daily', today_15_26 - timedelta(days=1), today_15_26) ]))

        # previous timestamp is too close; should send nothing
        notif_tool._cron_heartbeat(datetime.combine(today, time(18, 10)))
        self.failUnlessEqual(self.fetch_test_newsletters(), set())

        # after next regular time; should send newsletter
        tomorrow_10_15 = datetime.combine(today + timedelta(days=1), time(10, 15))
        notif_tool._cron_heartbeat(tomorrow_10_15)
        self.failUnlessEqual(self.fetch_test_newsletters(),
            set([ ('daily', today_15_26, tomorrow_10_15) ]))

    def test_weekly(self):
        notif_tool = self.portal.getNotificationTool()

        # weekly notifications are disabled; send nothing
        monday = datetime(2009, 8, 3, 15, 35) # monday, 15:35
        notif_tool._cron_heartbeat(monday)
        self.failUnlessEqual(self.fetch_test_newsletters(), set())

        # enable weekly notifications
        notif_tool.config['enable_weekly'] = True

        # no previous timestamp; should send weekly newsletter
        notif_tool._cron_heartbeat(monday)
        self.failUnlessEqual(self.fetch_test_newsletters(),
            set([ ('weekly', monday - timedelta(weeks=1), monday) ]))

        # again no previous timestamp, but this time after the designated
        # day; should still send newsletter
        del notif_tool.timestamps['weekly']
        friday = datetime(2009, 8, 7, 14, 20) # friday, 14:20
        notif_tool._cron_heartbeat(friday)
        self.failUnlessEqual(self.fetch_test_newsletters(),
            set([ ('weekly', friday - timedelta(weeks=1), friday) ]))

        # previous timestamp is too close; should send nothing
        notif_tool._cron_heartbeat(monday + timedelta(weeks=1))
        self.failUnlessEqual(self.fetch_test_newsletters(), set())

        # after next regular time; should send newsletter
        next_friday = friday + timedelta(weeks=1, hours=-3) # a bit less than one week
        notif_tool._cron_heartbeat(next_friday)
        self.failUnlessEqual(self.fetch_test_newsletters(),
            set([ ('weekly', friday, next_friday) ]))

    def test_monthly(self):
        notif_tool = self.portal.getNotificationTool()

        # monthly notifications are disabled; send nothing
        today = datetime(2009, 8, 3, 14, 20)
        notif_tool._cron_heartbeat(today)
        self.failUnlessEqual(self.fetch_test_newsletters(), set())

        # enable monthly notifications
        notif_tool.config['enable_monthly'] = True

        # no previous timestamp; should send monthly newsletter
        notif_tool._cron_heartbeat(today)
        self.failUnlessEqual(self.fetch_test_newsletters(),
            set([ ('monthly', today - timedelta(days=31), today) ]))

        # again no previous timestamp, but this time after the designated
        # day; should still send newsletter
        del notif_tool.timestamps['monthly']
        this_month = datetime(2009, 8, 28, 14, 20)
        notif_tool._cron_heartbeat(this_month)
        self.failUnlessEqual(self.fetch_test_newsletters(),
            set([ ('monthly', this_month - timedelta(days=31), this_month) ]))

        # previous timestamp is too close; should send nothing
        notif_tool._cron_heartbeat(today + timedelta(days=30))
        self.failUnlessEqual(self.fetch_test_newsletters(), set())

        # after next regular time; should send newsletter
        one_month_later = this_month + timedelta(days=26) # a bit less than one month
        notif_tool._cron_heartbeat(one_month_later)
        self.failUnlessEqual(self.fetch_test_newsletters(),
            set([ ('monthly', this_month, one_month_later) ]))

class NotificationsUiApiTest(BaseNotificationsTest):
    """ test the API exposed by NotificationTool to UI code """

    def assertRaisesWithMessage(self, exc, msg, *args):
        try:
            args[0](*args[1:])
            self.fail('Should have raised exception "%s"' % str(exc))
        except exc, e:
            self.assertTrue(str(msg) in str(e), 'Exception raised but message is wrong: '
                '%s not in %s' % (repr(msg), repr(str(e))))

    def test_add_account_subscription(self):
        notif_tool = self.portal.getNotificationTool()

        self.assertRaisesWithMessage(ValueError, ('Notifications of type "${type}" not allowed', {'type': 'instant'}, ),
            self.add_account_subscription, 'user1', '', 'instant', 'en')
        self.assertRaisesWithMessage(ValueError, ('Notifications of type "${type}" not allowed', {'type': 'weekly'}, ),
            self.add_account_subscription, 'user2', 'fol1', 'weekly', 'en')

        notif_tool.config['enable_instant'] = True
        self.add_account_subscription('user1', '', 'instant', 'en')

        notif_tool.config['enable_weekly'] = True
        self.add_account_subscription('user2', 'fol1', 'weekly', 'en')

        subs = self.walk_site_subscriptions()
        self.assertEqual(len(subs), 2)
        self.assertEqual(subs, set([
            ('user1', '', 'instant', 'en'),
            ('user2', 'fol1', 'weekly', 'en'), ]))

    def test_remove_subscription(self):
        notif_tool = self.portal.getNotificationTool()

        notif_tool.config['enable_weekly'] = True

        notif_tool.add_account_subscription('user1', 'fol1', 'weekly', 'en')
        self.assertEqual(self.walk_site_subscriptions(), set([
            ('user1', 'fol1', 'weekly', 'en'),
        ]))

        notif_tool.remove_account_subscription('user1', 'fol1', 'weekly', 'en')
        self.assertEqual(self.walk_site_subscriptions(), set())

        self.assertRaisesWithMessage(ValueError, 'Subscription not found',
            notif_tool.remove_account_subscription,
            'user1', 'fol1', 'weekly', 'en')

    def test_allowed_notif_types(self):
        notif_tool = self.portal.getNotificationTool()

        self.assertEqual(list(notif_tool.available_notif_types(location='')), [])

        notif_tool.config['enable_instant'] = True
        self.assertEqual(list(notif_tool.available_notif_types(location='')),
            ['instant'])

        notif_tool.config['enable_daily'] = True
        self.assertEqual(list(notif_tool.available_notif_types(location='')),
            ['instant', 'daily'])

        notif_tool.config['enable_weekly'] = True
        self.assertEqual(list(notif_tool.available_notif_types(location='')),
            ['instant', 'daily', 'weekly'])

        notif_tool.config['enable_monthly'] = True
        self.assertEqual(list(notif_tool.available_notif_types(location='')),
            ['instant', 'daily', 'weekly', 'monthly'])

        notif_tool.config['enable_weekly'] = False
        self.assertEqual(list(notif_tool.available_notif_types(location='fol1')),
            ['instant', 'daily', 'monthly'])

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NotificationsUnitTest))
    suite.addTest(makeSuite(NotificationsRestrictedUnitTest))
    suite.addTest(makeSuite(NotificationsCronUnitTest))
    suite.addTest(makeSuite(NotificationsUiApiTest))
    return suite
