import re
from unittest import TestSuite, makeSuite
from copy import deepcopy
from StringIO import StringIO
from BeautifulSoup import BeautifulSoup
from mock import patch

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase


class NyMediaFileFunctionalTestCase(NaayaFunctionalTestCase):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        self.portal.manage_install_pluggableitem('Naaya Media File')
        from Products.Naaya.NyFolder import addNyFolder
        from naaya.content.mediafile.mediafile_item import addNyMediaFile
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)
        addNyMediaFile(self.portal.myfolder, id='mymediafile', title='My media file',
            submitted=1, contributor='contributor', _skip_videofile_check=True)
        import transaction; transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder'])
        self.portal.manage_uninstall_pluggableitem('Naaya Media File')
        import transaction; transaction.commit()

    @patch('naaya.content.mediafile.converters.MediaConverter.can_convert')
    def test_add(self, mock_can_convert):
        mock_can_convert.return_value = False
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/mediafile_add_html')
        self.failUnless('<h1>Submit Media File</h1>' in self.browser.get_html())
        form = self.browser.get_form('frmAdd')
        expected_controls = set([
            'lang', 'title:utf8:ustring', 'description:utf8:ustring', 'coverage:utf8:ustring',
            'keywords:utf8:ustring', 'releasedate', 'discussion:boolean', 'file',
        ])
        found_controls = set(c.name for c in form.controls)
        self.failUnless(expected_controls.issubset(found_controls),
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['title:utf8:ustring'] = 'test_create_mediafile'
        form['description:utf8:ustring'] = 'test_mediafile_description'
        form['coverage:utf8:ustring'] = 'test_mediafile_coverage'
        form['keywords:utf8:ustring'] = 'keyw1, keyw2'

        form.find_control('file').add_file(StringIO('the_FLV_data'),
            filename='testvid.flv', content_type='video/x-flv')

        self.browser.submit()
        html = self.browser.get_html()
        self.failUnless('The administrator will analyze your request and you will be notified about the result shortly.' in html)

        self.portal.myfolder.test_create_mediafile.approveThis()

        self.browser.go('http://localhost/portal/myfolder/test_create_mediafile')
        html = self.browser.get_html()
        self.failUnless(re.search(r'<h1>.*test_create_mediafile.*</h1>', html, re.DOTALL))
        self.failUnless('test_mediafile_description' in html)
        self.failUnless('test_mediafile_coverage' in html)
        self.failUnless('keyw1, keyw2' in html)

        media_id = self.portal.myfolder.test_create_mediafile.getSingleMediaId()
        self.failUnlessEqual(media_id, 'testvid.flv')
        self.browser.go('http://localhost/portal/myfolder/test_create_mediafile/%s' % media_id)
        html = self.browser.get_html()
        headers = self.browser._browser._response._headers
        self.failUnlessEqual(headers.get('content-type', None), 'application/x-flash-video')

        # apparently the test publisher doesn't serve our flv file correctly.
        #self.failUnlessEqual(html, 'the_FLV_data')

        self.browser_do_logout()

    def test_add_error(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/mediafile_add_html')

        form = self.browser.get_form('frmAdd')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        # enter no values in the fields
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('The form contains errors' in html)
        self.failUnless('Value required for "Title"' in html)
        self.failUnless('No file was uploaded' in html)

    @patch('naaya.content.mediafile.converters.MediaConverter.can_convert')
    def test_edit(self, mock_can_convert):
        mock_can_convert.return_value = False
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder/mymediafile/edit_html')
        form = self.browser.get_form('frmEdit')

        self.failUnlessEqual(form['title:utf8:ustring'], 'My media file')

        form['title:utf8:ustring'] = 'new_mediafile_title'
        form.find_control('file').add_file(StringIO('the_FLV_data_B'),
            filename='testvid_B.flv', content_type='video/x-flv')

        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()
        html = self.browser.get_html()
        self.failUnless('<h1>Edit Media File</h1>' in html)

        self.failUnlessEqual(self.portal.myfolder.mymediafile.title, 'new_mediafile_title')
        self.portal.myfolder.mymediafile.approveThis()

        media_id = self.portal.myfolder.mymediafile.getSingleMediaId()
        self.failUnlessEqual(media_id, 'testvid_B.flv')
        self.browser.go('http://localhost/portal/myfolder/mymediafile/%s' % media_id)
        html = self.browser.get_html()
        headers = self.browser._browser._response._headers
        self.failUnlessEqual(headers.get('content-type', None), 'application/x-flash-video')
        # apparently the test publisher doesn't serve our flv file correctly.
        #self.failUnlessEqual(html, 'the_FLV_data_B')

        self.browser.go('http://localhost/portal/myfolder/mymediafile/edit_html?lang=fr')
        form = self.browser.get_form('frmEdit')
        form['title:utf8:ustring'] = 'french_title'
        form.find_control('file').add_file(StringIO('the_FLV_data_C'),
            filename='testvid_C.flv', content_type='video/x-flv')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()
        self.failUnless('Saved changes' in self.browser.get_html())

        media_id = self.portal.myfolder.mymediafile.getSingleMediaId()
        self.failUnlessEqual(media_id, 'testvid_B.flv') # the file is not renamed - is this correct?
        self.browser.go('http://localhost/portal/myfolder/mymediafile/%s' % media_id)
        html = self.browser.get_html()
        headers = self.browser._browser._response._headers
        self.failUnlessEqual(headers.get('content-type', None), 'application/x-flash-video')
        # apparently the test publisher doesn't serve our flv file correctly.
        #self.failUnlessEqual(html, 'the_FLV_data_C')

        self.failUnlessEqual(self.portal.myfolder.mymediafile.title, 'new_mediafile_title')
        self.failUnlessEqual(self.portal.myfolder.mymediafile.getLocalProperty('title', 'fr'), 'french_title')

        self.browser_do_logout()

    def test_edit_error(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/mymediafile/edit_html')

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

        self.browser.go('http://localhost/portal/myfolder/mymediafile/manage_edit_html')

        form = self.browser.get_form('frmEdit')
        # TODO: title control should be 'title:utf8:ustring'
        self.failUnlessEqual(form['title:utf8:ustring'], 'My media file')
        form['title:utf8:ustring'] = 'new_mediafile_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.mymediafile.title, 'new_mediafile_title')

        self.browser_do_logout()

    def test_view_in_folder(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)

        tables = soup.findAll('table', id='folderfile_list')
        self.assertTrue(len(tables) == 1)

        links_to_mediafile = tables[0].findAll('a', attrs={'href': 'http://localhost/portal/myfolder/mymediafile'})
        self.assertTrue(len(links_to_mediafile) == 1)
        self.assertTrue(links_to_mediafile[0].string == 'My media file')

        self.browser_do_logout()
