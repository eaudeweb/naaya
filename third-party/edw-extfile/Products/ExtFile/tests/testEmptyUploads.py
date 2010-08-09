#
# Test empty uploads
#

from Testing import ZopeTestCase

ZopeTestCase.installProduct('ExtFile')

from Products.ExtFile.testing import ExtFileTestCase
from Products.ExtFile.testing import notImage

from StringIO import StringIO
from OFS.Image import Pdata


class TestExtFileAdd(ExtFileTestCase):

    def testAddEmptyStringFile(self):
        # No disk file is created
        self.addExtFile(id='file', file='')
        self.assertEqual(self.reposit(), [])
        self.failUnless(self.file.is_broken())
        self.assertEqual(self.file.data, '')
        self.assertEqual(self.file.content_type, '')

    def testAddNoneFile(self):
        # AttributeError: 'NoneType' object has no attribute 'read'
        self.assertRaises(AttributeError,
                self.addExtFile, id='file', file=None)

    def testAddEmptyFile(self):
        self.addExtFile(id='file', file=StringIO())
        self.assertEqual(self.reposit(), ['file.tmp'])
        self.assertEqual(self.file.get_size(), 0)
        self.assertEqual(self.file.data, '')
        self.assertEqual(self.file.content_type, 'text/x-unknown-content-type')

    def testAddEmptyPdata(self):
        self.addExtFile(id='file', file=Pdata(''))
        self.assertEqual(self.reposit(), ['file.tmp'])
        self.assertEqual(self.file.get_size(), 0)
        self.assertEqual(self.file.data, '')
        self.assertEqual(self.file.content_type, 'text/x-unknown-content-type')


class TestExtImageAdd(ExtFileTestCase):

    def testAddEmptyStringFile(self):
        # No disk file is created
        self.addExtImage(id='image', file='')
        self.assertEqual(self.reposit(), [])
        self.failUnless(self.image.is_broken())
        self.assertEqual(self.image.data, '')
        self.assertEqual(self.image.content_type, '')

    def testAddNoneFile(self):
        # AttributeError: 'NoneType' object has no attribute 'read'
        self.assertRaises(AttributeError,
                self.addExtImage, id='image', file=None)

    def testAddEmptyFile(self):
        self.addExtImage(id='image', file=StringIO())
        self.assertEqual(self.reposit(), ['image.tmp'])
        self.assertEqual(self.image.get_size(), 0)
        self.assertEqual(self.image.data, '')
        self.assertEqual(self.image.content_type, 'text/x-unknown-content-type')

    def testAddEmptyPdata(self):
        self.addExtImage(id='image', file=Pdata(''))
        self.assertEqual(self.reposit(), ['image.tmp'])
        self.assertEqual(self.image.get_size(), 0)
        self.assertEqual(self.image.data, '')
        self.assertEqual(self.image.content_type, 'text/x-unknown-content-type')


class TestExtImageAddPreview(ExtFileTestCase):

    def testAddEmptyStringFile(self):
        # No disk file is created
        self.addExtImage(id='image', file='', is_preview=1)
        self.assertEqual(self.reposit(), [])
        self.failUnless(self.image.is_broken())
        self.assertEqual(self.image.prev_content_type, '')
        self.assertEqual(self.image.prev_filename, [])

    def testAddNoneFile(self):
        # AttributeError: 'NoneType' object has no attribute 'read'
        self.assertRaises(AttributeError,
                self.addExtImage, id='image', file=None, is_preview=1)

    def testAddEmptyFile(self):
        self.addExtImage(id='image', file=StringIO(), is_preview=1)
        self.assertEqual(self.reposit(), ['image.tmp'])
        self.assertEqual(self.image.get_prev_size(), 0)
        self.assertEqual(self.image.prev_content_type, 'text/x-unknown-content-type')
        self.assertEqual(self.image.prev_filename, ['image'])

    def testAddEmptyPdata(self):
        self.addExtImage(id='image', file=Pdata(''), is_preview=1)
        self.assertEqual(self.reposit(), ['image.tmp'])
        self.assertEqual(self.image.get_prev_size(), 0)
        self.assertEqual(self.image.prev_content_type, 'text/x-unknown-content-type')
        self.assertEqual(self.image.prev_filename, ['image'])


