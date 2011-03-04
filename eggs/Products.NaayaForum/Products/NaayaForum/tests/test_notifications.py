from datetime import date, timedelta
from unittest import TestSuite, makeSuite

import transaction

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.NaayaCore.NotificationTool.utils import \
    divert_notifications
from Products.NaayaForum.NyForum import addNyForum
from Products.NaayaForum.NyForumTopic import addNyForumTopic
from Products.NaayaForum.NyForumMessage import addNyForumMessage

class NotificationsTestCase(NaayaTestCase):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        self._notifications = []
        divert_notifications(True, self._notifications)

        addNyForum(self.portal, id='tforum', title='My Forum')
        tforum = self.portal['tforum']
        addNyForumTopic(tforum, id='ttopic', title='My Topic')
        addNyForumMessage(tforum['ttopic'], id='tmessage', title='My Message')
        notif_tool = self.portal.getNotificationTool()
        notif_tool.config['enable_instant'] = True
        notif_tool.config['enable_weekly'] = True
        notif_tool.add_account_subscription('contributor',
                                            'tforum', 'instant', 'en')
        notif_tool.add_account_subscription('contributor',
                                            'tforum', 'weekly', 'en')
        transaction.commit()

    def beforeTearDown(self):
        notif_tool = self.portal.getNotificationTool()
        notif_tool.config['enable_instant'] = False
        notif_tool.config['enable_weekly'] = False
        notif_tool.remove_account_subscription('contributor',
                                               'tforum', 'instant', 'en')
        notif_tool.remove_account_subscription('contributor',
                                               'tforum', 'weekly', 'en')
        self.portal.manage_delObjects(['tforum'])
        transaction.commit()

        divert_notifications(False)

    def test_notify_new_topic(self):
        addNyForumTopic(self.portal['tforum'], id='tt2', title='My New Topic')
        notif_tool = self.portal.getNotificationTool()

        # check instant notifications
        self.assertEqual(len(self._notifications), 1,
                         'No instant notification was sent')
        self.assertTrue('Change notification' in self._notifications[0][2])
        self.assertTrue('My New Topic' in self._notifications[0][3])
        self._notifications[:] = []

        # check weekly notifications
        notif_tool._send_newsletter('weekly',
                                    date.today() - timedelta(days=4),
                                    date.today() + timedelta(days=3))

        self.assertEqual(len(self._notifications), 1,
                         'No weekly notification was sent')
        self.assertTrue('weekly digest' in self._notifications[0][2])
        self.assertTrue('My New Topic' in self._notifications[0][3])
        self._notifications[:] = []

        # check weekly notifications in a different week
        notif_tool._send_newsletter('weekly',
                                    date.today() + timedelta(days=3),
                                    date.today() + timedelta(days=10))
        self.assertEqual(len(self._notifications), 0,
                         'Extra weekly notification was sent')

    def test_notify_new_message(self):
        addNyForumTopic(self.portal['tforum'],
                        id='newtopic', title='My New Topic')
        notif_tool = self.portal.getNotificationTool()
        self._notifications[:] = []
        addNyForumMessage(self.portal['tforum']['newtopic'],
                          title='My New Message')

        # check instant notifications
        self.assertEqual(len(self._notifications), 1,
                         'No instant notification was sent')
        self.assertTrue('Change notification' in self._notifications[0][2])
        self.assertTrue('My New Message' in self._notifications[0][3])
        self._notifications[:] = []

        # check weekly notifications
        notif_tool._send_newsletter('weekly',
                                    date.today() - timedelta(days=4),
                                    date.today() + timedelta(days=3))

        self.assertEqual(len(self._notifications), 1,
                         'No weekly notification was sent')
        self.assertTrue('weekly digest' in self._notifications[0][2])
        self.assertTrue('My New Topic' in self._notifications[0][3])
        self.assertTrue('My New Message' in self._notifications[0][3])
        self._notifications[:] = []

        # check weekly notifications in a different week
        notif_tool._send_newsletter('weekly',
                                    date.today() + timedelta(days=3),
                                    date.today() + timedelta(days=10))
        self.assertEqual(len(self._notifications), 0,
                         'Extra weekly notification was sent')

    def test_edit_notifications(self):
        self._notifications[:] = []

        topic = self.portal['tforum']['ttopic']
        topic.saveProperties(title=topic.title, description='asdf')

        self.assertEqual(len(self._notifications), 1)
        self._notifications[:] = []

        message = topic['tmessage']
        message.saveProperties(title=message.title, description='qwer')

        self.assertEqual(len(self._notifications), 1)

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NotificationsTestCase))
    return suite
