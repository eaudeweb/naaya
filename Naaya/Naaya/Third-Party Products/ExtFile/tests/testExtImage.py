#
# Tests the ExtFile product
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

ZopeTestCase.installProduct('ExtFile')
ZopeTestCase.installProduct('PythonScripts')
ZopeTestCase.utils.startZServer()

from Products.ExtFile.tests.ExtFileTestCase import ExtFileTestCase
from Products.ExtFile.tests.ExtFileTestCase import gifImage, jpegImage, tiffImage, notImage
from Products.ExtFile.tests.ExtFileTestCase import makeFileUpload
from Products.ExtFile.tests.ExtFileTestCase import copymove_perms
from Products.ExtFile import transaction
from Products.ExtFile import ExtFile, ExtImage, Config
from Products.ExtFile.ExtImage import UPLOAD_RESIZE


class TestExtFileAdd(ExtFileTestCase):
    '''Test ExtFile creation'''

    def testAddFileFromFileName(self):
        # Add File from file name
        self.addExtFile(id='file', file=notImage)
        self.file._finish()
        self.failUnless(self._exists('file.exe'))
        self.assertEqual(self.file.get_size(), self._fsize(notImage))

    def testAddFileFromFileHandle(self):
        # Add File from file handle
        self.addExtFile(id='file', file=open(notImage, 'rb'))
        self.file._finish()
        self.failUnless(self._exists('file.exe'))
        self.assertEqual(self.file.get_size(), self._fsize(notImage))

    def testAddFileFromFileUpload(self):
        # Add File from file upload
        self.addExtFile(id='file', file=makeFileUpload(notImage, 'application/octet-stream'))
        self.file._finish()
        self.failUnless(self._exists('file.exe'))
        self.assertEqual(self.file.get_size(), self._fsize(notImage))

    def testAddFileWithIdFromFilename(self):
        # Add File without id - should use filename instead
        self.addExtFile(id='', file=makeFileUpload(notImage, 'application/octet-stream', filename='foo'))
        self.file._finish()
        self.assertEqual(self.file.getId(), 'foo')
        self.failUnless(self._exists('foo.exe'))
        self.assertEqual(self.file.get_size(), self._fsize(notImage))

    def testAddFileWithLatin1Filename(self):
        # Add File without id - should use filename instead
        self.addExtFile(id='', file=makeFileUpload(notImage, 'application/octet-stream', filename='M\xe4dchen'))
        self.file._finish()
        self.assertEqual(self.file.getId(), 'Madchen')
        self.failUnless(self._exists('Madchen.exe'))
        self.assertEqual(self.file.get_size(), self._fsize(notImage))

    def testAddFileWithUTF8Filename(self):
        # Add File without id - should use filename instead
        self.addExtFile(id='', file=makeFileUpload(notImage, 'application/octet-stream', filename='M\303\244dchen'))
        self.file._finish()
        self.assertEqual(self.file.getId(), 'Madchen')
        self.failUnless(self._exists('Madchen.exe'))
        self.assertEqual(self.file.get_size(), self._fsize(notImage))


class TestExtImageAdd(ExtFileTestCase):
    '''Test ExtImage creation'''

    def testAddImageFromName(self):
        # Add Image from file name
        self.addExtImage(id='image', file=gifImage)
        self.image._finish()
        self.failUnless(self._exists('image.gif'))
        self.assertEqual(self.image.get_size(), self._fsize(gifImage))

    def testAddImageFromFileHandle(self):
        # Add Image from file handle
        self.addExtImage(id='image', file=open(gifImage, 'rb'))
        self.image._finish()
        self.failUnless(self._exists('image.gif'))
        self.assertEqual(self.image.get_size(), self._fsize(gifImage))

    def testAddImageFromFileUpload(self):
        # Add Image from file upload
        self.addExtImage(id='image', file=makeFileUpload(gifImage, 'image/gif'))
        self.image._finish()
        self.failUnless(self._exists('image.gif'))
        self.assertEqual(self.image.get_size(), self._fsize(gifImage))

    def testAddImageWithIdFromFilename(self):
        # Add File without id - should use filename instead
        self.addExtImage(id='', file=makeFileUpload(gifImage, 'image/gif', filename='foo'))
        self.image._finish()
        self.assertEqual(self.image.getId(), 'foo')
        self.failUnless(self._exists('foo.gif'))
        self.assertEqual(self.image.get_size(), self._fsize(gifImage))

    def testAddUnwrappedImage(self):
        # This is what Photo does with displays...
        file = ExtImage.ExtImage('foo')
        self.assertRaises(AttributeError,
                          file.manage_file_upload, file=gifImage)

    def testAddImageWithLatin1Filename(self):
        # Add File without id - should use filename instead
        self.addExtImage(id='', file=makeFileUpload(gifImage, 'image/gif', filename='M\xe4dchen'))
        self.image._finish()
        self.assertEqual(self.image.getId(), 'Madchen')
        self.failUnless(self._exists('Madchen.gif'))
        self.assertEqual(self.image.get_size(), self._fsize(gifImage))

    def testAddImageWithUTF8Filename(self):
        # Add File without id - should use filename instead
        self.addExtImage(id='', file=makeFileUpload(gifImage, 'image/gif', filename='M\303\244dchen'))
        self.image._finish()
        self.assertEqual(self.image.getId(), 'Madchen')
        self.failUnless(self._exists('Madchen.gif'))
        self.assertEqual(self.image.get_size(), self._fsize(gifImage))


