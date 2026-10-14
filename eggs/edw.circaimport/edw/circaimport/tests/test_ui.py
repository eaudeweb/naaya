import os
import shutil
from unittest import mock

from OFS.SimpleItem import SimpleItem
from Products.Naaya.NyFolder import addNyFolder
from Products.NaayaCore.AuthenticationTool.AuthenticationTool import \
    AuthenticationTool
from Products.NaayaCore.NotificationTool.utils import walk_subscriptions
from edw.circaimport import ui
from edw.circaimport.tests.test_middleware import (
    CircaImportTestCase, FIXTURES, write_circa_zip)


class FakeTemplate(object):
    """Record the options a page template is rendered with."""

    def __init__(self, result=''):
        self.result = result
        self.options = None

    def __of__(self, context):
        return self

    def __call__(self, **options):
        self.options = options
        return self.result


class UIFormatterTest(CircaImportTestCase):

    def afterSetUp(self):
        super(UIFormatterTest, self).afterSetUp()
        self.handlers = list(ui.logger.handlers)

    def beforeTearDown(self):
        ui.logger.handlers[:] = self.handlers
        super(UIFormatterTest, self).beforeTearDown()

    def test_format(self):
        log = ui.init_log_stream()
        ui.logger.info('Added %s for %s', 'role', 'bob')
        ui.logger.critical('Traceback: 100% failed')
        self.assertEqual(log.getvalue().splitlines(), [
            '<span style="color: green">INFO: Added role for bob</span>',
            '<span style="color: red">CRITICAL: Traceback: 100% failed'
            '</span>',
        ])


class ImportViewsTest(CircaImportTestCase):

    def afterSetUp(self):
        super(ImportViewsTest, self).afterSetUp()
        self.handlers = list(ui.logger.handlers)
        patcher = mock.patch.object(ui, 'upload_prefix', self.tmp_dir)
        patcher.start()
        self.addCleanup(patcher.stop)
        for name in os.listdir(FIXTURES):
            shutil.copy(os.path.join(FIXTURES, name), self.tmp_dir)
        write_circa_zip(os.path.join(self.tmp_dir, 'myig.zip'))
        self.app.acl_users._doAddUser('bob', 'bob', [], [])
        self.portal.getAuthenticationTool().manageAddSource('acl_users',
                                                            'Root users')
        self.portal.getNotificationTool().config['enable_instant'] = True
        addNyFolder(self.portal, 'library', title='Library')

    def beforeTearDown(self):
        ui.logger.handlers[:] = self.handlers
        super(ImportViewsTest, self).beforeTearDown()

    def call(self, view_class, context=None, method='POST', **form):
        request = self.portal.REQUEST
        request.environ['REQUEST_METHOD'] = method
        request.form.clear()
        request.form.update(form)
        return view_class(context or self.portal, request)()

    def subscriptions(self):
        return [(s.user_id, s.notif_type)
                for ob, n, s in walk_subscriptions(self.portal)]

    def test_no_upload_prefix(self):
        with mock.patch.object(ui, 'upload_prefix', None):
            for view_class in [ui.ImportAllFromCirca, ui.ImportFilesFromCirca,
                               ui.ImportRolesFromCirca,
                               ui.ImportNotificationsFromCirca,
                               ui.ImportACLsFromCirca]:
                self.assertEqual(self.call(view_class),
                                 'upload prefix not configured')

    def test_import_all_form(self):
        html = self.call(ui.ImportAllFromCirca, method='GET')
        self.assertIn('<h1>Import from CIRCA</h1>', html)
        self.assertIn('<option value="Root users">Root users</option>', html)
        self.assertIn('<option value="instant">instant</option>', html)

    def all_form(self, **extra):
        form = {'filename_files': 'myig.zip',
                'import_files_path': 'library',
                'filename_roles': 'circa.ldif',
                'source_title': 'Root users',
                'filename_notifications': 'usernotification.txt',
                'notif_type': 'instant',
                'filename_acls': 'itemsacls.txt'}
        form.update(extra)
        return form

    def test_import_all(self):
        html = self.call(ui.ImportAllFromCirca, **self.all_form())
        self.assertIn('Added role Administrator for user bob', html)
        self.assertIn('Added subscription for user user1 at location '
                      'library/docs', html)
        self.assertIn('Granted view on path library/docs for user user1',
                      html)
        self.assertNotIn('CRITICAL', html)
        self.assertEqual(self.portal.library.docs.title, 'Documents')
        self.assertEqual(self.portal.get_local_roles_for_userid('bob'),
                         ('Administrator',))
        self.assertEqual(self.subscriptions(), [('user1', 'instant')])

    def test_import_all_report(self):
        html = self.call(ui.ImportAllFromCirca, report='Report',
                         **self.all_form())
        self.assertIn('Added role Administrator for user bob', html)
        self.assertNotIn('CRITICAL', html)
        # report mode rolls back the changes
        self.assertNotIn('docs', self.portal.library.objectIds())
        self.assertEqual(self.portal.get_local_roles_for_userid('bob'), ())
        self.assertEqual(self.subscriptions(), [])

    def test_import_all_error(self):
        html = self.call(ui.ImportAllFromCirca,
                         **self.all_form(filename_files='missing.zip',
                                         filename_roles='',
                                         filename_notifications='',
                                         filename_acls=''))
        self.assertIn('<span style="color: red">CRITICAL: Traceback', html)
        self.assertIn('FileNotFoundError', html)

    def test_import_files(self):
        self.assertIn('Import files and folders from CIRCA',
                      self.call(ui.ImportFilesFromCirca_html,
                                self.portal.library, method='GET'))
        html = self.call(ui.ImportFilesFromCirca, self.portal.library,
                         filename='myig.zip')
        self.assertIn('Added folder:', html)
        self.assertNotIn('CRITICAL', html)
        self.assertEqual(self.portal.library.docs.link.locator,
                         'http://example.com/page')

    def test_import_files_default_name(self):
        os.rename(os.path.join(self.tmp_dir, 'myig.zip'),
                  os.path.join(self.tmp_dir, 'portal.zip'))
        self.call(ui.ImportFilesFromCirca, self.portal.library, filename='')
        self.assertEqual(self.portal.library.docs.title, 'Documents')

    def test_import_roles(self):
        html = self.call(ui.ImportRolesFromCirca, method='GET')
        self.assertIn('Root users', html)
        html = self.call(ui.ImportRolesFromCirca, filename='circa.ldif',
                         source_title='Root users')
        self.assertIn('Added role Administrator for user bob', html)
        self.assertEqual(self.portal.get_local_roles_for_userid('bob'),
                         ('Administrator',))

    def test_import_notifications(self):
        html = self.call(ui.ImportNotificationsFromCirca, method='GET')
        self.assertIn('<option value="instant">instant</option>', html)
        addNyFolder(self.portal.library, 'docs', title='Docs')
        html = self.call(ui.ImportNotificationsFromCirca, notif_type='instant',
                         filename='usernotification.txt')
        self.assertIn('Added subscription for user user1', html)
        self.assertEqual(self.subscriptions(), [('user1', 'instant')])

    def test_import_acls(self):
        html = self.call(ui.ImportACLsFromCirca, method='GET')
        self.assertIn('Import ACLs from CIRCA', html)
        addNyFolder(self.portal.library, 'docs', title='Docs')
        html = self.call(ui.ImportACLsFromCirca, filename='itemsacls.txt')
        self.assertIn('Granted view on path library/docs for user user1',
                      html)


