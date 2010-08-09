#
# Tests the ExtFile product
#

from Testing import ZopeTestCase

ZopeTestCase.installProduct('ExtFile')
ZopeTestCase.installProduct('PythonScripts')
ZopeTestCase.utils.startZServer()

from StringIO import StringIO
import transaction
import os

from Products.ExtFile.testing import ExtFileTestCase
from Products.ExtFile.testing import gifImage, jpegImage, tiffImage, notImage
from Products.ExtFile.testing import makeFileUpload
from Products.ExtFile.testing import makePdata
from Products.ExtFile.testing import copymove_perms
from Products.ExtFile import ExtFile
from Products.ExtFile import ExtImage
from Products.ExtFile import configuration


class TestExtFileAdd(ExtFileTestCase):
    '''Test ExtFile creation'''

    def testAddFileFromFileName(self):
        # Add File from file name
        self.addExtFile(id='file', file=notImage)
        self.file._finish()
        self.assertEqual(self.reposit(), ['file.exe'])
        self.assertEqual(self.file.get_size(), self._fsize(notImage))

    def testAddFileFromFileHandle(self):
        # Add File from file handle
        self.addExtFile(id='file', file=open(notImage, 'rb'))
        self.file._finish()
        self.assertEqual(self.reposit(), ['file.exe'])
        self.assertEqual(self.file.get_size(), self._fsize(notImage))

    def testAddFileFromFileUpload(self):
        # Add File from file upload
        self.addExtFile(id='file', file=makeFileUpload(notImage, 'application/octet-stream'))
        self.file._finish()
        self.assertEqual(self.reposit(), ['file.exe'])
        self.assertEqual(self.file.get_size(), self._fsize(notImage))

    def testAddFileFromPdata(self):
        # Add File from Pdata structure
        self.addExtFile(id='file', file=makePdata(notImage))
        self.file._finish()
        self.assertEqual(self.reposit(), ['file.exe'])
        self.assertEqual(self.file.get_size(), self._fsize(notImage))

    def testAddFileWithIdFromFilename(self):
        # Add File without id - should use filename instead
        self.addExtFile(id='', file=makeFileUpload(notImage, 'application/octet-stream', filename='foo'))
        self.file._finish()
        self.assertEqual(self.file.getId(), 'foo')
        self.assertEqual(self.reposit(), ['foo.exe'])
        self.assertEqual(self.file.get_size(), self._fsize(notImage))

    def testAddFileWithLatin1Filename(self):
        # Add File without id - should use filename instead
        self.addExtFile(id='', file=makeFileUpload(notImage, 'application/octet-stream', filename='M\xe4dchen'))
        self.file._finish()
        self.assertEqual(self.file.getId(), 'Madchen')
        self.assertEqual(self.reposit(), ['Madchen.exe'])
        self.assertEqual(self.file.get_size(), self._fsize(notImage))

    def testAddFileWithUTF8Filename(self):
        # Add File without id - should use filename instead
        self.addExtFile(id='', file=makeFileUpload(notImage, 'application/octet-stream', filename='M\303\244dchen'))
        self.file._finish()
        self.assertEqual(self.file.getId(), 'Madchen')
        self.assertEqual(self.reposit(), ['Madchen.exe'])
        self.assertEqual(self.file.get_size(), self._fsize(notImage))


class TestExtImageAdd(ExtFileTestCase):
    '''Test ExtImage creation'''

    def testAddImageFromFileName(self):
        # Add Image from file name
        self.addExtImage(id='image', file=gifImage)
        self.image._finish()
        self.assertEqual(self.reposit(), ['image.gif'])
        self.assertEqual(self.image.get_size(), self._fsize(gifImage))

    def testAddPreviewFromFileName(self):
        # Add Image preview from file name
        self.addExtImage(id='image', file=gifImage, is_preview=1)
        self.image._finish()
        self.assertEqual(self.reposit(), ['image.gif'])
        self.assertEqual(self.image.get_size(), 0)
        self.assertEqual(self.image.get_prev_size(), self._fsize(gifImage))

    def testAddImageFromFileHandle(self):
        # Add Image from file handle
        self.addExtImage(id='image', file=open(gifImage, 'rb'))
        self.image._finish()
        self.assertEqual(self.reposit(), ['image.gif'])
        self.assertEqual(self.image.get_size(), self._fsize(gifImage))

    def testAddPreviewFromFileHandle(self):
        # Add Image preview from file handle
        self.addExtImage(id='image', file=open(gifImage, 'rb'), is_preview=1)
        self.image._finish()
        self.assertEqual(self.reposit(), ['image.gif'])
        self.assertEqual(self.image.get_size(), 0)
        self.assertEqual(self.image.get_prev_size(), self._fsize(gifImage))

    def testAddImageFromFileUpload(self):
        # Add Image from file upload
        self.addExtImage(id='image', file=makeFileUpload(gifImage, 'image/gif'))
        self.image._finish()
        self.assertEqual(self.reposit(), ['image.gif'])
        self.assertEqual(self.image.get_size(), self._fsize(gifImage))

    def testAddPreviewFromFileUpload(self):
        # Add Image preview from file upload
        self.addExtImage(id='image', file=makeFileUpload(gifImage, 'image/gif'), is_preview=1)
        self.image._finish()
        self.assertEqual(self.reposit(), ['image.gif'])
        self.assertEqual(self.image.get_size(), 0)
        self.assertEqual(self.image.get_prev_size(), self._fsize(gifImage))

    def testAddImageFromPdata(self):
        # Add Image from Pdata structure
        self.addExtImage(id='image', file=makePdata(jpegImage))
        self.image._finish()
        self.assertEqual(self.reposit(), ['image.jpg'])
        self.assertEqual(self.image.get_size(), self._fsize(jpegImage))

    def testAddPreviewFromPdata(self):
        # Add Image preview from Pdata structure
        self.addExtImage(id='image', file=makePdata(jpegImage), is_preview=1)
        self.image._finish()
        self.assertEqual(self.reposit(), ['image.jpg'])
        self.assertEqual(self.image.get_size(), 0)
        self.assertEqual(self.image.get_prev_size(), self._fsize(jpegImage))

    def testAddImageWithIdFromFilename(self):
        # Add File without id - should use filename instead
        self.addExtImage(id='', file=makeFileUpload(gifImage, 'image/gif', filename='foo'))
        self.image._finish()
        self.assertEqual(self.image.getId(), 'foo')
        self.assertEqual(self.reposit(), ['foo.gif'])
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
        self.assertEqual(self.reposit(), ['Madchen.gif'])
        self.assertEqual(self.image.get_size(), self._fsize(gifImage))

    def testAddImageWithUTF8Filename(self):
        # Add File without id - should use filename instead
        self.addExtImage(id='', file=makeFileUpload(gifImage, 'image/gif', filename='M\303\244dchen'))
        self.image._finish()
        self.assertEqual(self.image.getId(), 'Madchen')
        self.assertEqual(self.reposit(), ['Madchen.gif'])
        self.assertEqual(self.image.get_size(), self._fsize(gifImage))