class TestExtFileUpload(ExtFileTestCase):
    '''Test ExtFile upload'''

    def testManageFileUploadFromFileName(self):
        # Upload File from file name
        self.addExtFile(id='file', file='')
        self.file.manage_file_upload(file=notImage)
        self.file._finish()
        self.failUnless(self._exists('file.exe'))
        self.assertEqual(self.file.get_size(), self._fsize(notImage))

    def testManageFileUploadFromFileHandle(self):
        # Upload File from file handle
        self.addExtFile(id='file', file='')
        self.file.manage_file_upload(file=open(notImage, 'rb'))
        self.file._finish()
        self.failUnless(self._exists('file.exe'))
        self.assertEqual(self.file.get_size(), self._fsize(notImage))

    def testManageFileUploadFromFileUpload(self):
        # Upload File from file upload
        self.addExtFile(id='file', file='')
        self.file.manage_file_upload(file=makeFileUpload(notImage, 'application/octet-stream'))
        self.file._finish()
        self.failUnless(self._exists('file.exe'))
        self.assertEqual(self.file.get_size(), self._fsize(notImage))

    def testManageUploadFromStringBuffer(self):
        # Upload File from file name
        self.addExtFile(id='file', file='')
        self.file.manage_upload(file=open(notImage, 'rb').read())
        self.file._finish()
        self.failUnless(self._exists('file.exe'))
        self.assertEqual(self.file.get_size(), self._fsize(notImage))

    def testManageUploadFromFileHandle(self):
        # Upload File from file handle
        self.addExtFile(id='file', file='')
        self.file.manage_upload(file=open(notImage, 'rb'))
        self.file._finish()
        self.failUnless(self._exists('file.exe'))
        self.assertEqual(self.file.get_size(), self._fsize(notImage))

    def testManageUploadFromFileUpload(self):
        # Upload File from file upload
        self.addExtFile(id='file', file='')
        self.file.manage_upload(file=makeFileUpload(notImage, 'application/octet-stream'))
        self.file._finish()
        self.failUnless(self._exists('file.exe'))
        self.assertEqual(self.file.get_size(), self._fsize(notImage))


class TestExtImageUpload(ExtFileTestCase):
    '''Test ExtImage upload'''

    def testManageFileUploadFromFileName(self):
        # Upload Image from file name
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=gifImage)
        self.image._finish()
        self.failUnless(self._exists('image.gif'))
        self.assertEqual(self.image.get_size(), self._fsize(gifImage))

    def testManageFileUploadFromFileHandle(self):
        # Upload Image from file handle
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=open(gifImage, 'rb'))
        self.image._finish()
        self.failUnless(self._exists('image.gif'))
        self.assertEqual(self.image.get_size(), self._fsize(gifImage))

    def testManageFileUploadFromFileUpload(self):
        # Upload Image from file upload
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=makeFileUpload(gifImage, 'image/gif'))
        self.image._finish()
        self.failUnless(self._exists('image.gif'))
        self.assertEqual(self.image.get_size(), self._fsize(gifImage))

    def testManageUploadFromStringBuffer(self):
        # Upload Image from file name
        self.addExtImage(id='image', file='')
        self.image.manage_upload(file=open(gifImage, 'rb').read())
        self.image._finish()
        self.failUnless(self._exists('image.gif'))
        self.assertEqual(self.image.get_size(), self._fsize(gifImage))

    def testManageUploadFromFileHandle(self):
        # Upload Image from file handle
        self.addExtImage(id='image', file='')
        self.image.manage_upload(file=open(gifImage, 'rb'))
        self.image._finish()
        self.failUnless(self._exists('image.gif'))
        self.assertEqual(self.image.get_size(), self._fsize(gifImage))

    def testManageUploadFromFileUpload(self):
        # Upload Image from file upload
        self.addExtImage(id='image', file='')
        self.image.manage_upload(file=makeFileUpload(gifImage, 'image/gif'))
        self.image._finish()
        self.failUnless(self._exists('image.gif'))
        self.assertEqual(self.image.get_size(), self._fsize(gifImage))


class TestExtFileContentType(ExtFileTestCase):
    '''Test ExtFile content-type detection'''

    def testDefaultContentType(self):
        # Use default content type
        self.addExtFile(id='file', file=notImage)
        self.file._finish()
        self.assertEqual(self.file.content_type, 'application/octet-stream')
        self.failUnless(self._exists('file.exe'))

    def testContentTypeExplicit(self):
        # Use passed-in content type
        self.addExtFile(id='file', file=notImage, content_type='image/jpeg')
        self.file._finish()
        self.assertEqual(self.file.content_type, 'image/jpeg')
        self.failUnless(self._exists('file.jpg'))

    def testContentTypeFromId(self):
        # Detect GIF content type from file id
        self.addExtFile(id='file.gif', file=notImage)
        self.file._finish()
        self.assertEqual(self.file.content_type, 'image/gif')
        self.failUnless(self._exists('file.gif'))

    def testContentTypeFromIdExplicit(self):
        # Passed-in content type trumps detection by id
        self.addExtFile(id='file.gif', file=notImage, content_type='image/jpeg')
        self.file._finish()
        self.assertEqual(self.file.content_type, 'image/jpeg')
        self.failUnless(self._exists('file.jpg'))

    def testContentTypeFromHeaders(self):
        # Detect GIF content type from file upload headers
        self.addExtFile(id='file', file=makeFileUpload(notImage, 'image/gif'))
        self.file._finish()
        self.assertEqual(self.file.content_type, 'image/gif')
        self.failUnless(self._exists('file.gif'))

    def testContentTypeFromHeadersExplicit(self):
        # Passed-in content type trumps detection by headers
        self.addExtFile(id='file', file=makeFileUpload(notImage, 'image/gif'), content_type='image/jpeg')
        self.file._finish()
        self.assertEqual(self.file.content_type, 'image/jpeg')
        self.failUnless(self._exists('file.jpg'))

    def testContentTypeFromHttpUpload(self):
        # Detect content type from download headers
        self.addExtFile(id='file', file=notImage)
        self.file.manage_http_upload(url=self.app.TiffImage.absolute_url())
        self.file._finish()
        self.assertEqual(self.file.content_type, 'image/tiff')
        # File is *not* renamed!
        self.failUnless(self._exists('file.exe'))

    def testContentTypeFromHttpUploadDefault(self):
        # Detect content type from download headers
        self.addExtFile(id='file', file=notImage)
        self.file.manage_http_upload(url=self.app.NotImage.absolute_url())
        self.file._finish()
        self.assertEqual(self.file.content_type, 'application/octet-stream')
        # File is *not* renamed!
        self.failUnless(self._exists('file.exe'))


