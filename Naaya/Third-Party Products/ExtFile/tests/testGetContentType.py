#
# Tests for _get_content_type.
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

ZopeTestCase.installProduct('ExtFile')

from Products.ExtFile.tests.ExtFileTestCase import ExtFileTestCase
from Products.ExtFile.tests.ExtFileTestCase import gifImage
from Products.ExtFile.tests.ExtFileTestCase import makeFileUpload

from Products.ExtFile.ExtFile import ExtFile

def get_content_type(file, body, id, content_type=None):
    func = ExtFile._get_content_type.im_func
    return func(None, file, body, id, content_type)


class TestGetContentType(ExtFileTestCase):

    def afterSetUp(self):
        ExtFileTestCase.afterSetUp(self)
        # Your setup code here

    def testDefault(self):
        upload = makeFileUpload(gifImage)
        content_type = get_content_type(upload, upload.read(100), '')
        self.assertEqual(content_type, 'application/octet-stream')

    def testContentType(self):
        upload = makeFileUpload(gifImage, content_type='image/gif')
        content_type = get_content_type(upload, upload.read(100), '')
        self.assertEqual(content_type, 'image/gif')

    def testFilename(self):
        upload = makeFileUpload(gifImage, filename='image.gif')
        content_type = get_content_type(upload, upload.read(100), '')
        self.assertEqual(content_type, 'image/gif')

    def testContentTypeFilename(self):
        upload = makeFileUpload(gifImage, content_type='image/jpeg', filename='image.gif')
        content_type = get_content_type(upload, upload.read(100), '')
        self.assertEqual(content_type, 'image/jpeg')

    def testFallbackContentType(self):
        upload = makeFileUpload(gifImage)
        content_type = get_content_type(upload, upload.read(100), '', 'image/gif')
        self.assertEqual(content_type, 'image/gif')

    def testFallbackId(self):
        upload = makeFileUpload(gifImage)
        content_type = get_content_type(upload, upload.read(100), 'image.gif')
        self.assertEqual(content_type, 'image/gif')

    def testFallbackContentTypeId(self):
        upload = makeFileUpload(gifImage)
        content_type = get_content_type(upload, upload.read(100), 'image.gif', 'image/jpeg')
        # XXX: Id trumps content type here
        self.assertEqual(content_type, 'image/gif')

    def testFallbackContentTypeWithCharset(self):
        upload = makeFileUpload(gifImage)
        content_type = get_content_type(upload, upload.read(100), '', 'text/plain; charset=utf-8')
        self.assertEqual(content_type, 'text/plain')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestGetContentType))
    return suite

if __name__ == '__main__':
    framework()