class TestExtFileUpload(ExtFileTestCase):
    '''Test ExtFile upload'''

    def testManageFileUploadFromFileName(self):
        # Upload File from file name
        self.addExtFile(id='file', file='')
        self.file.manage_file_upload(file=notImage)
        self.file._finish()
        self.assertEqual(self.reposit(), ['file.exe'])
        self.assertEqual(self.file.get_size(), self._fsize(notImage))

    def testManageFileUploadFromFileHandle(self):
        # Upload File from file handle
        self.addExtFile(id='file', file='')
        self.file.manage_file_upload(file=open(notImage, 'rb'))
        self.file._finish()
        self.assertEqual(self.reposit(), ['file.exe'])
        self.assertEqual(self.file.get_size(), self._fsize(notImage))

    def testManageFileUploadFromFileUpload(self):
        # Upload File from file upload
        self.addExtFile(id='file', file='')
        self.file.manage_file_upload(file=makeFileUpload(notImage, 'application/octet-stream'))
        self.file._finish()
        self.assertEqual(self.reposit(), ['file.exe'])
        self.assertEqual(self.file.get_size(), self._fsize(notImage))

    def testManageFileUploadFromPdata(self):
        # Upload File from Pdata structure
        self.addExtFile(id='file', file='')
        self.file.manage_file_upload(file=makePdata(notImage))
        self.file._finish()
        self.assertEqual(self.reposit(), ['file.exe'])
        self.assertEqual(self.file.get_size(), self._fsize(notImage))

    def testManageUploadFromStringBuffer(self):
        # Upload File from file name
        self.addExtFile(id='file', file='')
        self.file.manage_upload(file=open(notImage, 'rb').read())
        self.file._finish()
        self.assertEqual(self.reposit(), ['file.exe'])
        self.assertEqual(self.file.get_size(), self._fsize(notImage))

    def testManageUploadFromFileHandle(self):
        # Upload File from file handle
        self.addExtFile(id='file', file='')
        self.file.manage_upload(file=open(notImage, 'rb'))
        self.file._finish()
        self.assertEqual(self.reposit(), ['file.exe'])
        self.assertEqual(self.file.get_size(), self._fsize(notImage))

    def testManageUploadFromFileUpload(self):
        # Upload File from file upload
        self.addExtFile(id='file', file='')
        self.file.manage_upload(file=makeFileUpload(notImage, 'application/octet-stream'))
        self.file._finish()
        self.assertEqual(self.reposit(), ['file.exe'])
        self.assertEqual(self.file.get_size(), self._fsize(notImage))

    def testManageUploadFromPdata(self):
        # Upload File from Pdata
        self.addExtFile(id='file', file='')
        self.file.manage_upload(file=makePdata(notImage))
        self.file._finish()
        self.assertEqual(self.reposit(), ['file.exe'])
        self.assertEqual(self.file.get_size(), self._fsize(notImage))


class TestExtImageUpload(ExtFileTestCase):
    '''Test ExtImage upload'''

    def testManageFileUploadFromFileName(self):
        # Upload Image from file name
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=gifImage)
        self.image._finish()
        self.assertEqual(self.reposit(), ['image.gif'])
        self.assertEqual(self.image.get_size(), self._fsize(gifImage))

    def testManageFileUploadFromFileHandle(self):
        # Upload Image from file handle
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=open(gifImage, 'rb'))
        self.image._finish()
        self.assertEqual(self.reposit(), ['image.gif'])
        self.assertEqual(self.image.get_size(), self._fsize(gifImage))

    def testManageFileUploadFromFileUpload(self):
        # Upload Image from file upload
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=makeFileUpload(gifImage, 'image/gif'))
        self.image._finish()
        self.assertEqual(self.reposit(), ['image.gif'])
        self.assertEqual(self.image.get_size(), self._fsize(gifImage))

    def testManageFileUploadFromPdata(self):
        # Upload Image from Pdata structure
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=makePdata(jpegImage), content_type='image/jpeg')
        self.image._finish()
        self.assertEqual(self.reposit(), ['image.jpg'])
        self.assertEqual(self.image.get_size(), self._fsize(jpegImage))

    def testManageUploadFromStringBuffer(self):
        # Upload Image from file name
        self.addExtImage(id='image', file='')
        self.image.manage_upload(file=open(gifImage, 'rb').read())
        self.image._finish()
        self.assertEqual(self.reposit(), ['image.gif'])
        self.assertEqual(self.image.get_size(), self._fsize(gifImage))

    def testManageUploadFromFileHandle(self):
        # Upload Image from file handle
        self.addExtImage(id='image', file='')
        self.image.manage_upload(file=open(gifImage, 'rb'))
        self.image._finish()
        self.assertEqual(self.reposit(), ['image.gif'])
        self.assertEqual(self.image.get_size(), self._fsize(gifImage))

    def testManageUploadFromFileUpload(self):
        # Upload Image from file upload
        self.addExtImage(id='image', file='')
        self.image.manage_upload(file=makeFileUpload(gifImage, 'image/gif'))
        self.image._finish()
        self.assertEqual(self.reposit(), ['image.gif'])
        self.assertEqual(self.image.get_size(), self._fsize(gifImage))

    def testManageUploadFromPdata(self):
        # Upload Image from Pdata
        self.addExtImage(id='image', file='')
        self.image.manage_upload(file=makePdata(jpegImage), content_type='image/jpeg')
        self.image._finish()
        self.assertEqual(self.reposit(), ['image.jpg'])
        self.assertEqual(self.image.get_size(), self._fsize(jpegImage))


