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

from datetime import date, timedelta
from unittest import TestSuite, makeSuite

import transaction

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.NaayaCore.NotificationTool.NotificationTool import \
    set_testing_mode as notif_testing_mode
from Products.NaayaForum.NyForum import manage_addNyForum
from Products.NaayaForum.NyForumTopic import addNyForumTopic
from Products.NaayaForum.NyForumMessage import addNyForumMessage

class NotificationsTestCase(NaayaTestCase):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        self._notifications = []
        notif_testing_mode(True, self._notifications)

        manage_addNyForum(self.portal, id='tforum', title='My Forum')
        tforum = self.portal['tforum']
        notif_tool = self.portal.getNotificationTool()
        notif_tool.config['enable_instant'] = True
        notif_tool.config['enable_weekly'] = True
        notif_tool.add_subscription('contributor', 'tforum', 'instant', 'en')
        notif_tool.add_subscription('contributor', 'tforum', 'weekly', 'en')
        transaction.commit()

    def beforeTearDown(self):
        notif_tool = self.portal.getNotificationTool()
        notif_tool.config['enable_instant'] = False
        notif_tool.config['enable_weekly'] = False
        notif_tool.remove_subscription('contributor', 'tforum', 'instant', 'en')
        notif_tool.remove_subscription('contributor', 'tforum', 'weekly', 'en')
        self.portal.manage_delObjects(['tforum'])
        transaction.commit()

        notif_testing_mode(False)

    def test_notify_new_topic(self):
        addNyForumTopic(self.portal['tforum'], id='tt2', title='My Topic')
        notif_tool = self.portal.getNotificationTool()

        # check instant notifications
        self.assertEqual(len(self._notifications), 1,
                         'No instant notification was sent')
        self.assertTrue('Change notification' in self._notifications[0][2])
        self.assertTrue('My Topic' in self._notifications[0][3])
        self._notifications[:] = []

        # check weekly notifications
        notif_tool._send_newsletter('weekly',
                                    date.today() - timedelta(days=4),
                                    date.today() + timedelta(days=3))

        self.assertEqual(len(self._notifications), 1,
                         'No weekly notification was sent')
        self.assertTrue('weekly digest' in self._notifications[0][2])
        self.assertTrue('My Topic' in self._notifications[0][3])
        self._notifications[:] = []

        # check weekly notifications in a different week
        notif_tool._send_newsletter('weekly',
                                    date.today() + timedelta(days=3),
                                    date.today() + timedelta(days=10))
        self.assertEqual(len(self._notifications), 0,
                         'Extra weekly notification was sent')

    def test_notify_new_message(self):
        addNyForumTopic(self.portal['tforum'], id='ttopic', title='My Topic')
        notif_tool = self.portal.getNotificationTool()
        self._notifications[:] = []
        addNyForumMessage(self.portal['tforum']['ttopic'], title='My Message')

        # check instant notifications
        self.assertEqual(len(self._notifications), 1,
                         'No instant notification was sent')
        self.assertTrue('Change notification' in self._notifications[0][2])
        self.assertTrue('My Message' in self._notifications[0][3])
        self._notifications[:] = []

        # check weekly notifications
        notif_tool._send_newsletter('weekly',
                                    date.today() - timedelta(days=4),
                                    date.today() + timedelta(days=3))

        self.assertEqual(len(self._notifications), 1,
                         'No weekly notification was sent')
        self.assertTrue('weekly digest' in self._notifications[0][2])
        self.assertTrue('My Topic' in self._notifications[0][3])
        self.assertTrue('My Message' in self._notifications[0][3])
        self._notifications[:] = []

        # check weekly notifications in a different week
        notif_tool._send_newsletter('weekly',
                                    date.today() + timedelta(days=3),
                                    date.today() + timedelta(days=10))
        self.assertEqual(len(self._notifications), 0,
                         'Extra weekly notification was sent')


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NotificationsTestCase))
    return suite
