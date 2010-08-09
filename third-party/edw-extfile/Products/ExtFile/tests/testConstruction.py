#
# Test construction errors reported by Bruno Grampa
#

from Testing import ZopeTestCase

ZopeTestCase.installProduct('ExtFile')

from Products.ExtFile.testing import ExtFileTestCase
from Products.ExtFile.testing import gifImage
from Products.ExtFile.testing import notImage
from Products.ExtFile.testing import makeFileUpload

write_file = """
<dtml-call
"manage_addProduct['ExtFile'].manage_addExtFile(id=REQUEST['id'],title='',descr='',
                              file=REQUEST['file'],content_type='',
                              permission_check=0)">
Ok, done.
"""

write_image = """
<dtml-call
"manage_addProduct['ExtFile'].manage_addExtImage(id=REQUEST['id'],title='',descr='',
                              file=REQUEST['file'],content_type='',create_prev=1,
                              maxx='100', maxy='100', ratio=1,
                              permission_check=0)">
Ok, done.
"""


class TestConstruction(ExtFileTestCase):

    def afterSetUp(self):
        ExtFileTestCase.afterSetUp(self)
        self.setPermissions(('Add ExtFiles', 'Add ExtImages'))

    def testFileConstruction(self):
        self.folder.manage_addDTMLMethod('write', file=write_file)
        self.app.REQUEST['id'] = 'foo'
        self.app.REQUEST['file'] = makeFileUpload(gifImage, 'image/gif', 'foo')
        body = self.folder.write(self.folder, self.app.REQUEST)
        self.failUnless(body.find('Ok, done.') >= 0)
        self.failUnless('foo' in self.folder.objectIds())

    def testFileConstructionNoContentType(self):
        self.folder.manage_addDTMLMethod('write', file=write_file)
        self.app.REQUEST['id'] = 'foo'
        self.app.REQUEST['file'] = makeFileUpload(notImage, '', 'foo')
        body = self.folder.write(self.folder, self.app.REQUEST)
        self.failUnless(body.find('Ok, done.') >= 0)
        self.failUnless('foo' in self.folder.objectIds())

    def testImageConstruction(self):
        self.folder.manage_addDTMLMethod('write', file=write_image)
        self.app.REQUEST['id'] = 'foo'
        self.app.REQUEST['file'] = makeFileUpload(gifImage, 'image/gif', 'foo')
        body = self.folder.write(self.folder, self.app.REQUEST)
        self.failUnless(body.find('Ok, done.') >= 0)
        self.failUnless('foo' in self.folder.objectIds())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestConstruction))
    return suite