class TestExtFileUpload(ExtFileTestCase):

    def testManageUploadEmptyStringFile(self):
        self.addExtFile(id='file', file='')
        self.file.manage_upload(file='')
        self.assertEqual(self.reposit(), ['file.tmp'])
        self.assertEqual(self.file.get_size(), 0)
        self.assertEqual(self.file.content_type, 'text/x-unknown-content-type')

    def testManageUploadNoneFile(self):
        self.addExtFile(id='file', file='')
        # AttributeError: 'NoneType' object has no attribute 'read'
        self.assertRaises(AttributeError,
                self.file.manage_upload, file=None)

    def testManageUploadEmptyFile(self):
        self.addExtFile(id='file', file='')
        self.file.manage_upload(file=StringIO())
        self.assertEqual(self.reposit(), ['file.tmp'])
        self.assertEqual(self.file.get_size(), 0)
        self.assertEqual(self.file.content_type, 'text/x-unknown-content-type')

    def testManageUploadEmptyPdata(self):
        self.addExtFile(id='file', file='')
        self.file.manage_upload(file=Pdata(''))
        self.assertEqual(self.reposit(), ['file.tmp'])
        self.assertEqual(self.file.get_size(), 0)
        self.assertEqual(self.file.content_type, 'text/x-unknown-content-type')

    def testManageFileUploadEmptyStringFile(self):
        self.addExtFile(id='file', file='')
        # IOError: [Errno 2] No such file or directory: ''
        self.assertRaises(IOError,
                self.file.manage_file_upload, file='')

    def testManageFileUploadNoneFile(self):
        self.addExtFile(id='file', file='')
        # AttributeError: 'NoneType' object has no attribute 'read'
        self.assertRaises(AttributeError,
                self.file.manage_file_upload, file=None)

    def testManageFileUploadEmptyFile(self):
        self.addExtFile(id='file', file='')
        self.file.manage_file_upload(file=StringIO())
        self.assertEqual(self.reposit(), ['file.tmp'])
        self.assertEqual(self.file.get_size(), 0)
        self.assertEqual(self.file.content_type, 'text/x-unknown-content-type')

    def testManageFileUploadEmptyPdata(self):
        self.addExtFile(id='file', file='')
        self.file.manage_file_upload(file=Pdata(''))
        self.assertEqual(self.reposit(), ['file.tmp'])
        self.assertEqual(self.file.get_size(), 0)
        self.assertEqual(self.file.content_type, 'text/x-unknown-content-type')


class TestExtImageUpload(ExtFileTestCase):

    def testManageUploadEmptyStringFile(self):
        self.addExtImage(id='image', file='')
        self.image.manage_upload(file='')
        self.assertEqual(self.reposit(), ['image.tmp'])
        self.assertEqual(self.image.get_size(), 0)
        self.assertEqual(self.image.content_type, 'text/x-unknown-content-type')

    def testManageUploadNoneFile(self):
        self.addExtImage(id='image', file='')
        # AttributeError: 'NoneType' object has no attribute 'read'
        self.assertRaises(AttributeError,
                self.image.manage_upload, file=None)

    def testManageUploadEmptyFile(self):
        self.addExtImage(id='image', file='')
        self.image.manage_upload(file=StringIO())
        self.assertEqual(self.reposit(), ['image.tmp'])
        self.assertEqual(self.image.get_size(), 0)
        self.assertEqual(self.image.content_type, 'text/x-unknown-content-type')

    def testManageUploadEmptyPdata(self):
        self.addExtImage(id='image', file='')
        self.image.manage_upload(file=Pdata(''))
        self.assertEqual(self.reposit(), ['image.tmp'])
        self.assertEqual(self.image.get_size(), 0)
        self.assertEqual(self.image.content_type, 'text/x-unknown-content-type')

    def testManageFileUploadEmptyStringFile(self):
        self.addExtImage(id='image', file='')
        # IOError: [Errno 2] No such file or directory: ''
        self.assertRaises(IOError,
                self.image.manage_file_upload, file='')

    def testManageFileUploadNoneFile(self):
        self.addExtImage(id='image', file='')
        # AttributeError: 'NoneType' object has no attribute 'read'
        self.assertRaises(AttributeError,
                self.image.manage_file_upload, file=None)

    def testManageFileUploadEmptyFile(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=StringIO())
        self.assertEqual(self.reposit(), ['image.tmp'])
        self.assertEqual(self.image.get_size(), 0)
        self.assertEqual(self.image.content_type, 'text/x-unknown-content-type')

    def testManageFileUploadEmptyPdata(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=Pdata(''))
        self.assertEqual(self.reposit(), ['image.tmp'])
        self.assertEqual(self.image.get_size(), 0)
        self.assertEqual(self.image.content_type, 'text/x-unknown-content-type')


