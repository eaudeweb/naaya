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

from Products.NaayaContent import discover

class NaayaContentParserTestCase(ZopeTestCase.TestCase):
    """ TestCase for NaayaContent parser of content types """

    def afterSetUp(self):
        self.orig_list_dirs = discover._list_dirs

    def beforeTearDown(self):
        discover._list_dirs = self.orig_list_dirs

    def test_content_listing(self):
        from Products.NaayaContent.NyFile import NyFile as NyFile_module

        content_types = discover._discover_content_types()

    def testParser(self):
        discover._list_dirs = lambda: ['NyFile']
        from Products.NaayaContent.NyFile import NyFile as NyFile_module

        content_types = discover._discover_content_types()

        self.failUnlessEqual(set(content_types.keys()), set(['content', 'constants', 'misc_']))
        self.failUnless(set(content_types['content'].keys()), set(['Naaya File']))

        file_content_type = content_types['content']['Naaya File']
        self.failUnlessEqual(set(file_content_type.keys()), set([
                '_module', 'product', '_class', 'description', 'permission',
                'constructors', 'addform', 'module', 'label', 'forms', 'meta_type',
                'package_path', 'validation', 'properties', 'default_schema']))
        self.failUnlessEqual(file_content_type['product'], 'NaayaContent')
        self.failUnlessEqual(file_content_type['_module'], NyFile_module)
        self.failUnlessEqual(file_content_type['_class'], NyFile_module.NyFile)
        self.failUnlessEqual(file_content_type['description'], 'This is Naaya File type.')
        self.failUnlessEqual(file_content_type['permission'], 'Naaya - Add Naaya File objects')

        self.failUnlessEqual(content_types['constants'], {
            'METATYPE_NYFILE': 'Naaya File',
            'PERMISSION_ADD_NYFILE': 'Naaya - Add Naaya File objects',
            'METATYPE_FOLDER': 'Naaya Folder',
            'PERMISSION_ADD_FOLDER': 'Naaya - Add Naaya Folder objects',
        })

        self.failUnlessEqual(set(content_types['misc_'].keys()), set(['NyFile.gif', 'NyFile_marked.gif']))

    def test_load_misc(self):
        discover._list_dirs = lambda: ['NyMediaFile']
        content_types = discover._discover_content_types()
        self.failUnlessEqual(set(content_types['misc_'].keys()),
            set(['NyMediaFile.gif', 'NyMediaFile_marked.gif', 'EdWideoPlayer.swf',
            'NyMediaFileLoading.gif', 'NyMediaFileBroken.gif']))

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NaayaContentParserTestCase))
    return suite
