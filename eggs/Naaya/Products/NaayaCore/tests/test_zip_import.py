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
# David Batranu, Eau de Web

from unittest import TestSuite, makeSuite
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.tests.NaayaTestCase import load_test_file
from Products.Naaya.NyFolder import addNyFolder

zip_one_file = load_test_file('./data/one_file_zip.zip', globals())
folder_with_files = load_test_file('./data/folder_with_files_zip.zip', globals())
complicated_zip = load_test_file('./data/complicated_zip.zip', globals())
mac_zip = load_test_file('./data/mac_zip.zip', globals())

class NyZipImport(NaayaTestCase):
    """ TestCase for Naaya CSV import """

    def afterSetUp(self):
        addNyFolder(self.portal, 'zip_imported',
                    contributor='contributor', submitted=1)
        self.test_folder = self.portal['zip_imported']

    def beforeTearDown(self):
        self.portal.manage_delObjects(['zip_imported'])

    def test_import_ok(self):
        errors = self.test_folder.zip_import.do_import(data=zip_one_file)
        self.assertEqual(errors, [])
        self.assertEqual(self.test_folder.objectIds(), ['one_file.txt'])

    def test_import_folder_with_files(self):
        errors = self.test_folder.zip_import.do_import(data=folder_with_files)
        self.assertEqual(errors, [])
        self.assertTrue(self.test_folder._getOb('one_folder', False))
        self.assertEqual(self.test_folder['one_folder'].objectIds(),
                        ['one_file.txt', 'three_file.txt', 'two_file.txt'])

    def test_import_complicated(self):
        def get_folder_ids(container):
            return [x.getId() for x in container.objectValues('Naaya Folder')]

        def get_file_ids(container):
            return [x.getId() for x in \
                    container.objectValues(['Naaya File', 'Naaya Blob File'])]

        def assert_three_files(container):
            return self.assertEqual(get_file_ids(container),
                             ['one_file.txt', 'three_file.txt', 'two_file.txt'])
    
        errors = self.test_folder.zip_import.do_import(data=complicated_zip)
        self.assertEqual(errors, [])

        container = self.test_folder['complicated_zip']
        self.assertEqual(get_folder_ids(container),
                         ['empty_folder', 'one_folder', 'two_folder'])
        self.assertEqual(get_file_ids(container),
                         ['one_file.txt', 'two_file.txt'])

        zip_folder = self.test_folder['complicated_zip']
        container = zip_folder['empty_folder']
        self.assertEqual(container.objectIds(), [])


        container = zip_folder['one_folder']
        self.assertEqual(get_folder_ids(container),
                         ['one_empty_subfolder', 'one_subfolder1',
                          'one_subfolder3', 'one_subfolder4', 'one_subfolder5'])

        assert_three_files(container)

        assert_three_files(zip_folder['two_folder'])
        
        container = zip_folder['one_folder']['one_empty_subfolder']
        self.assertEqual(container.objectIds(), [])

        assert_three_files(zip_folder['one_folder']['one_subfolder1'])
        assert_three_files(zip_folder['one_folder']['one_subfolder3'])
        assert_three_files(zip_folder['one_folder']['one_subfolder4'])
        assert_three_files(zip_folder['one_folder']['one_subfolder5'])

    def test_import_mac(self):
        errors = self.test_folder.zip_import.do_import(data=mac_zip)
        self.assertEqual(errors, [])
        container = self.test_folder['mac_zip']
        self.assertEqual(container.objectIds(),
                         ['Picture_1.png', 'Picture_2.png'])


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NyZipImport))
    return suite


