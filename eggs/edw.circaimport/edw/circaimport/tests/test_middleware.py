import os
import shutil
import tarfile
import tempfile
import zipfile

from Products.Naaya.NyFolder import addNyFolder
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.NaayaCore.NotificationTool.utils import walk_subscriptions
from naaya.content.url.url_item import addNyURL
from naaya.core.zope2util import relative_object_path
from edw.circaimport import ldif_extract, middleware

FIXTURES = os.path.join(os.path.dirname(__file__), 'fixtures')

INDEX = (
    'FILENAME\tTITLE\tABSTRACT\tOWNER\tCREATED\tUPLOADDATE\tKEYWORDS\t'
    'REFERENCE\tSTATUS\tRANKING\r\n'
    'lib/docs/\tDocuments\tMain\talice@circa\t02/03/2009\t\t\t\t\t\r\n'
    'lib/docs/sub/\tSub\t\tbob@circa\t\t\t\t\t\t\r\n'
    'lib/docs/report.dpl/EN_1/report.pdf\tReport\tYearly\talice@circa\t\t'
    '15/06/2010\twater\t\tDraft\tPublic\r\n'
    'lib/docs/sub/caf\xe9.dpl/EN_1/caf\xe9.txt\tCaf\xe9\t\tbob@circa\t\t'
    '00/00/0000\t\t\t\tPublic\r\n'
    'lib/docs/link.dpl/EN_1/link.url\tLink\t\talice@circa\t\t01/01/2012\t'
    '\t\t\tPublic\r\n'
)


class Latin1ZipInfo(zipfile.ZipInfo):
    """Store the member name as latin-1, like the CIRCA exports."""

    def _encodeFilenameFlags(self):
        # without the UTF-8 flag (0x800), which Python 3.14 sets for non-ASCII names
        return self.filename.encode('latin-1'), self.flag_bits & ~0x800


def write_circa_zip(path):
    with zipfile.ZipFile(path, 'w') as zf:
        zf.writestr('index.txt', INDEX.encode('latin-1'))
        zf.writestr('lib/docs/report.dpl/EN_1/report.pdf', b'%PDF data')
        info = Latin1ZipInfo('lib/docs/sub/caf\xe9.dpl/EN_1/caf\xe9.txt',
                             date_time=(2008, 7, 9, 10, 0, 0))
        zf.writestr(info, b'menu')
        zf.writestr('lib/docs/link.dpl/EN_1/link.url',
                    b'[InternetShortcut]\r\nURL=http://example.com/page\r\n')


class CircaImportTestCase(NaayaTestCase):

    def afterSetUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.login()

    def beforeTearDown(self):
        self.logout()
        shutil.rmtree(self.tmp_dir)

    def log_messages(self, cm):
        return [r.getMessage() for r in cm.records]


class ImportFilesTest(CircaImportTestCase):

    def test_import_files_and_folders(self):
        write_circa_zip(os.path.join(self.tmp_dir, 'myig.zip'))
        addNyFolder(self.portal, 'importroot', title='Import root')
        ctx = self.portal['importroot']

        middleware.add_files_and_folders_from_circa_export(
            ctx, 'myig.zip', self.tmp_dir)

        docs = ctx['docs']
        self.assertEqual(docs.title, 'Documents')
        self.assertEqual(docs.contributor, 'alice')
        self.assertEqual(docs.releasedate.strftime('%Y-%m-%d'), '2009-03-02')
        self.assertEqual(docs['sub'].title, 'Sub')

        report = docs['report']
        self.assertEqual(report.meta_type, 'Naaya Blob File')
        self.assertEqual(report.title, 'Report')
        self.assertEqual(report.contributor, 'alice')
        ver = report.current_version
        self.assertEqual(ver.filename, 'report.pdf')
        self.assertEqual(ver.open().read(), b'%PDF data')

        cafe = [ob for ob in docs['sub'].objectValues()
                if ob.title == 'Caf\xe9']
        self.assertEqual(len(cafe), 1)
        ver = cafe[0].current_version
        self.assertEqual(ver.filename, 'caf\xe9.txt')
        self.assertEqual(ver.open().read(), b'menu')
        # bad upload date, the date is read from the zip member
        self.assertEqual(cafe[0].releasedate.strftime('%Y-%m-%d'),
                         '2008-07-09')

        link = docs['link']
        self.assertEqual(link.meta_type, 'Naaya URL')
        self.assertEqual(link.locator, 'http://example.com/page')

    def test_import_member_name_mismatch(self):
        # a member whose file name differs from the index is found by prefix
        index = INDEX.split('\r\n')
        with zipfile.ZipFile(os.path.join(self.tmp_dir, 'myig.zip'),
                             'w') as zf:
            zf.writestr('index.txt',
                        '\r\n'.join(index[:2] + index[3:4] + ['']))
            info = zipfile.ZipInfo('lib/docs/report.dpl/EN_1/report?.pdf',
                                   date_time=(2007, 1, 2, 0, 0, 0))
            zf.writestr(info, b'%PDF renamed')
        addNyFolder(self.portal, 'importroot', title='Import root')
        ctx = self.portal['importroot']
        middleware.add_files_and_folders_from_circa_export(
            ctx, 'myig.zip', self.tmp_dir)
        ver = ctx['docs']['report'].current_version
        self.assertEqual(ver.open().read(), b'%PDF renamed')

    def test_import_rejects_path(self):
        with self.assertRaises(AssertionError):
            middleware.add_files_and_folders_from_circa_export(
                self.portal, '../myig.zip', self.tmp_dir)


