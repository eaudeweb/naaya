import re
from unittest import TestSuite, makeSuite
from BeautifulSoup import BeautifulSoup

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

class NyBlogEntryFunctionalTestCase(NaayaFunctionalTestCase):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        self.portal.manage_install_pluggableitem('Naaya Blog Entry')
        from Products.Naaya.NyFolder import addNyFolder
        from Products.NaayaContent.NyBlogEntry.NyBlogEntry import addNyBlogEntry
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)
        self.portal.myfolder._Naaya___Add_Naaya_Blog_Entry_objects_Permission = ['Contributor',]
        addNyBlogEntry(self.portal.myfolder, id='myentry', title='My entry',
                       submitted=1, contributor='contributor')
        import transaction; transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder'])
        import transaction; transaction.commit()

    def test_add(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/blog_entry_add_html')
        self.failUnless('<h1>Submit Blog Entry</h1>' in self.browser.get_html())
        form = self.browser.get_form('frmAdd')
        expected_controls = set([
            'lang', 'title:utf8:ustring', 'keywords:utf8:ustring',
            'releasedate', 'content:utf8:ustring',
        ])
        found_controls = set(c.name for c in form.controls)
        self.failUnless(expected_controls.issubset(found_controls),
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['title:utf8:ustring'] = 'test_entry'
        form['content:utf8:ustring'] = 'test_entry_content'
        form['keywords:utf8:ustring'] = 'keyw1, keyw2'

        self.browser.submit()
        html = self.browser.get_html()
        self.failUnless('The administrator will analyze your request and you will be notified about the result shortly.' in html)

        self.portal.myfolder.test_entry.approveThis()

        self.browser.go('http://localhost/portal/myfolder/test_entry')
        html = self.browser.get_html()
        self.failUnless(re.search(r'<h1>.*test_entry.*</h1>', html, re.DOTALL))
        self.failUnless('test_entry_content' in html)
        self.failUnless('keyw1, keyw2' in html)

        self.browser_do_logout()

    def test_add_error(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/blog_entry_add_html')

        form = self.browser.get_form('frmAdd')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        # enter no values in the fields
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('The form contains errors' in html)
        self.failUnless('Value required for "Headline"' in html)

    def test_edit(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder/myentry/edit_html')
        form = self.browser.get_form('frmEdit')

        self.failUnlessEqual(form['title:utf8:ustring'], 'My entry')

        form['title:utf8:ustring'] = 'new_entry_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.myentry.title, 'new_entry_title')

        self.browser.go('http://localhost/portal/myfolder/myentry/edit_html?lang=fr')
        form = self.browser.get_form('frmEdit')
        form['title:utf8:ustring'] = 'french_entry_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.myentry.title, 'new_entry_title')
        self.failUnlessEqual(self.portal.myfolder.myentry.getLocalProperty('title', 'fr'), 'french_entry_title')

        self.browser_do_logout()


    def test_manage(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder/myentry/manage_edit_html')
        form = self.browser.get_form('frmEdit')
        self.failUnlessEqual(form['title:utf8:ustring'], 'My entry')
        form['title:utf8:ustring'] = 'new_entry_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.myentry.title, 'new_entry_title')

        self.browser_do_logout()

    def test_view_in_folder(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)

        tables = soup.findAll('table', id='folderfile_list')
        self.assertTrue(len(tables) == 1)

        links_to_entry = tables[0].findAll('a', attrs={'href': 'http://localhost/portal/myfolder/myentry'})
        self.assertTrue(len(links_to_entry) == 1)
        self.assertTrue(links_to_entry[0].string == 'My entry')

        self.browser_do_logout()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NyBlogEntryFunctionalTestCase))
    return suite
