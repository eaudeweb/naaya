import re
from unittest import TestSuite, makeSuite
from StringIO import StringIO

from Globals import InitializeClass
from Testing import ZopeTestCase
from OFS.SimpleItem import SimpleItem

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.NaayaCore.managers.utils import make_id, slugify

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
        slug = slugify(initial_string)
        self.assertEqual(slug, expected_slug)

    def test_simple(self):
        self.assert_slug('asdf', 'asdf')
        self.assert_slug('here we are', 'here-we-are')
        self.assert_slug('something-else', 'something-else')

    def test_multiple_dashes(self):
        self.assert_slug('---covered    wITTh  d4sh3s of fire----',
                         'covered-witth-d4sh3s-fire')
        self.assert_slug('t-----s-', 't-s')

    def test_latin_1(self):
        self.assert_slug(u'ab\xe9c\xfc\xe7\xe8de', 'abecucede')

    def test_utf8(self):
        self.assert_slug(u'ab\xc3\xa9c\xc3\xbc\xc3\xa7\xc3\xa8de', 'aba-c-ca1-4assa-de')

    def test_arabic(self):
        self.assert_slug((u'\u0640\u0622\u0622\u0640\u0627\u0627\u0628\u0640\u0628\u0640'
        u'\u0628\u0628\u062A\u0640\u062A\u0640\u062A\u062A\u062B\u0640\u062B\u0640\u062B'
        u'\u062B\u062C\u0640\u062C\u0640\u062C\u062C\u062D\u0640\u062D\u0640\u062D\u062D'
        u'\u062E\u0640\u062E\u0640\u062E\u062E\u0640\u062F\u062F\u0640\u0630\u0630\u0640'
        u'\u0631\u0631\u0640\u0632\u0632\u0633\u0640\u0633\u0640\u0633\u0633\u0634\u0640'
        u'\u0634\u0640\u0634\u0634\u0635\u0640\u0635\u0640\u0635\u0635\u0636\u0640\u0636'
        u'\u0640\u0636\u0636\u0637\u0640\u0637\u0640\u0637\u0637\u0638\u0640\u0638\u0640'
        u'\u0638\u0638'),
        'aabbbbttttththththjjjjhhhhkhkhkhkhdddhdhrrzzssssshshshshssssddddttttzzzz'.lower())
