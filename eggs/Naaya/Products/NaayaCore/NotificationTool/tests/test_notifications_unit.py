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

from Testing.ZopeTestCase import TestCase
from Products.NaayaCore.NotificationTool.NotificationTool \
    import set_testing_mode as set_notif_testing_mode
from Products.NaayaCore.NotificationTool.NotificationTool import NotificationTool

class TestObject(namedtuple('TestObject', 'title path modif_datetime')):
    def get_path_in_site(self):
        return self.path
    def title_or_id(self):
        return self.title

class TestedNotificationTool(NotificationTool):
    """
    subclass of NotificationTool that saves messages to a list instead
    of sending them
    """
    def __init__(self, *args, **kwargs):
        self._objects = []
        super(TestedNotificationTool, self).__init__(*args, **kwargs)

    def _get_user_info(self, user_id):
        return {
            'user_id': user_id,
            'full_name': 'Test User',
            'email': '%s@example.com' % user_id,
        }

    def _list_modified_objects(self, when_start, when_end):
        for ob in self._objects:
            if when_start < ob.modif_datetime < when_end:
                yield ob

    def _get_template(self, template_name):
        def single_tmpl(ob, person):
            return {'subject': 'notifications',
                'body_text': 'instant [%s]' % ob.path}

        def group_tmpl(items):
            keyer = lambda item: item['ob'].path
            sorted_items = sorted(items, key=keyer)
            items_str = ''.join('[%s]' % item['ob'].path for item in sorted_items)
            body = '%s %s' % (template_name, items_str)
            return {'subject': 'notifications', 'body_text': body}

        if template_name == 'instant':
            return single_tmpl
        else:
            return group_tmpl

    def _get_email_tool(self):
        class MockEmailTool(object):
            def _get_from_address(self):
                return 'notif@example.com'
        return MockEmailTool()

