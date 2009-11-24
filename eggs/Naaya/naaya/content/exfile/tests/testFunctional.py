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

import re
from unittest import TestSuite, makeSuite
from copy import deepcopy
from StringIO import StringIO
from BeautifulSoup import BeautifulSoup

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase


class NyExFileFunctionalTestCase(NaayaFunctionalTestCase):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        self.portal.manage_install_pluggableitem('Naaya Extended File')
        from Products.Naaya.NyFolder import addNyFolder
        from naaya.content.exfile.exfile_item import addNyExFile
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)
        addNyExFile(self.portal.myfolder, id='myexfile', title='My file', submitted=1, contributor='contributor')
        import transaction; transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder'])
        self.portal.manage_uninstall_pluggableitem('Naaya Extended File')
        import transaction; transaction.commit()

    def test_add(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/exfile_add_html')
        self.failUnless('<h1>Submit ExFile</h1>' in self.browser.get_html())
        form = self.browser.get_form('frmAdd')
        expected_controls = set([
            'lang', 'title:utf8:ustring', 'description:utf8:ustring', 'coverage:utf8:ustring',
            'keywords:utf8:ustring', 'releasedate', 'discussion:boolean',
            'source', 'url', 'file',
        ])
        found_controls = set(c.name for c in form.controls)
        self.failUnless(expected_controls.issubset(found_controls),
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['title:utf8:ustring'] = 'test_create_exfile'
        form['description:utf8:ustring'] = 'test_exfile_description'
        form['coverage:utf8:ustring'] = 'test_exfile_coverage'
        form['keywords:utf8:ustring'] = 'keyw1, keyw2'

        form.find_control('file').add_file(StringIO('added_en_data'),
            filename='testcreateexfile.txt', content_type='text/plain')

        self.browser.submit()
        html = self.browser.get_html()
        self.failUnless('The administrator will analyze your request and you will be notified about the result shortly.' in html)

        self.portal.myfolder['testcreateexfile.txt'].approveThis()

        self.browser.go('http://localhost/portal/myfolder/testcreateexfile.txt')
        html = self.browser.get_html()
        self.failUnless(re.search(r'<h1>.*test_create_exfile.*</h1>', html, re.DOTALL))
        self.failUnless('test_exfile_description' in html)
        self.failUnless('test_exfile_coverage' in html)
        self.failUnless('keyw1, keyw2' in html)

        self.browser.go('http://localhost/portal/myfolder/testcreateexfile.txt/download')
        html = self.browser.get_html()
        headers = self.browser._browser._response._headers
        self.failUnlessEqual(headers.get('content-disposition', None),
            'attachment;filename=testcreateexfile.txt')
        self.failUnlessEqual(html, 'added_en_data')

        self.browser_do_logout()

    def test_add_error(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/exfile_add_html')

        form = self.browser.get_form('frmAdd')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        # enter no values in the fields
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('The form contains errors' in html)
        self.failUnless('Value required for "Title"' in html)

    def test_edit(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder/myexfile/edit_html')
        form = self.browser.get_form('frmEdit')

        self.failUnlessEqual(form['title:utf8:ustring'], 'My file')

        form['title:utf8:ustring'] = 'new_exfile_title'
        form.find_control('file').add_file(StringIO('edit_en_data'),
            filename='edit_en_file.txt', content_type='text/plain')

        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()
        html = self.browser.get_html()
        self.failUnless('<h1>Edit File</h1>' in html)

        self.failUnlessEqual(self.portal.myfolder.myexfile.title, 'new_exfile_title')
        self.portal.myfolder.myexfile.approveThis()

        self.browser.go('http://localhost/portal/myfolder/myexfile/download')
        html = self.browser.get_html()
        headers = self.browser._browser._response._headers
        self.failUnlessEqual(headers.get('content-disposition', None),
            'attachment;filename=edit_en_file.txt')
        self.failUnlessEqual(html, 'edit_en_data')

        self.browser.go('http://localhost/portal/myfolder/myexfile/edit_html?lang=fr')
        form = self.browser.get_form('frmEdit')
        form['title:utf8:ustring'] = 'french_title'
        form.find_control('file').add_file(StringIO('edit_fr_data'),
            filename='edit_fr_file.txt', content_type='text/plain')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.browser.go('http://localhost/portal/myfolder/myexfile/download')
        html = self.browser.get_html()
        headers = self.browser._browser._response._headers
        self.failUnlessEqual(headers.get('content-disposition', None),
            'attachment;filename=edit_en_file.txt')
        self.failUnlessEqual(html, 'edit_en_data')

        self.browser.go('http://localhost/portal/myfolder/myexfile/download?lang=fr')
        html = self.browser.get_html()
        headers = self.browser._browser._response._headers
        self.failUnlessEqual(headers.get('content-disposition', None),
            'attachment;filename=edit_fr_file.txt')
        self.failUnlessEqual(html, 'edit_fr_data')

        self.failUnlessEqual(self.portal.myfolder.myexfile.title, 'new_exfile_title')
        self.failUnlessEqual(self.portal.myfolder.myexfile.getLocalProperty('title', 'fr'), 'french_title')

        self.browser_do_logout()

    def test_edit_error(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/myexfile/edit_html')

        form = self.browser.get_form('frmEdit')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        form['title:utf8:ustring'] = ''
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('The form contains errors' in html)
        self.failUnless('Value required for "Title"' in html)

        self.browser_do_logout()

    def test_manage(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder/myexfile/manage_edit_html')
        form = self.browser.get_form('frmEdit')
        self.failUnlessEqual(form['title:utf8:ustring'], 'My file')
        form['title:utf8:ustring'] = 'new_exfile_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.myexfile.title, 'new_exfile_title')

        self.browser_do_logout()

    def test_view_in_folder(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)

        tables = soup.findAll('table', id='folderfile_list')
        self.assertTrue(len(tables) == 1)

        links_to_extfile = tables[0].findAll('a', attrs={'href': 'http://localhost/portal/myfolder/myexfile'})
        self.assertTrue(len(links_to_extfile) == 1)
        self.assertTrue(links_to_extfile[0].string == 'My file')

        self.browser_do_logout()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NyExFileFunctionalTestCase))
    return suite