class TestExtImageContentType(ExtFileTestCase):
    '''Test ExtImage content-type detection'''

    def testDefaultContentType(self):
        # Use default content type
        self.addExtImage(id='image', file=notImage)
        self.image._finish()
        self.assertEqual(self.image.content_type, 'application/octet-stream')
        self.failUnless(self._exists('image.exe'))

    def testContentTypeExplicit(self):
        # Use passed-in content type when we cannot detect from content
        self.addExtImage(id='image', file=notImage, content_type='image/jpeg')
        self.image._finish()
        self.assertEqual(self.image.content_type, 'image/jpeg')
        self.failUnless(self._exists('image.jpg'))

    def testContentTypeFromId(self):
        # Detect GIF content type from file id
        self.addExtImage(id='image.gif', file=notImage)
        self.image._finish()
        self.assertEqual(self.image.content_type, 'image/gif')
        self.failUnless(self._exists('image.gif'))

    def testContentTypeFromIdExplicit(self):
        # Passed-in content type trumps detection by id
        self.addExtImage(id='image.gif', file=notImage, content_type='image/jpeg')
        self.image._finish()
        self.assertEqual(self.image.content_type, 'image/jpeg')
        self.failUnless(self._exists('image.jpg'))

    def testContentTypeFromHeaders(self):
        # Detect GIF content type from file upload headers
        self.addExtImage(id='image', file=makeFileUpload(notImage, 'image/gif'))
        self.image._finish()
        self.assertEqual(self.image.content_type, 'image/gif')
        self.failUnless(self._exists('image.gif'))

    def testContentTypeFromHeadersExplicit(self):
        # Passed-in content type trumps detection by headers
        self.addExtImage(id='image', file=makeFileUpload(notImage, 'image/gif'), content_type='image/jpeg')
        self.image._finish()
        self.assertEqual(self.image.content_type, 'image/jpeg')
        self.failUnless(self._exists('image.jpg'))

    def testContentTypeFromHttpUpload(self):
        # Detect content type from download headers
        self.addExtImage(id='image', file=notImage)
        self.image.manage_http_upload(url=self.app.TiffImage.absolute_url())
        self.image._finish()
        self.assertEqual(self.image.content_type, 'image/tiff')
        # File is *not* renamed!
        self.failUnless(self._exists('image.exe'))
        # Check TIFF dimension sniffing
        self.assertEqual(self.image.width(), 200)
        self.assertEqual(self.image.height(), 136)

    def testContentTypeFromGifContent(self):
        # Detect GIF content type from file contents
        self.addExtImage(id='image', file=gifImage)
        self.image._finish()
        self.assertEqual(self.image.content_type, 'image/gif')
        self.failUnless(self._exists('image.gif'))

    def testContentTypeFromGifContentExplicit(self):
        # Detect GIF content type even when passing a content type
        self.addExtImage(id='image', file=gifImage, content_type='image/jpeg')
        self.image._finish()
        self.assertEqual(self.image.content_type, 'image/gif')
        self.failUnless(self._exists('image.gif'))

    def testContentTypeFromJpegContent(self):
        # Detect JPEG content type from file contents
        self.addExtImage(id='image', file=jpegImage)
        self.image._finish()
        self.assertEqual(self.image.content_type, 'image/jpeg')
        self.failUnless(self._exists('image.jpg'))

    def testContentTypeFromJpegContentExplicit(self):
        # Detect JPEG content type even when passing a content type
        self.addExtImage(id='image', file=jpegImage, content_type='image/tiff')
        self.image._finish()
        self.assertEqual(self.image.content_type, 'image/jpeg')
        self.failUnless(self._exists('image.jpg'))

    def testContentTypeFromGifString(self):
        # Detect GIF content type from string buffer
        self.addExtImage(id='image', file=notImage)
        self.image.manage_upload(file=open(gifImage, 'rb').read())
        self.image._finish()
        self.assertEqual(self.image.content_type, 'image/gif')
        # File is *not* renamed!
        self.failUnless(self._exists('image.exe'))

    def testContentTypeFromJpegPUT(self):
        # Detect JPEG content type from PUT' image
        self.addExtImage(id='image', file=open(notImage, 'rb'))
        request = self.app.REQUEST
        request['BODYFILE'] = open(jpegImage, 'rb')
        self.image.PUT(request, request.RESPONSE)
        self.image._finish()
        self.assertEqual(self.image.content_type, 'image/jpeg')
        # File is *not* renamed!
        self.failUnless(self._exists('image.exe'))
        # Check PUT works
        self.assertEqual(self.image.get_size(), self._fsize(jpegImage))


