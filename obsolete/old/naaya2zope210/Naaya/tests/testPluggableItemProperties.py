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
from Testing import ZopeTestCase

from Products.NaayaContent import constants
from Products.Naaya.NySite import NySite

class DummyTranslations(object):
    def translate(self, arg1, msg):
        return msg

class DummyNySiteForPropCheck(NySite):
    def __init__(self, attrs, session):
        self.portal_translations = DummyTranslations()
        self.attrs = attrs
        self.session = session

    def getSession(self, name, default):
        return self.session.get(name, default)

    def get_pluggable_content(self):
        return {'Naaya Dummy': {'properties': self.attrs}}

class PluggableItemPropertiesTestCase(ZopeTestCase.TestCase):
    """ TestCase for NySite.check_pluggable_item_properties """

    def afterSetUp(self):
        return
        self.orig_get_pluggable_content = NySite.get_pluggable_content

    def beforeTearDown(self):
        return
        NySite.get_pluggable_content = self.orig_get_pluggable_content

    def do_check(self, schema, data, session={}):
        site = DummyNySiteForPropCheck(schema, session=session)
        return site.check_pluggable_item_properties('Naaya Dummy', **data)

    def test_no_data(self):
        self.failUnlessEqual(self.do_check({}, {}), [])

    def test_missing_parameter(self):
        # TODO: the following is probably not correct behaviour (if a property is
        # mandatory then its absence should be an error)
        template = {'a1': (1, constants.MUST_BE_DATETIME_STRICT, 'errmsg')}
        self.failUnlessEqual(self.do_check(template, {}), [])

    def test_MUST_BE_NONEMPTY(self):
        template = {'a1': (1, constants.MUST_BE_NONEMPTY, 'errmsg')}
        self.failUnlessEqual(self.do_check(template, {'a1': 'xz'}), [])
        self.failUnlessEqual(self.do_check(template, {'a1': ''}), ['errmsg'])
        self.failUnlessEqual(self.do_check(template, {'a1': ' \t\r\n '}), ['errmsg'])

    def test_MUST_BE_DATETIME(self):
        template = {'a1': (1, constants.MUST_BE_DATETIME, 'errmsg')}
        self.failUnlessEqual(self.do_check(template, {'a1': ''}), [])
        self.failUnlessEqual(self.do_check(template, {'a1': '24/12/2008'}), [])
        # let's try some invalid dates
        self.failUnlessEqual(self.do_check(template, {'a1': '24/13/2008'}), ['errmsg'])
        self.failUnlessEqual(self.do_check(template, {'a1': '2008-12-24'}), ['errmsg'])
        self.failUnlessEqual(self.do_check(template, {'a1': 'asdf'}), ['errmsg'])

    def test_MUST_BE_DATETIME_STRICT(self):
        template = {'a1': (1, constants.MUST_BE_DATETIME_STRICT, 'errmsg')}
        self.failUnlessEqual(self.do_check(template, {'a1': '24/12/2008'}), [])
        self.failUnlessEqual(self.do_check(template, {'a1': ''}), ['errmsg'])
        self.failUnlessEqual(self.do_check(template, {'a1': 'asdf'}), ['errmsg'])

    def test_MUST_BE_POSITIV_INT(self):
        template = {'a1': (1, constants.MUST_BE_POSITIV_INT, 'errmsg')}
        self.failUnlessEqual(self.do_check(template, {'a1': '13'}), [])
        self.failUnlessEqual(self.do_check(template, {'a1': '0'}), [])
        self.failUnlessEqual(self.do_check(template, {'a1': '0.13'}), ['errmsg'])
        self.failUnlessEqual(self.do_check(template, {'a1': '-13'}), ['errmsg'])
        self.failUnlessEqual(self.do_check(template, {'a1': ''}), ['errmsg'])
        self.failUnlessEqual(self.do_check(template, {'a1': 'asdf'}), ['errmsg'])

    def test_MUST_BE_POSITIV_FLOAT(self):
        template = {'a1': (1, constants.MUST_BE_POSITIV_FLOAT, 'errmsg')}
        self.failUnlessEqual(self.do_check(template, {'a1': '13'}), [])
        self.failUnlessEqual(self.do_check(template, {'a1': '0'}), [])
        self.failUnlessEqual(self.do_check(template, {'a1': '0.13'}), [])
        self.failUnlessEqual(self.do_check(template, {'a1': '-13'}), []) # TODO: this test should fail!
        self.failUnlessEqual(self.do_check(template, {'a1': ''}), ['errmsg'])
        self.failUnlessEqual(self.do_check(template, {'a1': 'asdf'}), ['errmsg'])

    def test_MUST_BE_CAPTCHA(self):
        template = {'a1': (1, constants.MUST_BE_CAPTCHA, 'errmsg')}
        self.failUnlessEqual(self.do_check(template, {'a1': '123'}, session={'captcha': '123'}), [])
        self.failUnlessEqual(self.do_check(template, {'a1': 'asdf'}, session={'captcha': '123'}), ['errmsg'])

    def test_MUST_BE_FLVFILE(self):
        class DummyFlvFile(object):
            def __init__(self, headers):
                self.headers = headers

        template = {'a1': (1, constants.MUST_BE_FLVFILE, 'errmsg')}
        self.failUnlessEqual(self.do_check(template, {'a1': DummyFlvFile({'content-type': "video/x-flv"})}), [])
        self.failUnlessEqual(self.do_check(template, {'a1': DummyFlvFile({'content-type': "application/x-flash-video"})}), [])
        self.failUnlessEqual(self.do_check(template, {'a1': DummyFlvFile({'content-type': 'some_other'})}), ['errmsg'])
        self.failUnlessEqual(self.do_check(template, {'a1': DummyFlvFile({})}), ['errmsg'])
        self.failUnlessEqual(self.do_check(template, {'a1': None}), ['errmsg'])

    def test_MUST_BE_VIDEOFILE(self):
        template = {'a1': (1, constants.MUST_BE_VIDEOFILE, 'errmsg')}
        # MUST_BE_VIDEOFILE makes no checks whatsoever
        self.failUnlessEqual(self.do_check(template, {'a1': None}), [])

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(PluggableItemPropertiesTestCase))
    return suite
