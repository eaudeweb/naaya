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
# Alex Morega, Eau de Web

from unittest import TestSuite, makeSuite
from naaya.content.talkback.tbconsultation_item import addNyTalkBackConsultation
from Products.Naaya.NyFolder import addNyFolder
from Products.Naaya.tests import NaayaTestCase
from naaya.content.talkback.parser import parse

try:
    set()
except:
    from sets import Set as set

class NaayaContentTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for NaayaContent object
    """
    def afterSetUp(self):
        self.login()

        #plug TalkBack Consultation content type
        self.portal.manage_install_pluggableitem(
            meta_type='Naaya TalkBack Consultation'
        )

        #add the test folder
        addNyFolder(self.portal, id='test_folder')
        self.test_folder = self.portal._getOb('test_folder')

    def beforeTearDown(self):
        self.logout()

    def test_main(self):
        """ Add, Edit and Delete Naaya TalkBack Consultation """
        #add NyConsultation
        addNyTalkBackConsultation(self.test_folder,
                                id='sc1',
                                title='sc1',
                                lang='en')

        addNyTalkBackConsultation(self.test_folder,
                                id='sc1_fr',
                                title='sc1_fr',
                                lang='fr')

        meta = self.test_folder.objectValues(['Naaya TalkBack Consultation'])

        #get added Consultation
        for x in meta:
            if x.getLocalProperty('title', 'en') == 'sc1':
                meta = x
            if x.getLocalProperty('title', 'fr') == 'sc1_fr':
                meta_fr = x

        self.assertEqual(meta.getLocalProperty('title', 'en'), 'sc1')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'sc1_fr')

        #change Consultation title
        meta.saveProperties(title='sc1_edited', lang='en')
        meta_fr.saveProperties(title='sc1_fr_edited', lang='fr')

        self.assertEqual(meta.getLocalProperty('title', 'en'),
                         'sc1_edited')

        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'),
                         'sc1_fr_edited')

        #delete Consultation
        self.test_folder.manage_delObjects([meta.getId(), meta_fr.getId()])

        meta = self.test_folder.objectValues(['Naaya TalkBack Consultation'])
        self.assertEqual(meta, [])

class TestSimpleParsing(NaayaTestCase.NaayaTestCase):
    def assert_parse_ok(self, input_text, expected_output):
        output = parse(''.join(input_text))
        self.failUnless(isinstance(output, list))
        self.failUnlessEqual(len(expected_output), len(output))
        self.failUnlessEqual(set(expected_output), set(output))

    def test_two_paragraphs(self):
        self.assert_parse_ok(
            '<p>This is the first paragraph.</p>\n'
            '<p>This is the second one.</p>\n',
            [
                '<p>This is the first paragraph.</p>',
                '\n<p>This is the second one.</p>\n',
            ]
        )

    def test_grouping(self):
        self.assert_parse_ok(
            '<p>This is the first paragraph.</p>\nblabla\n'
            '<p>This is the second one.</p> and some more stuff\n',
            [
                '<p>This is the first paragraph.</p>',
                '\nblabla\n',
                '<p>This is the second one.</p>',
                ' and some more stuff\n',
            ]
        )

    def test_empty_paragraph(self):
        self.assert_parse_ok(
            '<p>&nbsp;</p>'
            'blah',
            [
                '<p>&nbsp;</p>blah',
            ]
        )

        self.assert_parse_ok(
            '<p> <span>some text</span></p>'
            'etc',
            [
                '<p> <span>some text</span></p>',
                'etc',
            ]
        )

    def test_toplevel_elements(self):
        #self.assert_parse_ok(
            #'<img src="blabla" />'
            #'and some other stuff',
            #[
                #'<img src="blabla" />',
                #'and some other stuff',
            #]
        #)

        #self.assert_parse_ok(
            #'some stuff'
            #'<b>and some other stuff</b>'
            #'some final stuff',
            #[
                #'some stuff<b>and some other stuff</b>some final stuff',
            #]
        #)

        self.assert_parse_ok(
            '<p align="center">&nbsp;</p><br />'
            '<p align="center"><strong>Annex</strong></p>',
            [
                '<p align="center">&nbsp;</p><br /><p align="center"><strong>Annex</strong></p>',
            ]
        )


    def test_headings(self):
        self.assert_parse_ok(
            'blah blah'
            '<h2>the heading</h2>'
            'and next content',
            [
                'blah blah',
                '<h2>the heading</h2>and next content',
            ]
        )

        self.assert_parse_ok(
            '<p><strong>t</strong></p>'
            '<h3>Achievements</h3>'
            '<p>&nbsp;</p>'
            '<p>x</p>',
            [
                '<p><strong>t</strong></p>',
                '<h3>Achievements</h3><p>&nbsp;</p><p>x</p>',
            ]
        )

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NaayaContentTestCase))
    suite.addTest(makeSuite(TestSimpleParsing))
    return suite
