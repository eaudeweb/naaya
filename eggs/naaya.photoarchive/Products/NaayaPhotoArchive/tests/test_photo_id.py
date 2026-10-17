import os
import unittest
from io import BytesIO

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.NaayaPhotoArchive.NyPhoto import clean_display_id
from Products.NaayaPhotoArchive.NyPhotoFolder import addNyPhotoFolder
from Products.NaayaPhotoArchive.NyPhotoGallery import addNyPhotoGallery

from . import patchTestEnv  # noqa: F401


class CleanDisplayIdTest(unittest.TestCase):

    def test_ascii_unchanged(self):
        for name in ('Original', 'XSmall', 'My_photo-01.JPG', 'photo.png'):
            self.assertEqual(clean_display_id(name), name)
        self.assertEqual(clean_display_id('my photo.png'), 'my-photo.png')

    def test_romanian_french(self):
        self.assertEqual(clean_display_id('photo ț.png'), 'photo-t.png')
        self.assertEqual(clean_display_id('șțăîâ ȘȚĂÎÂ.png'),
                         'staia-STAIA.png')
        self.assertEqual(clean_display_id('Bruxelles – éèà'), 'Bruxelles-eea')

    def test_cyrillic(self):
        self.assertEqual(clean_display_id('Фото дом.jpg'), 'Foto-dom.jpg')


class UploadPhotoIdTest(NaayaTestCase):

    def afterSetUp(self):
        addNyPhotoGallery(self.portal, id='gallery', title='Gallery',
                          submitted=1, contributor='contributor')
        addNyPhotoFolder(self.portal.gallery, id='album', title='Album')

    def test_upload_non_ascii_filename(self):
        path = os.path.join(os.path.dirname(__file__), 'data', 'pink.png')
        with open(path, 'rb') as f:
            upload = BytesIO(f.read())
        upload.filename = 'photo ț.png'
        album = self.portal.gallery.album
        album.uploadPhotoOrZip(upload)
        self.assertIn('photo-t.png', album.objectIds())
