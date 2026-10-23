from io import BytesIO
from zipfile import ZipFile

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from Products.Naaya.NyFolder import addNyFolder
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from naaya.content.event.event_item import addNyEvent

from Products.EnviroWindows.EnviroWindowsSite import (
    manage_addEnviroWindowsSite, ZipUploadError)


def make_zip(files):
    data = BytesIO()
    with ZipFile(data, 'w') as zf:
        for name, content in files:
            zf.writestr(name, content)
    data.seek(0)
    return data


class EnviroWindowsSiteTest(NaayaTestCase):

    def setUp(self):
        super(EnviroWindowsSiteTest, self).setUp()
        self.app._delObject(self.portal.getId())
        manage_addEnviroWindowsSite(self.app, 'ew')
        self.portal = self.app['ew']
        addNyFolder(self.portal, 'docs', contributor='admin', submitted=1)
        acl_users = self.portal.acl_users
        acl_users._doAddUser('manager', 'secret', ['Manager'], '', 'Site',
                             'Manager', 'manager@example.com')
        user = acl_users.getUserById('manager').__of__(acl_users)
        self.portal.REQUEST.AUTHENTICATED_USER = user
        newSecurityManager(None, user)

    def tearDown(self):
        noSecurityManager()
        super(EnviroWindowsSiteTest, self).tearDown()

    def test_local_events(self):
        calendar = self.portal.portal_rdfcalendar
        self.assertIn('rdf_cataloged_items', calendar.local_events.read())
        addNyEvent(self.portal.docs, id='fair', title='Fair', lang='en',
                   start_date='10/03/2030', end_date='11/03/2030')
        self.portal.docs.fair.approveThis()
        self.portal.docs.recatalogNyObject(self.portal.docs.fair)
        titles = [e['title'] for e in calendar.get_events(2030, 3)]
        self.assertEqual(titles, ['Fair'])
        self.assertEqual(calendar.get_events(2030, 4), [])

    def test_zip_upload_and_download(self):
        folder = self.portal.docs
        errors = self.portal._zipUploadDocuments(
            folder, make_zip([('report.txt', b'first'),
                              ('notes ț.txt', b'second')]))
        self.assertEqual(errors, [])
        files = folder.objectValues('Naaya Extended File')
        self.assertEqual(sorted(f.title for f in files),
                         ['notes t.txt', 'report.txt'])
        data = self.portal._zipDownloadDocuments(
            'docs', [f.getId() for f in files])
        archive = ZipFile(BytesIO(data))
        contents = {name: archive.read(name) for name in archive.namelist()}
        self.assertEqual(sorted(contents.values()), [b'first', b'second'])

    def test_zip_upload_rejects_folders(self):
        self.assertRaises(ZipUploadError, self.portal._zipUploadDocuments,
                          self.portal.docs, make_zip([('sub/a.txt', b'a')]))
        self.assertRaises(ZipUploadError, self.portal._zipUploadDocuments,
                          self.portal.docs, BytesIO(b'not a zip'))

    def test_import_contacts_from_csv(self):
        csv = ('Title,First name,Last name,Email,Organisation\n'
               ',Ana,Pop,ana@example.com,Primăria\n'
               'Office,,,office@example.com,EEA\n').encode('utf-8')
        self.portal.import_contacts_from_csv(file=BytesIO(csv),
                                             location='docs')
        contacts = {c.title: c for c in
                    self.portal.docs.objectValues('Naaya Contact')}
        self.assertEqual(sorted(contacts), ['Ana Pop', 'Office'])
        self.assertEqual(contacts['Ana Pop'].email, 'ana@example.com')
        self.assertEqual(
            contacts['Ana Pop'].getLocalProperty('organisation', 'en'),
            'Primăria')

    def test_contacts_admin_page(self):
        self.assertIn('Contact - listing', self.portal.admin_contacts_html())
        self.portal.REQUEST.set('section', 'csv')
        html = self.portal.admin_contacts_html()
        self.assertIn('Contacts - CSV import/export', html)
        self.assertIn('import_contacts_from_csv', html)
        self.assertIn('export_contacts_to_csv', html)
        template = self.portal.contacts_csv_template(self.portal.REQUEST)
        self.assertTrue(template.startswith('Title,Description,Coverage'))
