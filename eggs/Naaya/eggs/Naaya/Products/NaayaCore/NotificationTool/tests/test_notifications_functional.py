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

import transaction

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.NaayaCore.NotificationTool.NotificationTool \
    import set_testing_mode as set_notif_testing_mode

from Products.Naaya.NyFolder import addNyFolder
from naaya.content.document.document_item import addNyDocument

class NotificationsTest(NaayaFunctionalTestCase):
    """ functional test for notifications """

    def afterSetUp(self):
        self._notifications = []
        set_notif_testing_mode(True, save_to=self._notifications)
        addNyFolder(self.portal, 'notifol', contributor='contributor', submitted=1)
        addNyDocument(self.portal.notifol, id='notidoc',
            title='Notifying document', submitted=1, contributor='contributor')
        _notif = self.portal.portal_notification
        self._original_config = dict(_notif.config)
        _notif.config['enable_instant'] = True
        _notif.config['enable_daily'] = True
        _notif.config['enable_weekly'] = True
        _notif.config['enable_monthly'] = True
        transaction.commit()

    def beforeTearDown(self):
        _notif = self.portal.portal_notification
        _notif.config.clear()
        _notif.config.update(self._original_config)
        _notif.config.update(self._original_config)
        self.portal.manage_delObjects(['notifol'])
        set_notif_testing_mode(False)
        transaction.commit()

    def _fetch_test_notifications(self):
        notifications = list(self._notifications)
        self._notifications[:] = []
        return notifications

    def test_notify_on_object_upload(self):
        add_subscription = self.portal.portal_notification.add_subscription
        add_subscription('contributor', '', 'instant', 'en')
        add_subscription('admin', '', 'weekly', 'en')
        transaction.commit()

        self.browser_do_login('contributor', 'contributor')

        self.browser.go('http://localhost/portal/notifol/notidoc/edit_html')
        form = self.browser.get_form('frmEdit')

        form['description:utf8:ustring'] = 'i have been changed'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.browser_do_logout()

        self.assertEqual(self._fetch_test_notifications(), [('from.zope@example.com',
            'contrib@example.com', u'Change notification - Notifying document',
            u'This is an automatically generated message to inform you that the item '
            u'"Notifying document" has been edited at '
            'http://localhost/portal/notifol/notidoc by "contributor".')])

        remove_subscription = self.portal.portal_notification.remove_subscription
        remove_subscription('contributor', '', 'instant', 'en')
        remove_subscription('admin', '', 'weekly', 'en')
        transaction.commit()

    def test_notify_with_restricted_obj(self):
        add_subscription = self.portal.portal_notification.add_subscription
        add_subscription('contributor', '', 'instant', 'en')
        add_subscription('reviewer', '', 'instant', 'en')
        self.portal.notifol._View_Permission = ('Reviewer','Manager')
        transaction.commit()

        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/notifol/notidoc/edit_html')
        form = self.browser.get_form('frmEdit')

        form['description:utf8:ustring'] = 'i have been changed'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.browser_do_logout()

        notifications = self._fetch_test_notifications()
        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0][1], 'reviewer@example.com')

        remove_subscription = self.portal.portal_notification.remove_subscription
        remove_subscription('contributor', '', 'instant', 'en')
        remove_subscription('reviewer', '', 'instant', 'en')
        transaction.commit()

    def test_object_rename_hook(self):
        # test is here only because we want to set a "current user" that
        # has "rename" permissions
        notif = self.portal.portal_notification
        notif.add_subscription('contributor', 'notifol',
                                    'instant', 'en')
        notif.add_subscription('reviewer', 'notifol/notidoc',
                                    'weekly', 'en')

        def subscr():
            for s in notif.list_subscriptions():
                yield (s.location, s.notif_type, s.user_id)

        self.assertEqual(set(subscr()),
                         set([ ('notifol', 'instant', 'contributor'),
                               ('notifol/notidoc', 'weekly', 'reviewer') ]))
        transaction.commit()

        # rename the folder using ZMI
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/manage_main')
        form = self.browser.get_form('objectItems')
        form['ids:list'] = ['notifol']
        self.browser.clicked(form, self.browser.get_form_field(form,
                                'manage_renameForm:method'))
        self.browser.submit()
        form = self.browser.get_form(1)
        form['new_ids:list'] = 'newname'
        self.browser.clicked(form, self.browser.get_form_field(form,
                                'manage_renameObjects:method'))
        self.browser.submit()
        self.browser_do_logout()
        # done renaming the folder using ZMI

        self.assertEqual(set(subscr()),
                         set([ ('newname', 'instant', 'contributor'),
                               ('newname/notidoc', 'weekly', 'reviewer') ]))

        notif.remove_subscription('contributor', 'newname',
                                       'instant', 'en')
        notif.remove_subscription('reviewer', 'newname/notidoc',
                                       'weekly', 'en')

        # do our own cleanup, since we renamed the folder
        self.portal.manage_delObjects(['newname'])
        addNyFolder(self.portal, 'notifol', contributor='contributor', submitted=1)
        transaction.commit()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NotificationsTest))
    return suite
