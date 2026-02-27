import re
from unittest import TestSuite, TestLoader
from bs4 import BeautifulSoup
from DateTime import DateTime

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

class NyURLFunctionalTestCase(NaayaFunctionalTestCase):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        from Products.Naaya.NyFolder import addNyFolder
        from naaya.content.url.url_item import addNyURL
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)
        addNyURL(self.portal.myfolder, id='myurl', title='My url',
            locator='http://www.eaudeweb.ro', submitted=1, contributor='contributor')
        import transaction; transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder'])
        import transaction; transaction.commit()

    def test_add(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/url_add_html')
        self.assertTrue('<h1>Submit URL</h1>' in self.browser.get_html())
        form = self.browser.get_form('frmAdd')
        expected_controls = set([
            'lang', 'title:utf8:string', 'description:utf8:string', 'coverage:utf8:string',
            'keywords:utf8:string', 'releasedate', 'locator:utf8:string',
        ])
        found_controls = set(c.name for c in form.controls)
        self.assertTrue(expected_controls.issubset(found_controls),
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.assertEqual(form['sortorder:utf8:string'], '100')
        self.assertEqual(form['releasedate'], DateTime().strftime('%d/%m/%Y'))

        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['title:utf8:string'] = 'test_url'
        form['description:utf8:string'] = 'test_url_description'
        form['coverage:utf8:string'] = 'test_url_coverage'
        form['keywords:utf8:string'] = 'keyw1, keyw2'
        form['locator:utf8:string'] = 'http://www.eaudeweb.ro'
        form['redirect:boolean'] = []

        self.browser.submit()
        html = self.browser.get_html()
        self.assertTrue('The administrator will analyze your request and you will be notified about the result shortly.' in html)

        self.portal.myfolder.test_url.approveThis()

        self.browser.go('http://localhost/portal/myfolder/test_url')
        html = self.browser.get_html()
        self.assertTrue(re.search(r'<h1>.*test_url.*</h1>', html, re.DOTALL))
        self.assertTrue('test_url_description' in html)
        self.assertTrue('test_url_coverage' in html)
        self.assertTrue('keyw1, keyw2' in html)
        self.assertTrue('http://www.eaudeweb.ro' in html)

        self.browser_do_logout()

    def test_add_error(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/url_add_html')

        form = self.browser.get_form('frmAdd')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        # enter no values in the fields
        self.browser.submit()

        html = self.browser.get_html()
        self.assertTrue('The form contains errors' in html)
        self.assertTrue('Value required for "Title"' in html)

    def test_edit(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder/myurl/edit_html')
        form = self.browser.get_form('frmEdit')

        self.assertEqual(form['title:utf8:string'], 'My url')

        form['title:utf8:string'] = 'new_url_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:string'))
        self.browser.submit()

        self.assertEqual(self.portal.myfolder.myurl.title, 'new_url_title')

        self.browser.go('http://localhost/portal/myfolder/myurl/edit_html?lang=fr')
        form = self.browser.get_form('frmEdit')
        form['title:utf8:string'] = 'french_title'
        form['locator:utf8:string'] = 'http://www.eaudeweb.ro/?lang=fr'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:string'))
        self.browser.submit()

        self.assertEqual(self.portal.myfolder.myurl.title, 'new_url_title')
        self.assertEqual(self.portal.myfolder.myurl.locator, 'http://www.eaudeweb.ro')
        self.assertEqual(self.portal.myfolder.myurl.getLocalProperty('title', 'fr'), 'french_title')
        self.assertEqual(self.portal.myfolder.myurl.getLocalProperty('locator', 'fr'), 'http://www.eaudeweb.ro/?lang=fr')

        # try out redirecting
        self.browser.go('http://localhost/portal/myfolder/myurl/edit_html')
        form = self.browser.get_form('frmEdit')
        form['redirect:boolean'] = ['on']
        form['locator:utf8:string'] = 'http://localhost/portal/info'
        self.browser.clicked(form, form.find_control('title:utf8:string'))
        self.browser.submit()

        self.browser.go('http://localhost/portal/myfolder/myurl')
        self.assertEqual(self.browser.get_url(), 'http://localhost/portal/info')

        self.browser_do_logout()

    def test_edit_error(self):
        return # this test is disabled
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/myurl/edit_html')

        form = self.browser.get_form('frmEdit')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:string'))
        form['title:utf8:string'] = ''
        self.browser.submit()

        html = self.browser.get_html()
        self.assertTrue('The form contains errors' in html)
        self.assertTrue('Value required for "Title"' in html)

        self.browser_do_logout()

    def test_manage(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder/myurl/manage_edit_html')
        form = self.browser.get_form('frmEdit')
        self.assertEqual(form['title:utf8:string'], 'My url')
        form['title:utf8:string'] = 'new_url_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:string'))
        self.browser.submit()

        self.assertEqual(self.portal.myfolder.myurl.title, 'new_url_title')

        self.browser_do_logout()

    def test_view_in_folder(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder')
        html = self.browser.get_html()
        soup = BeautifulSoup(html, "lxml")

        tables = soup.findAll('table', id='folderfile_list')
        self.assertTrue(len(tables) == 1)

        links_to_url = tables[0].findAll('a', attrs={'href': 'http://localhost/portal/myfolder/myurl'})
        self.assertTrue(len(links_to_url) == 1)
        self.assertTrue(links_to_url[0].string == 'My url')

        self.browser_do_logout()