class TestExtFileCopyPaste(ExtFileTestCase):
    '''Tests cut/copy/paste/rename/clone'''

    def afterSetUp(self):
        ExtFileTestCase.afterSetUp(self)
        self.folder.manage_addFolder('subfolder')
        self.subfolder = self.folder['subfolder']
        self.setPermissions(copymove_perms)
        self.addExtFile(id='image.gif', file=gifImage)
        transaction.savepoint(1) # need a _p_jar

    def testClone(self):
        # Clone a file
        self.subfolder.manage_clone(self.file, 'image.gif')
        self.file._finish()
        self.subfolder['image.gif']._finish()
        self.failUnless(self._exists('image.gif'))
        self.failIf(self._exists('image.gif.undo'))
        self.failUnless(self._exists('image.1.gif'))

    def testCopyPaste(self):
        # Copy and paste a file
        cb = self.folder.manage_copyObjects(['image.gif'])
        self.subfolder.manage_pasteObjects(cb)
        self.file._finish()
        self.subfolder['image.gif']._finish()
        self.failUnless(self._exists('image.gif'))
        self.failIf(self._exists('image.gif.undo'))
        self.failUnless(self._exists('image.1.gif'))
        self.assertEqual(self.subfolder['image.gif'].get_size(), self._fsize(gifImage))

    def testCutPaste(self):
        # Cut and paste a file
        cb = self.folder.manage_cutObjects(['image.gif'])
        self.subfolder.manage_pasteObjects(cb)
        self.file._finish()
        self.subfolder['image.gif']._finish()
        self.failUnless(self._exists('image.gif'))
        self.failIf(self._exists('image.gif.undo'))
        self.failIf(self._exists('image.1.gif'))

    def testRename(self):
        # Rename a file
        self.folder.manage_renameObject('image.gif', 'image44.gif')
        self.file._finish()
        self.folder['image44.gif']._finish()
        self.failUnless(self._exists('image.gif'))
        self.failIf(self._exists('image.gif.undo'))
        self.failIf(self._exists('image.1.gif'))

    def testCOPY(self):
        # WebDAV copy a file
        req = self.app.REQUEST
        req.environ['HTTP_DEPTH'] = 'infinity'
        req.environ['HTTP_DESTINATION'] = 'http://dummy.org/%s/subfolder/image.gif' % ZopeTestCase.folder_name
        self.folder['image.gif'].COPY(req, req.RESPONSE)
        self.file._finish()
        self.subfolder['image.gif']._finish()
        self.failUnless(self._exists('image.gif'))
        self.failIf(self._exists('image.gif.undo'))
        self.failUnless(self._exists('image.1.gif'))
        self.assertEqual(self.subfolder['image.gif'].get_size(), self._fsize(gifImage))

    def testMOVE(self):
        # WebDAV move a file
        req = self.app.REQUEST
        req.environ['HTTP_DEPTH'] = 'infinity'
        req.environ['HTTP_DESTINATION'] = 'http://dummy.org/%s/subfolder/image.gif' % ZopeTestCase.folder_name
        self.folder['image.gif'].MOVE(req, req.RESPONSE)
        self.file._finish()
        self.subfolder['image.gif']._finish()
        self.failUnless(self._exists('image.gif'))
        self.failIf(self._exists('image.gif.undo'))
        self.failIf(self._exists('image.1.gif'))
        self.failIf(self._exists('image.1.gif.undo'))
        self.assertEqual(self.subfolder['image.gif'].get_size(), self._fsize(gifImage))

    def testCopyOfProtection(self):
        # Copy and paste a file into the same folder.
        # The filenames should not begin with 'copy_of_'
        cb = self.folder.manage_copyObjects(['image.gif'])
        self.folder.manage_pasteObjects(cb)
        self.file._finish()
        self.folder['copy_of_image.gif']._finish()
        self.failUnless(self._exists('image.gif'))
        self.failIf(self._exists('image.gif.undo'))
        self.failIf(self._exists('copy_of_image.gif'))
        self.failUnless(self._exists('image.1.gif'))
        self.assertEqual(self.folder['copy_of_image.gif'].get_size(), self._fsize(gifImage))