class NotificationsUnitTest(TestCase):
    """ unit test for notifications """

    def afterSetUp(self):
        self.notif = TestedNotificationTool('notif', 'NotificationTool')
        self.notif.config['enable_instant'] = True
        self.notif.config['enable_daily'] = True
        self.notif.config['enable_weekly'] = True
        self.notif.config['enable_monthly'] = True
        self._notifications = []
        set_notif_testing_mode(True, save_to=self._notifications)

    def beforeTearDown(self):
        set_notif_testing_mode(False)
        del self.notif

    def _fetch_test_notifications(self):
        notifications = list(self._notifications)
        self._notifications[:] = []
        return notifications

    def test_add_subscription(self):
        self.notif.add_subscription('gigel', '', 'instant', 'en')
        self.notif.add_subscription('user2', '', 'instant', 'en')

        self.assertEqual(set(self.notif.list_subscriptions()), set([
            ('gigel', '', 'instant', 'en'), ('user2', '', 'instant', 'en'),
        ]))
        self.assertEqual(set(self.notif.list_subscriptions('gigel')), set([
            ('gigel', '', 'instant', 'en'),
        ]))

    def test_weekly_notification_interval(self):
        self.notif.add_subscription('user1', '', 'weekly', 'en')
        self.notif.add_subscription('user2', '', 'weekly', 'en')

        self.notif._objects = [
            TestObject('doc_a', 'fol1/doc_a', datetime(2009, 7, 16)),
            TestObject('doc_b', 'fol1/doc_b', datetime(2009, 8, 3)),
        ]

        self.notif._send_newsletter('weekly',
            datetime(2009, 7, 30), datetime(2009, 8, 5))
        self.assertEqual(set(self._fetch_test_notifications()), set([
            ('notif@example.com', 'user1@example.com', 'notifications',
                'weekly [fol1/doc_b]'),
            ('notif@example.com', 'user2@example.com', 'notifications',
                'weekly [fol1/doc_b]'),
        ]))

    def test_notification_type_checking(self):
        self.notif.add_subscription('user1', 'fol1', 'instant', 'en')
        self.notif.add_subscription('user2', 'fol1', 'daily', 'en')
        self.notif.add_subscription('user3', 'fol1', 'weekly', 'en')

        self.notif._objects = [
            TestObject('doc_a', 'fol1/doc_a', datetime(2009, 7, 16)),
            TestObject('doc_b', 'fol1/doc_b', datetime(2009, 8, 3)),
        ]

        self.notif._send_newsletter('daily',
            datetime(2009, 7, 30), datetime(2009, 8, 5))
        self.assertEqual(set(self._fetch_test_notifications()), set([
            ('notif@example.com', 'user2@example.com', 'notifications',
                'daily [fol1/doc_b]'),
        ]))

        self.notif._send_newsletter('weekly',
            datetime(2009, 7, 30), datetime(2009, 8, 5))
        self.assertEqual(set(self._fetch_test_notifications()), set([
            ('notif@example.com', 'user3@example.com', 'notifications',
                'weekly [fol1/doc_b]'),
        ]))

        self.notif._send_newsletter('monthly',
            datetime(2009, 7, 30), datetime(2009, 8, 5))
        self.assertEqual(set(self._fetch_test_notifications()), set())

    def test_weekly_notification_paths(self):
        self.notif.add_subscription('user1', 'fol1', 'weekly', 'en')
        self.notif.add_subscription('user2', 'fol2', 'weekly', 'en')
        self.notif.add_subscription('user3', '', 'weekly', 'en')

        self.notif._objects = [
            TestObject('doc_a', 'fol1/doc_a', datetime(2009, 8, 3)),
            TestObject('doc_b', 'fol2/doc_b', datetime(2009, 8, 3)),
            TestObject('doc_c', 'doc_c', datetime(2009, 8, 3)),
        ]

        self.notif._send_newsletter('weekly',
            datetime(2009, 7, 30), datetime(2009, 8, 5))
        self.assertEqual(set(self._fetch_test_notifications()), set([
            ('notif@example.com', 'user1@example.com', 'notifications',
                'weekly [fol1/doc_a]'),
            ('notif@example.com', 'user2@example.com', 'notifications',
                'weekly [fol2/doc_b]'),
            ('notif@example.com', 'user3@example.com', 'notifications',
                'weekly [doc_c][fol1/doc_a][fol2/doc_b]'),
        ]))

    def test_instant_notifications(self):
        self.notif.add_subscription('user1', 'fol1', 'instant', 'en')
        self.notif.add_subscription('user2', 'fol2', 'instant', 'en')
        self.notif.add_subscription('user3', '', 'instant', 'en')

        ob = TestObject('doc_a', 'fol1/doc_a', datetime(2009, 8, 3))
        self.notif.notify_instant(ob, 'somebody')
        self.assertEqual(set(self._fetch_test_notifications()), set([
            ('notif@example.com', 'user1@example.com', 'notifications',
                'instant [fol1/doc_a]'),
            ('notif@example.com', 'user3@example.com', 'notifications',
                'instant [fol1/doc_a]'),
        ]))

class CronTestedNotificationTool(NotificationTool):
    """
    subclass of NotificationTool that inercepts and logs newsletter calls
    """
    def __init__(self, *args, **kwargs):
        self._newsletters = []
        super(CronTestedNotificationTool, self).__init__(*args, **kwargs)

    def _send_newsletter(self, notif_type, when_start, when_end):
        self._newsletters.append( (notif_type, when_start, when_end) )

    def fetch_test_newsletters(self):
        newsletters = self._newsletters
        self._newsletters = []
        return newsletters

