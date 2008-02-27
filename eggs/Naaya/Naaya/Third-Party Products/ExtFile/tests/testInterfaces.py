#
# Tests the interfaces
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

ZopeTestCase.installProduct('ExtFile')

from Products.ExtFile.tests.ExtFileTestCase import ExtFileTestCase
from Products.ExtFile.IExtFile import IExtFile
from Products.ExtFile.IExtFile import IExtImage

try:
    from Interface.Verify import verifyObject
    have_verify = 1
except ImportError:
    print 'testInterfaces.py: The tests in this module require Zope >= 2.6'
    have_verify = 0


class TestInterfaces(ExtFileTestCase):

    def afterSetUp(self):
        ExtFileTestCase.afterSetUp(self)
        self.addExtFile(id='file', file='')
        self.addExtImage(id='image', file='')

    def testIExtFile(self):
        self.failUnless(verifyObject(IExtFile, self.file))

    def testIExtImage(self):
        self.failUnless(verifyObject(IExtImage, self.image))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    if have_verify:
        suite.addTest(makeSuite(TestInterfaces))
    return suite

if __name__ == '__main__':
    framework()

