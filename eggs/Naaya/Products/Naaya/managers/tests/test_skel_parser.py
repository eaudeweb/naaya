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
# Eau de Web

# Python imports
from unittest import TestSuite, makeSuite
from os.path import join, dirname

# Zope imports
import Globals

# Naaya imports
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.managers.skel_parser import skel_parser

class SkelTestCase(NaayaTestCase):
    
    def test_parser(self):
        skel_path = join(dirname(__file__), '../../skel')
        skel_content = self.portal.futRead(join(skel_path, 'skel.xml'), 'r')
        sk, error = skel_parser().parse(skel_content)
        self.assertEqual(error, '')
        self.assertNotEqual(sk.root, None)
        self.assertFalse(isinstance(sk.root.forms, list))
        self.assertTrue(isinstance(sk.root.forms.forms, list))
        self.assertTrue(len(sk.root.forms.forms) > 1)
        self.assertNotEqual(sk.root.forms.forms[1].id, None)
        self.assertEqual(sk.root.layout.skins[0].styles, [])
        self.assertEqual(sk.root.syndication.remotechannels, [])
        self.assertFalse(isinstance(sk.root.others.images, list))
        self.assertNotEqual(sk.root.security, None)
        for role in sk.root.security.roles:
            self.assertNotEqual(role.name, None)
            self.assertNotEqual(role.name, '')
            for permission in role.permissions:
                self.assertNotEqual(permission.name, None)
                self.assertNotEqual(permission.name, '')
    
def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(SkelTestCase))
    return suite