#
# Tests the ZCacheable implementation
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

ZopeTestCase.installProduct('ExtFile')
ZopeTestCase.utils.startZServer()

from Products.ExtFile.tests.ExtFileTestCase import ExtFileTestCase
from Products.ExtFile.tests.ExtFileTestCase import gifImage, notImage

from Testing.ZopeTestCase import Functional
from Testing.ZopeTestCase import user_name
from Testing.ZopeTestCase import user_password
user_auth = '%s:%s' % (user_name, user_password)

from OFS.SimpleItem import SimpleItem
from OFS.Cache import ZCM_MANAGERS
from webdav.common import rfc1123_date
from DateTime import DateTime
from StringIO import StringIO
from Products.ExtFile.ExtImage import UPLOAD_RESIZE
from Products.ExtFile.ExtFile import IStreamIterator

from Products.ExtFile.ExtFile import ChangePermission
from AccessControl.Permissions import ftp_access as FTPAccess


class DummyCache:
    def __init__(self):
        self.data = ''
        self.called = []
    def ZCache_set(self, ob, data, *args, **kw):
        self.called.append('set')
        self.data = data
    def ZCache_get(self, ob, *args, **kw):
        self.called.append('get')
        return self.data
    def ZCache_invalidate(self, ob):
        self.called.append('invalidate')
        self.data = ''

class DummyCacheManager(SimpleItem):
    meta_type = 'Dummy Cache Manager'
    def __init__(self, id):
        self.id = id
        self.cache = DummyCache()
    def ZCacheManager_getCache(self):
        return self.cache


class ExtFileCacheableTests(Functional, ExtFileTestCase):

    def afterSetUp(self):
        ExtFileTestCase.afterSetUp(self)
        # Set up cache
        self.folder.cache = DummyCacheManager('cache')
        setattr(self.folder, ZCM_MANAGERS, ('cache',))
        self.cache = self.folder.cache.cache
        # Set up cached file
        self.addExtFile(id='file.exe', file=notImage)
        self.file.ZCacheable_setManagerId('cache')
        self.file_path = self.file.absolute_url(1)

    def test304ResponseSetsCache(self):
        response = self.publish(self.file_path,
                                env={'HTTP_IF_MODIFIED_SINCE': rfc1123_date(DateTime()+7)},
                                basic=user_auth)
        self.assertEqual(response.getStatus(), 304)
        self.assertEqual(self.cache.data, None)
        self.assertEqual(self.cache.called, ['set'])

    def test200ResponseSetsCache(self):
        response = self.publish(self.file_path, basic=user_auth)
        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(self.cache.data, None)
        self.assertEqual(self.cache.called, ['set'])

    def testManageUploadInvalidatesCache(self):
        self.file.manage_upload(open(gifImage, 'rb'))
        self.assertEqual(self.cache.data, '')
        self.assertEqual(self.cache.called, ['invalidate'])

    def testManageFileUploadInvalidatesCache(self):
        self.file.manage_file_upload(gifImage)
        self.assertEqual(self.cache.data, '')
        self.assertEqual(self.cache.called, ['invalidate'])

    def testManageHTTPUploadInvalidatesCache(self):
        self.file.manage_http_upload(url=self.app.GifImage.absolute_url())
        self.assertEqual(self.cache.data, '')
        self.assertEqual(self.cache.called, ['invalidate'])

    def testPUTInvalidatesCache(self):
        self.setPermissions([ChangePermission])
        response = self.publish(self.file_path,
                                request_method='PUT',
                                env={'CONTENT_TYPE': 'image/gif'},
                                stdin=open(gifImage, 'rb'),
                                basic=user_auth)
        self.assertEqual(response.getStatus(), 204)
        self.assertEqual(self.cache.data, '')
        self.assertEqual(self.cache.called, ['invalidate'])

    def testManageEditInvalidatesCache(self):
        self.file.manage_editExtFile(title='Foo')
        self.assertEqual(self.cache.data, '')
        self.assertEqual(self.cache.called, ['invalidate'])

    def testRedirectDefaultViewReturns304(self):
        self.file.manage_file_upload(gifImage)
        self.file.redirect_default_view = 1
        response = self.publish(self.file_path,
                                env={'HTTP_IF_MODIFIED_SINCE': rfc1123_date(DateTime()+7)},
                                basic=user_auth)
        self.assertEqual(response.getStatus(), 304)
        self.assertEqual(response.getHeader('Location'), None)

    def testRedirectDefaultViewReturns302(self):
        self.file.redirect_default_view = 1
        saved = os.environ.copy()
        os.environ['EXTFILE_STATIC_PATH'] = '/static'
        try:
            response = self.publish(self.file_path, basic=user_auth)
        finally:
            os.environ = saved
        self.assertEqual(response.getStatus(), 302)
        self.assertEqual(response.getHeader('Location'),
                         self.app.REQUEST.SERVER_URL+'/static/file.exe')

    if IStreamIterator is not None:

        def testStreamIterator(self):
            response = self.publish(self.file_path, basic=user_auth)
            self.assertEqual(response.getStatus(), 200)
            # FIXME
            self.failUnless(response.getBody().startswith('<Products.ExtFile.ExtFile.stream_iterator'))
            self.assertEqual(self.cache.called, ['set'])

        def testFTPgetStreamIterator(self):
            self.setPermissions([FTPAccess])
            response = self.publish(self.file_path+'/manage_FTPget',
                                    basic=user_auth)
            self.assertEqual(response.getStatus(), 200)
            # FIXME
            self.failUnless(response.getBody().startswith('<Products.ExtFile.ExtFile.stream_iterator'))
            self.assertEqual(self.cache.called, ['set'])

        def testNoRequestNoStreamIterator(self):
            body = self.file.index_html()
            self.assertEqual(self.app.REQUEST.RESPONSE.getStatus(), 200)
            # Not taken from cache
            self.assertEqual(body, open(notImage, 'rb').read())
            self.assertEqual(self.cache.called, [])


