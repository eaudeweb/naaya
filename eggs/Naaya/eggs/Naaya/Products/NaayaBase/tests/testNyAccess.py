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
# Andrei Laza, Eau de Web

# Pythons imports
from unittest import TestSuite, makeSuite

# Zope imports
from Testing import ZopeTestCase
import transaction
from AccessControl import getSecurityManager

# Naaya imports
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.Naaya.NyFolder import addNyFolder
from Products.NaayaBase.NyAccess import NyAccess
from Products.Naaya.NySite import NySite

class NyAccessTestCase(NaayaFunctionalTestCase):
    def afterSetUp(self):
        addNyFolder(self.portal.info, 'testfolder', contributor='admin', submission=1)
        self.portal.info.testfolder._setOb('ny_access', NyAccess(['View', 'View History']))

        transaction.commit()

        self.object = self.portal.info.testfolder

    def beforeTearDown(self):
        self.portal.info.testfolder._delOb('ny_access')
        self.portal.info.manage_delObjects(['testfolder'])

        transaction.commit()

    def test_structure(self):
        self.assertEqual(self.object.ny_access.aq_parent, self.object)

    def test_roles(self):
        set_mapping = {'View': ('Manager',), 'View History': ('Manager', 'Reviewer')}

        # internal test: all the permissions get new values
        self.assertEqual(set(set_mapping.keys()), set(self.object.ny_access.permissions))

        self.object.ny_access.setPermissionMapping(set_mapping)

        got_mapping = self.object.ny_access.getPermissionMapping()

        self.assertEqual(set_mapping, got_mapping)

    def _test_user_perm(self, username, password, permname, value):
        self.browser_do_login(username, password)
        logged_user = getSecurityManager().getUser()
        self.assertEqual(logged_user.getUserName(), username)

        # this is changed to match the _check_context
        # it is based on the structure of the site&zope_app
        # this has to change if the acl_users change
        if isinstance(logged_user.aq_parent.aq_parent, NySite):
            context_object = logged_user.aq_parent.aq_parent.info.testfolder
        else:
            context_object = logged_user.aq_parent.aq_parent.portal.info.testfolder

        self.assertEqual(logged_user._check_context(context_object), 1)

        if value is None:
            self.assertTrue(context_object.checkPermission(permname) is None)
        else:
            self.assertEqual(context_object.checkPermission(permname), value)

        self.browser_do_logout()

    def test_users(self):
        set_mapping = {'View': ('Contributor',), 'View History': ('Contributor', 'Reviewer')}
        self.object.ny_access.setPermissionMapping(set_mapping)

        self._test_user_perm('contributor', 'contributor', 'View', 1)
        self._test_user_perm('reviewer', 'reviewer', 'View', None)

        self._test_user_perm('contributor', 'contributor', 'View History', 1)
        self._test_user_perm('reviewer', 'reviewer', 'View History', 1)

    def test_users_functional(self):
        set_mapping = {'View': ('Contributor',), 'View History': ('Contributor', 'Reviewer')}
        self.object.ny_access.setPermissionMapping(set_mapping)

        self.browser_do_login('admin', '')

        self.browser.go(self.object.absolute_url(1) + '/manage_permissionForm?permission_to_manage=View')
        form = self.browser.get_form(1)
        field = self.browser.get_form_field(form, 'roles:list')
        for item in field.items:
            if item.name == 'Contributor':
                self.assertTrue(item._selected)
            else:
                self.assertFalse(item._selected)

        self.browser.go(self.object.absolute_url(1) + '/manage_permissionForm?permission_to_manage=View%20History')
        form = self.browser.get_form(1)
        field = self.browser.get_form_field(form, 'roles:list')
        for item in field.items:
            if item.name == 'Contributor' or item.name == 'Reviewer':
                self.assertTrue(item._selected)
            else:
                self.assertFalse(item._selected)

        self.browser_do_logout()

    def test_get_permissions(self):
        self.browser_do_login('admin', '')

        self.browser.go(self.object.absolute_url(1) + '/manage_permissionForm?permission_to_manage=View')
        form = self.browser.get_form(1)
        form['roles:list'] = ('Contributor',)
        self.browser.submit()

        self.assertEqual(self.object.ny_access.getPermissionMapping()['View'], ['Contributor'])

        self.browser_do_logout()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NyAccessTestCase))
    return suite
