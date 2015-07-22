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
# Andrei Laza, Eau de Web

#Python imports
from unittest import TestSuite, makeSuite

#Zope imports
import transaction

#Product imports
from Products.Naaya.NyFolder import addNyFolder
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase


class SubscriptionsTest(NaayaFunctionalTestCase):
    """ functional test for subscribing for notifications """

    def afterSetUp(self):
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
        transaction.commit()

    def test_subscribe_instant(self):
        _notif = self.portal.portal_notification
        self.browser_do_login('contributor', 'contributor')

        self.browser.go('http://localhost/portal/notifications_subscribe')

        num_forms_before = len(self.browser.get_all_forms())

        form = self.browser.get_form('subscribe')
        form['notif_type'] = ['instant']
        self.browser.clicked(form, self.browser.get_form_field(form, 'submit'))

        self.browser.submit()

        num_forms_after = len(self.browser.get_all_forms())

        self.assertEqual(num_forms_after, num_forms_before + 1)

        found_form = False
        for form in self.browser.get_all_forms():
            controls = form.controls
            if [c.value for c in controls] == ['', 'instant', 'en', 'unsubscribe']:
                found_form = True
                break
        self.assert_(found_form)

        self.browser_do_logout()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(SubscriptionsTest))
    return suite

