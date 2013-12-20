import re
from unittest import TestSuite, makeSuite
from StringIO import StringIO
from BeautifulSoup import BeautifulSoup

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

class NyFileFunctionalTestCase(NaayaFunctionalTestCase):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        from Products.Naaya.NyFolder import addNyFolder
        from naaya.content.file.file_item import addNyFile
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)
        addNyFile(self.portal.myfolder, id='myfile', title='My file', submitted=1, contributor='contributor')
        import transaction; transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder'])
        import transaction; transaction.commit()

    def test_add(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/file_add_html')
        self.failUnless('<h1>Submit File</h1>' in self.browser.get_html())
        form = self.browser.get_form('frmAdd')
        expected_controls = set([
            'lang', 'title:utf8:ustring', 'description:utf8:ustring', 'coverage:utf8:ustring',
            'keywords:utf8:ustring', 'releasedate', 'discussion:boolean',
            'source', 'url', 'file', 'downloadfilename:utf8:ustring',
        ])
        found_controls = set(c.name for c in form.controls)
        self.failUnless(expected_controls.issubset(found_controls),
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['title:utf8:ustring'] = 'test_create_file'
        form['description:utf8:ustring'] = 'test_file_description'
        form['coverage:utf8:ustring'] = 'test_file_coverage'
        form['keywords:utf8:ustring'] = 'keyw1, keyw2'

        TEST_FILE_DATA = 'some data for my data file'
        form.find_control('file').add_file(StringIO(TEST_FILE_DATA),
            filename='testcreatefile.txt', content_type='text/plain')

        self.browser.submit()
        html = self.browser.get_html()
        self.failUnless('The administrator will analyze your request and you will be notified about the result shortly.' in html)

        self.portal.myfolder['testcreatefile.txt'].approveThis()

        self.browser.go('http://localhost/portal/myfolder/testcreatefile.txt')
        html = self.browser.get_html()
        self.failUnless(re.search(r'<h1>.*test_create_file.*</h1>', html, re.DOTALL))
        self.failUnless('test_file_description' in html)
        self.failUnless('test_file_coverage' in html)
        self.failUnless('keyw1, keyw2' in html)

        self.browser.go('http://localhost/portal/myfolder/testcreatefile.txt/download')
        html = self.browser.get_html()
        headers = self.browser._browser._response._headers
        self.failUnlessEqual(headers.get('content-disposition', None),
            'attachment;filename=testcreatefile.txt')
        self.failUnlessEqual(html, TEST_FILE_DATA)

        self.browser_do_logout()

    def test_add_error(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/file_add_html')

        form = self.browser.get_form('frmAdd')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        # enter no values in the fields
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('The form contains errors' in html)
        self.failUnless('Value required for "Title"' in html)

    def test_edit(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder/myfile/edit_html')
        form = self.browser.get_form('frmEdit')

        self.failUnlessEqual(form['title:utf8:ustring'], 'My file')

        form['title:utf8:ustring'] = 'new_file_title'
        TEST_FILE_DATA_2 = 'some new data for my file'
        form.find_control('file').add_file(StringIO(TEST_FILE_DATA_2),
            filename='the_new_file.txt', content_type='text/plain')

        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()
        html = self.browser.get_html()
        self.failUnless('<h1>Edit File</h1>' in html)

        self.failUnlessEqual(self.portal.myfolder.myfile.title, 'new_file_title')
        self.portal.myfolder.myfile.approveThis()

        self.browser.go('http://localhost/portal/myfolder/myfile/download')
        html = self.browser.get_html()
        headers = self.browser._browser._response._headers
        self.failUnlessEqual(headers.get('content-disposition', None),
            'attachment;filename=the_new_file.txt')
        self.failUnlessEqual(html, TEST_FILE_DATA_2)

        self.browser.go('http://localhost/portal/myfolder/myfile/edit_html?lang=fr')
        form = self.browser.get_form('frmEdit')
        form['title:utf8:ustring'] = 'french_title'
        TEST_FILE_DATA_3 = 'some new data for my file'
        form.find_control('file').add_file(StringIO(TEST_FILE_DATA_3),
            filename='the_new_file.txt', content_type='text/plain')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.browser.go('http://localhost/portal/myfolder/myfile/download')
        html = self.browser.get_html()
        headers = self.browser._browser._response._headers
        self.failUnlessEqual(headers.get('content-disposition', None),
            'attachment;filename=the_new_file.txt')
        self.failUnlessEqual(html, TEST_FILE_DATA_3)

        self.failUnlessEqual(self.portal.myfolder.myfile.title, 'new_file_title')
        self.failUnlessEqual(self.portal.myfolder.myfile.getLocalProperty('title', 'fr'), 'french_title')

        self.browser_do_logout()

    def test_edit_error(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/myfile/edit_html')

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

        self.browser.go('http://localhost/portal/myfolder/myfile/manage_edit_html')
        form = self.browser.get_form('frmEdit')
        self.failUnlessEqual(form['title:utf8:ustring'], 'My file')
        form['title:utf8:ustring'] = 'new_file_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.myfile.title, 'new_file_title')

        self.browser_do_logout()

    def test_view_in_folder(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)

        tables = soup.findAll('table', id='folderfile_list')
        self.assertTrue(len(tables) == 1)

        links_to_file = tables[0].findAll('a', attrs={'href': 'http://localhost/portal/myfolder/myfile'})
        self.assertTrue(len(links_to_file) == 1)
        self.assertTrue(links_to_file[0].string == 'My file')

        self.browser_do_logout()