class TestExtImageCopyPaste(ExtFileTestCase):
    '''Tests cut/copy/paste/rename/clone'''

    def afterSetUp(self):
        ExtFileTestCase.afterSetUp(self)
        self.folder.manage_addFolder('subfolder')
        self.subfolder = self.folder['subfolder']
        self.setPermissions(copymove_perms)
        self.addExtImage(id='image.gif', file=gifImage)
        # Add a preview image as well
        self.folder['image.gif'].manage_file_upload(file=jpegImage, is_preview=1,
                                                    create_prev=UPLOAD_RESIZE,
                                                    maxx=100, maxy=100, ratio=1)
        transaction.savepoint(1) # need a _p_jar

    def testClone(self):
        # Clone an image
        self.subfolder.manage_clone(self.image, 'image.gif')
        self.image._finish()
        self.subfolder['image.gif']._finish()
        self.failUnless(self._exists('image.gif'))
        self.failIf(self._exists('image.gif.undo'))
        self.failUnless(self._exists('image.jpg'))
        self.failIf(self._exists('image.jpg.undo'))
        self.failUnless(self._exists('image.1.gif'))
        self.failUnless(self._exists('image.1.jpg'))

    def testCopyPaste(self):
        # Copy and paste an image
        cb = self.folder.manage_copyObjects(['image.gif'])
        self.subfolder.manage_pasteObjects(cb)
        self.image._finish()
        self.subfolder['image.gif']._finish()
        self.failUnless(self._exists('image.gif'))
        self.failIf(self._exists('image.gif.undo'))
        self.failUnless(self._exists('image.1.gif'))
        self.failIf(self._exists('image.1.gif.undo'))
        self.failUnless(self._exists('image.jpg'))
        self.failUnless(self._exists('image.1.jpg'))
        self.assertEqual(self.subfolder['image.gif'].get_size(), self._fsize(gifImage))

    def testCutPaste(self):
        # Cut and paste an image
        cb = self.folder.manage_cutObjects(['image.gif'])
        self.subfolder.manage_pasteObjects(cb)
        self.image._finish()
        self.subfolder['image.gif']._finish()
        self.failUnless(self._exists('image.gif'))
        self.failIf(self._exists('image.gif.undo'))
        self.failUnless(self._exists('image.jpg'))
        self.failIf(self._exists('image.jpg.undo'))
        self.failIf(self._exists('image.1.gif'))
        self.failIf(self._exists('image.1.jpg'))

    def testRename(self):
        # Rename an image
        self.folder.manage_renameObject('image.gif', 'image44.gif')
        self.image._finish()
        self.folder['image44.gif']._finish()
        self.failUnless(self._exists('image.gif'))
        self.failIf(self._exists('image.gif.undo'))
        self.failUnless(self._exists('image.jpg'))
        self.failIf(self._exists('image.jpg.undo'))
        self.failIf(self._exists('image.1.gif'))
        self.failIf(self._exists('image.1.jpg'))

    def testCOPY(self):
        # WebDAV copy an image
        req = self.app.REQUEST
        req.environ['HTTP_DEPTH'] = 'infinity'
        req.environ['HTTP_DESTINATION'] = 'http://dummy.org/%s/subfolder/image.gif' % ZopeTestCase.folder_name
        self.folder['image.gif'].COPY(req, req.RESPONSE)
        self.image._finish()
        self.subfolder['image.gif']._finish()
        self.failUnless(self._exists('image.gif'))
        self.failIf(self._exists('image.gif.undo'))
        self.failUnless(self._exists('image.1.gif'))
        self.failIf(self._exists('image.1.gif.undo'))
        self.failUnless(self._exists('image.jpg'))
        self.failUnless(self._exists('image.1.jpg'))
        self.assertEqual(self.subfolder['image.gif'].get_size(), self._fsize(gifImage))

    def testMOVE(self):
        # WebDAV move an image
        req = self.app.REQUEST
        req.environ['HTTP_DEPTH'] = 'infinity'
        req.environ['HTTP_DESTINATION'] = 'http://dummy.org/%s/subfolder/image.gif' % ZopeTestCase.folder_name
        self.folder['image.gif'].MOVE(req, req.RESPONSE)
        self.image._finish()
        self.subfolder['image.gif']._finish()
        self.failUnless(self._exists('image.gif'))
        self.failIf(self._exists('image.gif.undo'))
        self.failUnless(self._exists('image.jpg'))
        self.failIf(self._exists('image.jpg.undo'))
        self.failIf(self._exists('image.1.gif'))
        self.failIf(self._exists('image.1.jpg'))
        self.assertEqual(self.subfolder['image.gif'].get_size(), self._fsize(gifImage))

    def testPUTRecreatesPreview(self):
        # PUT an image; the preview should be regenerated.
        self.image._finish()
        self.failUnless(self._exists('image.gif'))
        self.failUnless(self._exists('image.jpg'))  # preview
        self.failIf(self._exists('image.gif.tmp'))
        self.failIf(self._exists('image.jpg.tmp'))
        req = self.app.REQUEST
        req['BODYFILE'] = open(gifImage, 'rb')
        self.image.PUT(req, req.RESPONSE)
        self.failUnless(self._exists('image.gif'))
        self.failUnless(self._exists('image.jpg'))  # preview
        self.failUnless(self._exists('image.gif.tmp'))  # newly put image
        self.failUnless(self._exists('image.jpg.tmp'))  # regenerated preview
        self.image._finish()
        self.failUnless(self._exists('image.gif'))
        self.failUnless(self._exists('image.jpg'))  # regenerated preview
        self.failIf(self._exists('image.gif.tmp'))
        self.failIf(self._exists('image.jpg.tmp'))

    def testPUTRetainsPreviewBoundaries(self):
        # PUT an image; the preview should retain maxx and maxy.
        self.failUnless(self.image.has_preview)
        self.assertEqual(self.image.prev_width(), 100)
        self.assertEqual(self.image.prev_height(), 64)
        req = self.app.REQUEST
        req['BODYFILE'] = open(tiffImage, 'rb')
        self.image.PUT(req, req.RESPONSE)
        self.assertEqual(self.image.prev_width(), 100)
        self.assertEqual(self.image.prev_height(), 68)

    def testManageHTTPUploadDoesNotAffectPreview(self):
        # HTTP upload an image; the preview should not change.
        self.failUnless(self.image.has_preview)
        self.assertEqual(self.image.prev_width(), 100)
        self.assertEqual(self.image.prev_height(), 64)
        self.image.manage_http_upload(url=self.app.TiffImage.absolute_url())
        self.assertEqual(self.image.prev_width(), 100)
        self.assertEqual(self.image.prev_height(), 64)


