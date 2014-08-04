import re
from unittest import TestSuite, makeSuite
from BeautifulSoup import BeautifulSoup

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

class NyDocumentFunctionalTestCase(NaayaFunctionalTestCase):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        from Products.Naaya.NyFolder import addNyFolder
        from naaya.content.document.document_item import addNyDocument
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)
        addNyDocument(self.portal.myfolder, id='mydoc', title='My document', submitted=1, contributor='contributor')
        import transaction; transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder'])
        import transaction; transaction.commit()

    def test_add(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/info/document_add')
        self.failUnless('<h1>Submit HTML Document</h1>' in self.browser.get_html())
        form = self.browser.get_form('frmAdd')
        expected_controls = set([
            'lang', 'title:utf8:ustring', 'description:utf8:ustring', 'coverage:utf8:ustring',
            'keywords:utf8:ustring', 'releasedate', 'discussion:boolean',
        ])
        found_controls = set(c.name for c in form.controls)
        self.failUnless(expected_controls.issubset(found_controls),
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['title:utf8:ustring'] = 'test_doc'
        form['description:utf8:ustring'] = 'test_doc_description'
        form['coverage:utf8:ustring'] = 'test_doc_coverage'
        form['keywords:utf8:ustring'] = 'keyw1, keyw2'
        form['body:utf8:ustring'] = 'test_doc_body'

        self.browser.submit()
        html = self.browser.get_html()
        self.failUnless('The administrator will analyze your request and you will be notified about the result shortly.' in html)

        self.portal.info.test_doc.approveThis()

        self.browser.go('http://localhost/portal/info/test_doc')
        html = self.browser.get_html()
        self.failUnless(re.search(r'<h1>.*test_doc.*</h1>', html, re.DOTALL))
        self.failUnless('test_doc_description' in html)
        self.failUnless('test_doc_coverage' in html)
        self.failUnless('keyw1, keyw2' in html)
        self.failUnless('test_doc_body' in html)

        self.browser_do_logout()

    def test_add_error(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/document_add')

        form = self.browser.get_form('frmAdd')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        # enter no values in the fields
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('The form contains errors' in html)
        self.failUnless('Value required for "Title"' in html)

    def test_edit(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder/mydoc/edit_html')
        form = self.browser.get_form('frmEdit')

        self.failUnlessEqual(form['title:utf8:ustring'], 'My document')

        form['title:utf8:ustring'] = 'new_doc_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.mydoc.title, 'new_doc_title')

        self.browser.go('http://localhost/portal/myfolder/mydoc/edit_html?lang=fr')
        form = self.browser.get_form('frmEdit')
        form['title:utf8:ustring'] = 'french_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.mydoc.title, 'new_doc_title')
        self.failUnlessEqual(self.portal.myfolder.mydoc.getLocalProperty('title', 'fr'), 'french_title')

        self.browser_do_logout()

    def test_edit_error(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/mydoc/edit_html')

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

        self.browser.go('http://localhost/portal/myfolder/mydoc/manage_edit_html')
        form = self.browser.get_form('frmEdit')
        self.failUnlessEqual(form['title:utf8:ustring'], 'My document')
        form['title:utf8:ustring'] = 'new_doc_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.mydoc.title, 'new_doc_title')

        self.browser_do_logout()

    def test_view_in_folder(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)

        tables = soup.findAll('table', id='folderfile_list')
        self.assertTrue(len(tables) == 1)

        links_to_document = tables[0].findAll('a', attrs={'href': 'http://localhost/portal/myfolder/mydoc'})
        self.assertTrue(len(links_to_document) == 1)
        self.assertTrue(links_to_document[0].string == 'My document')

        self.browser_do_logout()

class NyDocumentVersioningFunctionalTestCase(NaayaFunctionalTestCase):
    """ TestCase for NaayaContent object """
    def afterSetUp(self):
        from naaya.content.document.document_item import addNyDocument
        addNyDocument(self.portal.info, id='ver_doc', title='ver_doc', submitted=1)
        import transaction; transaction.commit()

    def beforeTearDown(self):
        self.portal.info.manage_delObjects(['ver_doc'])
        import transaction; transaction.commit()

    def test_start_version(self):
        from naaya.content.document.document_item import document_item
        self.browser_do_login('admin', '')
        self.failUnlessEqual(self.portal.info.ver_doc.version, None)
        self.browser.go('http://localhost/portal/info/ver_doc/startVersion')
        self.failUnless(isinstance(self.portal.info.ver_doc.version, document_item))
        self.browser_do_logout()

    def test_edit_version(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/ver_doc/startVersion')

        form = self.browser.get_form('frmEdit')
        form['title:utf8:ustring'] = 'ver_doc_newtitle'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        ver_doc = self.portal.info.ver_doc
        self.failUnlessEqual(ver_doc.title, 'ver_doc')
        # we can't do ver_doc.version.title because version objects don't have the _languages property
        self.failUnlessEqual(ver_doc.version.getLocalProperty('title', 'en'), 'ver_doc_newtitle')

        self.browser_do_logout()

    def test_save_changes_version(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/ver_doc/startVersion')

        form = self.browser.get_form('frmEdit')
        form['title:utf8:ustring'] = 'ver_doc_version'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        form = self.browser.get_form('frmEdit')
        self.failUnlessEqual(form['title:utf8:ustring'], 'ver_doc_version')

        self.browser_do_logout()
