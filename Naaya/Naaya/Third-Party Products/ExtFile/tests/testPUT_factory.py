#
# Tests the PUT_factory() and PUT() method, especially with
# SYNC_ZODB repository type.
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

ZopeTestCase.installProduct('SiteAccess')
ZopeTestCase.installProduct('ExternalMethod')
ZopeTestCase.installProduct('ExtFile')

from Products.ExtFile.tests.ExtFileTestCase import ExtFileTestCase
from Products.ExtFile.tests.ExtFileTestCase import gifImage
from Products.ExtFile.tests.ExtFileTestCase import copymove_perms

from Products.ExtFile import ExtFile, Config

from webdav.NullResource import NullResource
from Acquisition import aq_base

user_name = ZopeTestCase.user_name
user_password = ZopeTestCase.user_password

import base64
auth_info = 'Basic %s' % base64.encodestring('%s:%s' % (user_name, user_password)).rstrip()

from os.path import join


class TestPUTFactory(ExtFileTestCase):

    def afterSetUp(self):
        ExtFileTestCase.afterSetUp(self)
        self.setPermissions(copymove_perms)

        if not self.app.objectIds('Virtual Host Monster'):
            factory = self.app.manage_addProduct['SiteAccess']
            factory.manage_addVirtualHostMonster('VHM')

        factory = self.folder.manage_addProduct['ExternalMethod']
        factory.manage_addExternalMethod('PUT_factory', '', 'ExtFile.PUT_factory', 'PUT_factory')

        self.folder.manage_addFolder('subfolder')
        self.subfolder = self.folder.subfolder

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

    def testPUT_factoryAddsImageNoTraverse(self):
        request = self.app.REQUEST
        new = NullResource(self.folder, 'image', request).__of__(self.folder)
        new.PUT(request, request.RESPONSE)
        self.failUnless(hasattr(aq_base(self.folder), 'image'))
        self.failUnless(self._exists('image.gif.tmp'))

    def testPUT_factoryAddsImageFlat(self):
        ExtFile.REPOSITORY = Config.FLAT
        request = self.app.REQUEST
        put = request.traverse('/test_folder_1_/image')
        put(request, request.RESPONSE)
        self.failUnless(hasattr(aq_base(self.folder), 'image'))
        self.failUnless(self._exists('image.gif.tmp'))

    def testPUT_factoryAddsImageSyncZodb(self):
        ExtFile.REPOSITORY = Config.SYNC_ZODB
        request = self.app.REQUEST
        put = request.traverse('/test_folder_1_/image')
        put(request, request.RESPONSE)
        self.failUnless(hasattr(aq_base(self.folder), 'image'))
        self.failUnless(self._exists(join('test_folder_1_', 'image.gif.tmp')))

    def testPUT_factoryAddsImageSyncZodbSubfolder(self):
        ExtFile.REPOSITORY = Config.SYNC_ZODB
        request = self.app.REQUEST
        put = request.traverse('/test_folder_1_/subfolder/image')
        put(request, request.RESPONSE)
        self.failUnless(hasattr(aq_base(self.subfolder), 'image'))
        self.failUnless(self._exists(join('test_folder_1_', 'subfolder', 'image.gif.tmp')))

    def testPUT_factoryAddsImageSyncZodbVHM(self):
        ExtFile.REPOSITORY = Config.SYNC_ZODB
        request = self.app.REQUEST
        put = request.traverse('/VirtualHostBase/http/foo.com:80/VirtualHostRoot/test_folder_1_/subfolder/image')
        put(request, request.RESPONSE)
        self.failUnless(hasattr(aq_base(self.subfolder), 'image'))
        self.failUnless(self._exists(join('test_folder_1_', 'subfolder', 'image.gif.tmp')))

    def testPUT_factoryAddsImageSyncZodbVHMSubfolderHostingVirtual(self):
        ExtFile.REPOSITORY = Config.SYNC_ZODB
        request = self.app.REQUEST
        put = request.traverse('/VirtualHostBase/http/foo.com:80/test_folder_1_/VirtualHostRoot/subfolder/image')
        put(request, request.RESPONSE)
        self.failUnless(hasattr(aq_base(self.subfolder), 'image'))
        self.failUnless(self._exists(join('subfolder', 'image.gif.tmp')))

    def testPUT_factoryAddsImageSyncZodbVHMInsideOutHostingVirtual(self):
        ExtFile.REPOSITORY = Config.SYNC_ZODB
        request = self.app.REQUEST
        put = request.traverse('/VirtualHostBase/http/foo.com:80/VirtualHostRoot/_vh_foo/test_folder_1_/subfolder/image')
        put(request, request.RESPONSE)
        self.failUnless(hasattr(aq_base(self.subfolder), 'image'))
        self.failUnless(self._exists(join('test_folder_1_', 'subfolder', 'image.gif.tmp')))

    def testPUT_factoryAddsImageSyncZodbVHMSubfolderInsideOutHostingVirtual(self):
        ExtFile.REPOSITORY = Config.SYNC_ZODB
        request = self.app.REQUEST
        put = request.traverse('/VirtualHostBase/http/foo.com:80/test_folder_1_/VirtualHostRoot/_vh_foo/subfolder/image')
        put(request, request.RESPONSE)
        self.failUnless(hasattr(aq_base(self.subfolder), 'image'))
        self.failUnless(self._exists(join('subfolder', 'image.gif.tmp')))

    def testPUT_factoryAddsImageSyncZodbVHMSubfolderHostingPhysical(self):
        ExtFile.REPOSITORY = Config.SYNC_ZODB
        ExtFile.ZODB_PATH = Config.PHYSICAL
        request = self.app.REQUEST
        put = request.traverse('/VirtualHostBase/http/foo.com:80/test_folder_1_/VirtualHostRoot/subfolder/image')
        put(request, request.RESPONSE)
        self.failUnless(hasattr(aq_base(self.subfolder), 'image'))
        self.failUnless(self._exists(join('test_folder_1_', 'subfolder', 'image.gif.tmp')))

    def testPUT_factoryAddsImageSyncZodbVHMInsideOutHostingPhysical(self):
        ExtFile.REPOSITORY = Config.SYNC_ZODB
        ExtFile.ZODB_PATH = Config.PHYSICAL
        request = self.app.REQUEST
        put = request.traverse('/VirtualHostBase/http/foo.com:80/VirtualHostRoot/_vh_foo/test_folder_1_/subfolder/image')
        put(request, request.RESPONSE)
        self.failUnless(hasattr(aq_base(self.subfolder), 'image'))
        self.failUnless(self._exists(join('test_folder_1_', 'subfolder', 'image.gif.tmp')))

    def testPUT_factoryAddsImageSyncZodbVHMSubfolderInsideOutHostingPhysical(self):
        ExtFile.REPOSITORY = Config.SYNC_ZODB
        ExtFile.ZODB_PATH = Config.PHYSICAL
        request = self.app.REQUEST
        put = request.traverse('/VirtualHostBase/http/foo.com:80/test_folder_1_/VirtualHostRoot/_vh_foo/subfolder/image')
        put(request, request.RESPONSE)
        self.failUnless(hasattr(aq_base(self.subfolder), 'image'))
        self.failUnless(self._exists(join('test_folder_1_', 'subfolder', 'image.gif.tmp')))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPUTFactory))
    return suite

if __name__ == '__main__':
    framework()

