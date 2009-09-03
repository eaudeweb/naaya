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

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

class NyDocumentFunctionalTestCase(NaayaFunctionalTestCase):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        from Products.Naaya.NyFolder import addNyFolder
        from Products.NaayaContent.NyDocument.NyDocument import addNyDocument
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
        self.failUnless('<h1>Thank you for your submission</h1>' in html)

        self.portal.info.testdoc.approveThis()

        self.browser.go('http://localhost/portal/info/testdoc')
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

class NyDocumentVersioningFunctionalTestCase(NaayaFunctionalTestCase):
    """ TestCase for NaayaContent object """
    def afterSetUp(self):
        from Products.NaayaContent.NyDocument.NyDocument import addNyDocument
        addNyDocument(self.portal.info, id='ver_doc', title='ver_doc', submitted=1)
        import transaction; transaction.commit()

    def beforeTearDown(self):
        self.portal.info.manage_delObjects(['ver_doc'])
        import transaction; transaction.commit()

    def test_start_version(self):
        from Products.NaayaContent.NyDocument.document_item import document_item
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

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NyDocumentFunctionalTestCase))
    suite.addTest(makeSuite(NyDocumentVersioningFunctionalTestCase))
    return suite