class TestExtFileContentType(ExtFileTestCase):
    '''Test ExtFile content-type detection'''

    def testDefaultContentType(self):
        # Use default content type
        self.addExtFile(id='file', file=notImage)
        self.file._finish()
        self.assertEqual(self.file.content_type, 'application/octet-stream')
        self.assertEqual(self.reposit(), ['file.exe'])

    def testContentTypeExplicit(self):
        # Use passed-in content type
        self.addExtFile(id='file', file=notImage, content_type='image/jpeg')
        self.file._finish()
        self.assertEqual(self.file.content_type, 'image/jpeg')
        self.assertEqual(self.reposit(), ['file.jpg'])

    def testContentTypeFromId(self):
        # Detect GIF content type from file id
        self.addExtFile(id='file.gif', file=notImage)
        self.file._finish()
        self.assertEqual(self.file.content_type, 'image/gif')
        self.assertEqual(self.reposit(), ['file.gif'])

    def testContentTypeFromIdExplicit(self):
        # Passed-in content type trumps detection by id
        self.addExtFile(id='file.gif', file=notImage, content_type='image/jpeg')
        self.file._finish()
        self.assertEqual(self.file.content_type, 'image/jpeg')
        self.assertEqual(self.reposit(), ['file.jpg'])

    def testContentTypeFromHeaders(self):
        # Detect GIF content type from file upload headers
        self.addExtFile(id='file', file=makeFileUpload(notImage, 'image/gif'))
        self.file._finish()
        self.assertEqual(self.file.content_type, 'image/gif')
        self.assertEqual(self.reposit(), ['file.gif'])

    def testContentTypeFromHeadersExplicit(self):
        # Passed-in content type trumps detection by headers
        self.addExtFile(id='file', file=makeFileUpload(notImage, 'image/gif'), content_type='image/jpeg')
        self.file._finish()
        self.assertEqual(self.file.content_type, 'image/jpeg')
        self.assertEqual(self.reposit(), ['file.jpg'])

    def testContentTypeFromHttpUpload(self):
        # Detect content type from download headers
        self.addExtFile(id='file', file=notImage)
        self.file.manage_http_upload(url=self.app.TiffImage.absolute_url())
        self.file._finish()
        self.assertEqual(self.file.content_type, 'image/tiff')
        # File is renamed
        self.assertEqual(self.reposit(), ['file.exe.undo', 'file.tif'])

    def testContentTypeFromHttpUploadDefault(self):
        # Detect content type from download headers
        self.addExtFile(id='file', file=notImage)
        self.file.manage_http_upload(url=self.app.NotImage.absolute_url())
        self.file._finish()
        self.assertEqual(self.file.content_type, 'application/octet-stream')
        self.assertEqual(self.reposit(), ['file.exe'])


