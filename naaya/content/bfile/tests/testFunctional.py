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

import blob_patch

import re
from unittest import TestSuite, makeSuite
from StringIO import StringIO
from copy import deepcopy

import transaction

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

class BFileMixin(object):
    """ testing mix-in that installs the Naaya Blob File content type """

    bfile_metatype = 'Naaya Blob File'
    bfile_permission = 'Naaya - Add Naaya Blob File objects'

    def bfile_install(self):
        self.portal.manage_install_pluggableitem(self.bfile_metatype)
        add_content_permissions = deepcopy(self.portal.acl_users.getPermission('Add content'))
        add_content_permissions['permissions'].append(self.bfile_permission)
        self.portal.acl_users.editPermission('Add content', **add_content_permissions)

    def bfile_uninstall(self):
        add_content_permissions = deepcopy(self.portal.acl_users.getPermission('Add content'))
        add_content_permissions['permissions'].remove(self.bfile_permission)
        self.portal.acl_users.editPermission('Add content', **add_content_permissions)
        self.portal.manage_uninstall_pluggableitem(self.bfile_metatype)

class BrowserFileTestingMixin(object):
    def make_file(self, filename, content_type, data):
        f = StringIO(data)
        f.filename = filename
        f.headers = {'content-type': content_type}
        return f

    def assertDownload(self, filename, content_type, data):
        self.assertEqual(self.browser.get_code(), 200)
        self.assertEqual(self.browser_get_header('content-length'), str(len(data)))
        self.assertEqual(self.browser_get_header('content-disposition'),
            'attachment;filename*=UTF-8\'\'' + filename)
        self.assertEqual(self.browser_get_header('content-type'), content_type)
        self.assertEqual(self.browser.get_html(), data)

class NyBFileFunctionalTestCase(NaayaFunctionalTestCase,
                                BFileMixin,
                                BrowserFileTestingMixin):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        self.bfile_install()
        from Products.Naaya.NyFolder import addNyFolder
        from naaya.content.bfile.bfile_item import addNyBFile
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)
        addNyBFile(self.portal.myfolder, id='mybfile', title='My file', submitted=1, contributor='contributor')
        transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder'])
        self.bfile_uninstall()
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

        self.browser.go('http://localhost/portal/myfolder/test-file/download?v=1')
        self.assertEqual(self.browser.get_code(), 200)
        html = self.browser.get_html()
        headers = self.browser._browser._response._headers
        self.failUnlessEqual(headers.get('content-disposition', None),
            'attachment;filename*=UTF-8\'\'testcreatebfile.txt')
        self.assertEqual(headers['content-type'], 'text/plain; charset=utf-8')
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

        self.browser.go('http://localhost/portal/myfolder/mybfile/download?v=1')
        html = self.browser.get_html()
        headers = self.browser._browser._response._headers
        self.failUnlessEqual(headers.get('content-disposition', None),
            'attachment;filename*=UTF-8\'\'the_new_bfile.txt')
        self.assertEqual(headers['content-type'], 'text/plain; charset=latin-1')
        self.failUnlessEqual(html, TEST_FILE_DATA_2)

        self.browser.go('http://localhost/portal/myfolder/mybfile/edit_html?lang=fr')
        form = self.browser.get_form('frmEdit')
        form['title:utf8:ustring'] = 'french_title'
        TEST_FILE_DATA_3 = 'some new data for my file'
        form.find_control('uploaded_file').add_file(StringIO(TEST_FILE_DATA_3),
            filename='the_new_bfile.txt', content_type='text/html; charset=utf-8')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.browser.go('http://localhost/portal/myfolder/mybfile/download?v=2')
        html = self.browser.get_html()
        headers = self.browser._browser._response._headers
        self.failUnlessEqual(headers.get('content-disposition', None),
            'attachment;filename*=UTF-8\'\'the_new_bfile.txt')
        self.assertEqual(headers['content-type'], 'text/html; charset=utf-8')
        self.failUnlessEqual(html, TEST_FILE_DATA_3)

        self.failUnlessEqual(self.portal.myfolder.mybfile.title, 'New Title')
        self.failUnlessEqual(self.portal.myfolder.mybfile.getLocalProperty('title', 'fr'), 'french_title')

        self.browser_do_logout()

    def test_edit_remove_versions(self):
        self.browser_do_login('admin', '')

        for c in range(4):
            f = self.make_file('afile', 'text/plain', 'some data')
            self.portal.myfolder['mybfile']._save_file(f)

        transaction.commit()

        self.browser.go('http://localhost/portal/myfolder/mybfile')
        html = self.browser.get_html()
        self.assertTrue('download?v=1' in html)
        self.assertTrue('download?v=2' in html)
        self.assertTrue('download?v=3' in html)
        self.assertTrue('download?v=4' in html)

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
        self.assertTrue('download?v=1' in html)
        self.assertTrue('download?v=2' not in html)
        self.assertTrue('download?v=3' in html)
        self.assertTrue('download?v=4' not in html)

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