class TestRepository(ExtFileTestCase):
    '''Test repository directories'''

    def afterClear(self):
        ExtFileTestCase.afterClear(self)
        ExtFile.REPOSITORY = Config.FLAT
        ExtFile.NORMALIZE_CASE = Config.KEEP
        ExtFile.CUSTOM_METHOD = 'getExtFilePath'

    def testRepositoryFlat(self):
        ExtFile.REPOSITORY = Config.FLAT
        self.addExtImage(id='image', file=gifImage)
        path = self.image.filename[:-1]
        self.assertEqual(path, [])

    def testRepositorySyncZodb(self):
        ExtFile.REPOSITORY = Config.SYNC_ZODB
        self.addExtImage(id='image', file=gifImage)
        path = self.image.filename[:-1]
        self.assertEqual(path, [ZopeTestCase.folder_name])

    def testRepositorySliced(self):
        ExtFile.REPOSITORY = Config.SLICED
        self.addExtImage(id='image', file=gifImage)
        path = self.image.filename[:-1]
        self.assertEqual(path, ['i', 'm'])

    def testRepositorySlicedReverse(self):
        ExtFile.REPOSITORY = Config.SLICED_REVERSE
        self.addExtImage(id='image', file=gifImage)
        path = self.image.filename[:-1]
        self.assertEqual(path, ['e', 'g'])

    def testRepositorySlicedHash(self):
        ExtFile.REPOSITORY = Config.SLICED_HASH
        self.addExtImage(id='image', file=gifImage)
        path = self.image.filename[:-1]
        self.assertEqual(path, ['F', 'E'])

    def testRepositorySlicedHashDifferentFolder(self):
        # Because the path is part of the hash, the results
        # are different from the above test.
        ExtFile.REPOSITORY = Config.SLICED_HASH
        self.folder.manage_addFolder('subfolder')
        self.subfolder = self.folder['subfolder']
        self.addExtImage(id='image', file=gifImage, folder=self.subfolder)
        path = self.image.filename[:-1]
        self.assertEqual(path, ['L', 'd'])

    def testRepositoryCustom(self):

        def getExtFilePath(path, id):
            return ['custom', 'path']
        setattr(self.folder, 'getExtFilePath', getExtFilePath)

        ExtFile.REPOSITORY = Config.CUSTOM
        self.addExtImage(id='image', file=gifImage)
        path = self.image.filename[:-1]
        self.assertEqual(path, ['custom', 'path'])

    def testRepositoryNormalizeCase(self):

        def getExtFilePath(path, id):
            return ['Custom', 'Path']
        setattr(self.folder, 'getExtFilePath', getExtFilePath)

        ExtFile.REPOSITORY = Config.CUSTOM
        ExtFile.NORMALIZE_CASE = Config.NORMALIZE
        self.addExtImage(id='image', file=gifImage)
        path = self.image.filename[:-1]
        self.assertEqual(path, ['custom', 'path'])

    def testRepositoryCustomScript(self):

        factory = self.folder.manage_addProduct['PythonScripts']
        factory.manage_addPythonScript('getExtFilePath')
        ps = self.folder.getExtFilePath
        ps.ZPythonScript_edit(params='path, id', body="return ['custom', 'path']")

        ExtFile.REPOSITORY = Config.CUSTOM
        self.addExtImage(id='image', file=gifImage)
        path = self.image.filename[:-1]
        self.assertEqual(path, ['custom', 'path'])

    def testRepositoryCustomContainer(self):
        from OFS.Folder import Folder

        class CustomContainer(Folder):
            def __init__(self, id):
                self.id = id
            def getExtFilePath(self, path, id):
                return ['custom', 'path']

        self.folder._setObject('subfolder', CustomContainer('subfolder'))
        self.folder = self.folder.subfolder

        ExtFile.REPOSITORY = Config.CUSTOM
        self.addExtImage(id='image', file=gifImage)
        path = self.image.filename[:-1]
        self.assertEqual(path, ['custom', 'path'])

    def testRepositoryCustomContainerContainer(self):
        from OFS.Folder import Folder

        class CustomContainer(Folder):
            def __init__(self, id):
                self.id = id
            def getExtFilePath(self, path, id):
                return ['custom', 'path']

        self.folder._setObject('subfolder', CustomContainer('subfolder'))
        self.folder = self.folder.subfolder
        self.folder._setObject('subsubfolder', Folder('subsubfolder'))
        self.folder = self.folder.subsubfolder

        ExtFile.REPOSITORY = Config.CUSTOM
        self.addExtImage(id='image', file=gifImage)
        path = self.image.filename[:-1]
        self.assertEqual(path, ['custom', 'path'])

    def testRepositoryCustomSubclass(self):

        class CustomImage(ExtImage.ExtImage):
            def getExtFilePath(self, path, id):
                return ['custom', 'path']

        ExtFile.REPOSITORY = Config.CUSTOM
        self.folder._setObject('image', CustomImage('image'))
        self.folder.image.manage_file_upload(gifImage)
        path = self.folder.image.filename[:-1]
        self.assertEqual(path, ['custom', 'path'])

    def testRepositoryCustomPrivateMethod(self):

        def _getExtFilePath(path, id):
            return ['custom', 'path']
        setattr(self.folder, '_getExtFilePath', _getExtFilePath)

        ExtFile.REPOSITORY = Config.CUSTOM
        ExtFile.CUSTOM_METHOD = '_getExtFilePath'
        self.addExtImage(id='image', file=gifImage)
        path = self.image.filename[:-1]
        self.assertEqual(path, ['custom', 'path'])


