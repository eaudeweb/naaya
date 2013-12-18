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
no_parent_folders = load_file('./data/parent_folders_not_explicit.zip')

class NyZipImport(NaayaTestCase):
    """ TestCase for Naaya CSV import """

    def afterSetUp(self):
        addNyFolder(self.portal, 'zip_imported',
                    contributor='contributor', submitted=1)
        self.test_folder = self.portal['zip_imported']
        self.portal.manage_install_pluggableitem('Naaya Blob File')

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
            ['picture-1', 'picture-2'])

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

    def test_parent_folders_not_explicit(self):
        errors = self.test_folder.zip_import.do_import(data=no_parent_folders)
        self.assertEqual(errors, [])
        self.assert_same_contents(self.test_folder.objectIds(), ['one_folder'])
        one_folder = self.test_folder['one_folder']
        self.assert_same_contents(one_folder.objectIds(), ['second_folder'])
        self.assert_same_contents(one_folder.second_folder.objectIds(),
                                  ['one_file', 'three_file', 'two_file'])

    def test_import_mails(self):
        diverted_mail = EmailTool.divert_mail()
        notification_tool = self.portal.getNotificationTool()
        notification_tool.config['enable_instant'] = True

        self.portal.getNotificationTool().add_account_subscription(
            'contributor', '', 'instant', 'en')
        self.test_folder.maintainer_email = 'someone@somehost'
        self.test_folder.zip_import.do_import(data=folder_with_files)

        self.assertEqual(len(diverted_mail), 3)

        expected_subject = u'Zip Import - zip_imported'
        expected_body = ('This is automatically generated message to inform '
                         'you that a Zip archive was uploaded in zip_imported '
                         '(http://nohost/portal/zip_imported):\n\n'
                         ' - one_folder/\n'
                         ' - one_folder/one_file\n'
                         ' - one_folder/three_file\n'
                         ' - one_folder/two_file')

        expected_recipients = ['site.admin@example.com',# administrator_email
                               'someone@somehost', # folder_maintainer
                               'contrib@example.com'] # subscriber

        expected_sender = 'from.zope@example.com'

        mail = diverted_mail[0]
        self.assertTrue(expected_body in mail[0])
        self.assertEqual(expected_recipients[0], diverted_mail[0][1][0])
        self.assertEqual(expected_recipients[1], diverted_mail[1][1][0])
        self.assertEqual(expected_recipients[2], diverted_mail[2][1][0])
        self.assertEqual(expected_sender, mail[3])
        self.assertEqual(expected_subject, mail[4])
        EmailTool.divert_mail(False)
