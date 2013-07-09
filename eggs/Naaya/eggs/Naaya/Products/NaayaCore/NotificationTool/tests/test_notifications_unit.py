import re
import mock
from datetime import time, date, datetime, timedelta

import transaction

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.NyFolder import addNyFolder
from Products.NaayaCore.NotificationTool.utils import (
    walk_subscriptions, divert_notifications, get_modified_objects)
from Products.NaayaCore.NotificationTool import constants
from Products.NaayaCore.EmailTool import EmailTool
from naaya.content.document.document_item import addNyDocument
from naaya.core.zope2util import path_in_site

class BaseNotificationsTest(NaayaTestCase):
    def afterSetUp(self):
        notif_tool = self.portal.getNotificationTool()
        self._notif_config = dict(notif_tool.config)
        self._notifications = []
        self._subscriptions_to_remove = []
        self.patches = []
        self.object_timestamps = []

        divert_notifications(True, save_to=self._notifications)
        addNyFolder(self.portal, 'fol1', contributor='contributor')
        addNyFolder(self.portal, 'fol2', contributor='contributor')

        def _get_template(self, template_name):
            """ Replacement for _get_template """
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

        self.patches.append(mock.patch(
            'Products.NaayaCore.NotificationTool.NotificationTool.'
            'NotificationTool._get_template', _get_template))


        def get_modified_objects(site, when_start, when_end):
            for ob_path, modif_datetime in self.object_timestamps:
                if when_start < modif_datetime < when_end:
                    yield site.unrestrictedTraverse(ob_path)

        self.patches.append(mock.patch(
            'Products.NaayaCore.NotificationTool.utils.get_modified_objects',
            get_modified_objects))

        transaction.commit()

        for patch in self.patches: #Apply patches
            patch.start()

    def beforeTearDown(self):
        notif_tool = self.portal.getNotificationTool()
        for args in self._subscriptions_to_remove:
            notif_tool.remove_account_subscription(*args)
        self.portal.manage_delObjects(['fol1', 'fol2'])
        notif_tool.config.update(self._notif_config)
        divert_notifications(False)

        for patch in self.patches: #Remove patches
            patch.stop()

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

    def test_anonymous_account_subscription(self):
        """ Add anonymous notification.
        This sends an email with a confirmation key. Confirm with confirm method
        and verify if subscription is in the container.

        """
        diverted_mail = EmailTool.divert_mail()
        notif_tool = self.portal.getNotificationTool()
        notif_tool.add_anonymous_subscription(email='some@email.com', lang='en',
                                              location='', notif_type='instant',
                                              content_types=[])
        assert diverted_mail[0][1] == ['some@email.com']
        assert diverted_mail[0][2] == 'from.zope@example.com'
        assert diverted_mail[0][0].find('confirm?key=') != -1
        confirm_key = re.search('confirm\?key=(\w+)',
                                    diverted_mail[0][0]).group(1)
        notif_tool.confirm(key=confirm_key)
        for obj, n, sub in walk_subscriptions(self.portal):
            if sub.email == 'some@email.com':
                break
        else:
            raise "No subscription found"
        EmailTool.divert_mail(False)

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
                'weekly [fol1/doc_b] Naaya Test Site'),
            ('from.zope@example.com', 'user2@example.com', 'notifications',
                'weekly [fol1/doc_b] Naaya Test Site'),
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
                'daily [fol1/doc_b] Naaya Test Site'),
        ]))

        notif_tool._send_newsletter('weekly',
            datetime(2009, 7, 30), datetime(2009, 8, 5))
        self.assertEqual(set(self._fetch_test_notifications()), set([
            ('from.zope@example.com', 'user3@example.com', 'notifications',
                'weekly [fol1/doc_b] Naaya Test Site'),
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
                'notifications', 'weekly [fol1/g/doc_a] Naaya Test Site'),
            ('from.zope@example.com', 'user2@example.com',
                'notifications', 'weekly [fol1/h/doc_b] Naaya Test Site'),
            ('from.zope@example.com', 'user3@example.com', 'notifications',
                'weekly [fol1/doc_c][fol1/g/doc_a][fol1/h/doc_b] Naaya Test Site'),
        ]))

    def test_instant_notifications(self):
        notif_tool = self.portal.getNotificationTool()

        self.add_account_subscription('user1', 'fol1', 'instant', 'en')
        self.add_account_subscription('user2', 'fol2', 'instant', 'en')
        self.add_account_subscription('user3', '', 'instant', 'en')

        addNyDocument(self.portal['fol1'], id='doc_a')
        self.portal.fol1.doc_a.approved = True
        self.object_timestamps = [
            ('fol1/doc_a', datetime(2009, 8, 3)),
        ]
        notif_tool.notify_instant(self.portal['fol1']['doc_a'], 'somebody')
        self.assertEqual(set(self._fetch_test_notifications()), set([
            ('from.zope@example.com', 'user1@example.com', 'notifications',
                'instant [fol1/doc_a] Naaya Test Site'),
            ('from.zope@example.com', 'user3@example.com', 'notifications',
                'instant [fol1/doc_a] Naaya Test Site'),
        ]))

    def test_sitemap(self):
        """ make sure sitemap returns the right stuff """

        notif_tool = self.portal.getNotificationTool()
        expected = [{'attributes': {'title': ''},
         'children': [{'attributes': {'title': 'info'},
                       'children': [],
                       'data': {'icon': 'misc_/Naaya/NyFolder.png',
                                'title': 'Information'}}],
         'data': {'title': 'Naaya Test Site', 'icon': 'misc_/Naaya/Site.gif'}}]
        self.assertEqual(notif_tool._sitemap_dict({'node': ''}), expected)
        self.assertEqual(notif_tool._sitemap_dict({'node': 'info'}), [])

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
        self.portal.fol1.doc_a.approved = True
        addNyDocument(self.portal['fol1'], id='doc_b', contributor='admin')
        self.portal.fol1.doc_b.approved = True
        self.portal['fol1']['doc_a']._View_Permission = ('Reviewer',)
        self.portal['fol1']['doc_b']._View_Permission = ('Contributor',)

        notif_tool.notify_instant(self.portal['fol1']['doc_a'], 'somebody')
        notif_tool.notify_instant(self.portal['fol1']['doc_b'], 'somebody')
        notifications = self._fetch_test_notifications()
        self.assertEqual(set(notifications), set([
            ('from.zope@example.com', 'reviewer@example.com',
                'notifications', 'instant [fol1/doc_a] Naaya Test Site'),
            ('from.zope@example.com', 'user2@example.com',
                'notifications', 'instant [fol1/doc_b] Naaya Test Site'),
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
                'weekly [fol1/doc_a] Naaya Test Site'),
            ('from.zope@example.com', 'user2@example.com', 'notifications',
                'weekly [fol1/doc_b] Naaya Test Site'),
        ]))

