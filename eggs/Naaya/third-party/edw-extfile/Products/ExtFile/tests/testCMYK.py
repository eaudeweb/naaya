#
# Test preview generation for CMYK images
#

from Testing import ZopeTestCase

ZopeTestCase.installProduct('ExtFile')

from Products.ExtFile.testing import ExtFileTestCase
from Products.ExtFile.testing import tiffImage


class TestCMYKPreview(ExtFileTestCase):

    def afterSetUp(self):
        ExtFileTestCase.afterSetUp(self)
        self.addExtImage(id='mountain.tif', file=tiffImage)

    def testSetup(self):
        self.assertEqual(self.image.content_type, 'image/tiff')
        self.assertEqual(self.reposit(), ['mountain.tif.tmp'])

    def testIsCMYK(self):
        from PIL import Image
        im = Image.open(self.image.get_fsname())
        self.assertEqual(im.mode, 'CMYK')

    def testManageCreatePreview(self):
        self.image.manage_create_prev(250, 250)
        self.assertEqual(self.reposit(), ['mountain.jpg.tmp',
                                          'mountain.tif.tmp'])

    def testCreatePreviewOnUpload(self):
        self.image.manage_file_upload(tiffImage, content_type='image/tiff', create_prev=1)
        self.assertEqual(self.reposit(), ['mountain.jpg.tmp',
                                          'mountain.tif.tmp'])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCMYKPreview))
    return suite

