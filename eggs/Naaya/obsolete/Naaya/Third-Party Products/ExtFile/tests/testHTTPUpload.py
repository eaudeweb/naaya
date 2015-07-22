#
# HTTPUpload tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

ZopeTestCase.installProduct('ExtFile')
ZopeTestCase.utils.startZServer()

from Products.ExtFile.tests.ExtFileTestCase import ExtFileTestCase
from Products.ExtFile.tests.ExtFileTestCase import gifImage
from Products.ExtFile.tests.ExtFileTestCase import makeFileUpload

from ZPublisher.HTTPRequest import FileUpload
from Products.ExtFile.ExtFile import HTTPUpload

import urllib


class TestHTTPUpload(ExtFileTestCase):

    def afterSetUp(self):
        ExtFileTestCase.afterSetUp(self)
        # Your setup code here

    def testFileUpload(self):
        upload = makeFileUpload(gifImage, content_type='image/gif')
        self.failUnless(isinstance(upload, FileUpload))
        upload = HTTPUpload(upload)
        self.failUnless(isinstance(upload, FileUpload))
        self.assertEqual(upload.headers['content-type'], 'image/gif')
        self.assertEqual(upload.filename, None)
        self.failUnless(hasattr(upload, 'read'))
        self.failUnless(hasattr(upload, 'seek'))

    def testFileUploadContentType(self):
        upload = makeFileUpload(gifImage, content_type='image/gif')
        self.failUnless(isinstance(upload, FileUpload))
        upload = HTTPUpload(upload, content_type='image/jpeg')
        self.failUnless(isinstance(upload, FileUpload))
        self.assertEqual(upload.headers['content-type'], 'image/jpeg')
        self.assertEqual(upload.filename, None)
        self.failUnless(hasattr(upload, 'read'))
        self.failUnless(hasattr(upload, 'seek'))

    def testFileUploadFilename(self):
        upload = makeFileUpload(gifImage, content_type='image/gif')
        self.failUnless(isinstance(upload, FileUpload))
        upload = HTTPUpload(upload, filename='image.gif')
        self.failUnless(isinstance(upload, FileUpload))
        self.assertEqual(upload.headers['content-type'], 'image/gif')
        self.assertEqual(upload.filename, 'image.gif')
        self.failUnless(hasattr(upload, 'read'))
        self.failUnless(hasattr(upload, 'seek'))

    def testFileUploadContentTypeFilename(self):
        upload = makeFileUpload(gifImage, content_type='image/gif')
        self.failUnless(isinstance(upload, FileUpload))
        upload = HTTPUpload(upload, content_type='image/jpeg', filename='image.jpg')
        self.failUnless(isinstance(upload, FileUpload))
        self.assertEqual(upload.headers['content-type'], 'image/jpeg')
        self.assertEqual(upload.filename, 'image.jpg')
        self.failUnless(hasattr(upload, 'read'))
        self.failUnless(hasattr(upload, 'seek'))

    def testFile(self):
        file = open(gifImage, 'rb')
        upload = HTTPUpload(file)
        self.failUnless(isinstance(upload, FileUpload))
        self.assertEqual(upload.headers['content-type'], 'application/x-www-form-urlencoded')
        self.assertEqual(upload.filename, None)
        # XXX: Must have content type for this to work
        self.failIf(hasattr(upload, 'read'))
        self.failIf(hasattr(upload, 'seek'))

    def testFileContentType(self):
        file = open(gifImage, 'rb')
        upload = HTTPUpload(file, content_type='image/jpeg')
        self.failUnless(isinstance(upload, FileUpload))
        self.assertEqual(upload.headers['content-type'], 'image/jpeg')
        self.assertEqual(upload.filename, None)
        self.failUnless(hasattr(upload, 'read'))
        self.failUnless(hasattr(upload, 'seek'))

    def testFileFilename(self):
        file = open(gifImage, 'rb')
        upload = HTTPUpload(file, filename='image.gif')
        self.failUnless(isinstance(upload, FileUpload))
        self.assertEqual(upload.headers['content-type'], 'application/x-www-form-urlencoded')
        self.assertEqual(upload.filename, 'image.gif')
        # XXX: Must have content type for this to work
        self.failIf(hasattr(upload, 'read'))
        self.failIf(hasattr(upload, 'seek'))

    def testFileContentTypeFilename(self):
        file = open(gifImage, 'rb')
        upload = HTTPUpload(file, content_type='image/jpeg', filename='image.jpg')
        self.failUnless(isinstance(upload, FileUpload))
        self.assertEqual(upload.headers['content-type'], 'image/jpeg')
        self.assertEqual(upload.filename, 'image.jpg')
        self.failUnless(hasattr(upload, 'read'))
        self.failUnless(hasattr(upload, 'seek'))

    def testUrlOpen(self):
        url = urllib.urlopen(self.app.GifImage.absolute_url())
        upload = HTTPUpload(url)
        self.failUnless(isinstance(upload, FileUpload))
        self.assertEqual(upload.headers['content-type'], 'image/gif')
        self.assertEqual(upload.filename, None)
        self.failUnless(hasattr(upload, 'read'))
        self.failUnless(hasattr(upload, 'seek'))

    def testUrlOpenContentType(self):
        url = urllib.urlopen(self.app.GifImage.absolute_url())
        upload = HTTPUpload(url, content_type='image/jpeg')
        self.failUnless(isinstance(upload, FileUpload))
        self.assertEqual(upload.headers['content-type'], 'image/jpeg')
        self.assertEqual(upload.filename, None)
        self.failUnless(hasattr(upload, 'read'))
        self.failUnless(hasattr(upload, 'seek'))

    def testUrlOpenFilename(self):
        url = urllib.urlopen(self.app.GifImage.absolute_url())
        upload = HTTPUpload(url, filename='image.gif')
        self.failUnless(isinstance(upload, FileUpload))
        self.assertEqual(upload.headers['content-type'], 'image/gif')
        self.assertEqual(upload.filename, 'image.gif')
        self.failUnless(hasattr(upload, 'read'))
        self.failUnless(hasattr(upload, 'seek'))

    def testUrlOpenContentTypeFilename(self):
        url = urllib.urlopen(self.app.GifImage.absolute_url())
        upload = HTTPUpload(url, content_type='image/jpeg', filename='image.jpg')
        self.failUnless(isinstance(upload, FileUpload))
        self.assertEqual(upload.headers['content-type'], 'image/jpeg')
        self.assertEqual(upload.filename, 'image.jpg')
        self.failUnless(hasattr(upload, 'read'))
        self.failUnless(hasattr(upload, 'seek'))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestHTTPUpload))
    return suite

if __name__ == '__main__':
    framework()