class NotificationsCronUnitTest(TestCase):
    """ unit test for notifications """

    def afterSetUp(self):
        self.notif = CronTestedNotificationTool('notif', 'NotificationTool')
        self.notif.config['daily_hour'] = 10
        self.notif.config['weekly_hour'] = 10
        self.notif.config['weekly_day'] = 3
        self.notif.config['monthly_hour'] = 10
        self.notif.config['monthly_day'] = 17

    def beforeTearDown(self):
        del self.notif

    def test_daily(self):
        # daily notifications are disabled; send nothing
        today = date(2009, 8, 3)
        self.notif._cron_heartbeat(datetime.combine(today, time(7, 15)))
        self.failUnlessEqual(set(self.notif.fetch_test_newsletters()), set())

        # enable daily notifications
        self.notif.config['enable_daily'] = True

        # no previous timestamp; should send daily newsletter
        today_7_15 = datetime.combine(today, time(7, 15))
        self.notif._cron_heartbeat(today_7_15)
        self.failUnlessEqual(set(self.notif.fetch_test_newsletters()),
            set([ ('daily', today_7_15 - timedelta(days=1), today_7_15) ]))

        # again no previous timestamp, but this time after the designated
        # hour; should still send newsletter
        del self.notif.timestamps['daily']
        today_15_26 = datetime.combine(today, time(15, 26))
        self.notif._cron_heartbeat(today_15_26)
        self.failUnlessEqual(set(self.notif.fetch_test_newsletters()),
            set([ ('daily', today_15_26 - timedelta(days=1), today_15_26) ]))

        # previous timestamp is too close; should send nothing
        self.notif._cron_heartbeat(datetime.combine(today, time(18, 10)))
        self.failUnlessEqual(set(self.notif.fetch_test_newsletters()), set())

        # after next regular time; should send newsletter
        tomorrow_10_15 = datetime.combine(today + timedelta(days=1), time(10, 15))
        self.notif._cron_heartbeat(tomorrow_10_15)
        self.failUnlessEqual(set(self.notif.fetch_test_newsletters()),
            set([ ('daily', today_15_26, tomorrow_10_15) ]))

    def test_weekly(self):
        # weekly notifications are disabled; send nothing
        monday = datetime(2009, 8, 3, 15, 35) # monday, 15:35
        self.notif._cron_heartbeat(monday)
        self.failUnlessEqual(set(self.notif.fetch_test_newsletters()), set())

        # enable weekly notifications
        self.notif.config['enable_weekly'] = True

        # no previous timestamp; should send weekly newsletter
        self.notif._cron_heartbeat(monday)
        self.failUnlessEqual(set(self.notif.fetch_test_newsletters()),
            set([ ('weekly', monday - timedelta(weeks=1), monday) ]))

        # again no previous timestamp, but this time after the designated
        # day; should still send newsletter
        del self.notif.timestamps['weekly']
        friday = datetime(2009, 8, 7, 14, 20) # friday, 14:20
        self.notif._cron_heartbeat(friday)
        self.failUnlessEqual(set(self.notif.fetch_test_newsletters()),
            set([ ('weekly', friday - timedelta(weeks=1), friday) ]))

        # previous timestamp is too close; should send nothing
        self.notif._cron_heartbeat(monday + timedelta(weeks=1))
        self.failUnlessEqual(set(self.notif.fetch_test_newsletters()), set())

        # after next regular time; should send newsletter
        next_friday = friday + timedelta(weeks=1, hours=-3) # a bit less than one week
        self.notif._cron_heartbeat(next_friday)
        self.failUnlessEqual(set(self.notif.fetch_test_newsletters()),
            set([ ('weekly', friday, next_friday) ]))

    def test_monthly(self):
        # monthly notifications are disabled; send nothing
        today = datetime(2009, 8, 3, 14, 20)
        self.notif._cron_heartbeat(today)
        self.failUnlessEqual(set(self.notif.fetch_test_newsletters()), set())

        # enable monthly notifications
        self.notif.config['enable_monthly'] = True

        # no previous timestamp; should send monthly newsletter
        self.notif._cron_heartbeat(today)
        self.failUnlessEqual(set(self.notif.fetch_test_newsletters()),
            set([ ('monthly', today - timedelta(days=31), today) ]))

        # again no previous timestamp, but this time after the designated
        # day; should still send newsletter
        del self.notif.timestamps['monthly']
        this_month = datetime(2009, 8, 28, 14, 20)
        self.notif._cron_heartbeat(this_month)
        self.failUnlessEqual(set(self.notif.fetch_test_newsletters()),
            set([ ('monthly', this_month - timedelta(days=31), this_month) ]))

        # previous timestamp is too close; should send nothing
        self.notif._cron_heartbeat(today + timedelta(days=30))
        self.failUnlessEqual(set(self.notif.fetch_test_newsletters()), set())

        # after next regular time; should send newsletter
        one_month_later = this_month + timedelta(days=26) # a bit less than one month
        self.notif._cron_heartbeat(one_month_later)
        self.failUnlessEqual(set(self.notif.fetch_test_newsletters()),
            set([ ('monthly', this_month, one_month_later) ]))

