import os
import re
from StringIO import StringIO
import urllib

import transaction

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.Naaya.NyFolder import addNyFolder
from naaya.content.bfile.bfile_item import addNyBFile

class BrowserFileTestingMixin(object):
    def make_file(self, filename, content_type, data):
        f = StringIO(data)
        f.filename = filename
        f.headers = {'content-type': content_type}
        return f

    def assertDownload(self, content_type, data, **kwargs):
        self.assertEqual(self.browser.get_code(), 200)
        self.assertEqual(self.browser_get_header('content-length'), str(len(data)))
        self.assertEqual(self.browser_get_header('content-disposition'),
                         'attachment')
        self.assertEqual(self.browser_get_header('content-type'), content_type)
        self.assertEqual(self.browser.get_html(), data)

class NyBFileFunctionalTestCase(NaayaFunctionalTestCase, BrowserFileTestingMixin):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        self.portal.manage_install_pluggableitem('Naaya Blob File')
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)
        addNyBFile(self.portal.myfolder, id='mybfile', title='My file', submitted=1, contributor='contributor')
        transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder'])
        self.portal.manage_uninstall_pluggableitem('Naaya Blob File')
        transaction.commit()

    def test_add(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/bfile_add_html')
        self.failUnless('<h1>Submit File</h1>' in self.browser.get_html())
        form = self.browser.get_form('frmAdd')
        expected_controls = set([
            'lang', 'title:utf8:ustring', 'description:utf8:ustring', 'coverage:utf8:ustring',
            'keywords:utf8:ustring', 'releasedate', 'discussion:boolean',
            'uploaded_file',
        ])
        found_controls = set(c.name for c in form.controls)
        self.failUnless(expected_controls.issubset(found_controls),
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['title:utf8:ustring'] = 'Test File'
        form['description:utf8:ustring'] = 'test_bfile_description'
        form['coverage:utf8:ustring'] = 'test_bfile_coverage'
        form['keywords:utf8:ustring'] = 'keyw1, keyw2'

        TEST_FILE_DATA = 'some data for my file'
        form.find_control('uploaded_file').add_file(StringIO(TEST_FILE_DATA),
            filename='testcreatebfile.txt', content_type='text/plain; charset=utf-8')

        self.browser.submit()
        html = self.browser.get_html()
        self.failUnless('The administrator will analyze your request' in html)

        self.portal.myfolder['test-file'].approveThis()

        self.browser.go('http://localhost/portal/myfolder/test-file')
        html = self.browser.get_html()
        self.failUnless(re.search(r'<h1>.*Test File.*</h1>', html, re.DOTALL))
        self.failUnless('test_bfile_description' in html)
        self.failUnless('test_bfile_coverage' in html)
        self.failUnless('keyw1, keyw2' in html)

        self.browser.go('http://localhost/portal/myfolder/test-file/'
                        'download/1/testcreatebfile.txt')
        self.assertEqual(self.browser.get_code(), 200)
        html = self.browser.get_html()
        headers = self.browser._browser._response._headers
        self.failUnlessEqual(headers.get('content-disposition', None),
                             'attachment')
        self.assertEqual(headers['content-type'], 'text/plain')
        self.failUnlessEqual(html, TEST_FILE_DATA)

        self.browser_do_logout()

    def test_add_error(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/bfile_add_html')

        form = self.browser.get_form('frmAdd')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        # enter no values in the fields
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('The form contains errors' in html)
        self.failUnless('Value required for "Title"' in html)

    def test_edit(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder/mybfile/edit_html')
        form = self.browser.get_form('frmEdit')

        self.failUnlessEqual(form['title:utf8:ustring'], 'My file')

        form['title:utf8:ustring'] = 'New Title'
        TEST_FILE_DATA_2 = 'some new data for my file'
        form.find_control('uploaded_file').add_file(StringIO(TEST_FILE_DATA_2),
            filename='the_new_bfile.txt', content_type='text/plain; charset=latin-1')

        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()
        html = self.browser.get_html()
        self.failUnless('<h1>Edit File</h1>' in html)

        self.failUnlessEqual(self.portal.myfolder.mybfile.title, 'New Title')
        self.portal.myfolder.mybfile.approveThis()

        self.browser.go('http://localhost/portal/myfolder/mybfile/'
                        'download/1/the_new_bfile.txt')
        html = self.browser.get_html()
        headers = self.browser._browser._response._headers
        self.failUnlessEqual(headers.get('content-disposition', None),
                             'attachment')
        self.assertEqual(headers['content-type'], 'text/plain')
        self.failUnlessEqual(html, TEST_FILE_DATA_2)

        self.browser.go('http://localhost/portal/myfolder/mybfile/edit_html?lang=fr')
        form = self.browser.get_form('frmEdit')
        form['title:utf8:ustring'] = 'french_title'
        TEST_FILE_DATA_3 = 'some new data for my file'
        form.find_control('uploaded_file').add_file(StringIO(TEST_FILE_DATA_3),
            filename='the_new_bfile.html', content_type='text/html; charset=utf-8')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.browser.go('http://localhost/portal/myfolder/mybfile/'
                        'download/2/the_new_bfile.html')
        html = self.browser.get_html()
        headers = self.browser._browser._response._headers
        self.failUnlessEqual(headers.get('content-disposition', None),
                             'attachment')
        self.assertEqual(headers['content-type'], 'text/html')
        self.failUnlessEqual(html, TEST_FILE_DATA_3)

        self.failUnlessEqual(self.portal.myfolder.mybfile.title, 'New Title')
        self.failUnlessEqual(self.portal.myfolder.mybfile.getLocalProperty('title', 'fr'), 'french_title')

        self.browser_do_logout()

    def test_edit_remove_versions(self):
        self.browser_do_login('admin', '')

        for c in range(4):
            f = self.make_file('afile', 'text/plain', 'some data')
            self.portal.myfolder['mybfile']._save_file(f,
                                                       contributor='contributor')

        transaction.commit()

        self.browser.go('http://localhost/portal/myfolder/mybfile')
        html = self.browser.get_html()

        self.assertTrue('download/1/afile' in html)
        self.assertTrue('download/2/afile' in html)
        self.assertTrue('download/3/afile' in html)
        self.assertTrue('download/4/afile' in html)

        self.browser.go('http://localhost/portal/myfolder/mybfile/edit_html')
        form = self.browser.get_form('frmEdit')
        form['versions_to_remove:list'] = ['2', '4']
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        mybfile = self.portal.myfolder['mybfile']
        self.assertEqual(mybfile._versions[0].removed, False)
        self.assertEqual(mybfile._versions[1].removed, True)
        self.assertEqual(mybfile._versions[1].removed_by, 'admin')
        self.assertEqual(mybfile._versions[2].removed, False)
        self.assertEqual(mybfile._versions[3].removed_by, 'admin')

        self.browser.go('http://localhost/portal/myfolder/mybfile')
        html = self.browser.get_html()
        self.assertTrue('download/1/afile' in html)
        self.assertTrue('download/2/afile' not in html)
        self.assertTrue('download/3/afile' in html)
        self.assertTrue('download/4/afile' not in html)

        self.browser_do_logout()

    def test_edit_error(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/mybfile/edit_html')

        form = self.browser.get_form('frmEdit')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        form['title:utf8:ustring'] = ''
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('The form contains errors' in html)
        self.failUnless('Value required for "Title"' in html)

        self.browser_do_logout()

    def test_utf8_filenames(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/bfile_add_html')
        form = self.browser.get_form('frmAdd')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        filename = u'un\u00efc\u00f6d\u04d4.txt'.encode('utf-8')
        form.find_control('uploaded_file').add_file(
            StringIO('simple contents'),
            filename=filename,
            content_type='text/plain; charset=utf-8')
        self.browser.submit()

        self.portal.myfolder['unicodae'].approveThis()

        self.browser.go('http://localhost/portal/myfolder/unicodae')
        html = self.browser.get_html()
        self.assertTrue('download/1/%s' % urllib.quote(filename) in html)

        self.browser.go('http://localhost/portal/myfolder/unicodae/'
                        'download/1/%s' % urllib.quote(filename))
        self.assertEqual(self.browser.get_code(), 200)
        html = self.browser.get_html()
        self.failUnlessEqual(self.browser_get_header('content-disposition'),
                             "attachment")
        self.assertEqual(self.browser_get_header('content-type'),
                         'text/plain')
        self.failUnlessEqual(html, 'simple contents')

        self.browser_do_logout()

    def test_view(self):
        """Same as download, but without the attachment header"""

        file_contents = 'simple contents'
        uploaded_file = StringIO(file_contents)
        uploaded_file.filename = 'test.txt'
        uploaded_file.headers = {'content-type': 'text/plain; charset=utf-8'}

        addNyBFile(self.portal.myfolder, submitted=1,
                   contributor='contributor', id='test', title="test",
                   uploaded_file=uploaded_file, approved=True)
        transaction.commit()
        #View the file
        self.browser.go('http://localhost/portal/myfolder/test/download/1/test.txt?action=view')
        self.assertEqual(file_contents, self.browser.get_html())

    def test_direct_download(self):
        """ In folder listing we should have a download link that allows users
        to download the last version directly

        """
        file_contents = 'simple contents'
        uploaded_file = StringIO(file_contents)
        uploaded_file.filename = 'test.txt'
        uploaded_file.headers = {'content-type': 'text/plain; charset=utf-8'}

        addNyBFile(self.portal.myfolder, id='mybfile_download', title='My file',
                   uploaded_file=uploaded_file, submitted=1,
                   contributor='admin')
        transaction.commit()

        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder')
        self.assertTrue(
        self.portal.myfolder.mybfile_download.current_version_download_url() in
        self.browser.get_html())

    def test_view_zip(self):
        """ Custom view of zipfile """
        from zipfile import ZipFile
        zfile = open(os.path.join(os.path.dirname(__file__), 'fixtures',
                              'one_file_zip.zip'), 'rb')

        upload_file = StringIO(zfile.read())
        upload_file.filename = 'test.zip'
        upload_file.headers = {'content-type': 'application/zip'}

        namelist = ZipFile(zfile).namelist()
        zfile.close()
        addNyBFile(self.portal.myfolder, submitted=1,
                   contributor='contributor', id='test', title="test",
                   uploaded_file=upload_file)
        transaction.commit()

        #The result is a simple html with the contents of the zipfile (filepaths)
        self.browser.go('http://localhost/portal/myfolder/test/download/1/test.zip?action=view')
        html_content = self.browser.get_html()

        for filepath in namelist:
            self.assertTrue(filepath in html_content)
        zfile.close()


class VersioningTestCase(NaayaFunctionalTestCase, BrowserFileTestingMixin):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        self.portal.manage_install_pluggableitem('Naaya Blob File')
        from Products.Naaya.NyFolder import addNyFolder
        from naaya.content.bfile.bfile_item import addNyBFile
        addNyFolder(self.portal, 'fol', contributor='contributor', submitted=1)
        addNyBFile(self.portal.fol, id='multiver', title='Mulitple versions',
            submitted=1, contributor='contributor')
        self.ob_url = 'http://localhost/portal/fol/multiver'
        transaction.commit()
        self.the_file = self.portal.fol.multiver

    def beforeTearDown(self):
        self.portal.manage_delObjects(['fol'])
        self.portal.manage_uninstall_pluggableitem('Naaya Blob File')
        transaction.commit()

    def test_no_file(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go(self.ob_url)
        self.assertEqual(self.browser.get_code(), 200)
        html = self.browser.get_html()
        self.assertTrue('No file uploaded' in html)
        self.assertFalse(self.ob_url + '/download' in html)
        self.browser.go(self.ob_url + '/download/1/lala')
        self.assertEqual(self.browser.get_code(), 404)
        self.browser_do_logout()

    def test_one_file(self):
        file_data = {
            'filename': 'my.png',
            'content_type': 'image/png',
            'data': '1234',
        }
        self.the_file._save_file(self.make_file(**file_data),
                                 contributor='contributor')
        transaction.commit()
        self.browser_do_login('contributor', 'contributor')
        self.browser.go(self.ob_url)
        self.assertEqual(self.browser.get_code(), 200)
        html = self.browser.get_html()
        self.assertFalse('No files uploaded' in html)
        self.assertTrue(self.ob_url + '/download/1/my.png' in html)
        self.assertFalse(self.ob_url + '/download/2' in html)
        self.assertTrue('image/png' in html)
        self.assertTrue('4 bytes' in html)
        self.browser.go(self.ob_url + '/download/1/my.png')
        self.assertDownload(**file_data)
        self.browser_do_logout()

    def test_two_files(self):
        file_data_1 = {
            'filename': 'my.png',
            'content_type': 'image/png',
            'data': 'asdf'*1024*1024,
        }
        file_data_2 = {
            'filename': 'my.jpg',
            'content_type': 'image/jpeg',
            'data': 'g'*int(1024*15.3),
        }
        self.the_file._save_file(self.make_file(**file_data_1),
                                 contributor='contributor')
        self.the_file._save_file(self.make_file(**file_data_2),
                                 contributor='contributor')
        transaction.commit()
        self.browser_do_login('contributor', 'contributor')
        self.browser.go(self.ob_url)
        self.assertEqual(self.browser.get_code(), 200)
        html = self.browser.get_html()
        self.assertFalse('No files uploaded' in html)
        self.assertTrue(self.ob_url + '/download/1/my.png' in html)
        self.assertTrue(self.ob_url + '/download/2/my.jpg' in html)
        self.assertTrue('4 MB' in html)
        self.assertTrue('15 KB' in html)
        # don't download 1st file, it takes too much time
        #self.browser.go(self.ob_url + '/download/1/my.png')
        #self.assertDownload(**file_data_1)
        self.browser.go(self.ob_url + '/download/2/my.jpg')
        self.assertDownload(**file_data_2)
        self.browser_do_logout()

class SecurityTestCase(NaayaFunctionalTestCase, BrowserFileTestingMixin):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        self.portal.manage_install_pluggableitem('Naaya Blob File')
        from Products.Naaya.NyFolder import addNyFolder
        from naaya.content.bfile.bfile_item import addNyBFile
        addNyFolder(self.portal, 'fol', contributor='contributor', submitted=1)
        addNyBFile(self.portal.fol, id='secur', title='Mulitple versions',
            submitted=1, contributor='contributor')
        self.ob_url = 'http://localhost/portal/fol/secur'
        transaction.commit()
        self.file_data = {
            'filename': 'my.png',
            'content_type': 'image/png',
            'data': 'asdf'*1024*64,
        }
        self.portal.fol.secur._save_file(self.make_file(**self.file_data),
                                 contributor='contributor')
        transaction.commit()
        self.the_file = self.portal.fol.secur

    def beforeTearDown(self):
        self.portal.manage_delObjects(['fol'])
        self.portal.manage_uninstall_pluggableitem('Naaya Blob File')
        transaction.commit()

    def test_restricted_access(self):
        self.the_file._View_Permission = ('Administrator', 'Owner')
        transaction.commit()

        self.browser_do_login('admin', '')
        self.browser.go(self.ob_url)
        self.assertEqual(self.browser.get_code(), 200)
        self.assertTrue(self.ob_url + '/download/1/my.png' in
                        self.browser.get_html())
        self.browser.go(self.ob_url + '/download/1/my.png')
        self.assertDownload(**self.file_data)
        self.browser_do_logout()

        self.browser.go(self.ob_url)
        self.assertRedirectLoginPage()
        self.browser.go(self.ob_url + '/download/1/my.png')
        self.assertRedirectLoginPage()