class TestExtImageContentType(ExtFileTestCase):
    '''Test ExtImage content-type detection'''

    def testDefaultContentType(self):
        # Use default content type
        self.addExtImage(id='image', file=notImage)
        self.image._finish()
        self.assertEqual(self.image.content_type, 'application/octet-stream')
        self.assertEqual(self.reposit(), ['image.exe'])

    def testContentTypeExplicit(self):
        # Use passed-in content type when we cannot detect from content
        self.addExtImage(id='image', file=notImage, content_type='image/jpeg')
        self.image._finish()
        self.assertEqual(self.image.content_type, 'image/jpeg')
        self.assertEqual(self.reposit(), ['image.jpg'])

    def testContentTypeFromId(self):
        # Detect GIF content type from file id
        self.addExtImage(id='image.gif', file=notImage)
        self.image._finish()
        self.assertEqual(self.image.content_type, 'image/gif')
        self.assertEqual(self.reposit(), ['image.gif'])

    def testContentTypeFromIdExplicit(self):
        # Passed-in content type trumps detection by id
        self.addExtImage(id='image.gif', file=notImage, content_type='image/jpeg')
        self.image._finish()
        self.assertEqual(self.image.content_type, 'image/jpeg')
        self.assertEqual(self.reposit(), ['image.jpg'])

    def testContentTypeFromHeaders(self):
        # Detect GIF content type from file upload headers
        self.addExtImage(id='image', file=makeFileUpload(notImage, 'image/gif'))
        self.image._finish()
        self.assertEqual(self.image.content_type, 'image/gif')
        self.assertEqual(self.reposit(), ['image.gif'])

    def testContentTypeFromHeadersExplicit(self):
        # Passed-in content type trumps detection by headers
        self.addExtImage(id='image', file=makeFileUpload(notImage, 'image/gif'), content_type='image/jpeg')
        self.image._finish()
        self.assertEqual(self.image.content_type, 'image/jpeg')
        self.assertEqual(self.reposit(), ['image.jpg'])

    def testContentTypeFromHttpUpload(self):
        # Detect content type from download headers
        self.addExtImage(id='image', file=notImage)
        self.image.manage_http_upload(url=self.app.TiffImage.absolute_url())
        self.image._finish()
        self.assertEqual(self.image.content_type, 'image/tiff')
        # File is renamed
        self.assertEqual(self.reposit(), ['image.exe.undo', 'image.tif'])

        # Check TIFF dimension sniffing
        self.assertEqual(self.image.width(), 200)
        self.assertEqual(self.image.height(), 136)

    def testContentTypeFromGifContent(self):
        # Detect GIF content type from file contents
        self.addExtImage(id='image', file=gifImage)
        self.image._finish()
        self.assertEqual(self.image.content_type, 'image/gif')
        self.assertEqual(self.reposit(), ['image.gif'])

    def testContentTypeFromGifContentExplicit(self):
        # Detect GIF content type even when passing a content type
        self.addExtImage(id='image', file=gifImage, content_type='image/jpeg')
        self.image._finish()
        self.assertEqual(self.image.content_type, 'image/gif')
        self.assertEqual(self.reposit(), ['image.gif'])

    def testContentTypeFromJpegContent(self):
        # Detect JPEG content type from file contents
        self.addExtImage(id='image', file=jpegImage)
        self.image._finish()
        self.assertEqual(self.image.content_type, 'image/jpeg')
        self.assertEqual(self.reposit(), ['image.jpg'])

    def testContentTypeFromJpegContentExplicit(self):
        # Detect JPEG content type even when passing a content type
        self.addExtImage(id='image', file=jpegImage, content_type='image/tiff')
        self.image._finish()
        self.assertEqual(self.image.content_type, 'image/jpeg')
        self.assertEqual(self.reposit(), ['image.jpg'])

    def testContentTypeFromGifString(self):
        # Detect GIF content type from string buffer
        self.addExtImage(id='image', file=notImage)
        self.image.manage_upload(file=open(gifImage, 'rb').read())
        self.image._finish()
        self.assertEqual(self.image.content_type, 'image/gif')
        # File is renamed
        self.assertEqual(self.reposit(), ['image.exe.undo', 'image.gif'])

    def testContentTypeFromJpegPUT(self):
        # Detect JPEG content type from PUT' image
        self.addExtImage(id='image', file=open(notImage, 'rb'))
        request = self.app.REQUEST
        request['BODYFILE'] = open(jpegImage, 'rb')
        self.image.PUT(request, request.RESPONSE)
        self.image._finish()
        self.assertEqual(self.image.content_type, 'image/jpeg')
        # File is renamed
        self.assertEqual(self.reposit(), ['image.exe.undo', 'image.jpg'])
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
        self.assertEqual(self.reposit(), ['image.1.gif', 'image.gif'])

    def testCopyPaste(self):
        # Copy and paste a file
        cb = self.folder.manage_copyObjects(['image.gif'])
        self.subfolder.manage_pasteObjects(cb)
        self.file._finish()
        self.subfolder['image.gif']._finish()
        self.assertEqual(self.reposit(), ['image.1.gif', 'image.gif'])
        self.assertEqual(self.subfolder['image.gif'].get_size(), self._fsize(gifImage))

    def testCutPaste(self):
        # Cut and paste a file
        cb = self.folder.manage_cutObjects(['image.gif'])
        self.subfolder.manage_pasteObjects(cb)
        self.file._finish()
        self.subfolder['image.gif']._finish()
        self.assertEqual(self.reposit(), ['image.1.gif', 'image.gif.undo'])
        self.assertEqual(self.subfolder['image.gif'].get_size(), self._fsize(gifImage))

    def testRename(self):
        # Rename a binary file
        self.folder.manage_renameObject('image.gif', 'image44.gif')
        self.file._finish()
        self.folder['image44.gif']._finish()
        self.assertEqual(self.reposit(), ['image.gif.undo', 'image44.gif'])

    def testRenameText(self):
        # Rename a text file
        os.remove(self._fsname('image.gif.tmp')) # :-P

        self.addExtFile(id='fred.txt', file=StringIO('abcdefg'))
        transaction.savepoint(1) # need a _p_jar

        self.folder.manage_renameObject('fred.txt', 'fred44.txt')
        self.file._finish()
        self.folder['fred44.txt']._finish()
        self.assertEqual(self.reposit(), ['fred.txt.undo', 'fred44.txt'])

    def testCOPY(self):
        # WebDAV copy a file
        req = self.app.REQUEST
        req.environ['HTTP_DEPTH'] = 'infinity'
        req.environ['HTTP_DESTINATION'] = 'http://dummy.org/%s/subfolder/image.gif' % ZopeTestCase.folder_name
        self.folder['image.gif'].COPY(req, req.RESPONSE)
        self.file._finish()
        self.subfolder['image.gif']._finish()
        self.assertEqual(self.reposit(), ['image.1.gif', 'image.gif'])
        self.assertEqual(self.subfolder['image.gif'].get_size(), self._fsize(gifImage))

    def testMOVE(self):
        # WebDAV move a file
        req = self.app.REQUEST
        req.environ['HTTP_DEPTH'] = 'infinity'
        req.environ['HTTP_DESTINATION'] = 'http://dummy.org/%s/subfolder/image.gif' % ZopeTestCase.folder_name
        self.folder['image.gif'].MOVE(req, req.RESPONSE)
        self.file._finish()
        self.subfolder['image.gif']._finish()
        self.assertEqual(self.reposit(), ['image.1.gif', 'image.gif.undo'])
        self.assertEqual(self.subfolder['image.gif'].get_size(), self._fsize(gifImage))

    def testDELETE(self):
        # WebDAV delete a file
        req = self.app.REQUEST
        req['URL'] = 'http://dummy.org/%s/image.gif' % ZopeTestCase.folder_name
        self.folder['image.gif'].DELETE(req, req.RESPONSE)
        self.file._finish()
        self.assertEqual(self.reposit(), ['image.gif.undo'])

    def testCopyOfProtection(self):
        # Copy and paste a file into the same folder.
        # The filenames should not begin with 'copy_of_'
        cb = self.folder.manage_copyObjects(['image.gif'])
        self.folder.manage_pasteObjects(cb)
        self.file._finish()
        self.folder['copy_of_image.gif']._finish()
        self.assertEqual(self.reposit(), ['image.1.gif', 'image.gif'])
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
                                                    create_prev=configuration.UPLOAD_RESIZE,
                                                    maxx=100, maxy=100, ratio=1)
        transaction.savepoint(1) # need a _p_jar

    def testClone(self):
        # Clone an image
        self.subfolder.manage_clone(self.image, 'image.gif')
        self.image._finish()
        self.subfolder['image.gif']._finish()
        self.assertEqual(self.reposit(), ['image.1.gif',
                                          'image.1.jpg',
                                          'image.gif',
                                          'image.jpg'])

    def testCopyPaste(self):
        # Copy and paste an image
        cb = self.folder.manage_copyObjects(['image.gif'])
        self.subfolder.manage_pasteObjects(cb)
        self.image._finish()
        self.subfolder['image.gif']._finish()
        self.assertEqual(self.reposit(), ['image.1.gif',
                                          'image.1.jpg',
                                          'image.gif',
                                          'image.jpg'])
        self.assertEqual(self.subfolder['image.gif'].get_size(), self._fsize(gifImage))

    def testCutPaste(self):
        # Cut and paste an image
        cb = self.folder.manage_cutObjects(['image.gif'])
        self.subfolder.manage_pasteObjects(cb)
        self.image._finish()
        self.subfolder['image.gif']._finish()
        self.assertEqual(self.reposit(), ['image.1.gif',
                                          'image.1.jpg',
                                          'image.gif.undo',
                                          'image.jpg.undo'])
        self.assertEqual(self.subfolder['image.gif'].get_size(), self._fsize(gifImage))

    def testRename(self):
        # Rename a GIF image with preview
        self.folder.manage_renameObject('image.gif', 'image44.gif')
        self.image._finish()
        self.folder['image44.gif']._finish()
        self.assertEqual(self.reposit(), ['image.gif.undo',
                                          'image.jpg.undo',
                                          'image44.gif',
                                          'image44.jpg'])
        self.assertEqual(self.folder['image44.gif'].filename[-1], 'image44.gif')
        self.assertEqual(self.folder['image44.gif'].prev_filename[-1], 'image44.jpg')

    def testRenameJpeg(self):
        # Rename a JPEG image with preview
        os.remove(self._fsname('image.gif.tmp')) # :-P
        os.remove(self._fsname('image.jpg.tmp')) # :-P

        self.addExtImage(id='image.jpg', file=jpegImage)
        self.folder['image.jpg'].manage_file_upload(file=jpegImage, is_preview=1,
                                                    create_prev=configuration.UPLOAD_RESIZE,
                                                    maxx=100, maxy=100, ratio=1)
        transaction.savepoint(1) # need a _p_jar

        self.folder.manage_renameObject('image.jpg', 'image44.jpg')
        self.image._finish()
        self.folder['image44.jpg']._finish()
        self.assertEqual(self.reposit(), ['image.1.jpg.undo',
                                          'image.jpg.undo',
                                          'image44.1.jpg',
                                          'image44.jpg'])
        self.assertEqual(self.folder['image44.jpg'].filename[-1], 'image44.jpg')
        self.assertEqual(self.folder['image44.jpg'].prev_filename[-1], 'image44.1.jpg')

    def testCOPY(self):
        # WebDAV copy an image
        req = self.app.REQUEST
        req.environ['HTTP_DEPTH'] = 'infinity'
        req.environ['HTTP_DESTINATION'] = 'http://dummy.org/%s/subfolder/image.gif' % ZopeTestCase.folder_name
        self.folder['image.gif'].COPY(req, req.RESPONSE)
        self.image._finish()
        self.subfolder['image.gif']._finish()
        self.assertEqual(self.reposit(), ['image.1.gif',
                                          'image.1.jpg',
                                          'image.gif',
                                          'image.jpg'])
        self.assertEqual(self.subfolder['image.gif'].get_size(), self._fsize(gifImage))

    def testMOVE(self):
        # WebDAV move an image
        req = self.app.REQUEST
        req.environ['HTTP_DEPTH'] = 'infinity'
        req.environ['HTTP_DESTINATION'] = 'http://dummy.org/%s/subfolder/image.gif' % ZopeTestCase.folder_name
        self.folder['image.gif'].MOVE(req, req.RESPONSE)
        self.image._finish()
        self.subfolder['image.gif']._finish()
        self.assertEqual(self.reposit(), ['image.1.gif',
                                          'image.1.jpg',
                                          'image.gif.undo',
                                          'image.jpg.undo'])
        self.assertEqual(self.subfolder['image.gif'].get_size(), self._fsize(gifImage))

    def testDELETE(self):
        # WebDAV delete an image
        req = self.app.REQUEST
        req['URL'] = 'http://dummy.org/%s/image.gif' % ZopeTestCase.folder_name
        self.folder['image.gif'].DELETE(req, req.RESPONSE)
        self.image._finish()
        self.assertEqual(self.reposit(), ['image.gif.undo',
                                          'image.jpg.undo'])

    def testPUTRecreatesPreview(self):
        # PUT an image; the preview should be regenerated.
        self.image._finish()
        self.assertEqual(self.reposit(), ['image.gif',       # main image
                                          'image.jpg'])      # preview
        req = self.app.REQUEST
        req['BODYFILE'] = open(gifImage, 'rb')
        self.image.PUT(req, req.RESPONSE)
        self.assertEqual(self.reposit(), ['image.gif',       # old image
                                          'image.gif.tmp',   # newly put image
                                          'image.jpg',       # old preview
                                          'image.jpg.tmp'])  # regenerated preview
        self.image._finish()
        self.assertEqual(self.reposit(), ['image.gif',       # new image
                                          'image.jpg'])      # regenerated preview

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


