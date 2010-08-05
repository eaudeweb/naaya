#
# Tests interaction with Photo product
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

have_photo = ZopeTestCase.hasProduct('Photo')

if have_photo:
    ZopeTestCase.installProduct('SiteAccess')
    ZopeTestCase.installProduct('ExtFile')
    ZopeTestCase.installProduct('Photo')

from Products.ExtFile.tests.ExtFileTestCase import ExtFileTestCase
from Products.ExtFile.tests.ExtFileTestCase import gifImage
from Products.ExtFile import ExtFile, Config
from Acquisition import aq_base

user_name = ZopeTestCase.user_name
photo_perms = ['Add Photos', 'Change Photos', 'Add Documents, Images, and Files']

import base64
auth_info = 'Basic %s' % base64.encodestring('%s:secret' % user_name)


class TestPhoto(ExtFileTestCase):

    def testAddPhoto(self):
        factory = self.folder.manage_addProduct['Photo']
        factory.manage_addPhoto('foo', '', open(gifImage, 'rb'), 'image/gif', store='ExtImage', engine='PIL', pregen=0)
        self.folder.foo._original._finish()
        self.failUnless(self._exists('foo.gif'))

    def testAddPhotoWithDisplays(self):
        factory = self.folder.manage_addProduct['Photo']
        factory.manage_addPhoto('foo', '', open(gifImage, 'rb'), 'image/gif', store='ExtImage', engine='PIL', pregen=1)
        self.folder.foo._original._finish()
        self.failUnless(self._exists('foo.gif'))

        for id in self.folder.foo.displayIds(None):
            self.folder.foo._photos[id]._finish()
        self.failUnless(self._exists('foo_large.gif'))
        self.failUnless(self._exists('foo_medium.gif'))
        self.failUnless(self._exists('foo_small.gif'))
        self.failUnless(self._exists('foo_thumbnail.gif'))
        self.failUnless(self._exists('foo_xlarge.gif'))
        self.failUnless(self._exists('foo_xsmall.gif'))