class NotificationsUnapprovedUnitTest(BaseNotificationsTest):
    """ When an object is created e.g. by a Contributor, and it's not
    approved yet, notifications should not be sent. Rather they should be
    sent when the object becomes approved.

    Tests: #525

    """

    def afterSetUp(self):
        super(NotificationsUnapprovedUnitTest, self).afterSetUp()
        self.portal.getNotificationTool().config.update({
            'enable_instant': True,
            'enable_daily': True,
            'enable_weekly': True,
            'enable_monthly': True,
        })
        transaction.commit()

    def test_instant(self):
        """ Instant notifications for unapproved objects
        When an object is added it calls the
        ``NotificationTool.handle_object_add`` subscriber that sends the
        notifications to the folder maintainers and the notification subribers
        Since we do not call directly that subscriber no notifications will
        be sent. See the tests from ``test_noitifications_functional`` for the
        above case.

        """
        self.add_account_subscription('contributor', 'fol1', 'instant', 'en')

        addNyDocument(self.portal['fol1'], id='doc_a', approved=0,
                      contributor='admin')

        notif_tool = self.portal.getNotificationTool()
        notif_tool.notify_instant(self.portal['fol1']['doc_a'], 'somebody')

        #No notifications should be sent at this point
        self.assertEqual(self._fetch_test_notifications(), [])


    def test_periodic(self):
        notif_tool = self.portal.getNotificationTool()

        self.add_account_subscription('contributor', 'fol1', 'instant', 'en')

        addNyDocument(self.portal['fol1'], id='doc_a', approved=0,
                      contributor='admin')
        self.object_timestamps = [
            ('fol1/doc_a', datetime(2009, 8, 3)),
        ]

        notif_tool._send_newsletter('weekly',
            datetime(2009, 7, 30), datetime(2009, 8, 5))

        self.assertEqual(self._fetch_test_notifications(), [])

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
        p = mock.patch(
            'Products.NaayaCore.NotificationTool.NotificationTool'
            '.NotificationTool._send_newsletter', testing_send_newsletter)
        self.patches.append(p) #This needs to be exited
        p.__enter__()
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

        self.assertRaisesWithMessage(ValueError,
                                     'Subscribing to instant notifications in '
                                     '"Naaya Test Site" not allowed',
            self.add_account_subscription, 'user1', '', 'instant', 'en')
        self.assertRaisesWithMessage(ValueError,
                                     'Subscribing to weekly notifications in '
                                     '"fol1" not allowed',
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

class NotificationsUtilsTest(BaseNotificationsTest):
    """ Testing utility functions of NotificationTool """

    def test_get_modified_objects(self):
        notif_tool = self.portal.getNotificationTool()
        action_logger = self.portal.getActionLogger()
        items = dict(action_logger.items())
        for entry_id, log_entry in items.items(): #clean action logger
            del action_logger[entry_id]

        #Create a few log entries
        action_logger.create(type=constants.LOG_TYPES['approved'],
                             path='info')
        action_logger.create(type=constants.LOG_TYPES['created'],
                             path='fol1')
        action_logger.create(type=constants.LOG_TYPES['modified'],
                             path='fol2')
        #Same as above. `get_modified_objects` should return 3 object
        action_logger.create(type=constants.LOG_TYPES['modified'],
                             path='fol2')

        modified_obj_list = list(get_modified_objects(self.portal,
            (datetime.utcnow() - timedelta(minutes=1)),
            (datetime.utcnow() + timedelta(minutes=1))))

        self.assertEqual(len(modified_obj_list), 3)