class NotificationsUiApiTest(TestCase):
    """ test the API exposed by NotificationTool to UI code """

    def afterSetUp(self):
        self.notif = NotificationTool('notif', 'NotificationTool')

    def beforeTearDown(self):
        del self.notif

    def assertRaisesWithMessage(self, exc, msg, *args):
        try:
            args[0](*args[1:])
            self.fail('Should have raised exception "%s"' % str(exc))
        except exc, e:
            self.assertTrue(msg in str(e), 'Exception raised but message is wrong: '
                '%s not in %s' % (repr(msg), repr(str(e))))

    def test_add_subscription(self):
        self.assertRaisesWithMessage(ValueError, 'Notifications of type "instant" not allowed',
            self.notif.add_subscription, 'user1', '', 'instant', 'en')
        self.assertRaisesWithMessage(ValueError, 'Notifications of type "weekly" not allowed',
            self.notif.add_subscription, 'user2', 'fol1', 'weekly', 'en')

        self.notif.config['enable_instant'] = True
        self.notif.add_subscription('user1', '', 'instant', 'en')

        self.notif.config['enable_weekly'] = True
        self.notif.add_subscription('user2', 'fol1', 'weekly', 'en')

        self.assertEqual(set(self.notif.list_subscriptions()), set([
            ('user1', '', 'instant', 'en'), ('user2', 'fol1', 'weekly', 'en'),
        ]))

    def test_remove_subscription(self):
        self.notif.config['enable_weekly'] = True

        self.notif.add_subscription('user1', 'fol1', 'weekly', 'en')
        self.assertEqual(set(self.notif.list_subscriptions()), set([
            ('user1', 'fol1', 'weekly', 'en'),
        ]))

        self.notif.remove_subscription('user1', 'fol1', 'weekly', 'en')
        self.assertEqual(set(self.notif.list_subscriptions()), set())

        self.assertRaisesWithMessage(ValueError, 'Subscription not found',
            self.notif.remove_subscription, 'user1', 'fol1', 'weekly', 'en')

    def test_list_subscriptions(self):
        self.notif.config['enable_instant'] = True
        self.notif.config['enable_daily'] = True

        self.notif.add_subscription('user1', 'fol1', 'instant', 'en')
        self.notif.add_subscription('user1', '', 'daily', 'en')
        self.notif.add_subscription('user2', 'fol1', 'daily', 'en')
        self.notif.add_subscription('user2', 'fol2', 'instant', 'en')

        def list_subscriptions(**kwargs):
            return set(self.notif.list_subscriptions(**kwargs))

        self.assertEqual(list_subscriptions(), set([
            ('user1', 'fol1', 'instant', 'en'), ('user1', '', 'daily', 'en'),
            ('user2', 'fol1', 'daily', 'en'), ('user2', 'fol2', 'instant', 'en'),
        ]))

        self.assertEqual(list_subscriptions(user_id='user1'), set([
            ('user1', 'fol1', 'instant', 'en'), ('user1', '', 'daily', 'en'),
        ]))

        self.assertEqual(list_subscriptions(notif_type='daily'), set([
            ('user1', '', 'daily', 'en'), ('user2', 'fol1', 'daily', 'en'),
        ]))

        self.assertEqual(list_subscriptions(location='fol1'), set([
            ('user1', 'fol1', 'instant', 'en'), ('user2', 'fol1', 'daily', 'en'),
        ]))

        self.assertEqual(list_subscriptions(location='fol1', inherit_location=True), set([
            ('user1', 'fol1', 'instant', 'en'), ('user1', '', 'daily', 'en'),
            ('user2', 'fol1', 'daily', 'en'),
        ]))

    def test_allowed_notif_types(self):
        self.assertEqual(list(self.notif.available_notif_types(location='')), [])

        self.notif.config['enable_instant'] = True
        self.assertEqual(list(self.notif.available_notif_types(location='')),
            ['instant'])

        self.notif.config['enable_daily'] = True
        self.assertEqual(list(self.notif.available_notif_types(location='')),
            ['instant', 'daily'])

        self.notif.config['enable_weekly'] = True
        self.assertEqual(list(self.notif.available_notif_types(location='')),
            ['instant', 'daily', 'weekly'])

        self.notif.config['enable_monthly'] = True
        self.assertEqual(list(self.notif.available_notif_types(location='')),
            ['instant', 'daily', 'weekly', 'monthly'])

        self.notif.config['enable_weekly'] = False
        self.assertEqual(list(self.notif.available_notif_types(location='fol1')),
            ['instant', 'daily', 'monthly'])

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NotificationsUnitTest))
    suite.addTest(makeSuite(NotificationsCronUnitTest))
    suite.addTest(makeSuite(NotificationsUiApiTest))
    return suite
