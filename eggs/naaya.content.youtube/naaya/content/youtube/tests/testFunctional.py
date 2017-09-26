import re
from BeautifulSoup import BeautifulSoup

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

class NyYoutubeFunctionalTestCase(NaayaFunctionalTestCase):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        self.portal.manage_install_pluggableitem('Naaya Youtube')
        from Products.Naaya.NyFolder import addNyFolder
        from naaya.content.youtube.youtube_item import addNyYoutube
        addNyFolder(self.portal, 'myfolder', contributor='contributor',
            submitted=1)
        addNyYoutube(self.portal.myfolder, id='myyoutube',
            title='My Youtube Video', submitted=1, contributor='contributor',
            youtube_id='uelHwf8o7_U', iframe_width='640', iframe_height='360')
        import transaction; transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder'])
        self.portal.manage_uninstall_pluggableitem('Naaya Youtube')
        import transaction; transaction.commit()

    def test_add(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/info/youtube_add_html')
        self.failUnless('<h1>Embed YouTube video</h1>' in self.browser.get_html())
        form = self.browser.get_form('frmAdd')
        expected_controls = set([
            'lang', 'title:utf8:ustring', 'description:utf8:ustring', 'coverage:utf8:ustring',
            'keywords:utf8:ustring', 'releasedate', 'discussion:boolean',
        ])
        found_controls = set(c.name for c in form.controls)
        self.failUnless(expected_controls.issubset(found_controls),
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['title:utf8:ustring'] = 'test_youtube'
        form['description:utf8:ustring'] = 'test_youtube_description'
        form['keywords:utf8:ustring'] = 'keyw1, keyw2'
        form['youtube_id:utf8:ustring'] = 'uelHwf8o7_U'

        self.browser.submit()
        html = self.browser.get_html()
        self.failUnless('The administrator will analyze your request and you will be notified about the result shortly.' in html)

        self.portal.info.test_youtube.approveThis()

        self.browser.go('http://localhost/portal/info/test_youtube')
        html = self.browser.get_html()
        self.failUnless(re.search(r'<h1>.*test_youtube.*</h1>', html, re.DOTALL))
        self.failUnless('test_youtube_description' in html)

        self.browser_do_logout()

    def test_add_error(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/youtube_add_html')

        form = self.browser.get_form('frmAdd')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        # enter no values in the fields
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('The form contains errors' in html)
        self.failUnless('Value required for "Title"' in html)

        form = self.browser.get_form('frmAdd')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['title:utf8:ustring'] = 'test_youtube'
        form['description:utf8:ustring'] = 'test_youtube_description'
        form['keywords:utf8:ustring'] = 'keyw1, keyw2'
        # enter an invalid Youtube ID
        form['youtube_id:utf8:ustring'] = 'aaaaaaaaaaa'
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('The form contains errors' in html)
        self.failUnless('Invalid Youtube ID (inexisting video)' in html)

    def test_edit(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder/myyoutube/edit_html')
        form = self.browser.get_form('frmEdit')

        self.failUnlessEqual(form['title:utf8:ustring'], 'My Youtube Video')

        form['title:utf8:ustring'] = 'new_youtube_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.myyoutube.title, 'new_youtube_title')

        self.browser.go('http://localhost/portal/myfolder/myyoutube/edit_html?lang=fr')
        form = self.browser.get_form('frmEdit')
        form['title:utf8:ustring'] = 'french_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.myyoutube.title, 'new_youtube_title')
        self.failUnlessEqual(self.portal.myfolder.myyoutube.getLocalProperty('title', 'fr'), 'french_title')

        self.browser_do_logout()

    def test_edit_error(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/myyoutube/edit_html')

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

        self.browser.go('http://localhost/portal/myfolder/myyoutube/manage_edit_html')
        form = self.browser.get_form('frmEdit')
        self.failUnlessEqual(form['title:utf8:ustring'], 'My Youtube Video')
        form['title:utf8:ustring'] = 'new_youtube_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.myyoutube.title, 'new_youtube_title')

        self.browser_do_logout()

    def test_view_in_folder(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)

        tables = soup.findAll('table', id='folderfile_list')
        self.assertTrue(len(tables) == 1)

        links_to_youtube = tables[0].findAll('a', attrs={'href': 'http://localhost/portal/myfolder/myyoutube'})
        self.assertTrue(len(links_to_youtube) == 1)
        self.assertTrue(links_to_youtube[0].string == 'My Youtube Video')

        self.browser_do_logout()
