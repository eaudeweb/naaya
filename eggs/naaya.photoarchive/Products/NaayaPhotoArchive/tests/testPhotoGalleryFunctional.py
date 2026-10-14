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
# David Batranu, Eau de Web

import re
from unittest import TestSuite, TestLoader

from Testing import ZopeTestCase
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

from . import patchTestEnv


class NyPhotoGalleryFunctionalTestCase(NaayaFunctionalTestCase):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        from Products.Naaya.NyFolder import addNyFolder
        from Products.NaayaPhotoArchive.NyPhotoGallery import addNyPhotoGallery
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)
        addNyPhotoGallery(self.portal.myfolder, id='mygallery', title='My photo gallery', submitted=1, contributor='contributor')
        import transaction; transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder'])
        import transaction; transaction.commit()

    def test_add(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/gallery_add_html')
        self.assertTrue('<h1>Submit photo gallery</h1>' in self.browser.get_html())
        form = self.browser.get_form('frmAdd')
        expected_controls = set([
            'lang', 'title:utf8:string', 'description:utf8:string', 'coverage:utf8:string',
            'keywords:utf8:string', 'releasedate', 'discussion:boolean',
        ])
        found_controls = set(c.name for c in form.controls)
        self.assertTrue(expected_controls.issubset(found_controls),
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['title:utf8:string'] = 'test_create_gallery'
        form['description:utf8:string'] = 'test_gallery_description'
        form['coverage:utf8:string'] = 'test_gallery_coverage'
        form['keywords:utf8:string'] = 'keyw1, keyw2'

        self.browser.submit()
        html = self.browser.get_html()

        self.assertEqual(self.browser.get_url(), 'http://localhost/portal/myfolder')
        self.assertTrue('test_create_gallery' in html)

        gallery = self.portal.myfolder['test_create_gallery']
        self.assertEqual(gallery.description, 'test_gallery_description')
        self.assertEqual(gallery.coverage, 'test_gallery_coverage')
        self.assertEqual(gallery.keywords, 'keyw1, keyw2')
        gallery.approveThis()

        self.browser.go('http://localhost/portal/myfolder/test_create_gallery')
        html = self.browser.get_html()
        self.assertTrue(re.search(r'<h1>.*test_create_gallery.*</h1>', html, re.DOTALL))

        self.browser_do_logout()

    def test_add_error(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/gallery_add_html')

        form = self.browser.get_form('frmAdd')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        # enter no values in the fields
        self.browser.submit()

        html = self.browser.get_html()
        self.assertTrue('The form contains errors' in html)
        self.assertTrue('Value required for "Title"' in html)

    def test_edit(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder/mygallery/edit_html')
        form = self.browser.get_form('frmEdit')

        self.assertEqual(form['title:utf8:string'], 'My photo gallery')

        form['title:utf8:string'] = 'new_gallery_title'

        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:string'))
        self.browser.submit()
        html = self.browser.get_html()
        self.assertTrue('<h1>Edit photo gallery</h1>' in html)

        self.assertEqual(self.portal.myfolder.mygallery.title, 'new_gallery_title')
        self.portal.myfolder.mygallery.approveThis()

        self.browser.go('http://localhost/portal/myfolder/mygallery/edit_html?lang=fr')
        form = self.browser.get_form('frmEdit')
        form['title:utf8:string'] = 'french_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:string'))
        self.browser.submit()

        self.assertEqual(self.portal.myfolder.mygallery.title, 'new_gallery_title')
        self.assertEqual(self.portal.myfolder.mygallery.getLocalProperty('title', 'fr'), 'french_title')

        self.browser_do_logout()

    def test_edit_error(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/mygallery/edit_html')

        form = self.browser.get_form('frmEdit')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:string'))
        form['title:utf8:string'] = ''
        self.browser.submit()

        html = self.browser.get_html()
        self.assertTrue('The form contains errors' in html)
        self.assertTrue('Value required for "Title"' in html)

        self.browser_do_logout()

    def test_manage(self):
        return #TODO: photo gallery has no manageProperties method
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder/mygallery/manage_edit_html')
        form = self.browser.get_form('frmEdit')
        self.assertEqual(form['title:utf8:string'], 'My photo gallery')
        form['title:utf8:string'] = 'new_gallery_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:string'))
        self.browser.submit()

        self.assertEqual(self.portal.myfolder.mygallery.title, 'new_gallery_title')

        self.browser_do_logout()

def test_suite():
    suite = TestSuite()
    suite.addTest(TestLoader().loadTestsFromTestCase(NyPhotoGalleryFunctionalTestCase))
    return suite