class TestExtImageUploadPreview(ExtFileTestCase):

    def testManageUploadEmptyStringFile(self):
        self.addExtImage(id='image', file='')
        self.image.manage_upload(file='', is_preview=1)
        self.assertEqual(self.reposit(), ['image.tmp'])
        self.assertEqual(self.image.get_prev_size(), 0)
        self.assertEqual(self.image.prev_content_type, 'text/x-unknown-content-type')

    def testManageUploadNoneFile(self):
        self.addExtImage(id='image', file='')
        # AttributeError: 'NoneType' object has no attribute 'read'
        self.assertRaises(AttributeError,
                self.image.manage_upload, file=None, is_preview=1)

    def testManageUploadEmptyFile(self):
        self.addExtImage(id='image', file='')
        self.image.manage_upload(file=StringIO(), is_preview=1)
        self.assertEqual(self.reposit(), ['image.tmp'])
        self.assertEqual(self.image.get_prev_size(), 0)
        self.assertEqual(self.image.prev_content_type, 'text/x-unknown-content-type')

    def testManageUploadEmptyPdata(self):
        self.addExtImage(id='image', file='')
        self.image.manage_upload(file=Pdata(''), is_preview=1)
        self.assertEqual(self.reposit(), ['image.tmp'])
        self.assertEqual(self.image.get_prev_size(), 0)
        self.assertEqual(self.image.prev_content_type, 'text/x-unknown-content-type')

    def testManageFileUploadEmptyStringFile(self):
        self.addExtImage(id='image', file='')
        # IOError: [Errno 2] No such file or directory: ''
        self.assertRaises(IOError,
                self.image.manage_file_upload, file='', is_preview=1)

    def testManageFileUploadNoneFile(self):
        self.addExtImage(id='image', file='')
        # AttributeError: 'NoneType' object has no attribute 'read'
        self.assertRaises(AttributeError,
                self.image.manage_file_upload, file=None, is_preview=1)

    def testManageFileUploadEmptyFile(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=StringIO(), is_preview=1)
        self.assertEqual(self.reposit(), ['image.tmp'])
        self.assertEqual(self.image.get_prev_size(), 0)
        self.assertEqual(self.image.prev_content_type, 'text/x-unknown-content-type')

    def testManageFileUploadEmptyPdata(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=Pdata(''), is_preview=1)
        self.assertEqual(self.reposit(), ['image.tmp'])
        self.assertEqual(self.image.get_prev_size(), 0)
        self.assertEqual(self.image.prev_content_type, 'text/x-unknown-content-type')


class TestExtFileContentType(ExtFileTestCase):

    def testAddEmptyStringContentType(self):
        self.addExtFile(id='file', file=notImage, content_type='')
        self.assertEqual(self.reposit(), ['file.exe.tmp'])
        self.assertEqual(self.file.content_type, 'application/octet-stream')

    def testAddNoneContentType(self):
        self.addExtFile(id='file', file=notImage, content_type=None)
        self.assertEqual(self.reposit(), ['file.exe.tmp'])
        self.assertEqual(self.file.content_type, 'application/octet-stream')

    def testAddEmptyStringContentTypeEmptyFile(self):
        self.addExtFile(id='file', file=StringIO(), content_type='')
        self.assertEqual(self.reposit(), ['file.tmp'])
        self.assertEqual(self.file.content_type, 'text/x-unknown-content-type')

    def testAddNoneContentTypeEmptyFile(self):
        self.addExtFile(id='file', file=StringIO(), content_type=None)
        self.assertEqual(self.reposit(), ['file.tmp'])
        self.assertEqual(self.file.content_type, 'text/x-unknown-content-type')

    def testAddEmptyStringContentTypeNoData(self):
        self.addExtFile(id='file', file='', content_type='')
        self.assertEqual(self.file.content_type, '')

    def testAddNoneContentTypeNoData(self):
        self.addExtFile(id='file', file='', content_type=None)
        self.assertEqual(self.file.content_type, '')


