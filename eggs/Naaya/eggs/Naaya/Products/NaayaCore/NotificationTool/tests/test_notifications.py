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

from unittest import TestSuite, makeSuite
from datetime import datetime, timedelta

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.NaayaCore.NotificationTool.NotificationTool import (
    divert_notifications, list_modified_objects)
from Products.NaayaCore.NotificationTool.interfaces import \
    ISubscriptionContainer

from Products.Naaya.NyFolder import addNyFolder
from naaya.content.document.document_item import addNyDocument

class NotificationsTest(NaayaTestCase):
    """ in-portal test for notifications """

    def afterSetUp(self):
        self._notifications = []
        divert_notifications(True, save_to=self._notifications)
        self.notif = self.portal.portal_notification
        self._original_config = dict(self.notif.config)
        self.notif.config['enable_instant'] = True
        self.notif.config['enable_daily'] = True
        self.notif.config['enable_weekly'] = True
        self.notif.config['enable_monthly'] = True
        addNyFolder(self.portal, 'notifol', contributor='contributor', submitted=1)
        addNyDocument(self.portal.notifol, id='notidoc',
            title='Notifying document', submitted=1, contributor='contributor')

    def beforeTearDown(self):
        self.portal.manage_delObjects(['notifol'])
        self.notif.config.clear()
        self.notif.config.update(self._original_config)
        divert_notifications(False)

    def test_get_email(self):
        self.notif.add_account_subscription('contributor', '', 'instant', 'en')
        subscription = list(ISubscriptionContainer(self.portal))[0]
        self.assertEqual(subscription.get_email(self.portal),
                         'contrib@example.com')

    def test_list_modified_objects(self):
        now = datetime.now() + timedelta(hours=1)
        modified_objects = list_modified_objects(
                self.portal, now-timedelta(days=7), now)
        self.failUnless('contact' in (ob.id for ob in modified_objects))

        modified_objects = list_modified_objects(
                self.portal, now, now+timedelta(days=7))
        self.failIf(len(list(modified_objects)) > 0)

    def test_mail_instant(self):
        self.notif.add_account_subscription('contributor', '', 'instant', 'en')
        self.notif.notify_instant(self.portal.info.contact, 'somebody')

        assert self._notifications[0][0] == 'from.zope@example.com'
        assert self._notifications[0][1] == 'contrib@example.com'
        assert self._notifications[0][2] == u'Change notification - Contact us'

        self.notif.remove_account_subscription('contributor',
                                               '', 'instant', 'en')

    def test_mail_weekly(self):
        self.notif.add_account_subscription('contributor',
                                            'notifol', 'weekly', 'en')

        now = datetime.now()
        self.notif._send_newsletter('weekly',
            now-timedelta(days=6), now+timedelta(days=1))
        assert self._notifications[0][0] == 'from.zope@example.com'
        assert self._notifications[0][1] == 'contrib@example.com'
        assert self._notifications[0][2] == u'Changed items - weekly digest'

        self.notif.remove_account_subscription('contributor',
                                               'notifol', 'weekly', 'en')

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NotificationsTest))
    return suite
