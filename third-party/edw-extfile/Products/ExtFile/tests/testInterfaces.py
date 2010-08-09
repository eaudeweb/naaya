#
# Tests the interfaces
#

from Testing import ZopeTestCase

ZopeTestCase.installProduct('ExtFile')

from Products.ExtFile.testing import ExtFileTestCase
from Products.ExtFile.interfaces import IExtFile
from Products.ExtFile.interfaces import IExtImage

from zope.interface.verify import verifyObject


class TestInterfaces(ExtFileTestCase):

    def afterSetUp(self):
        ExtFileTestCase.afterSetUp(self)
        self.file = self.addExtFile(id='file', file='')
        self.image = self.addExtImage(id='image', file='')

    def testIExtFile(self):
        self.failUnless(verifyObject(IExtFile, self.file))
        self.failUnless(verifyObject(IExtFile, self.image))

    def testIExtImage(self):
        self.failUnless(verifyObject(IExtImage, self.image))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestInterfaces))
    return suite

