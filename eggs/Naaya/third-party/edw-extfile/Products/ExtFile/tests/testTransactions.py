#
# Tests transactional behavior of ExtFiles
#

from Testing import ZopeTestCase

ZopeTestCase.installProduct('ExtFile')
ZopeTestCase.utils.startZServer()

from Products.ExtFile.testing import ExtFileTestCase
from Products.ExtFile.testing import gifImage, jpegImage, notImage
from Products.ExtFile.testing import copymove_perms
from Products.ExtFile.configuration import NO_PREVIEW, GENERATE
from Products.ExtFile.configuration import UPLOAD_NORESIZE, UPLOAD_RESIZE
from Products.ExtFile import TM
from Products.ExtFile import ExtFile
from Products.ExtFile import configuration
from Acquisition import aq_base

import os
import transaction


class TestTransactions(ExtFileTestCase):
    '''Test ExtFile/ExtImage transaction awareness.'''

    def beforeClose(self):
        transaction.commit()  # Commit the cleaned-up fixture

    def testAddFileCommit(self):
        self.addExtFile(id='file', file=gifImage)
        transaction.commit()
        self.assertEqual(self.reposit(), ['file.exe'])

    def testAddFileAbort(self):
        # Aborting the transaction leaves the repository empty
        self.addExtFile(id='file', file=gifImage)
        transaction.savepoint(1)   # Wuhuu, force object rollback
        transaction.abort()
        self.failIf(hasattr(aq_base(self.folder), 'file'))
        self.assertEqual(self.reposit(), [])

    def testAddImageCommit(self):
        self.addExtImage(id='image', file=gifImage)
        transaction.commit()
        self.assertEqual(self.reposit(), ['image.gif'])

    def testAddImageAbort(self):
        # Aborting the transaction leaves the repository empty
        self.addExtImage(id='image', file=gifImage)
        transaction.savepoint(1)   # Wuhuu, force object rollback
        transaction.abort()
        self.failIf(hasattr(aq_base(self.folder), 'image'))
        self.assertEqual(self.reposit(), [])

    def testAddImageAbortWithPreview(self):
        # Aborting the transaction leaves the repository empty
        self.addExtImage(id='image', file=gifImage)
        self.image.manage_create_prev(maxx=10, maxy=10)
        transaction.savepoint(1)   # Wuhuu, force object rollback
        transaction.abort()
        self.failIf(hasattr(aq_base(self.folder), 'image'))
        self.assertEqual(self.reposit(), [])

    def testAddMoreThanOneFileInSeparateTransactions(self):
        # First file
        self.addExtFile(id='fred', file=notImage)
        transaction.commit()
        self.assertEqual(self.reposit(), ['fred.exe'])

        # Second file
        self.addExtFile(id='barney', file=notImage)
        transaction.commit()
        self.assertEqual(self.reposit(), ['barney.exe',
                                          'fred.exe'])
        # Third file
        self.addExtFile(id='betty', file=notImage)
        transaction.commit()
        self.assertEqual(self.reposit(), ['barney.exe',
                                          'betty.exe',
                                          'fred.exe'])

    def testUploadFileIntoExistingInSeparateTransactions(self):
        # Create a file 'fred'
        self.addExtFile(id='fred', file=notImage)
        self.failUnless(TM.contains(self.file))
        self.assertEqual(self.reposit(), ['fred.exe.tmp'])
        transaction.commit()
        self.failIf(TM.contains(self.file))
        self.assertEqual(self.reposit(), ['fred.exe'])
        # Upload new file into 'fred'
        self.file.manage_file_upload(file=gifImage)
        self.failUnless(TM.contains(self.file))
        self.assertEqual(self.reposit(), ['fred.exe', 'fred.exe.tmp'])
        transaction.commit()
        self.failIf(TM.contains(self.file))
        self.assertEqual(self.reposit(), ['fred.exe'])


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
        self.folder.manage_addFolder('subfolder')
        self.subfolder = self.folder.subfolder
        self.setPermissions(copymove_perms)

    def beforeClose(self):
        transaction.commit()  # Commit the cleaned-up fixture

    def testManageFileUploadCreatesTempFile(self):
        self.addExtFile(id='file', file='')
        self.file.manage_file_upload(file=notImage)
        self.assertEqual(self.reposit(), ['file.exe.tmp'])

    def testManageHTTPUploadCreatesTempFile(self):
        self.addExtFile(id='file', file='')
        self.file.manage_http_upload(url=self.app.NotImage.absolute_url())
        self.assertEqual(self.reposit(), ['file.exe.tmp'])

    def testPUTCreatesTempFile(self):
        self.addExtFile(id='file', file='')
        request = self.app.REQUEST
        request['BODYFILE'] = open(notImage, 'rb')
        self.file.PUT(request, request.RESPONSE)
        self.assertEqual(self.reposit(), ['file.exe.tmp'])

    def testFinishCommitsTempFile(self):
        self.addExtFile(id='file', file=notImage)
        self.assertEqual(self.reposit(), ['file.exe.tmp'])
        self.file._finish()
        self.assertEqual(self.reposit(), ['file.exe'])

    def testAbortNukesTempFile(self):
        self.addExtFile(id='file', file=notImage)
        self.assertEqual(self.reposit(), ['file.exe.tmp'])
        self.file._abort()
        self.assertEqual(self.reposit(), [])

    def testUndoCreatesTempFile(self):
        self.addExtFile(id='file', file=notImage)
        self.file._finish()
        os.rename(self._fsname('file.exe'), self._fsname('file.exe.undo'))
        self.file._undo(self.file.filename)
        self.assertEqual(self.reposit(), ['file.exe.tmp'])

    def testIsBrokenUsesTempFile(self):
        self.addExtFile(id='file', file=notImage)
        self.assertEqual(self.reposit(), ['file.exe.tmp'])
        self.failIf(self.file.is_broken())

    def testIsBrokenUsesMainFileIfTempFileNotPresent(self):
        self.addExtFile(id='file', file=notImage)
        self.file._finish()
        self.assertEqual(self.reposit(), ['file.exe'])
        self.failIf(self.file.is_broken())

    def testIsBrokenTriesToUndoIfMainFileNotPresent(self):
        self.addExtFile(id='file', file=notImage)
        os.rename(self._fsname('file.exe.tmp'), self._fsname('file.exe.undo'))
        self.assertEqual(self.reposit(), ['file.exe.undo'])
        self.failIf(self.file.is_broken())
        self.assertEqual(self.reposit(), ['file.exe.tmp'])

    def testIsBrokenReturnsTrueIfBroken(self):
        self.addExtFile(id='file', file=notImage)
        os.remove(self._fsname('file.exe.tmp'))
        self.failUnless(self.file.is_broken())

    def testGetSizeUsesTempFile(self):
        self.addExtFile(id='file', file=notImage)
        self.assertEqual(self.reposit(), ['file.exe.tmp'])
        self.failIfEqual(self.file.get_size(), 0)

    def testGetSizeUsesMainFileIfTempFileNotPresent(self):
        self.addExtFile(id='file', file=notImage)
        self.file._finish()
        self.assertEqual(self.reposit(), ['file.exe'])
        self.failIfEqual(self.file.get_size(), 0)

    def testGetSizeTriesToUndoIfMainFileNotPresent(self):
        self.addExtFile(id='file', file=notImage)
        self.file._finish()
        os.rename(self._fsname('file.exe'), self._fsname('file.exe.undo'))
        self.assertEqual(self.reposit(), ['file.exe.undo'])
        self.failIfEqual(self.file.get_size(), 0)
        self.assertEqual(self.reposit(), ['file.exe.tmp'])

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
        self.file._undo(self.file.filename)
        self.assertEqual(getattr(self.file, '_v_begin_called', 0), 1)
        self.assertEqual(self.reposit(), ['file.exe.tmp'])

    def testGetNewUfnSkipsTempFile(self):
        self.addExtFile(id='file', file=notImage)
        self.assertEqual(self.reposit(), ['file.exe.tmp'])
        fn = self.file._get_new_ufn(self.file.filename)
        self.assertEqual(fn, ['file.1.exe'])

    def testGetFileToServeDoesNotUseTempFile(self):
        self.addExtFile(id='file', file=notImage)
        self.assertEqual(self.reposit(), ['file.exe.tmp'])
        fn = self.file._get_file_to_serve()[0]
        self.assertEqual(fn, ['file.exe'])

    def testManageBeforeDeleteUsesTempFile(self):
        self.addExtFile(id='file', file=notImage)
        self.assertEqual(self.reposit(), ['file.exe.tmp'])
        self.folder._delObject('file')
        self.assertEqual(self.reposit(), ['file.exe.undo'])

    def testManageBeforeDeleteNukesMainFileIfTempFilePresent(self):
        self.addExtFile(id='file', file=notImage)
        self.file._finish()
        self.file.manage_file_upload(file=notImage)
        self.assertEqual(self.reposit(), ['file.exe',
                                          'file.exe.tmp'])
        self.folder._delObject('file')
        self.assertEqual(self.reposit(), ['file.exe.undo'])

    def testManageBeforeDeleteUsesMainFileIfTempFileNotPresent(self):
        self.addExtFile(id='file', file=notImage)
        self.file._finish()
        self.assertEqual(self.reposit(), ['file.exe'])
        self.folder._delObject('file')
        self.assertEqual(self.reposit(), ['file.exe.undo'])

    def testManageAfterCloneCreatesTempFile(self):
        self.addExtFile(id='file', file=notImage)
        self.file._finish()
        transaction.savepoint(1) # Need a _p_oid
        cb = self.folder.manage_copyObjects(['file'])
        self.subfolder.manage_pasteObjects(cb)
        self.assertEqual(self.reposit(), ['file.1.exe.tmp', # copy
                                          'file.exe'])      # original
        self.assertEqual(self.subfolder.file.filename, ['file.1.exe'])

    def testManageAfterCloneUsesTempFileAsSource(self):
        self.addExtFile(id='file', file=notImage)
        transaction.savepoint(1) # Need a _p_oid
        self.subfolder.manage_clone(self.file, 'file')
        self.assertEqual(self.reposit(), ['file.1.exe.tmp', # copy
                                          'file.exe.tmp'])  # original

    def testManageAfterCloneUsesMainFileIfTempFileNotPresent(self):
        self.addExtFile(id='file', file=notImage)
        self.file._finish()
        transaction.savepoint(1) # Need a _p_oid
        self.subfolder.manage_clone(self.file, 'file')
        self.assertEqual(self.reposit(), ['file.1.exe.tmp', # copy
                                          'file.exe'])      # original

    def testManageAfterCloneTriesToUndoIfTempFileNotPresent(self):
        self.addExtFile(id='file', file=notImage)
        self.file._finish()
        os.rename(self._fsname('file.exe'), self._fsname('file.exe.undo'))
        transaction.savepoint(1) # Need a _p_oid
        self.subfolder.manage_clone(self.file, 'file')
        self.assertEqual(self.reposit(), ['file.1.exe.tmp', # copy
                                          'file.exe.tmp'])  # original

    def testManageAfterCloneRegistersWithTM(self):
        self.addExtFile(id='file', file=notImage)
        self.file._finish()
        self.file._v_begin_called = 0   # Clear
        TM.remove(self.file)            # Clear
        transaction.savepoint(1) # Need a _p_oid
        self.assertEqual(getattr(self.subfolder.file, '_v_begin_called', 0), 0)
        self.subfolder.manage_clone(self.file, 'file')
        self.assertEqual(getattr(self.subfolder.file, '_v_begin_called', 0), 1)

    def testGetUfnRegistersWithTM(self):
        self.addExtFile(id='file', file=notImage)
        self.file._finish()
        self.file._v_begin_called = 0   # Clear
        TM.remove(self.file)            # Clear
        self.file._delete(self.file.filename) # _get_ufn will attempt to undo
        self.assertEqual(getattr(self.file, '_v_begin_called', 0), 0)
        self.assertEqual(self.reposit(), ['file.exe.undo'])
        self.file._get_ufn(self.file.filename)
        self.assertEqual(getattr(self.file, '_v_begin_called', 0), 1)
        self.assertEqual(self.reposit(), ['file.exe.tmp'])