class TestPUTPhoto(ExtFileTestCase):

    def afterSetUp(self):
        ExtFileTestCase.afterSetUp(self)

        if not self.app.objectIds('Virtual Host Monster'):
            factory = self.app.manage_addProduct['SiteAccess']
            factory.manage_addVirtualHostMonster('VHM')

        request = self.app.REQUEST
        request['PARENTS'] = [self.app]

        # Fake a dav PUT request
        request['BODYFILE'] = open(gifImage, 'rb')
        request.environ['CONTENT_TYPE'] = 'image/gif'
        request.environ['REQUEST_METHOD'] = 'PUT'
        request._auth = auth_info

    def afterClear(self):
        ExtFileTestCase.afterClear(self)
        ExtFile.REPOSITORY = Config.FLAT
        ExtFile.ZODB_PATH = Config.VIRTUAL

    def testPUTPhoto(self):

        def PUT_factory(name, typ, body):
            """Creates a Photo."""
            from Products.Photo.Photo import Photo
            return Photo(name, '', body, content_type=typ, store='ExtImage', engine='PIL', pregen=0)

        self.folder.PUT_factory = PUT_factory
        self.setPermissions(photo_perms)

        request = self.app.REQUEST
        put = request.traverse('/test_folder_1_/image')
        put(request, request.RESPONSE)
        self.failUnless(hasattr(aq_base(self.folder), 'image'))
        self.folder.image._original._finish()
        self.failUnless(self._exists('image.gif'))

    def testPUTPhotoWithDisplays(self):

        def PUT_factory(name, typ, body):
            """Creates a Photo."""
            from Products.Photo.Photo import Photo
            return Photo(name, '', body, content_type=typ, store='ExtImage', engine='PIL', pregen=1)

        self.folder.PUT_factory = PUT_factory
        self.setPermissions(photo_perms)

        request = self.app.REQUEST
        put = request.traverse('/test_folder_1_/image')
        put(request, request.RESPONSE)
        self.failUnless(hasattr(aq_base(self.folder), 'image'))
        self.folder.image._original._finish()
        self.failUnless(self._exists('image.gif'))

        for id in self.folder.image.displayIds(None):
            self.folder.image._photos[id]._finish()
        self.failUnless(self._exists('image_large.gif'))
        self.failUnless(self._exists('image_medium.gif'))
        self.failUnless(self._exists('image_small.gif'))
        self.failUnless(self._exists('image_thumbnail.gif'))
        self.failUnless(self._exists('image_xlarge.gif'))
        self.failUnless(self._exists('image_xsmall.gif'))

    def testPUTPhotoSyncZodbVirtual(self):

        def PUT_factory(name, typ, body):
            """Creates a Photo."""
            from Products.Photo.Photo import Photo
            return Photo(name, '', body, content_type=typ, store='ExtImage', engine='PIL', pregen=0)

        self.folder.PUT_factory = PUT_factory
        self.setPermissions(photo_perms)

        ExtFile.REPOSITORY = Config.SYNC_ZODB
        ExtFile.ZODB_PATH = Config.VIRTUAL
        request = self.app.REQUEST
        put = request.traverse('/test_folder_1_/image')
        put(request, request.RESPONSE)
        self.failUnless(hasattr(aq_base(self.folder), 'image'))

        self.assertEqual(self.folder.image._original.filename, ['test_folder_1_', 'image', 'image.gif'])

    def testPUTPhotoSyncZodbPhysical(self):

        def PUT_factory(name, typ, body):
            """Creates a Photo."""
            from Products.Photo.Photo import Photo
            return Photo(name, '', body, content_type=typ, store='ExtImage', engine='PIL', pregen=0)

        self.folder.PUT_factory = PUT_factory
        self.setPermissions(photo_perms)

        ExtFile.REPOSITORY = Config.SYNC_ZODB
        ExtFile.ZODB_PATH = Config.PHYSICAL
        request = self.app.REQUEST
        put = request.traverse('/test_folder_1_/image')
        put(request, request.RESPONSE)
        self.failUnless(hasattr(aq_base(self.folder), 'image'))

        self.assertEqual(self.folder.image._original.filename, ['test_folder_1_', 'image', 'image.gif'])

    def testPUTPhotoSyncZodbVHMVirtual(self):

        def PUT_factory(name, typ, body):
            """Creates a Photo."""
            from Products.Photo.Photo import Photo
            return Photo(name, '', body, content_type=typ, store='ExtImage', engine='PIL', pregen=0)

        self.folder.PUT_factory = PUT_factory
        self.setPermissions(photo_perms)

        ExtFile.REPOSITORY = Config.SYNC_ZODB
        ExtFile.ZODB_PATH = Config.VIRTUAL
        request = self.app.REQUEST
        put = request.traverse('/VirtualHostBase/http/foo.com:80/VirtualHostRoot/test_folder_1_/image')
        put(request, request.RESPONSE)
        self.failUnless(hasattr(aq_base(self.folder), 'image'))

        self.assertEqual(self.folder.image._original.filename, ['test_folder_1_', 'image', 'image.gif'])

    def testPUTPhotoSyncZodbVHMPhysical(self):

        def PUT_factory(name, typ, body):
            """Creates a Photo."""
            from Products.Photo.Photo import Photo
            return Photo(name, '', body, content_type=typ, store='ExtImage', engine='PIL', pregen=0)

        self.folder.PUT_factory = PUT_factory
        self.setPermissions(photo_perms)

        ExtFile.REPOSITORY = Config.SYNC_ZODB
        ExtFile.ZODB_PATH = Config.PHYSICAL
        request = self.app.REQUEST
        put = request.traverse('/VirtualHostBase/http/foo.com:80/VirtualHostRoot/test_folder_1_/image')
        put(request, request.RESPONSE)
        self.failUnless(hasattr(aq_base(self.folder), 'image'))

        # XXX: Photos always use VIRTUAL
        self.assertEqual(self.folder.image._original.filename, ['test_folder_1_', 'image', 'image.gif'])

    def testPUTPhotoSyncZodbVHMSubfolderHostingVirtual(self):

        def PUT_factory(name, typ, body):
            """Creates a Photo."""
            from Products.Photo.Photo import Photo
            return Photo(name, '', body, content_type=typ, store='ExtImage', engine='PIL', pregen=0)

        self.folder.PUT_factory = PUT_factory
        self.setPermissions(photo_perms)

        ExtFile.REPOSITORY = Config.SYNC_ZODB
        ExtFile.ZODB_PATH = Config.VIRTUAL
        request = self.app.REQUEST
        put = request.traverse('/VirtualHostBase/http/foo.com:80/test_folder_1_/VirtualHostRoot/image')
        put(request, request.RESPONSE)
        self.failUnless(hasattr(aq_base(self.folder), 'image'))

        self.assertEqual(self.folder.image._original.filename, ['image', 'image.gif'])

    def testPUTPhotoSyncZodbVHMSubfolderHostingPhysical(self):

        def PUT_factory(name, typ, body):
            """Creates a Photo."""
            from Products.Photo.Photo import Photo
            return Photo(name, '', body, content_type=typ, store='ExtImage', engine='PIL', pregen=0)

        self.folder.PUT_factory = PUT_factory
        self.setPermissions(photo_perms)

        ExtFile.REPOSITORY = Config.SYNC_ZODB
        ExtFile.ZODB_PATH = Config.PHYSICAL
        request = self.app.REQUEST
        put = request.traverse('/VirtualHostBase/http/foo.com:80/test_folder_1_/VirtualHostRoot/image')
        put(request, request.RESPONSE)
        self.failUnless(hasattr(aq_base(self.folder), 'image'))

        # XXX: Photos always use VIRTUAL
        self.assertEqual(self.folder.image._original.filename, ['image', 'image.gif'])

    def testPUTPhotoSyncZodbVHMInsideOutHostingVirtual(self):

        def PUT_factory(name, typ, body):
            """Creates a Photo."""
            from Products.Photo.Photo import Photo
            return Photo(name, '', body, content_type=typ, store='ExtImage', engine='PIL', pregen=0)

        self.folder.PUT_factory = PUT_factory
        self.setPermissions(photo_perms)

        ExtFile.REPOSITORY = Config.SYNC_ZODB
        ExtFile.ZODB_PATH = Config.VIRTUAL
        request = self.app.REQUEST
        put = request.traverse('/VirtualHostBase/http/foo.com:80/VirtualHostRoot/_vh_foo/test_folder_1_/image')
        put(request, request.RESPONSE)
        self.failUnless(hasattr(aq_base(self.folder), 'image'))

        self.assertEqual(self.folder.image._original.filename, ['test_folder_1_', 'image', 'image.gif'])

    def testPUTPhotoSyncZodbVHMInsideOutHostingPhysical(self):

        def PUT_factory(name, typ, body):
            """Creates a Photo."""
            from Products.Photo.Photo import Photo
            return Photo(name, '', body, content_type=typ, store='ExtImage', engine='PIL', pregen=0)

        self.folder.PUT_factory = PUT_factory
        self.setPermissions(photo_perms)

        ExtFile.REPOSITORY = Config.SYNC_ZODB
        ExtFile.ZODB_PATH = Config.PHYSICAL
        request = self.app.REQUEST
        put = request.traverse('/VirtualHostBase/http/foo.com:80/VirtualHostRoot/_vh_foo/test_folder_1_/image')
        put(request, request.RESPONSE)
        self.failUnless(hasattr(aq_base(self.folder), 'image'))

        # XXX: Photos always use VIRTUAL
        self.assertEqual(self.folder.image._original.filename, ['test_folder_1_', 'image', 'image.gif'])

    def testPUTPhotoSyncZodbVHMSubfolderInsideOutHostingVirtual(self):

        def PUT_factory(name, typ, body):
            """Creates a Photo."""
            from Products.Photo.Photo import Photo
            return Photo(name, '', body, content_type=typ, store='ExtImage', engine='PIL', pregen=0)

        self.folder.PUT_factory = PUT_factory
        self.setPermissions(photo_perms)

        ExtFile.REPOSITORY = Config.SYNC_ZODB
        ExtFile.ZODB_PATH = Config.VIRTUAL
        request = self.app.REQUEST
        put = request.traverse('/VirtualHostBase/http/foo.com:80/test_folder_1_/VirtualHostRoot/_vh_foo/image')
        put(request, request.RESPONSE)
        self.failUnless(hasattr(aq_base(self.folder), 'image'))

        self.assertEqual(self.folder.image._original.filename, ['image', 'image.gif'])

    def testPUTPhotoSyncZodbVHMSubfolderInsideOutHostingPhysical(self):

        def PUT_factory(name, typ, body):
            """Creates a Photo."""
            from Products.Photo.Photo import Photo
            return Photo(name, '', body, content_type=typ, store='ExtImage', engine='PIL', pregen=0)

        self.folder.PUT_factory = PUT_factory
        self.setPermissions(photo_perms)

        ExtFile.REPOSITORY = Config.SYNC_ZODB
        ExtFile.ZODB_PATH = Config.PHYSICAL
        request = self.app.REQUEST
        put = request.traverse('/VirtualHostBase/http/foo.com:80/test_folder_1_/VirtualHostRoot/_vh_foo/image')
        put(request, request.RESPONSE)
        self.failUnless(hasattr(aq_base(self.folder), 'image'))

        # XXX: Photos always use VIRTUAL
        self.assertEqual(self.folder.image._original.filename, ['image', 'image.gif'])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    if have_photo:
        suite.addTest(makeSuite(TestPhoto))
        suite.addTest(makeSuite(TestPUTPhoto))
    return suite

if __name__ == '__main__':
    framework()