class TestExtImageContentType(ExtFileTestCase):

    def testAddEmptyStringContentType(self):
        self.addExtImage(id='image', file=notImage, content_type='')
        self.assertEqual(self.reposit(), ['image.exe.tmp'])
        self.assertEqual(self.image.content_type, 'application/octet-stream')

    def testAddNoneContentType(self):
        self.addExtImage(id='image', file=notImage, content_type=None)
        self.assertEqual(self.reposit(), ['image.exe.tmp'])
        self.assertEqual(self.image.content_type, 'application/octet-stream')

    def testAddEmptyStringContentTypeEmptyFile(self):
        self.addExtImage(id='image', file=StringIO(), content_type='')
        self.assertEqual(self.reposit(), ['image.tmp'])
        self.assertEqual(self.image.content_type, 'text/x-unknown-content-type')

    def testAddNoneContentTypeEmptyFile(self):
        self.addExtImage(id='image', file=StringIO(), content_type=None)
        self.assertEqual(self.reposit(), ['image.tmp'])
        self.assertEqual(self.image.content_type, 'text/x-unknown-content-type')

    def testAddEmptyStringContentTypeNoData(self):
        self.addExtImage(id='image', file='', content_type='')
        self.assertEqual(self.image.content_type, '')

    def testAddNoneContentTypeNoData(self):
        self.addExtImage(id='image', file='', content_type=None)
        self.assertEqual(self.image.content_type, '')


class TestExtImageContentTypePreview(ExtFileTestCase):

    def testAddEmptyStringContentType(self):
        self.addExtImage(id='image', file=notImage, content_type='', is_preview=1)
        self.assertEqual(self.reposit(), ['image.exe.tmp'])
        self.assertEqual(self.image.prev_content_type, 'application/octet-stream')

    def testAddNoneContentType(self):
        self.addExtImage(id='image', file=notImage, content_type=None, is_preview=1)
        self.assertEqual(self.reposit(), ['image.exe.tmp'])
        self.assertEqual(self.image.prev_content_type, 'application/octet-stream')

    def testAddEmptyStringContentTypeEmptyFile(self):
        self.addExtImage(id='image', file=StringIO(), content_type='', is_preview=1)
        self.assertEqual(self.reposit(), ['image.tmp'])
        self.assertEqual(self.image.prev_content_type, 'text/x-unknown-content-type')

    def testAddNoneContentTypeEmptyFile(self):
        self.addExtImage(id='image', file=StringIO(), content_type=None, is_preview=1)
        self.assertEqual(self.reposit(), ['image.tmp'])
        self.assertEqual(self.image.prev_content_type, 'text/x-unknown-content-type')

    def testAddEmptyStringContentTypeNoData(self):
        self.addExtImage(id='image', file='', content_type='', is_preview=1)
        self.assertEqual(self.image.prev_content_type, '')

    def testAddNoneContentTypeNoData(self):
        self.addExtImage(id='image', file='', content_type=None, is_preview=1)
        self.assertEqual(self.image.prev_content_type, '')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestExtFileAdd))
    suite.addTest(makeSuite(TestExtImageAdd))
    suite.addTest(makeSuite(TestExtImageAddPreview))
    suite.addTest(makeSuite(TestExtFileUpload))
    suite.addTest(makeSuite(TestExtImageUpload))
    suite.addTest(makeSuite(TestExtImageUploadPreview))
    suite.addTest(makeSuite(TestExtFileContentType))
    suite.addTest(makeSuite(TestExtImageContentType))
    suite.addTest(makeSuite(TestExtImageContentTypePreview))
    return suite

