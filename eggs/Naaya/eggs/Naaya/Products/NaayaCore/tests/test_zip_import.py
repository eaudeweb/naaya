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
from Products.Naaya.NyFolder import addNyFolder
from Products.NaayaCore.EmailTool import EmailTool

def load_file(filename):
    import os
    from StringIO import StringIO
    from Globals import package_home
    filename = os.path.sep.join([package_home(globals()), filename])
    data = StringIO(open(filename, 'rb').read())
    data.filename = os.path.basename(filename)
    return data

zip_one_file = load_file('./data/one_file_zip.zip')
folder_with_files = load_file('./data/folder_with_files_zip.zip')
complicated_zip = load_file('./data/complicated_zip.zip')
mac_zip = load_file('./data/mac_zip.zip')
spaces_zip = load_file('./data/Spaces in filename_zip.zip')

class NyZipImport(NaayaTestCase):
    """ TestCase for Naaya CSV import """

    def afterSetUp(self):
        addNyFolder(self.portal, 'zip_imported',
                    contributor='contributor', submitted=1)
        self.test_folder = self.portal['zip_imported']

    def beforeTearDown(self):
        self.portal.manage_delObjects(['zip_imported'])

    def assert_same_contents(self, a, b, *args):
        self.assertEqual(set(a), set(b), *args)

    def test_import_ok(self):
        errors = self.test_folder.zip_import.do_import(data=zip_one_file)
        self.assertEqual(errors, [])
        self.assert_same_contents(self.test_folder.objectIds(),
            ['one_file'])

    def test_import_folder_with_files(self):
        errors = self.test_folder.zip_import.do_import(data=folder_with_files)
        self.assertEqual(errors, [])
        self.assert_same_contents(self.test_folder['one_folder'].objectIds(),
            ['one_file', 'three_file', 'two_file'])

    def test_import_complicated(self):
        def get_folder_ids(container):
            return [x.getId() for x in container.objectValues('Naaya Folder')]

        def get_file_ids(container):
            return [x.getId() for x in
                    container.objectValues(['Naaya File', 'Naaya Blob File'])]

        def assert_three_files(container):
            return self.assert_same_contents(get_file_ids(container),
                       ['one_file', 'three_file', 'two_file'])

        errors = self.test_folder.zip_import.do_import(data=complicated_zip)
        self.assertEqual(errors, [])

        self.assert_same_contents(get_folder_ids(self.test_folder),
            ['empty_folder', 'one_folder', 'two_folder'])
        self.assert_same_contents(get_file_ids(self.test_folder),
            ['one_file', 'two_file'])

        container = self.test_folder['empty_folder']
        self.assert_same_contents(container.objectIds(), [])


        container = self.test_folder['one_folder']
        self.assert_same_contents(get_folder_ids(container),
            ['one_empty_subfolder', 'one_subfolder1',
             'one_subfolder3', 'one_subfolder4', 'one_subfolder5'])

        assert_three_files(container)

        assert_three_files(self.test_folder['two_folder'])

        container = self.test_folder['one_folder']['one_empty_subfolder']
        self.assert_same_contents(container.objectIds(), [])

        assert_three_files(self.test_folder['one_folder']['one_subfolder1'])
        assert_three_files(self.test_folder['one_folder']['one_subfolder3'])
        assert_three_files(self.test_folder['one_folder']['one_subfolder4'])
        assert_three_files(self.test_folder['one_folder']['one_subfolder5'])

    def test_import_mac(self):
        errors = self.test_folder.zip_import.do_import(data=mac_zip)
        self.assertEqual(errors, [])
        self.assert_same_contents(self.test_folder.objectIds(),
            ['Picture_1', 'Picture_2'])

    def test_folder_exists(self):
        errors = self.test_folder.zip_import.do_import(data=folder_with_files)
        errors = self.test_folder.zip_import.do_import(data=folder_with_files)
        self.assertEqual(errors, [])

        self.assert_same_contents(self.test_folder.objectIds(),
            ['one_folder', 'one_folder-1'])

        self.assert_same_contents(self.test_folder['one_folder'].objectIds(),
            ['one_file', 'three_file', 'two_file'])

        self.assert_same_contents(self.test_folder['one_folder-1'].objectIds(),
            ['one_file', 'three_file', 'two_file'])

    def test_import_spaces_in_filename(self):
        errors = self.test_folder.zip_import.do_import(data=spaces_zip)
        self.assertEqual(errors, [])
        self.assert_same_contents(self.test_folder.objectIds(), ['one_folder'])
        self.assert_same_contents(self.test_folder['one_folder'].objectIds(),
            ['one_file', 'three_file', 'two_file'])

    def test_import_mails(self):
        diverted_mail = EmailTool.divert_mail()
        self.test_folder.maintainer_email = 'someone@somehost'
        self.test_folder.zip_import.do_import(data=folder_with_files)

        # only the bulk csv import mail should have been sent
        self.assertEqual(len(diverted_mail), 1)

        expected_subject = u'Zip Import - zip_imported'
        expected_body = ('This is automatically generated message to inform '
                         'you that a Zip archive was uploaded in zip_imported '
                         '(http://nohost/portal/zip_imported):\n\n'
                         ' - one_folder/\n'
                         ' - one_folder/one_file\n'
                         ' - one_folder/three_file\n'
                         ' - one_folder/two_file')

        expected_recipients = ['someone@somehost', # folder_maintainer
                               'site.admin@example.com'] # administrator_email
        expected_sender = 'from.zope@example.com'

        mail = diverted_mail[0]
        self.assertTrue(expected_body in mail[0])
        self.assertEqual(expected_recipients, mail[1])
        self.assertEqual(expected_sender, mail[2])
        self.assertEqual(expected_subject, mail[3])
        EmailTool.divert_mail(False)

def test_suite():
    try:
        import naaya.content.bfile
    except ImportError:
        skip = True
    else:
        skip = False

    suite = TestSuite()
    if not skip:
        suite.addTest(makeSuite(NyZipImport))
    return suite


