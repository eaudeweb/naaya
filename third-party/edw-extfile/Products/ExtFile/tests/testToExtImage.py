#
# Test 'toExtImage' External Method
#

from Testing import ZopeTestCase

ZopeTestCase.installProduct('ExternalMethod')
ZopeTestCase.installProduct('ExtFile')

from Products.ExtFile.testing import ExtFileTestCase
from Products.ExtFile.testing import jpegImage
from Products.ExtFile.testing import copymove_perms


class TestToExtImage(ZopeTestCase.Functional, ExtFileTestCase):

    def afterSetUp(self):
        ExtFileTestCase.afterSetUp(self)
        self.setPermissions(copymove_perms+['Add Documents, Images, and Files'])
        factory = self.folder.manage_addProduct['ExternalMethod']
        factory.manage_addExternalMethod('toExtImage', '', 'ExtFile.toExtImage', 'toExtImage')
        factory = self.folder.manage_addProduct['OFSP']
        factory.manage_addImage('jpegImage', file=open(jpegImage, 'rb'), content_type='image/jpeg')
        self.folder_url = self.folder.absolute_url(1)
        self.basic_auth = '%s:%s' % (ZopeTestCase.user_name, ZopeTestCase.user_password)

    def testToExtImage(self):
        self.assertEqual(self.folder.jpegImage.meta_type, 'Image')
        self.assertEqual(self.folder.jpegImage.content_type, 'image/jpeg')
        self.assertEqual(self.folder.jpegImage.get_size(), 4205)

        response = self.publish(self.folder_url+'/toExtImage?id=jpegImage',
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(self.folder.jpegImage.meta_type, 'ExtImage')
        self.assertEqual(self.folder.jpegImage.content_type, 'image/jpeg')
        self.assertEqual(self.folder.jpegImage.get_size(), 4205)

    def testToExtImageBackup(self):
        self.assertEqual(self.folder.jpegImage.meta_type, 'Image')
        self.assertEqual(self.folder.jpegImage.content_type, 'image/jpeg')
        self.assertEqual(self.folder.jpegImage.get_size(), 4205)

        response = self.publish(self.folder_url+'/toExtImage?id=jpegImage&backup=1',
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 200)
        self.failUnless('jpegImage' in self.folder.objectIds())
        self.failUnless('jpegImage.bak' in self.folder.objectIds())

        self.assertEqual(self.folder.jpegImage.meta_type, 'ExtImage')
        self.assertEqual(self.folder.jpegImage.content_type, 'image/jpeg')
        self.assertEqual(self.folder.jpegImage.get_size(), 4205)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestToExtImage))
    return suite