class TestExtFileCopyPasteSyncZodb(ExtFileTestCase):
    '''Tests cut/copy/paste/rename/clone with sync-zodb on'''

    def afterSetUp(self):
        ExtFile.REPOSITORY = configuration.SYNC_ZODB
        ExtFileTestCase.afterSetUp(self)
        self.folder_path = self.folder.getPhysicalPath()[1:]
        self.folder.manage_addFolder('subfolder')
        self.subfolder = self.folder['subfolder']
        self.subfolder_path = self.subfolder.getPhysicalPath()[1:]
        self.setPermissions(copymove_perms)
        self.addExtFile(id='image.gif', file=gifImage)
        transaction.savepoint(1) # need a _p_jar

    def afterClear(self):
        ExtFileTestCase.afterClear(self)
        ExtFile.REPOSITORY = configuration.FLAT

    def testClone(self):
        # Clone a file
        self.subfolder.manage_clone(self.file, 'image.gif')
        self.file._finish()
        self.subfolder['image.gif']._finish()
        self.assertEqual(self.reposit(*self.folder_path), ['image.gif', 'subfolder'])
        self.assertEqual(self.reposit(*self.subfolder_path), ['image.gif'])

    def testCopyPaste(self):
        # Copy and paste a file
        cb = self.folder.manage_copyObjects(['image.gif'])
        self.subfolder.manage_pasteObjects(cb)
        self.file._finish()
        self.subfolder['image.gif']._finish()
        self.assertEqual(self.reposit(*self.folder_path), ['image.gif', 'subfolder'])
        self.assertEqual(self.reposit(*self.subfolder_path), ['image.gif'])
        self.assertEqual(self.subfolder['image.gif'].get_size(), self._fsize(gifImage))

    def testCutPaste(self):
        # Cut and paste a file
        cb = self.folder.manage_cutObjects(['image.gif'])
        self.subfolder.manage_pasteObjects(cb)
        self.file._finish()
        self.subfolder['image.gif']._finish()
        self.assertEqual(self.reposit(*self.folder_path), ['image.gif.undo', 'subfolder'])
        self.assertEqual(self.reposit(*self.subfolder_path), ['image.gif'])

    def testRename(self):
        # Rename a file
        self.folder.manage_renameObject('image.gif', 'image44.gif')
        self.file._finish()
        self.folder['image44.gif']._finish()
        self.assertEqual(self.reposit(*self.folder_path), ['image.gif.undo', 'image44.gif'])

    def testCOPY(self):
        # WebDAV copy a file
        req = self.app.REQUEST
        req.environ['HTTP_DEPTH'] = 'infinity'
        req.environ['HTTP_DESTINATION'] = 'http://dummy.org/%s/subfolder/image.gif' % ZopeTestCase.folder_name
        self.folder['image.gif'].COPY(req, req.RESPONSE)
        self.file._finish()
        self.subfolder['image.gif']._finish()
        self.assertEqual(self.reposit(*self.folder_path), ['image.gif', 'subfolder'])
        self.assertEqual(self.reposit(*self.subfolder_path), ['image.gif'])
        self.assertEqual(self.subfolder['image.gif'].get_size(), self._fsize(gifImage))

    def testMOVE(self):
        # WebDAV move a file
        req = self.app.REQUEST
        req.environ['HTTP_DEPTH'] = 'infinity'
        req.environ['HTTP_DESTINATION'] = 'http://dummy.org/%s/subfolder/image.gif' % ZopeTestCase.folder_name
        self.folder['image.gif'].MOVE(req, req.RESPONSE)
        self.file._finish()
        self.subfolder['image.gif']._finish()
        self.assertEqual(self.reposit(*self.folder_path), ['image.gif.undo', 'subfolder'])
        self.assertEqual(self.reposit(*self.subfolder_path), ['image.gif'])
        self.assertEqual(self.subfolder['image.gif'].get_size(), self._fsize(gifImage))