class VersioningTestCase(NaayaFunctionalTestCase, BFileMixin, BrowserFileTestingMixin):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        self.bfile_install()
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
        self.bfile_uninstall()
        transaction.commit()

    def test_no_file(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go(self.ob_url)
        self.assertEqual(self.browser.get_code(), 200)
        html = self.browser.get_html()
        self.assertTrue('No file uploaded' in html)
        self.assertFalse(self.ob_url + '/download' in html)
        self.browser.go(self.ob_url + '/download?v=1')
        self.assertEqual(self.browser.get_code(), 404)
        self.browser_do_logout()

    def test_one_file(self):
        file_data = {
            'filename': 'my.png',
            'content_type': 'image/png',
            'data': '1234',
        }
        self.the_file._save_file(self.make_file(**file_data))
        transaction.commit()
        self.browser_do_login('contributor', 'contributor')
        self.browser.go(self.ob_url)
        self.assertEqual(self.browser.get_code(), 200)
        html = self.browser.get_html()
        self.assertFalse('No files uploaded' in html)
        self.assertTrue(self.ob_url + '/download?v=1' in html)
        self.assertFalse(self.ob_url + '/download?v=2' in html)
        self.assertTrue('image/png' in html)
        self.assertTrue('4 bytes' in html)
        self.browser.go(self.ob_url + '/download?v=1')
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
        self.the_file._save_file(self.make_file(**file_data_1))
        self.the_file._save_file(self.make_file(**file_data_2))
        transaction.commit()
        self.browser_do_login('contributor', 'contributor')
        self.browser.go(self.ob_url)
        self.assertEqual(self.browser.get_code(), 200)
        html = self.browser.get_html()
        self.assertFalse('No files uploaded' in html)
        self.assertTrue(self.ob_url + '/download?v=1' in html)
        self.assertTrue(self.ob_url + '/download?v=2' in html)
        self.assertTrue('4 MB' in html)
        self.assertTrue('15 KB' in html)
        self.browser.go(self.ob_url + '/download?v=1')
        self.assertDownload(**file_data_1)
        self.browser.go(self.ob_url + '/download?v=2')
        self.assertDownload(**file_data_2)
        self.browser_do_logout()

class SecurityTestCase(NaayaFunctionalTestCase, BFileMixin, BrowserFileTestingMixin):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        self.bfile_install()
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
            'data': 'asdf'*1024*1024,
        }
        self.portal.fol.secur._save_file(self.make_file(**self.file_data))
        transaction.commit()
        self.the_file = self.portal.fol.secur

    def beforeTearDown(self):
        self.portal.manage_delObjects(['fol'])
        self.bfile_uninstall()
        transaction.commit()

    def test_restricted_access(self):
        self.the_file._View_Permission = ('Administrator', 'Owner')
        transaction.commit()

        self.browser_do_login('admin', '')
        self.browser.go(self.ob_url)
        self.assertEqual(self.browser.get_code(), 200)
        self.assertTrue(self.ob_url + '/download?v=1' in self.browser.get_html())
        self.browser.go(self.ob_url + '/download?v=1')
        self.assertDownload(**self.file_data)
        self.browser_do_logout()

        self.browser.go(self.ob_url)
        self.assertRedirectLoginPage()
        self.browser.go(self.ob_url + '/download?v=1')
        self.assertRedirectLoginPage()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NyBFileFunctionalTestCase))
    suite.addTest(makeSuite(VersioningTestCase))
    suite.addTest(makeSuite(SecurityTestCase))
    return suite
