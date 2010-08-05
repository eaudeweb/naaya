#
# Tests transactional behavior of ExtFiles
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

ZopeTestCase.installProduct('ExtFile')
ZopeTestCase.utils.startZServer()

from Products.ExtFile.tests.ExtFileTestCase import ExtFileTestCase
from Products.ExtFile.tests.ExtFileTestCase import gifImage, jpegImage, notImage
from Products.ExtFile.tests.ExtFileTestCase import copymove_perms
from Products.ExtFile.ExtImage import NO_PREVIEW, GENERATE, UPLOAD_NORESIZE, UPLOAD_RESIZE
from Products.ExtFile import transaction, TM
from Acquisition import aq_base


class TestTransactions(ExtFileTestCase):
    '''Test ExtFile/ExtImage transaction awareness.'''

    def beforeClose(self):
        transaction.commit()  # Commit the cleaned-up fixture

    def testAddFileCommit(self):
        self.addExtFile(id='file', file=gifImage)
        transaction.commit()
        self.failUnless(self._exists('file.exe'))

    def testAddFileAbort(self):
        # Aborting the transaction leaves the repository empty
        self.addExtFile(id='file', file=gifImage)
        transaction.savepoint(1)   # Wuhuu, force object rollback
        transaction.abort()
        self.failIf(hasattr(aq_base(self.folder), 'file'))
        self.failIf(self._exists('file.exe'))
        self.failIf(self._exists('file.exe.tmp'))

    def testAddImageCommit(self):
        self.addExtImage(id='image', file=gifImage)
        transaction.commit()
        self.failUnless(self._exists('image.gif'))

    def testAddImageAbort(self):
        # Aborting the transaction leaves the repository empty
        self.addExtImage(id='image', file=gifImage)
        transaction.savepoint(1)   # Wuhuu, force object rollback
        transaction.abort()
        self.failIf(hasattr(aq_base(self.folder), 'image'))
        self.failIf(self._exists('image.gif'))
        self.failIf(self._exists('image.gif.tmp'))

    def testAddImageAbortWithPreview(self):
        # Aborting the transaction leaves the repository empty
        self.addExtImage(id='image', file=gifImage)
        self.image.manage_create_prev(maxx=10, maxy=10)
        transaction.savepoint(1)   # Wuhuu, force object rollback
        transaction.abort()
        self.failIf(hasattr(aq_base(self.folder), 'image'))
        self.failIf(self._exists('image.gif'))
        self.failIf(self._exists('image.gif.tmp'))
        self.failIf(self._exists('image.jpg'))
        self.failIf(self._exists('image.jpg.tmp'))

    def testAddMoreThanOneFileInSeparateTransactions(self):
        # First file
        self.addExtFile(id='fred', file=notImage)
        transaction.commit()
        self.failUnless(self._exists('fred.exe'))
        self.failIf(self._exists('fred.exe.tmp'))
        # Second file
        self.addExtFile(id='barney', file=notImage)
        transaction.commit()
        self.failUnless(self._exists('barney.exe'))
        self.failIf(self._exists('barney.exe.tmp'))
        # Third file
        self.addExtFile(id='betty', file=notImage)
        transaction.commit()
        self.failUnless(self._exists('betty.exe'))
        self.failIf(self._exists('betty.exe.tmp'))

    def testUploadFileIntoExistingInSeparateTransactions(self):
        # Create a file 'fred'
        self.addExtFile(id='fred', file=notImage)
        self.failUnless(TM.contains(self.file))
        self.failUnless(self._exists('fred.exe.tmp'))
        transaction.commit()
        self.failIf(TM.contains(self.file))
        self.failUnless(self._exists('fred.exe'))
        self.failIf(self._exists('fred.exe.tmp'))
        # Upload new file into 'fred'
        self.file.manage_file_upload(file=gifImage)
        self.failUnless(TM.contains(self.file))
        self.failUnless(self._exists('fred.exe'))
        self.failUnless(self._exists('fred.exe.tmp'))
        transaction.commit()
        self.failIf(TM.contains(self.file))
        self.failUnless(self._exists('fred.exe'))
        self.failIf(self._exists('fred.exe.tmp'))