class TestExtImageCopyPasteSyncZodb(ExtFileTestCase):
    '''Tests cut/copy/paste/rename/clone with sync-zodb on'''

    def afterSetUp(self):
        ExtFile.REPOSITORY = configuration.SYNC_ZODB
        ExtFileTestCase.afterSetUp(self)
        self.folder_path = self.folder.getPhysicalPath()[1:]
        self.folder.manage_addFolder('subfolder')
        self.subfolder = self.folder['subfolder']
        self.subfolder_path = self.subfolder.getPhysicalPath()[1:]
        self.setPermissions(copymove_perms)
        self.addExtImage(id='image.gif', file=gifImage)
        # Add a preview image as well
        self.folder['image.gif'].manage_file_upload(file=jpegImage, is_preview=1,
                                                    create_prev=configuration.UPLOAD_RESIZE,
                                                    maxx=100, maxy=100, ratio=1)
        transaction.savepoint(1) # need a _p_jar

    def afterClear(self):
        ExtFileTestCase.afterClear(self)
        ExtFile.REPOSITORY = configuration.FLAT

    def testClone(self):
        # Clone an image
        self.subfolder.manage_clone(self.image, 'image.gif')
        self.image._finish()
        self.subfolder['image.gif']._finish()
        self.assertEqual(self.reposit(*self.folder_path), ['image.gif',
                                                           'image.jpg',
                                                           'subfolder'])
        self.assertEqual(self.reposit(*self.subfolder_path), ['image.gif',
                                                              'image.jpg'])

    def testCopyPaste(self):
        # Copy and paste an image
        cb = self.folder.manage_copyObjects(['image.gif'])
        self.subfolder.manage_pasteObjects(cb)
        self.image._finish()
        self.subfolder['image.gif']._finish()
        self.assertEqual(self.reposit(*self.folder_path), ['image.gif',
                                                           'image.jpg',
                                                           'subfolder'])
        self.assertEqual(self.reposit(*self.subfolder_path), ['image.gif',
                                                              'image.jpg'])
        self.assertEqual(self.subfolder['image.gif'].get_size(), self._fsize(gifImage))

    def testCutPaste(self):
        # Cut and paste a file
        cb = self.folder.manage_cutObjects(['image.gif'])
        self.subfolder.manage_pasteObjects(cb)
        self.image._finish()
        self.subfolder['image.gif']._finish()
        self.assertEqual(self.reposit(*self.folder_path), ['image.gif.undo',
                                                           'image.jpg.undo',
                                                           'subfolder'])
        self.assertEqual(self.reposit(*self.subfolder_path), ['image.gif',
                                                              'image.jpg'])

    def testRename(self):
        # Rename an image
        self.folder.manage_renameObject('image.gif', 'image44.gif')
        self.image._finish()
        self.folder['image44.gif']._finish()
        self.assertEqual(self.reposit(*self.folder_path), ['image.gif.undo',
                                                           'image.jpg.undo',
                                                           'image44.gif',
                                                           'image44.jpg'])
        self.assertEqual(self.folder['image44.gif'].filename[-1], 'image44.gif')
        self.assertEqual(self.folder['image44.gif'].prev_filename[-1], 'image44.jpg')

    def testCOPY(self):
        # WebDAV copy an image
        req = self.app.REQUEST
        req.environ['HTTP_DEPTH'] = 'infinity'
        req.environ['HTTP_DESTINATION'] = 'http://dummy.org/%s/subfolder/image.gif' % ZopeTestCase.folder_name
        self.folder['image.gif'].COPY(req, req.RESPONSE)
        self.image._finish()
        self.subfolder['image.gif']._finish()
        self.assertEqual(self.reposit(*self.folder_path), ['image.gif',
                                                           'image.jpg',
                                                           'subfolder'])
        self.assertEqual(self.reposit(*self.subfolder_path), ['image.gif',
                                                              'image.jpg'])
        self.assertEqual(self.subfolder['image.gif'].get_size(), self._fsize(gifImage))

    def testMOVE(self):
        # WebDAV move a file
        req = self.app.REQUEST
        req.environ['HTTP_DEPTH'] = 'infinity'
        req.environ['HTTP_DESTINATION'] = 'http://dummy.org/%s/subfolder/image.gif' % ZopeTestCase.folder_name
        self.folder['image.gif'].MOVE(req, req.RESPONSE)
        self.image._finish()
        self.subfolder['image.gif']._finish()
        self.assertEqual(self.reposit(*self.folder_path), ['image.gif.undo',
                                                           'image.jpg.undo',
                                                           'subfolder'])
        self.assertEqual(self.reposit(*self.subfolder_path), ['image.gif',
                                                              'image.jpg'])
        self.assertEqual(self.subfolder['image.gif'].get_size(), self._fsize(gifImage))