class ZexpViewsTest(CircaImportTestCase):

    def afterSetUp(self):
        super(ZexpViewsTest, self).afterSetUp()
        self.app._setObject('applications', SimpleItem())
        self.app.applications.mail_from = 'from@example.com'
        user = mock.Mock(mail='admin@example.com')
        for target, name, value in [
                (AuthenticationTool, 'get_user_with_userid',
                 mock.Mock(return_value=user)),
                (ui.zexpcopy, 'send_action_completed_mail', mock.Mock()),
                (ui, 'zexpcopy_import_zpt', FakeTemplate()),
                (ui, 'zexpcopy_export_zpt', FakeTemplate())]:
            patcher = mock.patch.object(target, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def call(self, view_class, **form):
        request = self.portal.REQUEST
        request.form.clear()
        request.form.update(form)
        view_class(self.app, request)()
        template = (ui.zexpcopy_import_zpt if view_class is ui.ZImportData
                    else ui.zexpcopy_export_zpt)
        return template.options

    def test_import_missing_file(self):
        options = self.call(ui.ZImportData, submit='Import', ig='portal',
                            location='info',
                            zexp_path=os.path.join(self.tmp_dir, 'x.zexp'))
        self.assertTrue(options['performed'])
        self.assertIn('Can not read file with exported data.',
                      options['error'])
        self.assertIn('No such file or directory', options['error'])
        self.assertEqual(options['new_ids'], [])
        self.assertIn(('portal', 'Naaya Test Site'), options['igs'])

    def test_import_error(self):
        with mock.patch.object(ui.zexpcopy, 'load_zexp',
                               side_effect=ValueError('bad', 'data')):
            options = self.call(ui.ZImportData, submit='Import', ig='portal',
                                location='info', zexp_path='x.zexp')
        self.assertEqual(options['error'], 'Error importing data from zexp '
                         "file: ('bad', 'data')")
        ui.zexpcopy.send_action_completed_mail.assert_called_once_with(
            options['error'], 'from@example.com', 'admin@example.com',
            'Error importing IG Data')

    def test_import(self):
        with mock.patch.object(ui.zexpcopy, 'load_zexp',
                               return_value=['newob']):
            options = self.call(ui.ZImportData, submit='Import', ig='portal',
                                location='info', zexp_path='x.zexp')
        self.assertEqual(options['error'], '')
        self.assertIn('/portal/info/newob', options['info'])

    def test_import_form(self):
        options = self.call(ui.ZImportData)
        self.assertFalse(options['performed'])

    def test_export(self):
        with mock.patch.object(ui.zexpcopy, 'write_zexp',
                               return_value='/tmp/info.zexp'), \
                mock.patch.object(ui.zexpcopy, 'export_completed_message_zpt',
                                  FakeTemplate('Done\nok')):
            options = self.call(ui.ZExportData, submit='Export', ig='portal',
                                location='info')
        self.assertEqual(options['zexp_path'], '/tmp/info.zexp')
        self.assertEqual(options['info'], 'Done<br />\nok')
        self.assertEqual(options['error'], '')

    def test_export_error(self):
        with mock.patch.object(ui.zexpcopy, 'write_zexp',
                               side_effect=IOError('disk full')):
            options = self.call(ui.ZExportData, submit='Export', ig='portal',
                                location='info')
        self.assertEqual(options['error'], "Error while exporting portal IG "
                         "Data: ('disk full',)")
        self.assertEqual(options['zexp_path'], '')
