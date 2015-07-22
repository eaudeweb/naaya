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
from Products.NaayaCore.NotificationTool.NotificationTool \
    import set_testing_mode as set_notif_testing_mode

from Products.Naaya.NyFolder import addNyFolder
from naaya.content.document.document_item import addNyDocument

class NotificationsTest(NaayaTestCase):
    """ in-portal test for notifications """

    def afterSetUp(self):
        self._notifications = []
        set_notif_testing_mode(True, save_to=self._notifications)
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
        set_notif_testing_mode(False)

    def test_get_user_info(self):
        test_contrib_data = {
            'user_id': 'contributor',
            'full_name': 'Contributor Test',
            'email': 'contrib@example.com',
        }
        contrib_data = self.notif._get_user_info('contributor')
        self.failUnlessEqual(contrib_data, test_contrib_data)

    def test_list_modified_objects(self):
        now = datetime.now() + timedelta(hours=1)
        modified_objects = self.notif._list_modified_objects(now-timedelta(days=7), now)
        self.failUnless('contact' in (ob.id for ob in modified_objects))

        modified_objects = self.notif._list_modified_objects(now, now+timedelta(days=7))
        self.failIf(len(list(modified_objects)) > 0)

    def test_mail_instant(self):
        self.notif.add_subscription('contributor', '', 'instant', 'en')
        self.notif.notify_instant(self.portal.info.contact, 'somebody')

        self.assertEqual(self._notifications, [
            ('from.zope@example.com', 'contrib@example.com',
            u'Change notification - Contact us',
            u'This is an automatically generated message to inform you '
            u'that the item "Contact us" has been created at '
            u'http://nohost/portal/info/contact by "somebody".')])

        self.notif.remove_subscription('contributor', '', 'instant', 'en')

    def test_mail_weekly(self):
        self.notif.add_subscription('contributor', 'notifol', 'weekly', 'en')

        now = datetime.now()
        self.notif._send_newsletter('weekly',
            now-timedelta(days=6), now+timedelta(days=1))
        self.assertEqual(self._notifications, [
            ('from.zope@example.com', 'contrib@example.com',
            u'Changed items - weekly digest',
            u'This is an automatically generated weekly message '
            u'listing modified items in the "portal" portal.\n\n'
            u'notifol (at http://nohost/portal/notifol)\n'
            u'Notifying document (at http://nohost/portal/notifol/notidoc)')])

        self.notif.remove_subscription('contributor', 'notifol', 'weekly', 'en')

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NotificationsTest))
    return suite