class TestRepository(ExtFileTestCase):
    '''Test repository directories'''

    def afterClear(self):
        ExtFileTestCase.afterClear(self)
        ExtFile.REPOSITORY = configuration.FLAT
        ExtFile.NORMALIZE_CASE = configuration.KEEP
        ExtFile.CUSTOM_METHOD = 'getExtFilePath'

    def testRepositoryFlat(self):
        ExtFile.REPOSITORY = configuration.FLAT
        self.addExtImage(id='image', file=gifImage)
        path = self.image.filename[:-1]
        self.assertEqual(path, [])

    def testRepositorySyncZodb(self):
        ExtFile.REPOSITORY = configuration.SYNC_ZODB
        self.addExtImage(id='image', file=gifImage)
        path = self.image.filename[:-1]
        self.assertEqual(path, [ZopeTestCase.folder_name])

    def testRepositorySliced(self):
        ExtFile.REPOSITORY = configuration.SLICED
        self.addExtImage(id='image', file=gifImage)
        path = self.image.filename[:-1]
        self.assertEqual(path, ['i', 'm'])

    def testRepositorySlicedReverse(self):
        ExtFile.REPOSITORY = configuration.SLICED_REVERSE
        self.addExtImage(id='image', file=gifImage)
        path = self.image.filename[:-1]
        self.assertEqual(path, ['e', 'g'])

    def testRepositorySlicedHash(self):
        ExtFile.REPOSITORY = configuration.SLICED_HASH
        self.addExtImage(id='image', file=gifImage)
        path = self.image.filename[:-1]
        self.assertEqual(path, ['F', 'E'])

    def testRepositorySlicedHashDifferentFolder(self):
        # Because the path is part of the hash, the results
        # are different from the above test.
        ExtFile.REPOSITORY = configuration.SLICED_HASH
        self.folder.manage_addFolder('subfolder')
        self.subfolder = self.folder['subfolder']
        self.addExtImage(id='image', file=gifImage, folder=self.subfolder)
        path = self.image.filename[:-1]
        self.assertEqual(path, ['L', 'd'])

    def testRepositoryCustom(self):

        def getExtFilePath(path, id):
            return ['custom', 'path']
        setattr(self.folder, 'getExtFilePath', getExtFilePath)

        ExtFile.REPOSITORY = configuration.CUSTOM
        self.addExtImage(id='image', file=gifImage)
        path = self.image.filename[:-1]
        self.assertEqual(path, ['custom', 'path'])

    def testRepositoryNormalizeCase(self):

        def getExtFilePath(path, id):
            return ['Custom', 'Path']
        setattr(self.folder, 'getExtFilePath', getExtFilePath)

        ExtFile.REPOSITORY = configuration.CUSTOM
        ExtFile.NORMALIZE_CASE = configuration.NORMALIZE
        self.addExtImage(id='image', file=gifImage)
        path = self.image.filename[:-1]
        self.assertEqual(path, ['custom', 'path'])

    def testRepositoryCustomScript(self):

        factory = self.folder.manage_addProduct['PythonScripts']
        factory.manage_addPythonScript('getExtFilePath')
        ps = self.folder.getExtFilePath
        ps.ZPythonScript_edit(params='path, id', body="return ['custom', 'path']")

        ExtFile.REPOSITORY = configuration.CUSTOM
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

        ExtFile.REPOSITORY = configuration.CUSTOM
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

        ExtFile.REPOSITORY = configuration.CUSTOM
        self.addExtImage(id='image', file=gifImage)
        path = self.image.filename[:-1]
        self.assertEqual(path, ['custom', 'path'])

    def testRepositoryCustomSubclass(self):

        class CustomImage(ExtImage.ExtImage):
            def getExtFilePath(self, path, id):
                return ['custom', 'path']

        ExtFile.REPOSITORY = configuration.CUSTOM
        self.folder._setObject('image', CustomImage('image'))
        self.folder.image.manage_file_upload(gifImage)
        path = self.folder.image.filename[:-1]
        self.assertEqual(path, ['custom', 'path'])

    def testRepositoryCustomPrivateMethod(self):

        def _getExtFilePath(path, id):
            return ['custom', 'path']
        setattr(self.folder, '_getExtFilePath', _getExtFilePath)

        ExtFile.REPOSITORY = configuration.CUSTOM
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
        self.assertEqual(self.reposit(), ['image.1.gif', 'image.gif'])

    def testUniquePreviewName(self):
        # Create a unique preview name
        self.addExtImage(id='image', file=jpegImage)
        self.image.manage_create_prev(100, 100, ratio=1)
        self.image._finish()
        self.assertEqual(self.reposit(), ['image.1.jpg', 'image.jpg'])

    def testUndoNameOnDelete(self):
        # Create a .undo file on delete
        self.addExtImage(id='image', file=gifImage)
        self.folder.manage_delObjects(['image'])
        self.assertEqual(self.reposit(), ['image.gif.undo'])

    def testUndoNameOnDeletePreview(self):
        # Create a .undo file for the preview image on delete
        self.addExtImage(id='image', file=gifImage)
        self.image.manage_create_prev(100, 100, ratio=1)
        self.image._finish()
        self.assertEqual(self.reposit(), ['image.gif', 'image.jpg'])
        self.folder.manage_delObjects(['image'])
        self.assertEqual(self.reposit(), ['image.gif.undo', 'image.jpg.undo'])

    def testUndoNameOnUpload(self):
        # Do not create a .undo file on upload
        self.addExtImage(id='image', file=gifImage)
        self.image.manage_file_upload(file=gifImage)
        self.image._finish()
        self.assertEqual(self.reposit(), ['image.gif'])

    def testUndoNameIsNotReused(self):
        # If an .undo file exists the name is not reused
        self.addExtImage(id='image', file=gifImage)
        self.folder.manage_delObjects(['image'])
        self.addExtImage(id='image', file=gifImage)
        self.image._finish()
        self.assertEqual(self.reposit(), ['image.1.gif', 'image.gif.undo'])


