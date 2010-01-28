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
# Valentin Dumitru, Eau de Web

import re
from unittest import TestSuite, makeSuite
from StringIO import StringIO

from Globals import InitializeClass
from Testing import ZopeTestCase
from OFS.SimpleItem import SimpleItem

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.NaayaCore.managers.utils import make_id, genObjectId

class Parent(object):

    def __init__(self, *args):
        for arg in args:
            setattr(self, arg, True)

    def _getOb(self, id, alt):
        return getattr(self, id, alt)

InitializeClass(Parent)

class make_id_TestCase(NaayaFunctionalTestCase):
    """ TestCase for the make_id function """

    def afterSetUp(self):
        pass

    def beforeTearDown(self):
        pass

    def test_by_id(self):
        self.parent = Parent('contact', 'contact-1', 'contact-3')
        id = make_id(self.parent, id='contact', title='bogus', prefix='bogus')
        self.assertEqual(id, 'contact-2')

    def test_by_title(self):
        self.parent = Parent('contact', 'contact-1', 'contact-3')
        id = make_id(self.parent, id='', title='contact', prefix='bogus')
        self.assertEqual(id, 'contact-2')

    def test_by_prefix(self):
        self.parent = Parent('contact', 'contact-1', 'contact-3')
        id = make_id(self.parent, id='', title='', prefix='contact')
        self.assertEqual(id[:-5], 'contact')

    def test_by_nothing(self):
        self.parent = Parent('contact', 'contact-1', 'contact-3')
        id = make_id(self.parent, id='', title='', prefix='')
        self.assertEqual(len(id), 5)

    def test_by_id_with_temp(self):
        self.parent = Parent('contact', 'contact-1', 'contact-3')
        self.temp_parent = Parent('contact-2', 'contact-4', 'contact-6')
        id = make_id(self.parent, temp_parent=self.temp_parent, id='contact', title='bogus', prefix='bogus')
        self.assertEqual(id, 'contact-5')

    def test_by_title_with_temp(self):
        self.parent = Parent('contact', 'contact-1', 'contact-3')
        self.temp_parent = Parent('contact-2', 'contact-4', 'contact-6')
        id = make_id(self.parent, temp_parent=self.temp_parent, id='', title='contact', prefix='bogus')
        self.assertEqual(id, 'contact-5')

    def test_by_prefix_with_temp(self):
        self.parent = Parent('contact', 'contact-1', 'contact-3')
        self.temp_parent = Parent('contact-2', 'contact-4', 'contact-6')
        id = make_id(self.parent, temp_parent=self.temp_parent, id='', title='', prefix='contact')
        self.assertEqual(id[:-5], 'contact')

    def test_by_nothing_with_temp(self):
        self.parent = Parent('contact', 'contact-1', 'contact-3')
        self.temp_parent = Parent('contact-2', 'contact-4', 'contact-6')
        id = make_id(self.parent, temp_parent=self.temp_parent, id='', title='', prefix='')
        self.assertEqual(len(id), 5)

class SlugifyTestCase(ZopeTestCase.TestCase):
    def assert_slug(self, initial_string, expected_slug):
        slug = genObjectId(initial_string)
        self.assertEqual(slug, expected_slug)

    def test_simple(self):
        self.assert_slug('asdf', 'asdf')
        self.assert_slug('here we are', 'here-we-are')
        self.assert_slug('something-else', 'something-else')

    def test_multiple_dashes(self):
        self.assert_slug('-----', '-')
        self.assert_slug('t-----s-', 't-s-')

    def test_latin_1(self):
        self.assert_slug('ab\xe9c\xfc\xe7\xe8de', 'abecucede')

    def test_utf8(self):
        self.assert_slug('ab\xc3\xa9c\xc3\xbc\xc3\xa7\xc3\xa8de', 'abecucede')

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(make_id_TestCase))
    suite.addTest(makeSuite(SlugifyTestCase))
    return suite
