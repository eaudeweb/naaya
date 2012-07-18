import os
import re
from StringIO import StringIO
import urllib

import transaction
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.Naaya.NyFolder import addNyFolder
from naaya.content.localizedbfile.localizedbfile_item import addNyLocalizedBFile
from naaya.content.bfile.tests.testFunctional import BrowserFileTestingMixin

class NyLocalizedBFileFunctional(NaayaFunctionalTestCase, BrowserFileTestingMixin):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        self.portal.gl_add_site_language('fr')
        self.portal.manage_install_pluggableitem('Naaya Localized Blob File')
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)
        addNyLocalizedBFile(self.portal.myfolder, id='mylocalizedbfile', title='My localized file',
            submitted=1, contributor='contributor')
        transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder'])
        self.portal.manage_uninstall_pluggableitem('Naaya Localized Blob File')
        transaction.commit()

    def test_add(self):
        """ """
        self.browser_do_login('contributor', 'contributor')
        lang_map = self.portal.gl_get_languages()

        for lang in lang_map:

            path = 'http://localhost/portal/%(language)s/myfolder/localizedbfile_add_html' % {'language':lang}
            self.browser.go(path)
            self.failUnless('<h1>Submit Localized File</h1>' in self.browser.get_html())
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
            form['title:utf8:ustring'] = 'Test Localized File-%(language)s'%{'language':lang}
            form['description:utf8:ustring'] = 'test_localizedbfile_description'
            form['coverage:utf8:ustring'] = 'test_localizedbfile_coverage'
            form['keywords:utf8:ustring'] = 'keyw1, keyw2'

            TEST_FILE_DATA = 'some data for my file'
            form.find_control('uploaded_file').add_file(StringIO(TEST_FILE_DATA),
                filename='testcreatelocalizedbfile.txt', content_type='text/plain; charset=utf-8')

            self.browser.submit()
            html = self.browser.get_html()
            self.failUnless('The administrator will analyze your request' in html)

            go_file = 'test-localized-file-%(gof)s' %{'gof':lang}
            self.portal.myfolder[go_file].approveThis()

            self.browser.go('http://localhost/portal/%(language)s/myfolder/%(gof)s'
                %{'language':lang, 'gof':go_file})
            html = self.browser.get_html()

            to_search = r'<h1>.*Test Localized File-%(language)s.*</h1>' % {'language':lang}

            self.failUnless(re.search(to_search, html, re.DOTALL))
            self.failUnless('test_localizedbfile_description' in html)
            self.failUnless('test_localizedbfile_coverage' in html)
            self.failUnless('keyw1, keyw2' in html)

            self.browser.go('http://localhost/portal/%(language)s/myfolder/%(gof)s/'
                            'download/1/testcreatelocalizedbfile.txt'%{'language':lang, 'gof':go_file})
            self.assertEqual(self.browser.get_code(), 200)
            html = self.browser.get_html()
            headers = self.browser._browser._response._headers
            self.failUnlessEqual(headers.get('content-disposition', None),
                                 'attachment')
            self.assertEqual(headers['content-type'], 'text/plain')
            self.failUnlessEqual(html, TEST_FILE_DATA)

        self.browser_do_logout()

    def test_add_error(self):
        """ """
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/localizedbfile_add_html')

        form = self.browser.get_form('frmAdd')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        # enter no values in the fields
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('The form contains errors' in html)
        self.failUnless('Value required for "Title"' in html)

    def test_edit(self):
        """ """
        self.browser_do_login('admin', '')
        lang_map = self.portal.gl_get_languages()

        for lang in lang_map:
            if lang == 'fr':
                self.browser.go('http://localhost/portal/fr/myfolder/mylocalizedbfile/')
                html = self.browser.get_html()
                self.failUnless('No file uploaded' in html)

            self.browser.go('http://localhost/portal/%(language)s/myfolder/mylocalizedbfile/edit_html'
                %{'language':lang})
            form = self.browser.get_form('frmEdit')

            if(lang == 'en'):
                self.failUnlessEqual(form['title:utf8:ustring'], 'My localized file')

            form['title:utf8:ustring'] = 'New Title - %(language)s' %{'language':lang}
            TEST_FILE_DATA_2 = 'some new data for my file'
            form.find_control('uploaded_file').add_file(StringIO(TEST_FILE_DATA_2),
                filename='the_new_localizedbfile-%(language)s.txt' %{'language':lang},
                content_type='text/plain; charset=latin-1')

            self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
            self.browser.submit()
            html = self.browser.get_html()
            self.failUnless('<h1>Edit Localized File</h1>' in html)

            self.failUnlessEqual(self.portal.myfolder.mylocalizedbfile.title, 'New Title - en')
            self.portal.myfolder.mylocalizedbfile.approveThis()

            self.browser.go('http://localhost/portal/myfolder/mylocalizedbfile/'
                            'download/1/the_new_localizedbfile-%(language)s.txt' %{'language':lang})
            html = self.browser.get_html()
            headers = self.browser._browser._response._headers
            self.failUnlessEqual(headers.get('content-disposition', None),
                                 'attachment')
            self.assertEqual(headers['content-type'], 'text/plain')
            self.failUnlessEqual(html, TEST_FILE_DATA_2)

        self.browser_do_logout()

    def test_edit_remove_versions(self):
        """ """
        self.browser_do_login('admin', '')

        _lang = 'en'
        for c in range(4):
            f = self.make_file('afile%(lang)s' %{'lang':c+1}, 'text/plain', 'some data for file%(file)s'
                    %{'file':c+1})
            self.portal.myfolder['mylocalizedbfile']._save_file(f, _lang,
                                                                contributor='contributor')

        transaction.commit()

        self.browser.go('http://localhost/portal/myfolder/mylocalizedbfile')
        html = self.browser.get_html()

        self.assertTrue('download/1/afile1' in html)
        self.assertTrue('download/2/afile2' in html)
        self.assertTrue('download/3/afile3' in html)
        self.assertTrue('download/4/afile4' in html)

        self.browser.go('http://localhost/portal/fr/myfolder/mylocalizedbfile')
        html = self.browser.get_html()
        self.failUnless('No file uploaded' in html)

        self.browser.go('http://localhost/portal/myfolder/mylocalizedbfile/edit_html')
        form = self.browser.get_form('frmEdit')
        form['versions_to_remove:list'] = ['2']
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()
        
        self.browser.go('http://localhost/portal/myfolder/mylocalizedbfile/edit_html')
        form = self.browser.get_form('frmEdit')
        form['versions_to_remove:list'] = ['3']
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        mylocalizedbfile = self.portal.myfolder['mylocalizedbfile']

        self.assertEqual(mylocalizedbfile._versions[_lang][0].removed, False)
        self.assertEqual(mylocalizedbfile._versions[_lang][1].removed, True)
        self.assertEqual(mylocalizedbfile._versions[_lang][2].removed, True)
        self.assertEqual(mylocalizedbfile._versions[_lang][3].removed, False)

        self.browser.go('http://localhost/portal/myfolder/mylocalizedbfile')
        html = self.browser.get_html()
       
        self.assertTrue('download/1/afile1' in html)
        self.assertTrue('download/2/afile3' not in html)
        self.assertTrue('download/3/afile2' not in html)
        self.assertTrue('download/3/afile3' not in html)
        self.assertTrue('download/4/afile4' in html)

        self.browser_do_logout()

    def test_edit_error(self):
        """ """
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/mylocalizedbfile/edit_html')

        form = self.browser.get_form('frmEdit')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        form['title:utf8:ustring'] = ''
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('The form contains errors' in html)
        self.failUnless('Value required for "Title"' in html)

        self.browser_do_logout()

    def test_utf8_filenames(self):
        """ """
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/localizedbfile_add_html')
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

        addNyLocalizedBFile(self.portal.myfolder, submitted=1,
                   contributor='contributor', id='test', title="test",
                   uploaded_file=uploaded_file, approved=True)
        transaction.commit()
        #View the file
        self.browser.go('http://localhost/portal/myfolder/test/download/1/test.txt?action=view')
        self.assertEqual(file_contents, self.browser.get_html())

    def test_exceptions(self):
        """Different Exceptions"""

        file_contents = 'simple contents'
        uploaded_file = StringIO(file_contents)
        uploaded_file.filename = 'test.txt'
        uploaded_file.headers = {'content-type': 'text/plain; charset=utf-8'}

        addNyLocalizedBFile(self.portal.myfolder, submitted=1,
                   contributor='contributor', id='test', title="test",
                   uploaded_file=uploaded_file, approved=True)
        transaction.commit()

        self.browser.go('http://localhost/portal/myfolder/test/download/0/test.txt?action=view')
        self.failUnless('An error was encountered' in self.browser.get_html())
        self.failUnless('NotFound' in self.browser.get_html())

        self.browser.go('http://localhost/portal/de/myfolder/test/download/1/test.txt?action=view')
        self.failUnless('An error was encountered' in self.browser.get_html())
        self.failUnless('NotFound' in self.browser.get_html())

        self.browser.go('http://localhost/portal/fr/myfolder/test/download/1/test.txt?action=view')
        self.failUnless('An error was encountered' in self.browser.get_html())
        self.failUnless('NotFound' in self.browser.get_html())

    def test_random_action(self):
        """Radom action"""

        file_contents = 'simple contents'
        uploaded_file = StringIO(file_contents)
        uploaded_file.filename = 'test.txt'
        uploaded_file.headers = {'content-type': 'text/plain; charset=utf-8'}

        addNyLocalizedBFile(self.portal.myfolder, submitted=1,
                   contributor='contributor', id='test', title="test",
                   uploaded_file=uploaded_file, approved=True)
        transaction.commit()
    
        self.browser.go('http://localhost/portal/de/myfolder/test/download/1/test.txt?action=shop')
        self.failUnless('An error was encountered' in self.browser.get_html())
        self.failUnless('NotFound' in self.browser.get_html())

    def test_direct_download(self):
        """ In folder listing we should have a download link that allows users
        to download the last version directly

        """
        file_contents = 'simple contents'
        uploaded_file = StringIO(file_contents)
        uploaded_file.filename = 'test.txt'
        uploaded_file.headers = {'content-type': 'text/plain; charset=utf-8'}

        addNyLocalizedBFile(self.portal.myfolder, id='mylocalizedbfile_download', title='My Localized file',
                   uploaded_file=uploaded_file, submitted=1,
                   contributor='admin')
        transaction.commit()

        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder')
        self.assertTrue(
        self.portal.myfolder.mylocalizedbfile_download.current_version_download_url() in
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
        addNyLocalizedBFile(self.portal.myfolder, submitted=1,
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
        self.portal.gl_add_site_language('fr')
        self.portal.manage_install_pluggableitem('Naaya Localized Blob File')
        from Products.Naaya.NyFolder import addNyFolder
        from naaya.content.localizedbfile.localizedbfile_item import addNyLocalizedBFile
        addNyFolder(self.portal, 'fol', contributor='contributor', submitted=1)
        addNyLocalizedBFile(self.portal.fol, id='multiver', title='Mulitple versions',
            submitted=1, contributor='contributor')
        self.ob_url_en = 'http://localhost/portal/fol/multiver'
        self.ob_url_fr = 'http://localhost/portal/fr/fol/multiver'
        self.lang_map = self.portal.gl_get_languages()
        transaction.commit()
        self.the_file = self.portal.fol.multiver

    def beforeTearDown(self):
        self.portal.manage_delObjects(['fol'])
        self.portal.manage_uninstall_pluggableitem('Naaya Localized Blob File')
        transaction.commit()

    def test_no_file(self):
        self.browser_do_login('contributor', 'contributor')
        for lang in self.lang_map:
            if lang == 'en':
                ob_url = self.ob_url_en
            else:
                ob_url = self.ob_url_fr

            self.browser.go(ob_url)
            self.assertEqual(self.browser.get_code(), 200)
            html = self.browser.get_html()
            self.assertTrue('No file uploaded' in html)
            self.assertFalse(ob_url + '/download' in html)
            self.browser.go(ob_url + '/download/1/lala')
            self.assertEqual(self.browser.get_code(), 404)

        self.browser_do_logout()

    def test_one_file(self):
        file_data = {
            'filename': 'my.png',
            'content_type': 'image/png',
            'data': '1234',
        }
        lang = 'en'
        self.the_file._save_file(self.make_file(**file_data), lang,
                                 contributor='contributor')
        transaction.commit()
        self.browser_do_login('contributor', 'contributor')
        self.browser.go(self.ob_url_en)
        self.assertEqual(self.browser.get_code(), 200)
        html = self.browser.get_html()
        self.assertFalse('No files uploaded' in html)
        self.assertTrue(self.ob_url_en + '/download/1/my.png' in html)
        self.assertFalse(self.ob_url_en + '/download/2' in html)
        self.assertTrue('image/png' in html)
        self.assertTrue('4 bytes' in html)
        self.browser.go(self.ob_url_en + '/download/1/my.png')
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
        lang = 'en'
        self.the_file._save_file(self.make_file(**file_data_1), lang,
                                 contributor='contributor')
        self.the_file._save_file(self.make_file(**file_data_2), lang,
                                 contributor='contributor')
        transaction.commit()
        self.browser_do_login('contributor', 'contributor')
        self.browser.go(self.ob_url_en)
        self.assertEqual(self.browser.get_code(), 200)
        html = self.browser.get_html()
        self.assertFalse('No files uploaded' in html)
        self.assertTrue(self.ob_url_en + '/download/1/my.png' in html)
        self.assertTrue(self.ob_url_en + '/download/2/my.jpg' in html)
        self.assertTrue('4 MB' in html)
        self.assertTrue('15 KB' in html)
        self.browser.go(self.ob_url_en + '/download/2/my.jpg')
        self.assertDownload(**file_data_2)
        self.browser_do_logout()

class SecurityTestCase(NaayaFunctionalTestCase, BrowserFileTestingMixin):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        self.portal.manage_install_pluggableitem('Naaya Localized Blob File')
        from Products.Naaya.NyFolder import addNyFolder
        from naaya.content.localizedbfile.localizedbfile_item import addNyLocalizedBFile
        addNyFolder(self.portal, 'fol', contributor='contributor', submitted=1)
        addNyLocalizedBFile(self.portal.fol, id='secur', title='Mulitple versions',
            submitted=1, contributor='contributor')
        self.ob_url = 'http://localhost/portal/fol/secur'
        transaction.commit()
        self.file_data = {
            'filename': 'my.png',
            'content_type': 'image/png',
            'data': 'asdf'*1024*64,
        }
        lang = 'en'
        self.portal.fol.secur._save_file(self.make_file(**self.file_data), lang,
                                 contributor='contributor')
        transaction.commit()
        self.the_file = self.portal.fol.secur

    def beforeTearDown(self):
        self.portal.manage_delObjects(['fol'])
        self.portal.manage_uninstall_pluggableitem('Naaya Localized Blob File')
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
