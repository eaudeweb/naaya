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
from unittest import TestSuite, makeSuite

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.Naaya.tests.NaayaTestCase import load_test_file

import patchTestEnv

class NyPhotoFunctionalTestCase(NaayaFunctionalTestCase):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        from Products.Naaya.NyFolder import addNyFolder
        from Products.NaayaPhotoArchive.NyPhotoGallery import manage_addNyPhotoGallery
        from Products.NaayaPhotoArchive.NyPhotoFolder import manage_addNyPhotoFolder
        from Products.NaayaPhotoArchive.NyPhoto import addNyPhoto
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)
        manage_addNyPhotoGallery(self.portal.myfolder, id='g', title='My gallery', submitted=1, contributor='admin')
        manage_addNyPhotoFolder(self.portal.myfolder.g, id='f', title='My folder', submitted=1, contributor='admin')
        addNyPhoto(self.portal.myfolder.g.f, id='myphoto', title='My photo', submitted=1, contributor='contributor')
        import transaction; transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder'])
        import transaction; transaction.commit()

    def test_add(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/g/f/photo_add_html')
        self.failUnless('<h1>Photo submission</h1>' in self.browser.get_html())
        form = self.browser.get_form('frmAdd')
        expected_controls = set([
            'lang', 'title:utf8:ustring', 'description:utf8:ustring', 'author:utf8:ustring',
            'source:utf8:ustring', 'releasedate', 'discussion:boolean', 'file',
        ])
        found_controls = set(c.name for c in form.controls)
        self.failUnless(expected_controls.issubset(found_controls),
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['title:utf8:ustring'] = 'test_create_photo'
        form['description:utf8:ustring'] = 'test_photo_description'
        form['author:utf8:ustring'] = 'test_author'
        form['source:utf8:ustring'] = 'test_source'
        form.find_control('file').add_file(load_test_file('data/test.gif', globals()))

        self.browser.submit()
        html = self.browser.get_html()

        self.failUnlessEqual(self.browser.get_url(), 'http://localhost/portal/myfolder/g/f')
        self.failUnless('test_create_photo' in html)

        photo = self.portal.myfolder.g.f['testcreatephoto']
        self.failUnlessEqual(photo.description, 'test_photo_description')
        self.failUnlessEqual(photo.author, 'test_author')
        self.failUnlessEqual(photo.source, 'test_source')
        self.failUnlessEqual(photo.approved, 1)

        self.browser.go('http://localhost/portal/myfolder/g/f/testcreatephoto')
        html = self.browser.get_html()
        self.failUnless(re.search(r'<h1>.*My folder.*</h1>', html, re.DOTALL))
        self.failUnless('image/gif' in html)
        self.failUnless('26.66 KB' in html)
        self.failUnless('test_author' in html)
        self.failUnless('test_source' in html)
        self.failUnless('test_create_photo' in html)

        self.browser.go('http://localhost/portal/myfolder/g/f/testcreatephoto/view?display=Original')
        self.failUnlessEqual(self.browser_get_header('content-type'), 'image/gif')
        self.failUnlessEqual(self.browser.get_html(),
            load_test_file('data/test.gif', globals()).getvalue())

        self.failIf('XSmall-testcreatephoto' in self.portal.myfolder.g.f.testcreatephoto.objectIds())
        self.browser.go('http://localhost/portal/myfolder/g/f/testcreatephoto/view?display=XSmall')
        self.failUnless('XSmall-testcreatephoto' in self.portal.myfolder.g.f.testcreatephoto.objectIds())

        self.browser_do_logout()

    def test_add_error(self):
        return # NyPhoto items can be created without setting a title
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/g/f/photo_add_html')

        form = self.browser.get_form('frmAdd')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        # enter no values in the fields
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('The form contains errors' in html)
        self.failUnless('Value required for "Title"' in html)

    def test_edit(self):
        self.browser_do_login('contributor', 'contributor')

        self.browser.go('http://localhost/portal/myfolder/g/f/myphoto/edit_html')
        form = self.browser.get_form('frmEdit')

        self.failUnlessEqual(form['title:utf8:ustring'], 'My photo')

        form['title:utf8:ustring'] = 'new_photo_title'

        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()
        html = self.browser.get_html()
        self.failUnless('<h1>Edit photo</h1>' in html)

        self.failUnlessEqual(self.portal.myfolder.g.f.myphoto.title, 'new_photo_title')
        self.portal.myfolder.g.f.myphoto.approveThis()

        self.browser.go('http://localhost/portal/myfolder/g/f/myphoto/edit_html?lang=fr')
        form = self.browser.get_form('frmEdit')
        form['title:utf8:ustring'] = 'french_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.g.f.myphoto.title, 'new_photo_title')
        self.failUnlessEqual(self.portal.myfolder.g.f.myphoto.getLocalProperty('title', 'fr'), 'french_title')

        self.browser_do_logout()

    def test_edit_error(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/g/f/myphoto/edit_html')

        form = self.browser.get_form('frmEdit')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        form['title:utf8:ustring'] = ''
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('The form contains errors' in html)
        self.failUnless('Value required for "Title"' in html)

        self.browser_do_logout()

    def test_manage(self):
        return #TODO: photo has no manageProperties method
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder/g/f/myphoto/manage_edit_html')
        form = self.browser.get_form('frmEdit')
        self.failUnlessEqual(form['title:utf8:ustring'], 'My photo')
        form['title:utf8:ustring'] = 'new_photo_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.g.f.myphoto.title, 'new_photo_title')

        self.browser_do_logout()

    def test_photo_thumbnails(self):
        import StringIO
        from PIL import Image
        picture = load_test_file('data/pink.png', globals())
        self.portal.myfolder.g.f.myphoto.update_data(picture)
        import transaction; transaction.commit()
        picture.seek(0)
        picture = Image.open(picture)

        self.browser.go('http://localhost/portal/myfolder/g/f/myphoto/view?display=Gallery')
        gallery_picture = StringIO.StringIO(self.browser.get_html())
        gallery_picture.seek(0)
        gallery_picture = Image.open(gallery_picture)
        self.failUnlessEqual(gallery_picture.tostring(), picture.resize((200, 200)).tostring())

        self.browser.go('http://localhost/portal/myfolder/g/f/myphoto/view?display=Album')
        album_picture = StringIO.StringIO(self.browser.get_html())
        album_picture.seek(0)
        album_picture = Image.open(album_picture)
        self.failUnlessEqual(album_picture.tostring(), picture.resize((100, 100)).tostring())


        picture_formats = [
                {'size': 'XSmall', 'width': 200, 'height': 200},
                {'size': 'Small', 'width': 320, 'height': 320},
                {'size': 'Medium', 'width': 480, 'height': 480},
                {'size': 'Large', 'width': 768, 'height': 768},
                {'size': 'XLarge', 'width': 1024, 'height': 1024},
                {'size': 'Original', 'width': 5, 'height': 5}
        ]

        for format in picture_formats:
            self.browser.go('http://localhost/portal/myfolder/g/f/myphoto/?display=%s&view%%3Amethod=View' % format['size'])
            pic = StringIO.StringIO(self.browser.get_html())
            pic.seek(0)
            pic = Image.open(pic)
            self.failUnlessEqual(pic.tostring(), picture.resize((format['width'], format['height'])).tostring())


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NyPhotoFunctionalTestCase))
    return suite