class TestRepositoryExtensions(ExtFileTestCase):
    '''Test repository file extensions'''

    def afterClear(self):
        ExtFileTestCase.afterClear(self)
        ExtFile.REPOSITORY_EXTENSIONS = configuration.MIMETYPE_REPLACE

    def testDefaultContentType(self):
        # Use default content type
        self.addExtImage(id='image', file=notImage)
        self.image._finish()
        self.assertEqual(self.reposit(), ['image.exe'])

    def testDefaultContentTypeKeepsExistingExtension(self):
        # Retain existing file extension if content type is octet-stream
        self.addExtImage(id='image.foo', file=notImage)
        self.image._finish()
        self.assertEqual(self.reposit(), ['image.foo'])

    def testDefaultContentTypeMimetypeAppend(self):
        # Use default content type
        ExtFile.REPOSITORY_EXTENSIONS = configuration.MIMETYPE_APPEND
        self.testDefaultContentType()

    def testDefaultContentTypeKeepsExistingExtensionMimetypeAppend(self):
        # Retain existing file extension if content type is octet-stream
        ExtFile.REPOSITORY_EXTENSIONS = configuration.MIMETYPE_APPEND
        self.testDefaultContentTypeKeepsExistingExtension()

    def testKnownContentType(self):
        # Append content-type extension
        ExtFile.REPOSITORY_EXTENSIONS = configuration.MIMETYPE_APPEND
        self.addExtImage(id='image.foo', file=gifImage)
        self.image._finish()
        self.assertEqual(self.reposit(), ['image.foo.gif'])

    def testKnownContentTypeDoesntAppendExtensionTwice(self):
        # Don't append the same extension twice
        ExtFile.REPOSITORY_EXTENSIONS = configuration.MIMETYPE_APPEND
        self.addExtImage(id='image.gif', file=gifImage)
        self.image._finish()
        self.assertEqual(self.reposit(), ['image.gif'])

    def testKeepAcceptableExtension(self):
        # Don't change acceptable extensions - NOT
        self.addExtFile(id='birthday.qt', file=notImage, content_type='video/quicktime')
        self.file._finish()
        self.assertEqual(self.reposit(), ['birthday.mov'])

    def testKeepAcceptableExtensionMimetypeAppend(self):
        # Don't change acceptable extensions - NOT
        ExtFile.REPOSITORY_EXTENSIONS = configuration.MIMETYPE_APPEND
        self.addExtFile(id='birthday.qt', file=notImage, content_type='video/quicktime')
        self.file._finish()
        self.assertEqual(self.reposit(), ['birthday.qt.mov'])

    def testKeepAcceptableExtensionJpeg(self):
        # Don't change acceptable extensions - NOT
        self.addExtFile(id='image.jpeg', file=jpegImage)
        self.file._finish()
        self.assertEqual(self.reposit(), ['image.jpg'])

    def testKeepAcceptableExtensionJpegMimetypeAppend(self):
        # Don't change acceptable extensions - NOT
        ExtFile.REPOSITORY_EXTENSIONS = configuration.MIMETYPE_APPEND
        self.addExtFile(id='image.jpeg', file=jpegImage)
        self.file._finish()
        self.assertEqual(self.reposit(), ['image.jpeg.jpg'])


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
        self.addExtFile(id='file.zip', file=notImage)
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


class TestDataAccess(ExtFileTestCase):

    def testExtFile(self):
        self.addExtFile(id='file.zip', file=notImage)
        self.failIf(self.file.is_broken())
        self.assertEqual(self.file.data,
                         open(notImage, 'rb').read())
        self.assertEqual(str(self.file),
                         open(notImage, 'rb').read())

    def testBrokenExtFile(self):
        self.addExtFile(id='file.zip', file='')
        self.failUnless(self.file.is_broken())
        self.assertEqual(self.file.data, '')
        self.assertEqual(str(self.file), '')

    def testExtImage(self):
        self.addExtImage(id='image.gif', file=gifImage)
        self.failIf(self.image.is_broken())
        self.assertEqual(self.image.data,
                         open(gifImage, 'rb').read())

    def testBrokenExtImage(self):
        self.addExtImage(id='image.gif', file='')
        self.failUnless(self.image.is_broken())
        self.assertEqual(self.image.data, '')


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
    suite.addTest(makeSuite(TestExtFileCopyPasteSyncZodb))
    suite.addTest(makeSuite(TestExtImageCopyPasteSyncZodb))
    suite.addTest(makeSuite(TestRepository))
    suite.addTest(makeSuite(TestRepositoryFiles))
    suite.addTest(makeSuite(TestRepositoryExtensions))
    suite.addTest(makeSuite(TestDownloadPermission))
    suite.addTest(makeSuite(TestGetOwner))
    suite.addTest(makeSuite(TestFTPget))
    suite.addTest(makeSuite(TestPublish))
    suite.addTest(makeSuite(TestDataAccess))
    return suite