class TestRepositoryFiles(ExtFileTestCase):
    '''Test repository files'''

    def afterSetUp(self):
        ExtFileTestCase.afterSetUp(self)
        self.folder.manage_addFolder('subfolder')
        self.subfolder = self.folder['subfolder']

    def testUniqueFileName(self):
        # Create a unique file name
        self.addExtImage(id='image', file=gifImage)
        self.image._finish()
        self.addExtImage(id='image', file=gifImage, folder=self.subfolder)
        self.image._finish()
        self.failUnless(self._exists('image.gif'))
        self.failIf(self._exists('image.gif.undo'))
        self.failUnless(self._exists('image.1.gif'))
        self.failIf(self._exists('image.1.gif.undo'))

    def testUniquePreviewName(self):
        # Create a unique preview name
        self.addExtImage(id='image', file=jpegImage)
        self.image.manage_create_prev(100, 100, ratio=1)
        self.image._finish()
        self.failUnless(self._exists('image.jpg'))
        self.failIf(self._exists('image.jpg.undo'))
        self.failUnless(self._exists('image.1.jpg')) # Generated previews are always jpeg
        self.failIf(self._exists('image.1.jpg.undo'))

    def testUndoNameOnDelete(self):
        # Create a .undo file on delete
        self.addExtImage(id='image', file=gifImage)
        self.folder.manage_delObjects(['image'])
        self.failIf(self._exists('image.gif'))
        self.failUnless(self._exists('image.gif.undo'))

    def testUndoNameOnDeletePreview(self):
        # Create a .undo file for the preview image on delete
        self.addExtImage(id='image', file=gifImage)
        self.image.manage_create_prev(100, 100, ratio=1)
        self.image._finish()
        self.failUnless(self._exists('image.gif'))
        self.failUnless(self._exists('image.jpg'))  # Generated previews are always jpeg
        self.folder.manage_delObjects(['image'])
        self.failIf(self._exists('image.gif'))
        self.failUnless(self._exists('image.gif.undo'))
        self.failIf(self._exists('image.jpg'))
        self.failUnless(self._exists('image.jpg.undo'))

    def testUndoNameOnUpload(self):
        # Do not create a .undo file on upload
        self.addExtImage(id='image', file=gifImage)
        self.image.manage_file_upload(file=gifImage)
        self.image._finish()
        self.failUnless(self._exists('image.gif'))
        self.failIf(self._exists('image.gif.undo'))
        self.failIf(self._exists('image.1.gif'))

    def testUndoNameIsNotReused(self):
        # If an .undo file exists the name is not reused
        self.addExtImage(id='image', file=gifImage)
        self.folder.manage_delObjects(['image'])
        self.addExtImage(id='image', file=gifImage)
        self.image._finish()
        self.failIf(self._exists('image.gif'))
        self.failUnless(self._exists('image.gif.undo'))
        self.failUnless(self._exists('image.1.gif'))


class TestRepositoryExtensions(ExtFileTestCase):
    '''Test repository file extensions'''

    def afterClear(self):
        ExtFileTestCase.afterClear(self)
        ExtFile.REPOSITORY_EXTENSIONS = Config.MIMETYPE_REPLACE

    def testDefaultContentType(self):
        # Use default content type
        self.addExtImage(id='image', file=notImage)
        self.image._finish()
        self.failUnless(self._exists('image.exe'))

    def testDefaultContentTypeKeepsExistingExtension(self):
        # Retain existing file extension if content type is octet-stream
        self.addExtImage(id='image.foo', file=notImage)
        self.image._finish()
        self.failUnless(self._exists('image.foo'))

    def testDefaultContentTypeMimetypeAppend(self):
        # Use default content type
        ExtFile.REPOSITORY_EXTENSIONS = Config.MIMETYPE_APPEND
        self.testDefaultContentType()

    def testDefaultContentTypeKeepsExistingExtensionMimetypeAppend(self):
        # Retain existing file extension if content type is octet-stream
        ExtFile.REPOSITORY_EXTENSIONS = Config.MIMETYPE_APPEND
        self.testDefaultContentTypeKeepsExistingExtension()