class TestTransactionManager(ExtFileTestCase):

    def afterSetUp(self):
        ExtFileTestCase.afterSetUp(self)
        self.addExtFile(id='file', file=notImage)
        self.file._register()

    def beforeClose(self):
        transaction.commit()  # Commit the cleaned-up fixture

    def testBegin(self):
        self.assertEqual(self.file._v_begin_called, 1)

    def testFinish(self):
        transaction.commit()
        self.assertEqual(self.file._v_finish_called, 1)

    def testAbort(self):
        transaction.abort()
        self.assertEqual(self.file._v_abort_called, 1)


class TestExtFileTransactions(ExtFileTestCase):

    def afterSetUp(self):
        ExtFileTestCase.afterSetUp(self)
        self.setPermissions(copymove_perms)
        self.folder.manage_addFolder('subfolder')
        self.subfolder = self.folder.subfolder

    def beforeClose(self):
        transaction.commit()  # Commit the cleaned-up fixture

    def testManageFileUploadCreatesTempFile(self):
        self.addExtFile(id='file', file='')
        self.file.manage_file_upload(file=notImage)
        self.failUnless(self._exists('file.exe.tmp'), 'Missing .tmp file')
        self.failIf(self._exists('file.exe'), 'No .tmp file used')

    def testManageHTTPUploadCreatesTempFile(self):
        self.addExtFile(id='file', file='')
        self.file.manage_http_upload(url=self.app.NotImage.absolute_url())
        self.failUnless(self._exists('file.exe.tmp'), 'Missing .tmp file')
        self.failIf(self._exists('file.exe'), 'No .tmp file used')

    def testPUTCreatesTempFile(self):
        self.addExtFile(id='file', file='')
        request = self.app.REQUEST
        request['BODYFILE'] = open(notImage, 'rb')
        self.file.PUT(request, request.RESPONSE)
        self.failUnless(self._exists('file.exe.tmp'), 'Missing .tmp file')
        self.failIf(self._exists('file.exe'), 'No .tmp file used')

    def testFinishCommitsTempFile(self):
        self.addExtFile(id='file', file=notImage)
        self.failUnless(self._exists('file.exe.tmp'))
        self.file._finish()
        self.failUnless(self._exists('file.exe'))
        self.failIf(self._exists('file.exe.tmp'))

    def testAbortNukesTempFile(self):
        self.addExtFile(id='file', file=notImage)
        self.failUnless(self._exists('file.exe.tmp'))
        self.file._abort()
        self.failIf(self._exists('file.exe.tmp'))
        self.failIf(self._exists('file.exe'))

    def testUndoCreatesTempFile(self):
        self.addExtFile(id='file', file=notImage)
        self.file._finish()
        os.rename(self._fsname('file.exe'), self._fsname('file.exe.undo'))
        self.file._undo()
        self.failIf(self._exists('file.exe.undo'))
        self.failUnless(self._exists('file.exe.tmp'))

    def testIsBrokenUsesTempFile(self):
        self.addExtFile(id='file', file=notImage)
        self.failUnless(self._exists('file.exe.tmp'))
        self.failIf(self._exists('file.exe'))
        self.failIf(self.file.is_broken())

    def testIsBrokenUsesMainFileIfTempFileNotPresent(self):
        self.addExtFile(id='file', file=notImage)
        self.file._finish()
        self.failUnless(self._exists('file.exe'))
        self.failIf(self._exists('file.exe.tmp'))
        self.failIf(self.file.is_broken())

    def testIsBrokenTriesToUndoIfMainFileNotPresent(self):
        self.addExtFile(id='file', file=notImage)
        os.rename(self._fsname('file.exe.tmp'), self._fsname('file.exe.undo'))
        self.failUnless(self._exists('file.exe.undo'))
        self.failIf(self._exists('file.exe'))
        self.failIf(self.file.is_broken())
        self.failUnless(self._exists('file.exe.tmp'))
        self.failIf(self._exists('file.exe.undo'))

    def testIsBrokenReturnsTrueIfBroken(self):
        self.addExtFile(id='file', file=notImage)
        os.remove(self._fsname('file.exe.tmp'))
        self.failUnless(self.file.is_broken())

    def testGetSizeUsesTempFile(self):
        self.addExtFile(id='file', file=notImage)
        self.failUnless(self._exists('file.exe.tmp'))
        self.failIf(self._exists('file.exe'))
        self.failIfEqual(self.file.get_size(), 0)

    def testGetSizeUsesMainFileIfTempFileNotPresent(self):
        self.addExtFile(id='file', file=notImage)
        self.file._finish()
        self.failUnless(self._exists('file.exe'))
        self.failIf(self._exists('file.exe.tmp'))
        self.failIfEqual(self.file.get_size(), 0)

    def testGetSizeTriesToUndoIfMainFileNotPresent(self):
        self.addExtFile(id='file', file=notImage)
        self.file._finish()
        os.rename(self._fsname('file.exe'), self._fsname('file.exe.undo'))
        self.failUnless(self._exists('file.exe.undo'))
        self.failIf(self._exists('file.exe'))
        self.failIfEqual(self.file.get_size(), 0)
        self.failUnless(self._exists('file.exe.tmp'))
        self.failIf(self._exists('file.exe.undo'))

    def testGetSizeReturnsZeroIfBroken(self):
        self.addExtFile(id='file', file=notImage)
        os.remove(self._fsname('file.exe.tmp'))
        self.assertEqual(self.file.get_size(), 0)

    def testManageFileUploadRegistersWithTM(self):
        self.addExtFile(id='file', file='')
        self.assertEqual(getattr(self.file, '_v_begin_called', 0), 0)
        self.file.manage_file_upload(file=notImage)
        self.assertEqual(getattr(self.file, '_v_begin_called', 0), 1)

    def testManageHTTPUploadRegistersWithTM(self):
        self.addExtFile(id='file', file='')
        self.assertEqual(getattr(self.file, '_v_begin_called', 0), 0)
        self.file.manage_http_upload(url=self.app.NotImage.absolute_url())
        self.assertEqual(getattr(self.file, '_v_begin_called', 0), 1)

    def testPUTRegistersWithTM(self):
        self.addExtFile(id='file', file='')
        request = self.app.REQUEST
        request['BODYFILE'] = open(notImage, 'rb')
        self.assertEqual(getattr(self.file, '_v_begin_called', 0), 0)
        self.file.PUT(request, request.RESPONSE)
        self.assertEqual(getattr(self.file, '_v_begin_called', 0), 1)

    def testUndoRegistersWithTM(self):
        self.addExtFile(id='file', file=notImage)
        os.rename(self._fsname('file.exe.tmp'), self._fsname('file.exe.undo'))
        self.file._v_begin_called = 0   # Clear
        TM.remove(self.file)            # Clear
        self.assertEqual(getattr(self.file, '_v_begin_called', 0), 0)
        self.file._undo()
        self.assertEqual(getattr(self.file, '_v_begin_called', 0), 1)
        self.failUnless(self._exists('file.exe.tmp'))

    def testGetNewUfnSkipsTempFile(self):
        self.addExtFile(id='file', file=notImage)
        self.failUnless(self._exists('file.exe.tmp'))
        fn = self.file._get_new_ufn(self.file.filename)
        self.assertEqual(fn, ['file.1.exe'])

    def testGetFileToServeDoesNotUseTempFile(self):
        self.addExtFile(id='file', file=notImage)
        self.failUnless(self._exists('file.exe.tmp'))
        fn = self.file._get_file_to_serve()[0]
        self.assertEqual(fn, ['file.exe'])

    def testManageBeforeDeleteUsesTempFile(self):
        self.addExtFile(id='file', file=notImage)
        self.failUnless(self._exists('file.exe.tmp'))
        self.folder._delObject('file')
        self.failUnless(self._exists('file.exe.undo'))
        self.failIf(self._exists('file.exe'))

    def testManageBeforeDeleteNukesMainFileIfTempFilePresent(self):
        self.addExtFile(id='file', file=notImage)
        self.file._finish()
        self.file.manage_file_upload(file=notImage)
        self.failUnless(self._exists('file.exe'))
        self.failUnless(self._exists('file.exe.tmp'))
        self.folder._delObject('file')
        self.failUnless(self._exists('file.exe.undo'))
        self.failIf(self._exists('file.exe'))

    def testManageBeforeDeleteUsesMainFileIfTempFileNotPresent(self):
        self.addExtFile(id='file', file=notImage)
        self.file._finish()
        self.failUnless(self._exists('file.exe'))
        self.failIf(self._exists('file.exe.tmp'))
        self.folder._delObject('file')
        self.failUnless(self._exists('file.exe.undo'))
        self.failIf(self._exists('file.exe'))

    def testManageAfterCloneCreatesTempFile(self):
        self.addExtFile(id='file', file=notImage)
        self.file._finish()
        transaction.savepoint(1) # Need a _p_oid
        cb = self.folder.manage_copyObjects(['file'])
        self.subfolder.manage_pasteObjects(cb)
        self.failUnless(self._exists('file.exe'))       # original
        self.failUnless(self._exists('file.1.exe.tmp'))  # copy
        self.assertEqual(self.subfolder.file.filename, ['file.1.exe'])

    def testManageAfterCloneUsesTempFileAsSource(self):
        self.addExtFile(id='file', file=notImage)
        transaction.savepoint(1) # Need a _p_oid
        self.subfolder.manage_clone(self.file, 'file')
        self.failUnless(self._exists('file.exe.tmp'))   # original
        self.failUnless(self._exists('file.1.exe.tmp'))  # copy

    def testManageAfterCloneUsesMainFileIfTempFileNotPresent(self):
        self.addExtFile(id='file', file=notImage)
        self.file._finish()
        transaction.savepoint(1) # Need a _p_oid
        self.subfolder.manage_clone(self.file, 'file')
        self.failUnless(self._exists('file.exe'))       # original
        self.failUnless(self._exists('file.1.exe.tmp'))  # copy

    def testManageAfterCloneTriesToUndoIfTempFileNotPresent(self):
        self.addExtFile(id='file', file=notImage)
        self.file._finish()
        os.rename(self._fsname('file.exe'), self._fsname('file.exe.undo'))
        transaction.savepoint(1) # Need a _p_oid
        self.subfolder.manage_clone(self.file, 'file')
        self.failUnless(self._exists('file.exe.tmp'))   # restored original
        self.failUnless(self._exists('file.1.exe.tmp'))  # copy

    def testManageAfterCloneRegistersWithTM(self):
        self.addExtFile(id='file', file=notImage)
        self.file._finish()
        self.file._v_begin_called = 0   # Clear
        TM.remove(self.file)            # Clear
        transaction.savepoint(1) # Need a _p_oid
        self.assertEqual(getattr(self.subfolder.file, '_v_begin_called', 0), 0)
        self.subfolder.manage_clone(self.file, 'file')
        self.assertEqual(getattr(self.subfolder.file, '_v_begin_called', 0), 1)


