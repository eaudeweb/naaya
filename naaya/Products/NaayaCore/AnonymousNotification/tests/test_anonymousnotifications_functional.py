#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
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
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alexandru Plugaru, Eau de Web

#Python imports
from unittest import TestSuite, makeSuite

#Zope imports
import transaction

#Product imports
from naaya.content.infofolder.InfoFolder import addNyInfoFolder
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from naaya.Products.NaayaCore.AnonymousNotification.AnonymousNotification import AnonymousNotification

class AnonymousNotificationTest(NaayaFunctionalTestCase):
    """ functional test for subscribing for notifications """

    def afterSetUp(self):
        if not hasattr(self.portal, 'portal_anonymous_notification'):
            self.portal._setObject('portal_anonymous_notification', AnonymousNotification('portal_anonymous_notification'))
        _notif = self.portal.portal_notification
        self._original_config = dict(_notif.config)
        _notif.config['enable_instant'] = True
        _notif.config['enable_daily'] = True
        _notif.config['enable_weekly'] = True
        _notif.config['enable_monthly'] = True
        self.portal.manage_install_pluggableitem(meta_type="Naaya InfoFolder") # Install Naaya infoFolder
        transaction.commit()

    def beforeTearDown(self):
        _notif = self.portal.portal_notification
        _notif.config.clear()
        _notif.config.update(self._original_config)
        transaction.commit()

    def test_subscribe_instant(self):
        """ Subscribe unauthenticated user to NotificationTool via submit form"""
        self.browser.go('http://localhost/portal/sdo_notifications_subscribe')
        num_forms_before = len(self.browser.get_all_forms())
        
        form = self.browser.get_form('subscribe')
        form['notif_type'] = ['instant']
        form['email'] = 'contributor@eaudeweb.ro'
        form['organisation'] = 'Eaudeweb'
        self.browser.clicked(form, self.browser.get_form_field(form, 'submit'))

        self.browser.submit()
        self.assertEqual(self.browser.result.http_code, 200)
        
        
        num_forms_after = len(self.browser.get_all_forms())
        
        self.assertEqual(num_forms_after + 1, num_forms_before)
    
    def test_add_confirm_unsubscribe(self):
        """
        Subscribe unauthenticated user to NotificationTool via class method
        Confirm e-mail address
        Then remove subscribtion
        """
        _notif = self.portal.portal_anonymous_notification
        _notif.add_email_subscription(email='contributor@eaudeweb.ro',
            organisation=u'世界您好',
            notif_type='instant',
            sector='Other',
            country='Romania',
            lang='en'
        )
        self.assertRaises(ValueError, _notif.add_email_subscription, email='ale.o',
            organisation='Eau de web',
            notif_type='instant',
            sector='Other',
            country='Romania',
            lang='en'
        )
        transaction.commit()
        subscriber = _notif.subscriptions_temp[0]
        
        self.browser.go('http://localhost/portal/sdo_notifications_subscribe/confirm?key=%s' % subscriber.key)
        self.assertEqual(self.browser.result.http_code, 200)
        self.browser.go('http://localhost/portal/sdo_notifications_subscribe/confirm?key=%s' % subscriber.key)
        self.assertEqual(self.browser.result.http_code, 404) # User cannot confirm 2 time with the same code
        
        self.browser.go('http://localhost/portal/sdo_notifications_subscribe/delete_subscription?email=%s' % subscriber.email)
        self.assertEqual(self.browser.result.http_code, 200)
        self.browser.go('http://localhost/portal/sdo_notifications_subscribe/delete_subscription?email=%s' % subscriber.email)
        self.assertEqual(self.browser.result.http_code, 404) # Cannot delete unexistent subscribtion
def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(AnonymousNotificationTest))
    return suite