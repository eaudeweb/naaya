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

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

from . import patchTestEnv

def load_file(filename):
    import os
    from io import BytesIO
    pass  # package_home import removed (unused)
    filename = os.path.sep.join([os.path.dirname(os.path.abspath(__file__)), filename])
    with open(filename, 'rb') as f:
        data = BytesIO(f.read())
    data.filename = os.path.basename(filename)
    return data

class NyPhotoFunctionalTestCase(NaayaFunctionalTestCase):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        from Products.Naaya.NyFolder import addNyFolder
        from Products.NaayaPhotoArchive.NyPhotoGallery import addNyPhotoGallery
        from Products.NaayaPhotoArchive.NyPhotoFolder import addNyPhotoFolder
        from Products.NaayaPhotoArchive.NyPhoto import addNyPhoto
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)
        addNyPhotoGallery(self.portal.myfolder, id='g', title='My gallery', submitted=1, contributor='admin')
        addNyPhotoFolder(self.portal.myfolder.g, id='f', title='My folder', submitted=1, contributor='admin')
        addNyPhoto(self.portal.myfolder.g.f, id='myphoto', title='My photo', submitted=1, contributor='contributor')
        import transaction; transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder'])
        import transaction; transaction.commit()

    def test_add(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/g/f/photo_add_html')
        self.assertTrue('<h1>Photo submission</h1>' in self.browser.get_html())
        form = self.browser.get_form('frmAdd')
        expected_controls = set([
            'lang', 'title:utf8:string', 'description:utf8:string', 'author:utf8:string',
            'source:utf8:string', 'releasedate', 'discussion:boolean', 'file',
        ])
        found_controls = set(c.name for c in form.controls)
        self.assertTrue(expected_controls.issubset(found_controls),
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['title:utf8:string'] = 'test_create_photo'
        form['description:utf8:string'] = 'test_photo_description'
        form['author:utf8:string'] = 'test_author'
        form['source:utf8:string'] = 'test_source'
        form.find_control('file').add_file(load_file('data/test.gif'))

        self.browser.submit()
        html = self.browser.get_html()

        self.assertEqual(self.browser.get_url(), 'http://localhost/portal/myfolder/g/f')
        self.assertTrue('test_create_photo' in html)

        photo = self.portal.myfolder.g.f['test_create_photo']
        self.assertEqual(photo.description, 'test_photo_description')
        self.assertEqual(photo.author, 'test_author')
        self.assertEqual(photo.source, 'test_source')
        self.assertEqual(photo.approved, 1)

        self.browser.go('http://localhost/portal/myfolder/g/f/test_create_photo')
        html = self.browser.get_html()
        self.assertTrue(re.search(r'<h1>.*My folder.*</h1>', html, re.DOTALL))
        self.assertTrue('image/gif' in html)
        self.assertTrue('26.66 KB' in html)
        self.assertTrue('test_author' in html)
        self.assertTrue('test_source' in html)
        self.assertTrue('test_create_photo' in html)

        self.browser.go('http://localhost/portal/myfolder/g/f/test_create_photo/view?display=Original')
        self.assertEqual(self.browser_get_header('content-type'), 'image/gif')
        self.assertEqual(self.browser.result.content,
            load_file('data/test.gif').getvalue())

        self.assertFalse('XSmall-test_create_photo' in
                     self.portal.myfolder.g.f.test_create_photo.objectIds())
        self.browser.go('http://localhost/portal/myfolder/g/f/test_create_photo/view?display=XSmall')
        self.assertTrue('XSmall-test_create_photo' in
                         self.portal.myfolder.g.f.test_create_photo.objectIds())

        self.browser_do_logout()

    def test_edit(self):
        self.browser_do_login('contributor', 'contributor')

        self.browser.go('http://localhost/portal/myfolder/g/f/myphoto/edit_html')
        form = self.browser.get_form('frmEdit')

        self.assertEqual(form['title:utf8:string'], 'My photo')

        form['title:utf8:string'] = 'new_photo_title'

        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:string'))
        self.browser.submit()
        html = self.browser.get_html()
        self.assertTrue('<h1>Edit photo</h1>' in html)

        self.assertEqual(self.portal.myfolder.g.f.myphoto.title, 'new_photo_title')
        self.portal.myfolder.g.f.myphoto.approveThis()

        self.browser.go('http://localhost/portal/myfolder/g/f/myphoto/edit_html?lang=fr')
        form = self.browser.get_form('frmEdit')
        form['title:utf8:string'] = 'french_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:string'))
        self.browser.submit()

        self.assertEqual(self.portal.myfolder.g.f.myphoto.title, 'new_photo_title')
        self.assertEqual(self.portal.myfolder.g.f.myphoto.getLocalProperty('title', 'fr'), 'french_title')

        self.browser_do_logout()

    def test_edit_error(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/g/f/myphoto/edit_html')

        form = self.browser.get_form('frmEdit')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:string'))
        form['title:utf8:string'] = ''
        self.browser.submit()

        html = self.browser.get_html()
        self.assertTrue('The form contains errors' in html)
        self.assertTrue('Value required for "Title"' in html)

        self.browser_do_logout()

    def test_update_data_str(self):
        photo = self.portal.myfolder.g.f.myphoto
        photo.update_data('caf\xe9')
        original = photo._getOb('myphoto')
        self.assertEqual(original.size, 5)
        self.assertEqual(original.open().read(), 'caf\xe9'.encode('utf-8'))

    def test_watermark_display(self):
        from io import BytesIO
        from PIL import Image
        photo = self.portal.myfolder.g.f.myphoto
        photo.update_data(load_file('data/test.gif'))
        import transaction; transaction.commit()
        url = 'http://localhost/portal/myfolder/g/f/myphoto/view?display=Small'
        self.browser.go(url)
        plain = Image.open(BytesIO(self.browser.result.content))

        self.portal.myfolder.g.f.watermark_text = 'Naaya'
        transaction.commit()
        self.browser.go(url)
        marked = Image.open(BytesIO(self.browser.result.content))
        self.assertEqual(marked.size, plain.size)
        self.assertNotEqual(marked.convert('RGB').tobytes(),
                            plain.convert('RGB').tobytes())
        self.assertIn('watermark-Small-myphoto', photo.objectIds())

    def test_photo_thumbnails(self):
        from io import BytesIO
        from PIL import Image
        picture = load_file('data/pink.png')
        self.portal.myfolder.g.f.myphoto.update_data(picture)
        import transaction; transaction.commit()
        picture.seek(0)
        picture = Image.open(picture)

        self.browser.go('http://localhost/portal/myfolder/g/f/myphoto/view?display=Gallery')
        gallery_picture = BytesIO(self.browser.result.content)
        gallery_picture.seek(0)
        gallery_picture = Image.open(gallery_picture)
        self.assertEqual(gallery_picture.tobytes(), picture.resize((200, 200)).tobytes())

        self.browser.go('http://localhost/portal/myfolder/g/f/myphoto/view?display=Album')
        album_picture = BytesIO(self.browser.result.content)
        album_picture.seek(0)
        album_picture = Image.open(album_picture)
        self.assertEqual(album_picture.tobytes(), picture.resize((100, 100)).tobytes())


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
            pic = BytesIO(self.browser.result.content)
            pic.seek(0)
            pic = Image.open(pic)
            self.assertEqual(pic.tobytes(), picture.resize((format['width'], format['height'])).tobytes())


def test_suite():
    suite = TestSuite()
    suite.addTest(TestLoader().loadTestsFromTestCase(NyPhotoFunctionalTestCase))
    return suite
