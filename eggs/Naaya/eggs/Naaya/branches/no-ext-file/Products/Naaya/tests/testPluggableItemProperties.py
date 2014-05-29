from unittest import TestSuite

from naaya.content.base import constants
from Products.Naaya.NySite import NySite
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase


class PluggableItemPropertiesTestCase(NaayaFunctionalTestCase):
    """ TestCase for NySite.check_pluggable_item_properties """

    def do_check(self, schema, data, session={}):
        site = self.portal
        def get_pluggable_content():
            return {'Naaya Dummy': {'properties': schema}}
        def getSession(name, default):
            return site.session.get(name, default)

        site.get_pluggable_content = get_pluggable_content
        site.session = session
        site.getSession = getSession
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
