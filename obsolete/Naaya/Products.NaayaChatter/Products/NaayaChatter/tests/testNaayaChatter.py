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
# David Batranu, Eau de Web

from Products.Naaya.tests import NaayaTestCase
from unittest import TestSuite, makeSuite
from Testing import ZopeTestCase

ZopeTestCase.installProduct('NaayaChatter')

class ChatterTests(NaayaTestCase.NaayaTestCase):

    def afterSetUp(self):
        self.login()
        self.portal.manage_addProduct['NaayaChatter'].manage_addChatter(id='chatter')
        self.chatter = self.portal.chatter

    def test_add(self):
        chatters = self.portal.objectValues(['Naaya Chatter'])
        self.failUnlessEqual(len(chatters), 1)
        self.failUnlessEqual(chatters[0].getId(), 'chatter')

    def test_getChatter(self):
        getter = self.chatter.getChatter()
        self.assertEqual(self.chatter is getter, True)

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(ChatterTests))
    return suite