class TestExtImageTransactions(ExtFileTestCase):

    def afterSetUp(self):
        ExtFileTestCase.afterSetUp(self)
        self.folder.manage_addFolder('subfolder')
        self.subfolder = self.folder.subfolder
        self.setPermissions(copymove_perms)

    def beforeClose(self):
        transaction.commit()  # Commit the cleaned-up fixture

    def testManageFileUploadCreatesTempImage(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=gifImage)
        self.assertEqual(self.reposit(), ['image.gif.tmp'])

    def testManageFileUploadCreatesTempPreview(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        self.assertEqual(self.reposit(), ['image.jpg.tmp'])

    def testManageFileUploadCreatesTempPreviewIfResize(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=jpegImage, is_preview=1, create_prev=UPLOAD_RESIZE, maxx=10, maxy=10)
        self.assertEqual(self.reposit(), ['image.jpg.tmp'])

    def testManageFileUploadCreatesTempPreviewIfGenerate(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=jpegImage, create_prev=GENERATE, maxx=10, maxy=10)
        self.assertEqual(self.reposit(), ['image.1.jpg.tmp',
                                          'image.jpg.tmp'])

    def testManageHTTPUploadCreatesTempImage(self):
        self.addExtImage(id='image', file='')
        self.image.manage_http_upload(url=self.app.GifImage.absolute_url())
        self.assertEqual(self.reposit(), ['image.gif.tmp'])

    def testManageHTTPUploadCreatesTempPreview(self):
        self.addExtImage(id='image', file='')
        self.image.manage_http_upload(url=self.app.GifImage.absolute_url(), is_preview=1)
        self.assertEqual(self.reposit(), ['image.gif.tmp'])

    #def testManageHTTPUploadCreatesTempPreviewIfAutogen(self):
    #    self.addExtImage(id='image', file='')
    #    self.image.manage_file_upload(file=jpegImage, is_preview=1)
    #    preview_size = self.image.get_prev_size()
    #    self.image.manage_http_upload(url=self.app.GifImage.absolute_url())
    #    self.assertEqual(self.reposit(), ['image.gif.tmp',
    #                                      'image.jpg.tmp'])
    #    # The preview file should no longer be the same
    #    self.failIfEqual(preview_size, self.image.get_prev_size())

    def testPUTCreatesTempImage(self):
        self.addExtImage(id='image', file='')
        request = self.app.REQUEST
        request['BODYFILE'] = open(jpegImage, 'rb')
        self.image.PUT(request, request.RESPONSE)
        self.assertEqual(self.reposit(), ['image.jpg.tmp'])

    def testPUTCreatesTempPreviewIfAutogen(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        preview_size = self.image.get_prev_size()
        request = self.app.REQUEST
        request['BODYFILE'] = open(gifImage, 'rb')
        self.image.PUT(request, request.RESPONSE)
        self.assertEqual(self.reposit(), ['image.gif.tmp',
                                          'image.jpg.tmp'])
        # The preview file should no longer be the same
        self.failIfEqual(preview_size, self.image.get_prev_size())

    def testFinishCommitsTempImage(self):
        self.addExtImage(id='image', file=jpegImage)
        self.assertEqual(self.reposit(), ['image.jpg.tmp'])
        self.image._finish()
        self.assertEqual(self.reposit(), ['image.jpg'])

    def testFinishCommitsTempPreview(self):
        self.addExtImage(id='image', file=jpegImage)
        self.image.manage_create_prev(maxx=10, maxy=10)
        self.assertEqual(self.reposit(), ['image.1.jpg.tmp',
                                          'image.jpg.tmp'])
        self.image._finish()
        self.assertEqual(self.reposit(), ['image.1.jpg',
                                          'image.jpg'])

    def testAbortNukesTempImage(self):
        self.addExtImage(id='image', file=jpegImage)
        self.assertEqual(self.reposit(), ['image.jpg.tmp'])
        self.image._abort()
        self.assertEqual(self.reposit(), [])

    def testAbortNukesTempPreview(self):
        self.addExtImage(id='image', file=jpegImage)
        self.image.manage_create_prev(maxx=10, maxy=10)
        self.assertEqual(self.reposit(), ['image.1.jpg.tmp',
                                          'image.jpg.tmp'])
        self.image._abort()
        self.assertEqual(self.reposit(), [])

    def testUndoCreatesTempImage(self):
        self.addExtImage(id='image', file=jpegImage)
        self.image._finish()
        os.rename(self._fsname('image.jpg'), self._fsname('image.jpg.undo'))
        self.image._undo(self.image.filename)
        self.assertEqual(self.reposit(), ['image.jpg.tmp'])

    def testUndoCreatesTempPreview(self):
        self.addExtImage(id='image', file=jpegImage)
        self.image.manage_create_prev(maxx=10, maxy=10)
        self.image._finish()
        os.rename(self._fsname('image.1.jpg'), self._fsname('image.1.jpg.undo'))
        self.image._undo(self.image.prev_filename)
        self.assertEqual(self.reposit(), ['image.1.jpg.tmp',
                                          'image.jpg'])

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
        self.image._undo(self.image.prev_filename)
        self.assertEqual(getattr(self.image, '_v_begin_called', 0), 1)
        self.assertEqual(self.reposit(), ['image.jpg.tmp'])

    def testManageBeforeDeleteUsesTempPreview(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        self.assertEqual(self.reposit(), ['image.jpg.tmp'])
        self.folder._delObject('image')
        self.assertEqual(self.reposit(), ['image.jpg.undo'])

    def testManageBeforeDeleteNukesPreviewIfTempPreviewPresent(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        self.image._finish()
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        self.assertEqual(self.reposit(), ['image.jpg',
                                          'image.jpg.tmp'])
        self.folder._delObject('image')
        self.assertEqual(self.reposit(), ['image.jpg.undo'])

    def testManageBeforeDeleteUsesPreviewIfTempPreviewNotPresent(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        self.image._finish()
        self.assertEqual(self.reposit(), ['image.jpg'])
        self.folder._delObject('image')
        self.assertEqual(self.reposit(), ['image.jpg.undo'])

    def testManageAfterCloneCreatesTempPreview(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        self.image._finish()
        transaction.savepoint(1) # Need a _p_oid
        cb = self.folder.manage_copyObjects(['image'])
        self.subfolder.manage_pasteObjects(cb)
        self.assertEqual(self.reposit(), ['image.1.jpg.tmp', # copy
                                          'image.jpg'])      # original
        self.assertEqual(self.subfolder.image.prev_filename, ['image.1.jpg'])

    def testManageAfterCloneUsesTempPreviewAsSource(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        transaction.savepoint(1) # Need a _p_oid
        self.subfolder.manage_clone(self.image, 'image')
        self.assertEqual(self.reposit(), ['image.1.jpg.tmp', # copy
                                          'image.jpg.tmp'])  # original

    def testManageAfterCloneUsesPreviewIfTempPreviewNotPresent(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        self.image._finish()
        transaction.savepoint(1) # Need a _p_oid
        self.subfolder.manage_clone(self.image, 'image')
        self.assertEqual(self.reposit(), ['image.1.jpg.tmp', # copy
                                          'image.jpg'])      # original

    def testManageAfterCloneTriesToUndoIfTempPreviewNotPresent(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        self.image._finish()
        os.rename(self._fsname('image.jpg'), self._fsname('image.jpg.undo'))
        transaction.savepoint(1) # Need a _p_oid
        self.subfolder.manage_clone(self.image, 'image')
        self.assertEqual(self.reposit(), ['image.1.jpg.tmp', # copy
                                          'image.jpg.tmp'])  # restored original

    def testManageAfterCloneUsesTempPreviewIfOneFile(self):
        # XXX: Fishy. It seems this tests an impossible state
        self.addExtImage(id='image', file=jpegImage)
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        # Simulate main and preview being one file
        self.image.prev_filename = ['image.2.jpg']
        transaction.savepoint(1) # Need a _p_oid
        self.subfolder.manage_clone(self.image, 'image')
        self.assertEqual(self.reposit(), ['image.1.jpg.tmp', # original preview
                                          'image.2.jpg.tmp', # copy
                                          'image.jpg.tmp'])  # original
        self.assertEqual(self.subfolder.image.prev_filename, ['image.2.jpg'])
        self.assertEqual(self.subfolder.image.filename, ['image.2.jpg'])

    # XXX: Not testable atm
    def DISABLED_testManageAfterCloneRegistersWithTM(self):
        pass

    def testManageCreatePrevCreatesTempFile(self):
        self.addExtImage(id='image', file=jpegImage)
        self.image.manage_create_prev(maxx=10, maxy=10)
        self.assertEqual(self.reposit(), ['image.1.jpg.tmp', # preview
                                          'image.jpg.tmp'])  # original
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
        self.assertEqual(self.reposit(), ['image.jpg.tmp'])
        self.image.manage_del_prev()
        self.assertEqual(self.reposit(), ['image.jpg.undo'])

    def testManageDelPrevNukesPreviewIfTempPreviewPresent(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        self.image._finish()
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        self.assertEqual(self.reposit(), ['image.jpg',
                                          'image.jpg.tmp'])
        self.image.manage_del_prev()
        self.assertEqual(self.reposit(), ['image.jpg.undo'])

    def testManageDelPrevUsesPreviewIfTempPreviewNotPresent(self):
        self.addExtImage(id='image', file='')
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        self.image._finish()
        self.assertEqual(self.reposit(), ['image.jpg'])
        self.image.manage_del_prev()
        self.assertEqual(self.reposit(), ['image.jpg.undo'])


class TestExtFileUndo(ExtFileTestCase):

    def afterSetUp(self):
        ExtFileTestCase.afterSetUp(self)
        self.folder.manage_addFolder('subfolder')
        self.folder_path = self.folder.getPhysicalPath()[1:]
        self.subfolder = self.folder.subfolder
        self.subfolder_path = self.subfolder.getPhysicalPath()[1:]
        self.setPermissions(copymove_perms)

    def beforeClose(self):
        transaction.commit()  # Commit the cleaned-up fixture

    def afterClear(self):
        ExtFileTestCase.afterClear(self)
        ExtFile.REPOSITORY = configuration.FLAT

    def testCutPaste(self):
        self.addExtFile(id='file', file=notImage)
        self.file._finish()
        transaction.savepoint(1)
        self.assertEqual(self.reposit(), ['file.exe'])
        cb = self.folder.manage_cutObjects(['file'])
        self.subfolder.manage_pasteObjects(cb)
        self.assertEqual(self.reposit(), ['file.1.exe.tmp',
                                          'file.exe.undo'])
        # Simulate disaster
        self.file._abort()
        self.assertEqual(self.reposit(), ['file.exe.undo'])

    def testCutPasteNoFinish(self):
        self.addExtFile(id='file', file=notImage)
        transaction.savepoint(1)
        self.assertEqual(self.reposit(), ['file.exe.tmp'])
        cb = self.folder.manage_cutObjects(['file'])
        self.subfolder.manage_pasteObjects(cb)
        self.assertEqual(self.reposit(), ['file.1.exe.tmp',
                                          'file.exe.undo'])
        # Simulate disaster
        self.file._abort()
        self.assertEqual(self.reposit(), ['file.exe.undo'])

    def testCutPasteSyncZodb(self):
        ExtFile.REPOSITORY = configuration.SYNC_ZODB
        self.addExtFile(id='file', file=notImage)
        self.file._finish()
        transaction.savepoint(1)
        self.assertEqual(self.reposit(*self.folder_path), ['file.exe'])
        cb = self.folder.manage_cutObjects(['file'])
        self.subfolder.manage_pasteObjects(cb)
        self.assertEqual(self.reposit(*self.folder_path), ['file.exe.undo',
                                                           'subfolder'])
        self.assertEqual(self.reposit(*self.subfolder_path), ['file.exe.tmp'])
        # Simulate disaster
        self.file._abort()
        self.assertEqual(self.reposit(*self.folder_path), ['file.exe.undo',
                                                           'subfolder'])
        self.assertEqual(self.reposit(*self.subfolder_path), [])

    def testRename(self):
        self.addExtFile(id='file', file=notImage)
        self.file._finish()
        transaction.savepoint(1)
        self.assertEqual(self.reposit(), ['file.exe'])
        self.folder.manage_renameObject('file', 'file44')
        self.assertEqual(self.reposit(), ['file.exe.undo',
                                          'file44.exe.tmp'])
        # Simulate disaster
        self.file._abort()
        self.assertEqual(self.reposit(), ['file.exe.undo'])

    def testRenameNoFinish(self):
        self.addExtFile(id='file', file=notImage)
        transaction.savepoint(1)
        self.assertEqual(self.reposit(), ['file.exe.tmp'])
        self.folder.manage_renameObject('file', 'file44')
        self.assertEqual(self.reposit(), ['file.exe.undo',
                                          'file44.exe.tmp'])
        # Simulate disaster
        self.file._abort()
        self.assertEqual(self.reposit(), ['file.exe.undo'])

    def testRenameSyncZodb(self):
        ExtFile.REPOSITORY = configuration.SYNC_ZODB
        self.addExtFile(id='file', file=notImage)
        self.file._finish()
        transaction.savepoint(1)
        self.assertEqual(self.reposit(*self.folder_path), ['file.exe'])
        self.folder.manage_renameObject('file', 'file44')
        self.assertEqual(self.reposit(*self.folder_path), ['file.exe.undo',
                                                           'file44.exe.tmp'])
        # Simulate disaster
        self.file._abort()
        self.assertEqual(self.reposit(*self.folder_path), ['file.exe.undo'])


class TestExtImageUndo(ExtFileTestCase):

    def afterSetUp(self):
        ExtFileTestCase.afterSetUp(self)
        self.folder.manage_addFolder('subfolder')
        self.folder_path = self.folder.getPhysicalPath()[1:]
        self.subfolder = self.folder.subfolder
        self.subfolder_path = self.subfolder.getPhysicalPath()[1:]
        self.setPermissions(copymove_perms)

    def beforeClose(self):
        transaction.commit()  # Commit the cleaned-up fixture

    def afterClear(self):
        ExtFileTestCase.afterClear(self)
        ExtFile.REPOSITORY = configuration.FLAT

    def testCutPaste(self):
        self.addExtImage(id='image', file=gifImage)
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        self.image._finish()
        transaction.savepoint(1)
        self.assertEqual(self.reposit(), ['image.gif',
                                          'image.jpg'])
        cb = self.folder.manage_cutObjects(['image'])
        self.subfolder.manage_pasteObjects(cb)
        self.assertEqual(self.reposit(), ['image.1.gif.tmp',
                                          'image.1.jpg.tmp',
                                          'image.gif.undo',
                                          'image.jpg.undo'])
        # Simulate disaster
        self.image._abort()
        self.assertEqual(self.reposit(), ['image.gif.undo',
                                          'image.jpg.undo'])

    def testCutPasteNoFinish(self):
        self.addExtImage(id='image', file=gifImage)
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        transaction.savepoint(1)
        self.assertEqual(self.reposit(), ['image.gif.tmp',
                                          'image.jpg.tmp'])
        cb = self.folder.manage_cutObjects(['image'])
        self.subfolder.manage_pasteObjects(cb)
        self.assertEqual(self.reposit(), ['image.1.gif.tmp',
                                          'image.1.jpg.tmp',
                                          'image.gif.undo',
                                          'image.jpg.undo'])
        # Simulate disaster
        self.image._abort()
        self.assertEqual(self.reposit(), ['image.gif.undo',
                                          'image.jpg.undo'])

    def testCutPasteSyncZodb(self):
        ExtFile.REPOSITORY = configuration.SYNC_ZODB
        self.addExtImage(id='image', file=gifImage)
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        self.image._finish()
        transaction.savepoint(1)
        self.assertEqual(self.reposit(*self.folder_path), ['image.gif',
                                                           'image.jpg'])
        cb = self.folder.manage_cutObjects(['image'])
        self.subfolder.manage_pasteObjects(cb)
        self.assertEqual(self.reposit(*self.folder_path), ['image.gif.undo',
                                                           'image.jpg.undo',
                                                           'subfolder'])
        self.assertEqual(self.reposit(*self.subfolder_path), ['image.gif.tmp',
                                                              'image.jpg.tmp'])
        # Simulate disaster
        self.image._abort()
        self.assertEqual(self.reposit(*self.folder_path), ['image.gif.undo',
                                                           'image.jpg.undo',
                                                           'subfolder'])

    def testRename(self):
        self.addExtImage(id='image', file=gifImage)
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        self.image._finish()
        transaction.savepoint(1)
        self.assertEqual(self.reposit(), ['image.gif',
                                          'image.jpg'])
        self.folder.manage_renameObject('image', 'image44')
        self.assertEqual(self.reposit(), ['image.gif.undo',
                                          'image.jpg.undo',
                                          'image44.gif.tmp',
                                          'image44.jpg.tmp'])
        # Simulate disaster
        self.image._abort()
        self.assertEqual(self.reposit(), ['image.gif.undo',
                                          'image.jpg.undo'])

    def testRenameNoFinish(self):
        self.addExtImage(id='image', file=gifImage)
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        transaction.savepoint(1)
        self.assertEqual(self.reposit(), ['image.gif.tmp',
                                          'image.jpg.tmp'])
        self.folder.manage_renameObject('image', 'image44')
        self.assertEqual(self.reposit(), ['image.gif.undo',
                                          'image.jpg.undo',
                                          'image44.gif.tmp',
                                          'image44.jpg.tmp'])
        # Simulate disaster
        self.image._abort()
        self.assertEqual(self.reposit(), ['image.gif.undo',
                                          'image.jpg.undo'])

    def testRenameSyncZodb(self):
        ExtFile.REPOSITORY = configuration.SYNC_ZODB
        self.addExtImage(id='image', file=gifImage)
        self.image.manage_file_upload(file=jpegImage, is_preview=1)
        self.image._finish()
        transaction.savepoint(1)
        self.assertEqual(self.reposit(*self.folder_path), ['image.gif',
                                                           'image.jpg'])
        self.folder.manage_renameObject('image', 'image44')
        self.assertEqual(self.reposit(*self.folder_path), ['image.gif.undo',
                                                           'image.jpg.undo',
                                                           'image44.gif.tmp',
                                                           'image44.jpg.tmp'])
        # Simulate disaster
        self.image._abort()
        self.assertEqual(self.reposit(*self.folder_path), ['image.gif.undo',
                                                           'image.jpg.undo'])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTransactions))
    suite.addTest(makeSuite(TestTransactionManager))
    suite.addTest(makeSuite(TestExtFileTransactions))
    suite.addTest(makeSuite(TestExtImageTransactions))
    suite.addTest(makeSuite(TestExtFileUndo))
    suite.addTest(makeSuite(TestExtImageUndo))
    return suite