class ExtImageCacheableTests(ExtFileCacheableTests):

    def afterSetUp(self):
        ExtFileTestCase.afterSetUp(self)
        # Set up cache
        self.folder.cache = DummyCacheManager('cache')
        setattr(self.folder, ZCM_MANAGERS, ('cache',))
        self.cache = self.folder.cache.cache
        # Set up cached image
        self.addExtImage(id='file.exe', file=notImage)
        self.image.ZCacheable_setManagerId('cache')
        self.file = self.image
        self.file_path = self.image.absolute_url(1)

    def testManageUploadPreviewInvalidatesCache(self):
        self.image.manage_upload(open(gifImage, 'rb'), is_preview=1)
        self.assertEqual(self.cache.data, '')
        self.assertEqual(self.cache.called, ['invalidate'])

    def testManageUploadPreviewResizeInvalidatesCache(self):
        self.image.manage_upload(open(gifImage, 'rb'), is_preview=1, create_prev=UPLOAD_RESIZE)
        self.assertEqual(self.cache.data, '')
        self.assertEqual(self.cache.called, ['invalidate'])

    def testManageFileUploadPreviewInvalidatesCache(self):
        self.image.manage_file_upload(gifImage, is_preview=1)
        self.assertEqual(self.cache.data, '')
        self.assertEqual(self.cache.called, ['invalidate'])

    def testManageFileUploadPreviewResizeInvalidatesCache(self):
        self.image.manage_file_upload(gifImage, is_preview=1, create_prev=UPLOAD_RESIZE)
        self.assertEqual(self.cache.data, '')
        self.assertEqual(self.cache.called, ['invalidate'])

    def testManageHTTPUploadPreviewInvalidatesCache(self):
        self.image.manage_http_upload(url=self.app.GifImage.absolute_url(), is_preview=1)
        self.assertEqual(self.cache.data, '')
        self.assertEqual(self.cache.called, ['invalidate'])

    def testManageCreatePrevInvalidatesCache(self):
        self.image.manage_file_upload(gifImage)
        self.cache.ZCache_invalidate(None)
        self.cache.called = []
        self.image.manage_create_prev(maxx=100, maxy=100, ratio=1)
        self.assertEqual(self.cache.data, '')
        self.assertEqual(self.cache.called, ['invalidate'])

    def testManageDelPrevInvalidatesCache(self):
        self.image.manage_file_upload(gifImage)
        self.image.manage_create_prev(maxx=100, maxy=100, ratio=1)
        self.cache.ZCache_invalidate(None)
        self.cache.called = []
        self.image.manage_del_prev()
        self.assertEqual(self.cache.data, '')
        self.assertEqual(self.cache.called, ['invalidate'])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(ExtFileCacheableTests))
    suite.addTest(makeSuite(ExtImageCacheableTests))
    return suite

if __name__ == '__main__':
    framework()