class LdifExtractTest(CircaImportTestCase):

    expected_users = {'bob': 'Administrator', 'ghost': 'Contributor'}
    expected_groups = {'staff': 'Contributor'}

    def test_ldif_file(self):
        users, groups = ldif_extract.get_user_and_group_mapping(
            os.path.join(FIXTURES, 'circa.ldif'))
        self.assertEqual(users, self.expected_users)
        self.assertEqual(groups, self.expected_groups)

    def test_tgz_file(self):
        path = os.path.join(self.tmp_dir, 'myig.tgz')
        with tarfile.open(path, 'w:gz') as tar:
            tar.add(os.path.join(FIXTURES, 'circa.ldif'),
                    'myig/ldap/%s.myig.ircnode.ldif'
                    % ldif_extract.CIRCA_CIRCLE_NAME)
        users, groups = ldif_extract.get_user_and_group_mapping(path)
        self.assertEqual(users, self.expected_users)
        self.assertEqual(groups, self.expected_groups)

    def test_bad_extension(self):
        self.assertRaises(ValueError, ldif_extract.LDIFOpener, 'x.txt')

    def test_role_from_classname(self):
        f = ldif_extract.get_role_from_ldif_classname
        self.assertEqual(f('Leader'), 'Administrator')
        self.assertEqual(f('Registered'), 'Authenticated')
        self.assertEqual(f('Unknown'), 'Viewer')


class ImportRolesTest(CircaImportTestCase):

    def add_source(self):
        self.app.acl_users._doAddUser('bob', 'bob', [], [])
        auth_tool = self.portal.getAuthenticationTool()
        auth_tool.manageAddSource('acl_users', 'Root users')

    def test_sources_titles(self):
        self.add_source()
        self.assertEqual(middleware.get_acl_users_sources_titles(self.portal),
                         ['Root users'])

    def test_add_roles(self):
        self.add_source()
        with self.assertLogs('edw.circaimport.ui', 'DEBUG') as cm:
            middleware.add_roles_from_circa_export(
                self.portal, os.path.join(FIXTURES, 'circa.ldif'),
                'Root users')
        self.assertEqual(self.portal.get_local_roles_for_userid('bob'),
                         ('Administrator',))
        messages = self.log_messages(cm)
        self.assertIn('Added role Administrator for user bob', messages)
        self.assertIn('No user named ghost in source Root users', messages)
        # this source can not map groups
        self.assertTrue([m for m in messages
                         if m.startswith("Couldn't add role Contributor "
                                         "for group staff")])

    def test_add_roles_no_source(self):
        with self.assertLogs('edw.circaimport.ui', 'DEBUG') as cm:
            middleware.add_roles_from_circa_export(
                self.portal, os.path.join(FIXTURES, 'circa.ldif'), 'Missing')
        self.assertIn('No user source named Missing', self.log_messages(cm))


class ImportNotificationsAndACLsTest(CircaImportTestCase):

    def afterSetUp(self):
        super(ImportNotificationsAndACLsTest, self).afterSetUp()
        addNyFolder(self.portal, 'library', title='Library')
        addNyFolder(self.portal['library'], 'docs', title='Docs')
        addNyFolder(self.portal['library']['docs'], 'sub', title='Sub')
        addNyURL(self.portal['library']['docs'], 'page', title='Page',
                 locator='http://example.com')

    def test_add_notifications(self):
        notif_tool = self.portal.getNotificationTool()
        notif_tool.config['enable_instant'] = True
        with self.assertLogs('edw.circaimport.ui', 'DEBUG') as cm:
            middleware.add_notifications_from_circa_export(
                self.portal, os.path.join(FIXTURES, 'usernotification.txt'),
                'instant')
        subscriptions = [
            (s.user_id, s.notif_type, relative_object_path(ob, self.portal))
            for ob, n, s in walk_subscriptions(self.portal)]
        self.assertEqual(subscriptions,
                         [('user1', 'instant', 'library/docs')])
        messages = self.log_messages(cm)
        self.assertIn('User not found: ghost', messages)
        self.assertIn('Ignoring (turned off) subscription for user user1 at'
                      ' location /docs/sub', messages)
        self.assertIn("Couldn't find object at path: library/missing",
                      messages)

    def test_add_acls(self):
        with self.assertLogs('edw.circaimport.ui', 'DEBUG') as cm:
            middleware.add_acls_from_circa_export(
                self.portal, os.path.join(FIXTURES, 'itemsacls.txt'))
        messages = self.log_messages(cm)
        self.assertIn('(Deactivated) Granted view on path library/docs for '
                      'user user1', messages)
        self.assertIn('User not found: ghost', messages)
        self.assertIn("Not matched user or profile for ['someone']", messages)
        self.assertIn("Object 'library/docs/page' is not a folder "
                      "(Naaya can only restrict permissions on folders)",
                      messages)
        self.assertIn("Couldn't find object at path: library/missing",
                      messages)
        self.assertIn("Not matched rows (from the exported file): "
                      "['!!! not a row\\n']", messages)
        roles = [m for m in messages if m.startswith(
            '(Deactivated) Granted view on path library/docs for roles')]
        # __7 is the highest profile, mapped to Authenticated
        self.assertEqual(len(roles), 1)
        self.assertIn("'Viewer'", roles[0])
        self.assertIn("'Authenticated'", roles[0])

    def test_add_acls_without_profiles(self):
        path = os.path.join(self.tmp_dir, 'acls.txt')
        with open(path, 'w', encoding='utf-8') as f:
            f.write('/docs\t(user1@circa:1)\n')
        with self.assertLogs('edw.circaimport.ui', 'DEBUG') as cm:
            middleware.add_acls_from_circa_export(self.portal, path)
        self.assertIn('(Deactivated) Granted view on path library/docs for '
                      'user user1', self.log_messages(cm))
