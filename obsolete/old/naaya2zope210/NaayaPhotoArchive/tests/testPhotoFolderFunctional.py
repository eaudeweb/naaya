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
import zipfile
from StringIO import StringIO

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.Naaya.tests.NaayaTestCase import load_test_file

from Products.NaayaPhotoArchive.NyPhotoGallery import manage_addNyPhotoGallery
from Products.NaayaPhotoArchive.NyPhotoFolder import manage_addNyPhotoFolder
from Products.NaayaPhotoArchive.NyPhoto import addNyPhoto

import patchTestEnv


class NyPhotoFolderFunctionalTestCase(NaayaFunctionalTestCase):
    """ TestCase for the PhotoArchive product"""

    def afterSetUp(self):
        from Products.Naaya.NyFolder import addNyFolder
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)
        manage_addNyPhotoGallery(self.portal.myfolder, id='mygallery', title='My photo gallery', submitted=1, contributor='contributor')
        manage_addNyPhotoFolder(self.portal.myfolder.mygallery, id='myalbum', title='My photo album')
        addNyPhoto(self.portal.myfolder.mygallery.myalbum, id="myphoto1", title="My photo 1")
        addNyPhoto(self.portal.myfolder.mygallery.myalbum, id="myphoto2", title="My photo 2")
        self.portal.myfolder.approveThis()
        import transaction; transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder'])
        import transaction; transaction.commit()

    def test_add(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/mygallery/photofolder_add_html')
        self.failUnless('<h1>Submit album</h1>' in self.browser.get_html())
        form = self.browser.get_form('frmAdd')
        expected_controls = set([
            'lang', 'title:utf8:ustring', 'description:utf8:ustring', 'coverage:utf8:ustring',
            'keywords:utf8:ustring', 'releasedate', 'discussion:boolean',
            'author:utf8:ustring', 'source:utf8:ustring', 'file', 
        ])
        found_controls = set(c.name for c in form.controls)
        self.failUnless(expected_controls.issubset(found_controls),
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        form['title:utf8:ustring'] = 'test_create_album'
        form['description:utf8:ustring'] = 'test_album_description'
        form['coverage:utf8:ustring'] = 'test_album_coverage'
        form['keywords:utf8:ustring'] = 'keyw1, keyw2'
        form['author:utf8:ustring'] = 'test_album_author'
        form['source:utf8:ustring'] = 'test_album_source'

        picture = load_test_file('data/pink.png', globals())
        form.find_control('file').add_file(picture, filename="albumphoto.png", content_type='image/png')

        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnlessEqual(self.browser.get_url(), 'http://localhost/portal/myfolder/mygallery')
        self.failUnless('test_create_album' in html)

        album = self.portal.myfolder.mygallery['testcreatealbum']
        self.failUnlessEqual(album.description, 'test_album_description')
        self.failUnlessEqual(album.coverage, 'test_album_coverage')
        self.failUnlessEqual(album.keywords, 'keyw1, keyw2')
        self.failUnlessEqual(album.author, 'test_album_author')
        self.failUnlessEqual(album.source, 'test_album_source')

        self.browser.go('http://localhost/portal/myfolder/mygallery/testcreatealbum')
        html = self.browser.get_html()
        self.failUnless(re.search(r'<h1>.*test_create_album.*</h1>', html, re.DOTALL))
        self.failUnless('albumphoto.png' in html)
        self.failUnless('albumphoto.png' in album.objectIds())

        self.browser_do_logout()

    def test_add_with_zip(self):
        """ Test album adding with pictures submitted as zip archive """
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/mygallery/photofolder_add_html')
        form = self.browser.get_form('frmAdd')

        form['title:utf8:ustring'] = 'test_create_album_zip'

        pictures_zip = load_test_file('data/test.zip', globals())
        form.find_control('file').add_file(pictures_zip, filename="photos.zip", content_type='application/octet-stream')

        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        self.browser.submit()


        self.browser.go('http://localhost/portal/myfolder/mygallery/testcreatealbumzip')
        html = self.browser.get_html()
        self.failUnless(re.search(r'<h1>.*test_create_album_zip.*</h1>', html, re.DOTALL))

        album = self.portal.myfolder.mygallery['testcreatealbumzip']
        pics_in_zip = ['a.gif', 'b.gif', 'c-d.gif', 'd and d.gif', 'e-34.gif', 'k.gif']
        for pic in pics_in_zip:
            self.failUnless(pic in html)

        pics_ids = ['a.gif', 'b.gif', 'c-d.gif', 'd_and_d.gif', 'e-34.gif', 'k.gif']
        for pic in pics_ids:
            self.failUnless(pic in album.objectIds())
            self.failUnlessEqual(album[pic].approved, 1)

        self.browser_do_logout()

    def test_change_cover(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/mygallery/myalbum/changecover_html')
        html = self.browser.get_html()
        self.failUnless(re.search(r'<h1>.*Change cover.*</h1>', html, re.DOTALL))

        form = self.browser.get_form(2)
        form['cover'] = ['myphoto2']
        self.browser.clicked(form, 'cover')
        self.browser.submit()

        self.failUnlessEqual(self.browser.get_url(), 'http://localhost/portal/myfolder/mygallery/myalbum')

        self.browser.go('http://localhost/portal/myfolder/mygallery')
        html = self.browser.get_html()
        self.failUnless(re.search(r'<img src="http://localhost/portal/myfolder/mygallery/'
                                   'myalbum/myphoto2/view\?display=Gallery"\s+alt="My photo album" />', html))

        self.browser_do_logout()

    def test_add_error(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/mygallery/photofolder_add_html')

        form = self.browser.get_form('frmAdd')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        # enter no values in the fields
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('The form contains errors' in html)
        self.failUnless('Value required for "Title"' in html)

    def test_edit(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder/mygallery/myalbum/edit_html')
        form = self.browser.get_form('frmEdit')

        self.failUnlessEqual(form['title:utf8:ustring'], 'My photo album')

        form['title:utf8:ustring'] = 'new_album_title'

        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()
        html = self.browser.get_html()
        self.failUnless('<h1>Edit album</h1>' in html)

        self.failUnlessEqual(self.portal.myfolder.mygallery.myalbum.title, 'new_album_title')

        self.browser.go('http://localhost/portal/myfolder/mygallery/myalbum/edit_html?lang=fr')
        form = self.browser.get_form('frmEdit')
        form['title:utf8:ustring'] = 'french_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.mygallery.myalbum.title, 'new_album_title')
        self.failUnlessEqual(self.portal.myfolder.mygallery.myalbum.getLocalProperty('title', 'fr'), 'french_title')

        self.browser_do_logout()

    def test_edit_error(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/mygallery/myalbum/edit_html')

        form = self.browser.get_form('frmEdit')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        form['title:utf8:ustring'] = ''
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('The form contains errors' in html)
        self.failUnless('Value required for "Title"' in html)

        self.browser_do_logout()

    def test_manage(self):
        return #TODO: photo gallery has no saveProperties method
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder/mygallery/myalbum/manage_edit_html')
        form = self.browser.get_form('frmEdit')
        self.failUnlessEqual(form['title:utf8:ustring'], 'My photo album')
        form['title:utf8:ustring'] = 'new_album_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.mygallery.title, 'new_album_title')

        self.browser_do_logout()

    def test_download_zip_all(self):
        myphoto1 = load_test_file('data/pink.png', globals())
        self.portal.myfolder.mygallery.myalbum.myphoto1.update_data(myphoto1)

        myphoto2 = load_test_file('data/test.gif', globals())
        self.portal.myfolder.mygallery.myalbum.myphoto2.update_data(myphoto2)
        import transaction; transaction.commit()

        self.browser.go('http://localhost/portal/myfolder/mygallery/myalbum')
        form = self.browser.get_form(3)
        form['download'] = ['all']
        self.browser.clicked(form, 'downloadObjects:method')
        self.browser.submit()

        photo_zip = zipfile.ZipFile(StringIO(self.browser.get_html()))

        self.failUnlessEqual(photo_zip.namelist(), ['myalbum.zip/myphoto1', 'myalbum.zip/myphoto2'])
        self.failUnlessEqual(photo_zip.read('myalbum.zip/myphoto1'), myphoto1.getvalue())
        self.failUnlessEqual(photo_zip.read('myalbum.zip/myphoto2'), myphoto2.getvalue())

    def test_download_zip_selected(self):
        myphoto2 = load_test_file('data/test.gif', globals())
        self.portal.myfolder.mygallery.myalbum.myphoto2.update_data(myphoto2)
        import transaction; transaction.commit()

        self.browser.go('http://localhost/portal/myfolder/mygallery/myalbum')
        form = self.browser.get_form(3)
        form['download'] = ['selected']
        form['ids:list'] = ['myphoto2']
        self.browser.clicked(form, 'downloadObjects:method')
        self.browser.submit()

        photo_zip = zipfile.ZipFile(StringIO(self.browser.get_html()))

        self.failUnlessEqual(photo_zip.namelist(), ['myalbum.zip/myphoto2'])
        self.failUnlessEqual(photo_zip.read('myalbum.zip/myphoto2'), myphoto2.getvalue())

    def test_cut_paste(self):
        return #TODO: cannot paste from the test; some photos are not correctly pasted (d and d, e-34, and pasting when id exists)
        photos_zip = load_test_file('data/test.zip', globals())
        manage_addNyPhotoGallery(self.portal.myfolder, id='mygallery2', title='My second photo gallery', submitted=1, contributor='contributor')
        manage_addNyPhotoFolder(self.portal.myfolder.mygallery2, id='myalbum', title='My photo album')
        self.portal.myfolder.mygallery2.myalbum.uploadPhotoOrZip(photos_zip)
        import transaction; transaction.commit()

        album_source = self.portal.myfolder.mygallery2.myalbum
        album_destination = self.portal.myfolder.mygallery.myalbum
        pics = [
            {'zip': 'a.gif' , 'portal': 'a.gif'},
            {'zip': 'b.gif' , 'portal': 'b.gif'},
            {'zip': 'c-d.gif' , 'portal': 'c-d.gif'},
            {'zip': 'd and d.gif' , 'portal': 'd_and_d.gif'},
            {'zip': 'e-34.gif' , 'portal': 'e-34.gif'},
            {'zip': 'k.gif' , 'portal': 'k.gif'},
        ]

        photos_zip = zipfile.ZipFile(photos_zip)

        paste_data = album_source.cutObjects(ids=[pic['portal'] for pic in pics])
        album_destination.pasteObjects(cp_data=paste_data)

        for pic in pics:
            self.failIf(pic['portal'] not in album_destination.objectIds(), '%s not in destination.' % pic['portal'])
            self.browser.go('http://localhost/%s/%s/view?display=Original' % (album_destination.absolute_url(1), pic['portal']))
            self.failUnlessEqual(photos_zip.read(pic['zip']), self.browser.get_html(), '%s contents doesn\'t match original.' % pic['portal'])

    def test_delete(self):
        self.browser_do_login('admin', '')

        album = self.portal.myfolder.mygallery.myalbum
        self.failUnlessEqual(album.objectIds(), ['myphoto1', 'myphoto2'])
        album.deleteObjects(ids=['myphoto1', 'myphoto2'])
        self.failUnlessEqual(album.objectIds(), [])

        self.browser_do_logout()


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NyPhotoFolderFunctionalTestCase))
    return suite