class TestDownloadPermission(ExtFileTestCase):
    '''Tests the DownloadPermission'''

    def testPermissionExists(self):
        # DownloadPermission should exist
        perms = self.app.permissionsOfRole('Manager')
        perms = [x['name'] for x in perms if x['selected']]
        self.failUnless(ExtFile.DownloadPermission in perms)

    def testDownloadPermissionCheck(self):
        # The use_download_permission_check property
        # should control whether we can see the full image.
        self.addExtImage(id='image', file=gifImage)
        self.failUnless(self.image._access_permitted())
        self.image.use_download_permission_check = 1
        self.failIf(self.image._access_permitted())

    def testShowPreviewIfNoDownloadPermission(self):
        # If we don't have the permission we should only
        # see the preview.
        self.addExtImage(id='image', file=gifImage)
        self.image.use_download_permission_check = 1
        self.image.manage_create_prev(maxx=10, maxy=10, ratio=1)
        dummy, dummy, dummy, preview = self.image._get_file_to_serve()
        self.failUnless(preview)

    def testShowIconIfNoDownloadPermission(self):
        # If we don't have the permission, and there is no preview,
        # we should only see the icon.
        self.addExtImage(id='image', file=gifImage)
        self.image.use_download_permission_check = 1
        dummy, dummy, icon, dummy = self.image._get_file_to_serve()
        self.failUnless(icon)

    def testPreviewTagIfNoDownloadPermission(self):
        # If we don't have the permission we should only
        # see the preview.
        self.addExtImage(id='image', file=gifImage)
        self.image.use_download_permission_check = 1
        self.image.manage_create_prev(maxx=10, maxy=10, ratio=1)
        tag = self.image.tag()
        # Permission is not checked in static mode
        if self.image.static_mode():
            self.failUnless(tag.find('/image.jpg')>=0)
        else:
            self.failUnless(tag.find('/image?preview=1')>=0)

    def testIconTagIfNoDownloadPermission(self):
        # If we don't have the permission, and there is no preview,
        # we should only see the icon.
        self.addExtImage(id='image', file=gifImage)
        self.image.use_download_permission_check = 1
        tag = self.image.tag()
        self.failUnless(tag.find('/image?icon=1')>=0)

    def testPreviewTagIfNotWebviewable(self):
        # If the image is not webviewable we should only
        # see the preview.
        self.addExtImage(id='image', file=tiffImage)
        self.image.manage_create_prev(maxx=10, maxy=10, ratio=1)
        tag = self.image.tag()
        # Permission is not checked in static mode
        if self.image.static_mode():
            self.failUnless(tag.find('/image.jpg')>=0)
        else:
            self.failUnless(tag.find('/image?preview=1')>=0)


class TestGetOwner(ExtFileTestCase):

    def afterSetUp(self):
        ExtFileTestCase.afterSetUp(self)
        self.addExtFile(id='file.zip', file=gifImage)
        self.addExtImage(id='image.gif', file=gifImage)

    def testFileOwner(self):
        self.assertEqual(self.file.getOwner().getId(), ZopeTestCase.user_name)
        self.assertEqual(self.file.getOwnerTuple(),
                         ([ZopeTestCase.folder_name, 'acl_users'], ZopeTestCase.user_name))

    def testImageOwner(self):
        self.assertEqual(self.image.getOwner().getId(), ZopeTestCase.user_name)
        self.assertEqual(self.image.getOwnerTuple(),
                         ([ZopeTestCase.folder_name, 'acl_users'], ZopeTestCase.user_name))


class TestFTPget(ExtFileTestCase):

    def afterSetUp(self):
        ExtFileTestCase.afterSetUp(self)
        self.addExtFile(id='file.zip', file=gifImage)
        self.addExtImage(id='image.gif', file=gifImage)

    def testFTPgetFile(self):
        from StringIO import StringIO
        response = self.app.REQUEST.RESPONSE
        response.stdout = StringIO() # Shut up
        result = self.file.manage_FTPget()
        #self.assertEqual(result, '')
        self.assertEqual(response.headers.get('content-type'), 'application/zip')
        self.assertEqual(response.headers.get('content-length'), '%s' % self._fsize(gifImage))

    def testFTPgetImage(self):
        from StringIO import StringIO
        response = self.app.REQUEST.RESPONSE
        response.stdout = StringIO() # Shut up
        result = self.image.manage_FTPget()
        #self.assertEqual(result, '')
        self.assertEqual(response.headers.get('content-type'), 'image/gif')
        self.assertEqual(response.headers.get('content-length'), '%s' % self._fsize(gifImage))


class TestPublish(ZopeTestCase.Functional, ExtFileTestCase):

    def afterSetUp(self):
        ExtFileTestCase.afterSetUp(self)
        self.addExtFile(id='file.zip', file=gifImage)
        self.addExtImage(id='image.gif', file=gifImage)

    def testPublishFile(self):
        folder_path = self.folder.absolute_url(1)
        response = self.publish(folder_path+'/file.zip')
        self.assertEqual(response.getStatus(), 200)
        self.failUnless(response.getHeader('Content-Type').startswith('application/zip'))

    def testPublishImage(self):
        folder_path = self.folder.absolute_url(1)
        response = self.publish(folder_path+'/image.gif')
        self.assertEqual(response.getStatus(), 200)
        self.failUnless(response.getHeader('Content-Type').startswith('image/gif'))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestExtFileAdd))
    suite.addTest(makeSuite(TestExtImageAdd))
    suite.addTest(makeSuite(TestExtFileUpload))
    suite.addTest(makeSuite(TestExtImageUpload))
    suite.addTest(makeSuite(TestExtFileContentType))
    suite.addTest(makeSuite(TestExtImageContentType))
    suite.addTest(makeSuite(TestExtFileCopyPaste))
    suite.addTest(makeSuite(TestExtImageCopyPaste))
    suite.addTest(makeSuite(TestRepository))
    suite.addTest(makeSuite(TestRepositoryFiles))
    suite.addTest(makeSuite(TestRepositoryExtensions))
    suite.addTest(makeSuite(TestDownloadPermission))
    suite.addTest(makeSuite(TestGetOwner))
    suite.addTest(makeSuite(TestFTPget))
    suite.addTest(makeSuite(TestPublish))
    return suite

if __name__ == '__main__':
    framework()

