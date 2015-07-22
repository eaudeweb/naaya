import re
from unittest import TestSuite, makeSuite

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

class NyPointerFunctionalTestCase(NaayaFunctionalTestCase):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        from Products.Naaya.NyFolder import addNyFolder
        from Products.NaayaContent.NyPointer.NyPointer import addNyPointer
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)
        addNyPointer(self.portal.myfolder, id='mypointer', title='My pointer',
            pointer='http://www.eaudeweb.ro', submitted=1, contributor='contributor')
        import transaction; transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder'])
        import transaction; transaction.commit()

    def test_add(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/pointer_add_html')
        self.failUnless('<h1>Submit Pointer</h1>' in self.browser.get_html())
        form = self.browser.get_form('frmAdd')
        expected_controls = set([
            'lang', 'title:utf8:ustring', 'description:utf8:ustring', 'coverage:utf8:ustring',
            'keywords:utf8:ustring', 'releasedate', 'pointer:utf8:ustring',
        ])
        found_controls = set(c.name for c in form.controls)
        self.failUnless(expected_controls.issubset(found_controls),
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['title:utf8:ustring'] = 'test_pointer'
        form['description:utf8:ustring'] = 'test_pointer_description'
        form['coverage:utf8:ustring'] = 'test_pointer_coverage'
        form['keywords:utf8:ustring'] = 'keyw1, keyw2'
        form['pointer:utf8:ustring'] = 'portal'
        form['redirect:boolean'] = []

        self.browser.submit()
        html = self.browser.get_html()
        self.failUnless('<h1>Thank you for your submission</h1>' in html)

        self.portal.myfolder.testpointer.approveThis()

        self.browser.go('http://localhost/portal/myfolder/testpointer')
        html = self.browser.get_html()
        self.failUnless(re.search(r'<h1>.*test_pointer.*</h1>', html, re.DOTALL))
        self.failUnless('test_pointer_description' in html)

        self.browser_do_logout()

    def test_add_error(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/pointer_add_html')

        form = self.browser.get_form('frmAdd')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        # enter no values in the fields
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('The form contains errors' in html)
        self.failUnless('Value required for "Title"' in html)

    def test_edit(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder/mypointer/edit_html')
        form = self.browser.get_form('frmEdit')

        self.failUnlessEqual(form['title:utf8:ustring'], 'My pointer')

        form['title:utf8:ustring'] = 'new_pointer_title'
        form['pointer:utf8:ustring'] = 'portal'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.mypointer.title, 'new_pointer_title')
        self.failUnlessEqual(self.portal.myfolder.mypointer.pointer, 'portal')

        # try out redirecting
        self.browser.go('http://localhost/portal/myfolder/mypointer/edit_html')
        form = self.browser.get_form('frmEdit')
        form['redirect:boolean'] = ['on']
        form['pointer:utf8:ustring'] = 'portal/info'
        self.browser.clicked(form, form.find_control('title:utf8:ustring'))
        self.browser.submit()

        self.browser.go('http://localhost/portal/myfolder/mypointer')
        self.failUnlessEqual(self.browser.get_url(), 'http://localhost/portal/info')

        self.browser_do_logout()

    def test_edit_error(self):
        return # this test is disabled
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/mypointer/edit_html')

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

        self.browser.go('http://localhost/portal/myfolder/mypointer/manage_edit_html')
        form = self.browser.get_form('frmEdit')
        self.failUnlessEqual(form['title:utf8:ustring'], 'My pointer')
        form['title:utf8:ustring'] = 'new_pointer_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.mypointer.title, 'new_pointer_title')

        self.browser_do_logout()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NyPointerFunctionalTestCase))
    return suite