class TestExtImageTransactions(ExtFileTestCase):

    def afterSetUp(self):
        ExtFileTestCase.afterSetUp(self)
        self.setPermissions(copymove_perms)
        self.folder.manage_addFolder('subfolder')
        self.subfolder = self.folder.subfolder

    def beforeClose(self):
        transaction.commit()  # Commit the cleaned-up fixture

    def testManageFileUploadCreatesTempImage(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=gifImage)
        self.failUnless(self._exists('image.gif.tmp'), 'Missing .tmp file')
        self.failIf(self._exists('image.gif'), 'No .tmp file used')

    def testManageFileUploadCreatesTempPreview(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        self.failUnless(self._exists('image.jpg.tmp'), 'Missing .tmp file')
        self.failIf(self._exists('image.jpg'), 'No .tmp file used')

    def testManageFileUploadCreatesTempPreviewIfResize(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=jpegImage, is_preview=1, create_prev=UPLOAD_RESIZE, maxx=10, maxy=10)
        self.failUnless(self._exists('image.jpg.tmp'), 'Missing .tmp file')
        self.failIf(self._exists('image.jpg'), 'No .tmp file used')

    def testManageFileUploadCreatesTempPreviewIfGenerate(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=jpegImage, create_prev=GENERATE, maxx=10, maxy=10)
        self.failUnless(self._exists('image.jpg.tmp'), 'Missing .tmp file') # main image
        self.failIf(self._exists('image.jpg'), 'No .tmp file used')
        self.failUnless(self._exists('image.1.jpg.tmp'), 'Missing .tmp file') # preview
        self.failIf(self._exists('image.1.jpg'), 'No .tmp file used')

    def testManageHTTPUploadCreatesTempImage(self):
        self.addExtImage(id='image', file='')
        self.image.manage_http_upload(url=self.app.GifImage.absolute_url())
        self.failUnless(self._exists('image.gif.tmp'), 'Missing .tmp file')
        self.failIf(self._exists('image.gif'), 'No .tmp file used')

    def testManageHTTPUploadCreatesTempPreview(self):
        self.addExtImage(id='image', file='')
        self.image.manage_http_upload(url=self.app.GifImage.absolute_url(), is_preview=1)
        self.failUnless(self._exists('image.gif.tmp'), 'Missing .tmp file')
        self.failIf(self._exists('image.gif'), 'No .tmp file used')

    #def testManageHTTPUploadCreatesTempPreviewIfAutogen(self):
    #    self.addExtImage(id='image', file='')
    #    self.image.manage_file_upload(file=jpegImage, is_preview=1)
    #    preview_size = self.image.get_prev_size()
    #    self.image.manage_http_upload(url=self.app.GifImage.absolute_url())
    #    self.failUnless(self._exists('image.gif.tmp'), 'Missing .tmp file') # main image
    #    self.failIf(self._exists('image.gif'), 'No .tmp file used')
    #    self.failUnless(self._exists('image.jpg.tmp'), 'Missing .tmp file') # preview
    #    self.failIf(self._exists('image.jpg'), 'No .tmp file used')
    #    # The preview file should no longer be the same
    #    self.failIfEqual(preview_size, self.image.get_prev_size())

    def testPUTCreatesTempImage(self):
        self.addExtImage(id='image', file='')
        request = self.app.REQUEST
        request['BODYFILE'] = open(jpegImage, 'rb')
        self.image.PUT(request, request.RESPONSE)
        self.failUnless(self._exists('image.jpg.tmp'), 'Missing .tmp file')
        self.failIf(self._exists('image.jpg'), 'No .tmp file used')

    def testPUTCreatesTempPreviewIfAutogen(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        preview_size = self.image.get_prev_size()
        request = self.app.REQUEST
        request['BODYFILE'] = open(gifImage, 'rb')
        self.image.PUT(request, request.RESPONSE)
        self.failUnless(self._exists('image.gif.tmp'), 'Missing .tmp file') # main image
        self.failIf(self._exists('image.gif'), 'No .tmp file used')
        self.failUnless(self._exists('image.jpg.tmp'), 'Missing .tmp file') # preview
        self.failIf(self._exists('image.jpg'), 'No .tmp file used')
        # The preview file should no longer be the same
        self.failIfEqual(preview_size, self.image.get_prev_size())

    def testFinishCommitsTempImage(self):
        self.addExtImage(id='image', file=jpegImage)
        self.failUnless(self._exists('image.jpg.tmp'))
        self.image._finish()
        self.failUnless(self._exists('image.jpg'))
        self.failIf(self._exists('image.jpg.tmp'))

    def testFinishCommitsTempPreview(self):
        self.addExtImage(id='image', file=jpegImage)
        self.image.manage_create_prev(maxx=10, maxy=10)
        self.failUnless(self._exists('image.jpg.tmp'))
        self.failUnless(self._exists('image.1.jpg.tmp'))
        self.image._finish()
        self.failUnless(self._exists('image.jpg'))
        self.failIf(self._exists('image.jpg.tmp'))
        self.failUnless(self._exists('image.1.jpg'))
        self.failIf(self._exists('image.1.jpg.tmp'))

    def testAbortNukesTempImage(self):
        self.addExtImage(id='image', file=jpegImage)
        self.failUnless(self._exists('image.jpg.tmp'))
        self.image._abort()
        self.failIf(self._exists('image.jpg'))
        self.failIf(self._exists('image.jpg.tmp'))

    def testAbortNukesTempPreview(self):
        self.addExtImage(id='image', file=jpegImage)
        self.image.manage_create_prev(maxx=10, maxy=10)
        self.failUnless(self._exists('image.jpg.tmp'))
        self.failUnless(self._exists('image.1.jpg.tmp'))
        self.image._abort()
        self.failIf(self._exists('image.jpg'))
        self.failIf(self._exists('image.jpg.tmp'))
        self.failIf(self._exists('image.1.jpg'))
        self.failIf(self._exists('image.1.jpg.tmp'))

    def testUndoCreatesTempImage(self):
        self.addExtImage(id='image', file=jpegImage)
        self.image._finish()
        os.rename(self._fsname('image.jpg'), self._fsname('image.jpg.undo'))
        self.image._undo()
        self.failIf(self._exists('image.jpg.undo'))
        self.failUnless(self._exists('image.jpg.tmp'))

    def testUndoCreatesTempPreview(self):
        self.addExtImage(id='image', file=jpegImage)
        self.image.manage_create_prev(maxx=10, maxy=10)
        self.image._finish()
        os.rename(self._fsname('image.jpg'), self._fsname('image.jpg.undo'))
        os.rename(self._fsname('image.1.jpg'), self._fsname('image.1.jpg.undo'))
        self.image._undo()
        self.failIf(self._exists('image.jpg.undo'))
        self.failUnless(self._exists('image.jpg.tmp'))
        self.failIf(self._exists('image.1.jpg.undo'))
        self.failUnless(self._exists('image.1.jpg.tmp'))

    def testIsBrokenReturnsTrueIfPreviewBroken(self):
        self.addExtImage(id='image', file=jpegImage)
        self.image.manage_create_prev(maxx=10, maxy=10)
        os.remove(self._fsname('image.1.jpg.tmp'))
        self.failUnless(self.image.is_broken())

    def testManageFileUploadRegistersPreviewWithTM(self):
        self.addExtImage(id='image', file='')
        self.assertEqual(getattr(self.image, '_v_begin_called', 0), 0)
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        self.assertEqual(getattr(self.image, '_v_begin_called', 0), 1)

    def testManageFileUploadRegistersPreviewWithTMIfResize(self):
        self.addExtImage(id='image', file='')
        self.assertEqual(getattr(self.image, '_v_begin_called', 0), 0)
        self.image.manage_file_upload(file=jpegImage, is_preview=1, create_prev=UPLOAD_RESIZE, maxx=10, maxy=10)
        self.assertEqual(getattr(self.image, '_v_begin_called', 0), 1)

    # XXX: Not testable atm
    def DISABLED_testManageFileUploadRegistersPreviewWithTMIfGenerate(self):
        self.addExtImage(id='image', file='')
        self.assertEqual(getattr(self.image, '_v_begin_called', 0), 0)
        self.image.manage_file_upload(file=jpegImage, create_prev=GENERATE, maxx=10, maxy=10)
        self.assertEqual(getattr(self.image, '_v_begin_called', 0), 1)

    def testManageHTTPUploadRegistersPreviewWithTM(self):
        self.addExtImage(id='image', file='')
        self.assertEqual(getattr(self.image, '_v_begin_called', 0), 0)
        self.image.manage_http_upload(url=self.app.GifImage.absolute_url(), is_preview=1)
        self.assertEqual(getattr(self.image, '_v_begin_called', 0), 1)

    # XXX: Not testable atm
    def DISABLED_testManageHTTPUploadRegistersPreviewWithTMIfAutogen(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        self.image._v_begin_called = 0  # Clear
        TM.remove(self.image)           # Clear
        self.assertEqual(getattr(self.image, '_v_begin_called', 0), 0)
        self.image.manage_http_upload(url=self.app.GifImage.absolute_url())
        self.assertEqual(getattr(self.image, '_v_begin_called', 0), 1)

    # XXX: Not testable atm
    def DISABLED_testPUTRegistersPreviewWithTMIfAutogen(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        self.image._v_begin_called = 0  # Clear
        TM.remove(self.image)           # Clear
        request = self.app.REQUEST
        request['BODYFILE'] = open(jpegImage, 'rb')
        self.assertEqual(getattr(self.image, '_v_begin_called', 0), 0)
        self.image.PUT(request, request.RESPONSE)
        self.assertEqual(getattr(self.image, '_v_begin_called', 0), 1)

    def testUndoRegistersPreviewWithTM(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        os.rename(self._fsname('image.jpg.tmp'), self._fsname('image.jpg.undo'))
        self.image._v_begin_called = 0  # Clear
        TM.remove(self.image)           # Clear
        self.assertEqual(getattr(self.image, '_v_begin_called', 0), 0)
        self.image._undo()
        self.assertEqual(getattr(self.image, '_v_begin_called', 0), 1)
        self.failUnless(self._exists('image.jpg.tmp'))

    def testManageBeforeDeleteUsesTempPreview(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        self.failUnless(self._exists('image.jpg.tmp'))
        self.folder._delObject('image')
        self.failUnless(self._exists('image.jpg.undo'))
        self.failIf(self._exists('image.jpg.tmp'))
        self.failIf(self._exists('image.jpg'))

    def testManageBeforeDeleteNukesPreviewIfTempPreviewPresent(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        self.image._finish()
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        self.failUnless(self._exists('image.jpg'))
        self.failUnless(self._exists('image.jpg.tmp'))
        self.folder._delObject('image')
        self.failUnless(self._exists('image.jpg.undo'))
        self.failIf(self._exists('image.jpg.tmp'))
        self.failIf(self._exists('image.jpg'))

    def testManageBeforeDeleteUsesPreviewIfTempPreviewNotPresent(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        self.image._finish()
        self.failUnless(self._exists('image.jpg'))
        self.failIf(self._exists('image.jpg.tmp'))
        self.folder._delObject('image')
        self.failUnless(self._exists('image.jpg.undo'))
        self.failIf(self._exists('image.jpg.tmp'))
        self.failIf(self._exists('image.jpg'))

    def testManageAfterCloneCreatesTempPreview(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        self.image._finish()
        transaction.savepoint(1) # Need a _p_oid
        cb = self.folder.manage_copyObjects(['image'])
        self.subfolder.manage_pasteObjects(cb)
        self.failUnless(self._exists('image.jpg'))      # original
        self.failUnless(self._exists('image.1.jpg.tmp')) # copy
        self.assertEqual(self.subfolder.image.prev_filename, ['image.1.jpg'])

    def testManageAfterCloneUsesTempPreviewAsSource(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        transaction.savepoint(1) # Need a _p_oid
        self.subfolder.manage_clone(self.image, 'image')
        self.failUnless(self._exists('image.jpg.tmp'))  # original
        self.failUnless(self._exists('image.1.jpg.tmp')) # copy

    def testManageAfterCloneUsesPreviewIfTempPreviewNotPresent(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        self.image._finish()
        transaction.savepoint(1) # Need a _p_oid
        self.subfolder.manage_clone(self.image, 'image')
        self.failUnless(self._exists('image.jpg'))      # original
        self.failUnless(self._exists('image.1.jpg.tmp')) # copy

    def testManageAfterCloneTriesToUndoIfTempPreviewNotPresent(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        self.image._finish()
        os.rename(self._fsname('image.jpg'), self._fsname('image.jpg.undo'))
        transaction.savepoint(1) # Need a _p_oid
        self.subfolder.manage_clone(self.image, 'image')
        self.failUnless(self._exists('image.jpg.tmp'))  # restored original
        self.failUnless(self._exists('image.1.jpg.tmp')) # copy

    def testManageAfterCloneUsesTempPreviewIfOneFile(self):
        # XXX: Fishy. It seems this tests an impossible state
        self.addExtImage(id='image', file=jpegImage)
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        # Simulate main and preview being one file
        self.image.prev_filename = ['image.2.jpg']
        transaction.savepoint(1) # Need a _p_oid
        self.subfolder.manage_clone(self.image, 'image')
        self.failUnless(self._exists('image.jpg.tmp'))  # original
        self.failUnless(self._exists('image.1.jpg.tmp')) # original preview
        self.failUnless(self._exists('image.2.jpg.tmp')) # copy
        self.assertEqual(self.subfolder.image.prev_filename, ['image.2.jpg'])
        self.assertEqual(self.subfolder.image.filename, ['image.2.jpg'])

    # XXX: Not testable atm
    def DISABLED_testManageAfterCloneRegistersWithTM(self):
        pass

    def testManageCreatePrevCreatesTempFile(self):
        self.addExtImage(id='image', file=jpegImage)
        self.image.manage_create_prev(maxx=10, maxy=10)
        self.failUnless(self._exists('image.jpg.tmp'))
        self.failUnless(self._exists('image.1.jpg.tmp')) # preview
        self.assertEqual(self.image.prev_filename, ['image.1.jpg'])

    def testCreatePrevRegistersWithTM(self):
        self.addExtImage(id='image', file=jpegImage)
        self.assertEqual(getattr(self.image, '_v_begin_called', 0), 1)
        self.image._v_begin_called = 0  # Clear
        TM.remove(self.image)           # Clear
        self.assertEqual(getattr(self.image, '_v_begin_called', 0), 0)
        self.image.manage_create_prev(maxx=10, maxy=10)
        self.assertEqual(getattr(self.image, '_v_begin_called', 0), 1)

    def testManageDelPrevUsesTempFile(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        self.failUnless(self._exists('image.jpg.tmp'))
        self.image.manage_del_prev()
        self.failUnless(self._exists('image.jpg.undo'))
        self.failIf(self._exists('image.jpg.tmp'))
        self.failIf(self._exists('image.jpg'))

    def testManageDelPrevNukesPreviewIfTempPreviewPresent(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        self.image._finish()
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        self.failUnless(self._exists('image.jpg'))
        self.failUnless(self._exists('image.jpg.tmp'))
        self.image.manage_del_prev()
        self.failUnless(self._exists('image.jpg.undo'))
        self.failIf(self._exists('image.jpg.tmp'))
        self.failIf(self._exists('image.jpg'))

    def testManageDelPrevUsesPreviewIfTempPreviewNotPresent(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        self.image._finish()
        self.failUnless(self._exists('image.jpg'))
        self.failIf(self._exists('image.jpg.tmp'))
        self.image.manage_del_prev()
        self.failUnless(self._exists('image.jpg.undo'))
        self.failIf(self._exists('image.jpg.tmp'))
        self.failIf(self._exists('image.jpg'))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTransactions))
    suite.addTest(makeSuite(TestTransactionManager))
    suite.addTest(makeSuite(TestExtFileTransactions))
    suite.addTest(makeSuite(TestExtImageTransactions))
    return suite

if __name__ == '__main__':
    framework()

