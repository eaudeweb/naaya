#
# Tests Zope's CopySupport
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

from DateTime import DateTime
ZOPE274 = hasattr(DateTime, 'ISO8601')

from Products.ExtFile import transaction

from ExtensionClass import Base
from OFS.SimpleItem import SimpleItem
from OFS.Folder import Folder

copymove_perms = ['Copy or Move', 'View management screens', 'Add Folders',
                  'Add Documents, Images, and Files', 'Delete objects']

# Use layer to set up ZCML
import layer


class HookCounter(Base):
    '''Logs calls to old-school hooks'''
    def __init__(self):
        self.reset()
    def reset(self):
        self.count = 0
        self.afterAdd = [0]
        self.afterClone = [0]
        self.beforeDelete = [0]
    def manage_afterAdd(self, item, container):
        self.count = self.count + 1
        self.afterAdd.append(self.count)
    def manage_afterClone(self, item):
        self.count = self.count + 1
        self.afterClone.append(self.count)
    def manage_beforeDelete(self, item, container):
        self.count = self.count + 1
        self.beforeDelete.append(self.count)
    def order(self):
        return self.afterAdd[-1], self.afterClone[-1], self.beforeDelete[-1]


class TestItem(HookCounter, SimpleItem):
    def __init__(self, id):
        HookCounter.__init__(self)
        self.id = id


class TestFolder(HookCounter, Folder):
    def __init__(self, id):
        HookCounter.__init__(self)
        self.id = id
    def _verifyObjectPaste(self, object, validate_src=1):
        # Don't verify pastes
        pass
    def manage_afterAdd(self, item, container):
        HookCounter.manage_afterAdd(self, item, container)
        Folder.manage_afterAdd(self, item, container)
    def manage_afterClone(self, item):
        HookCounter.manage_afterClone(self, item)
        Folder.manage_afterClone(self, item)
    def manage_beforeDelete(self, item, container):
        HookCounter.manage_beforeDelete(self, item, container)
        Folder.manage_beforeDelete(self, item, container)


class RecursingFolder(TestFolder):
    def manage_afterAdd(self, item, container):
        TestFolder.manage_afterAdd(self, item, container)
        self.__recurse('manage_afterAdd', item, container)
    def manage_afterClone(self, item):
        TestFolder.manage_afterClone(self, item)
        self.__recurse('manage_afterClone', item)
    def manage_beforeDelete(self, item, container):
        self.__recurse('manage_beforeDelete', item, container)
        TestFolder.manage_beforeDelete(self, item, container)
    def __recurse(self, name, *args):
        # Recurse like CMFCatalogAware
        for ob in self.objectValues():
            getattr(ob, name)(*args)


class TestCopySupport(ZopeTestCase.ZopeTestCase):
    '''Tests the order in which the add/clone/del hooks are called'''

    if layer.USELAYER:
        layer = layer.CopySupport

    def afterSetUp(self):
        # A folder that does not verify pastes
        self.folder._setObject('folder', TestFolder('folder'))
        self.folder = getattr(self.folder, 'folder')
        # The subfolder we are going to copy/move to
        self.folder._setObject('subfolder', TestFolder('subfolder'))
        self.subfolder = self.folder['subfolder']
        # The document we are going to copy/move
        self.folder._setObject('mydoc', TestItem('mydoc'))
        # Set some permissions
        self.setPermissions(copymove_perms)
        # Need _p_jars
        transaction.savepoint(1)
        # Reset counters
        self.folder.mydoc.reset()

    def test_1_Clone(self):
        # Test clone
        self.subfolder.manage_clone(self.folder.mydoc, 'yourdoc')
        self.assertEqual(self.subfolder.yourdoc.order(), (1, 2, 0))     # add, clone

    def test_2_CopyPaste(self):
        # Test copy/paste
        cb = self.folder.manage_copyObjects(['mydoc'])
        self.subfolder.manage_pasteObjects(cb)
        self.assertEqual(self.subfolder.mydoc.order(), (1, 2, 0))       # add, clone

    def test_3_CutPaste(self):
        # Test cut/paste
        cb = self.folder.manage_cutObjects(['mydoc'])
        self.subfolder.manage_pasteObjects(cb)
        self.assertEqual(self.subfolder.mydoc.order(), (2, 0, 1))       # del, add

    def test_4_Rename(self):
        # Test rename
        self.folder.manage_renameObject('mydoc', 'yourdoc')
        self.assertEqual(self.folder.yourdoc.order(), (2, 0, 1))        # del, add

    def test_5_COPY(self):
        # Test webdav COPY
        req = self.app.REQUEST
        req.environ['HTTP_DEPTH'] = 'infinity'
        req.environ['HTTP_DESTINATION'] = '%s/subfolder/mydoc' % self.folder.absolute_url()
        self.folder.mydoc.COPY(req, req.RESPONSE)
        if ZOPE274:
            self.assertEqual(self.subfolder.mydoc.order(), (1, 2, 0))   # add, clone
        else:
            self.assertEqual(self.subfolder.mydoc.order(), (2, 1, 0))   # clone, add

    def test_6_MOVE(self):
        # Test webdav MOVE
        req = self.app.REQUEST
        req.environ['HTTP_DEPTH'] = 'infinity'
        req.environ['HTTP_DESTINATION'] = '%s/subfolder/mydoc' % self.folder.absolute_url()
        old = self.folder.mydoc
        self.folder.mydoc.MOVE(req, req.RESPONSE)
        self.assertEqual(old.order(), (0, 0, 1))                        # del
        self.assertEqual(self.subfolder.mydoc.order(), (1, 0, 0))       # add

    def test_7_DELETE(self):
        # Test webdav DELETE
        req = self.app.REQUEST
        req['URL'] = '%s/mydoc' % self.folder.absolute_url()
        olddoc = self.folder.mydoc
        self.folder.mydoc.DELETE(req, req.RESPONSE)
        self.assertEqual(olddoc.order(), (0, 0, 1))                     # del


class TestCopySupportSublocation(ZopeTestCase.ZopeTestCase):
    '''Tests the order in which the add/clone/del hooks are called'''

    if layer.USELAYER:
        layer = layer.CopySupport

    def afterSetUp(self):
        # A folder that does not verify pastes
        self.folder._setObject('folder', TestFolder('folder'))
        self.folder = getattr(self.folder, 'folder')
        # The subfolder we are going to copy/move to
        self.folder._setObject('subfolder', TestFolder('subfolder'))
        self.subfolder = self.folder['subfolder']
        # The folder we are going to copy/move
        self.folder._setObject('myfolder', TestFolder('myfolder'))
        self.myfolder = self.folder['myfolder']
        # The "sublocation" inside our folder we are going to watch
        self.myfolder._setObject('mydoc', TestItem('mydoc'))
        # Set some permissions
        self.setPermissions(copymove_perms)
        # Need _p_jars
        transaction.savepoint(1)
        # Reset counters
        self.myfolder.reset()
        self.myfolder.mydoc.reset()

    def test_1_Clone(self):
        # Test clone
        self.subfolder.manage_clone(self.folder.myfolder, 'yourfolder')
        self.assertEqual(self.subfolder.yourfolder.order(), (1, 2, 0))          # add, clone
        self.assertEqual(self.subfolder.yourfolder.mydoc.order(), (1, 2, 0))    # add, clone

    def test_2_CopyPaste(self):
        # Test copy/paste
        cb = self.folder.manage_copyObjects(['myfolder'])
        self.subfolder.manage_pasteObjects(cb)
        self.assertEqual(self.subfolder.myfolder.order(), (1, 2, 0))            # add, clone
        self.assertEqual(self.subfolder.myfolder.mydoc.order(), (1, 2, 0))      # add, clone

    def test_3_CutPaste(self):
        # Test cut/paste
        cb = self.folder.manage_cutObjects(['myfolder'])
        self.subfolder.manage_pasteObjects(cb)
        self.assertEqual(self.subfolder.myfolder.order(), (2, 0, 1))            # del, add
        self.assertEqual(self.subfolder.myfolder.mydoc.order(), (2, 0, 1))      # del, add

    def test_4_Rename(self):
        # Test rename
        self.folder.manage_renameObject('myfolder', 'yourfolder')
        self.assertEqual(self.folder.yourfolder.order(), (2, 0, 1))             # del, add
        self.assertEqual(self.folder.yourfolder.mydoc.order(), (2, 0, 1))       # del, add

    def test_5_COPY(self):
        # Test webdav COPY
        req = self.app.REQUEST
        req.environ['HTTP_DEPTH'] = 'infinity'
        req.environ['HTTP_DESTINATION'] = '%s/subfolder/yourfolder' % self.folder.absolute_url()
        self.folder.myfolder.COPY(req, req.RESPONSE)
        if ZOPE274:
            self.assertEqual(self.subfolder.yourfolder.order(), (1, 2, 0))       # add, clone
            self.assertEqual(self.subfolder.yourfolder.mydoc.order(), (1, 2, 0)) # add, clone
        else:
            self.assertEqual(self.subfolder.yourfolder.order(), (2, 1, 0))       # clone, add
            self.assertEqual(self.subfolder.yourfolder.mydoc.order(), (2, 1, 0)) # clone, add

    def test_6_MOVE(self):
        # Test webdav MOVE
        req = self.app.REQUEST
        req.environ['HTTP_DEPTH'] = 'infinity'
        req.environ['HTTP_DESTINATION'] = '%s/subfolder/yourfolder' % self.folder.absolute_url()
        oldfolder = self.folder.myfolder
        olddoc = self.folder.myfolder.mydoc
        self.folder.myfolder.MOVE(req, req.RESPONSE)
        self.assertEqual(oldfolder.order(), (0, 0, 1))                          # del
        self.assertEqual(self.subfolder.yourfolder.order(), (1, 0, 0))          # add
        self.assertEqual(olddoc.order(), (0, 0, 1))                             # del
        self.assertEqual(self.subfolder.yourfolder.mydoc.order(), (1, 0, 0))    # add

    def test_7_DELETE(self):
        # Test webdav DELETE
        req = self.app.REQUEST
        req['URL'] = '%s/myfolder' % self.folder.absolute_url()
        oldfolder = self.folder.myfolder
        olddoc = self.folder.myfolder.mydoc
        self.folder.myfolder.DELETE(req, req.RESPONSE)
        self.assertEqual(oldfolder.order(), (0, 0, 1))                          # del
        self.assertEqual(olddoc.order(), (0, 0, 1))                             # del


class TestCopySupportSublocationWithRecurse(ZopeTestCase.ZopeTestCase):
    '''Tests the order in which the add/clone/del hooks are called'''

    if layer.USELAYER:
        layer = layer.CopySupport

    def afterSetUp(self):
        # A folder that does not verify pastes
        self.folder._setObject('folder', TestFolder('folder'))
        self.folder = getattr(self.folder, 'folder')
        # The subfolder we are going to copy/move to
        self.folder._setObject('subfolder', TestFolder('subfolder'))
        self.subfolder = self.folder['subfolder']
        # The folder we are going to copy/move
        self.folder._setObject('myfolder', RecursingFolder('myfolder'))
        self.myfolder = self.folder['myfolder']
        # The "sublocation" inside our folder we are going to watch
        self.myfolder._setObject('mydoc', TestItem('mydoc'))
        # Set some permissions
        self.setPermissions(copymove_perms)
        # Need _p_jars
        transaction.savepoint(1)
        # Reset counters
        self.myfolder.reset()
        self.myfolder.mydoc.reset()

    def test_1_Clone(self):
        # Test clone
        self.subfolder.manage_clone(self.folder.myfolder, 'yourfolder')
        self.assertEqual(self.subfolder.yourfolder.order(), (1, 2, 0))          # add, clone
        self.assertEqual(self.subfolder.yourfolder.mydoc.order(), (2, 4, 0))    # add, clone
        self.assertEqual(self.subfolder.yourfolder.mydoc.afterAdd, [0, 1, 2])
        self.assertEqual(self.subfolder.yourfolder.mydoc.afterClone, [0, 3, 4])

    def test_2_CopyPaste(self):
        # Test copy/paste
        cb = self.folder.manage_copyObjects(['myfolder'])
        self.subfolder.manage_pasteObjects(cb)
        self.assertEqual(self.subfolder.myfolder.order(), (1, 2, 0))            # add, clone
        self.assertEqual(self.subfolder.myfolder.mydoc.order(), (2, 4, 0))      # add, clone

    def test_3_CutPaste(self):
        # Test cut/paste
        cb = self.folder.manage_cutObjects(['myfolder'])
        self.subfolder.manage_pasteObjects(cb)
        self.assertEqual(self.subfolder.myfolder.order(), (2, 0, 1))            # del, add
        self.assertEqual(self.subfolder.myfolder.mydoc.order(), (4, 0, 2))      # del, add

    def test_4_Rename(self):
        # Test rename
        self.folder.manage_renameObject('myfolder', 'yourfolder')
        self.assertEqual(self.folder.yourfolder.order(), (2, 0, 1))             # del, add
        self.assertEqual(self.folder.yourfolder.mydoc.order(), (4, 0, 2))       # del, add

    def test_5_COPY(self):
        # Test webdav COPY
        req = self.app.REQUEST
        req.environ['HTTP_DEPTH'] = 'infinity'
        req.environ['HTTP_DESTINATION'] = '%s/subfolder/yourfolder' % self.folder.absolute_url()
        self.folder.myfolder.COPY(req, req.RESPONSE)
        if ZOPE274:
            self.assertEqual(self.subfolder.yourfolder.order(), (1, 2, 0))       # add, clone
            self.assertEqual(self.subfolder.yourfolder.mydoc.order(), (2, 4, 0)) # add, clone
            self.assertEqual(self.subfolder.yourfolder.mydoc.afterAdd, [0, 1, 2])
            self.assertEqual(self.subfolder.yourfolder.mydoc.afterClone, [0, 3, 4])
        else:
            self.assertEqual(self.subfolder.yourfolder.order(), (2, 1, 0))       # clone, add
            self.assertEqual(self.subfolder.yourfolder.mydoc.order(), (4, 2, 0)) # clone, add

    def test_6_MOVE(self):
        # Test webdav MOVE
        req = self.app.REQUEST
        req.environ['HTTP_DEPTH'] = 'infinity'
        req.environ['HTTP_DESTINATION'] = '%s/subfolder/yourfolder' % self.folder.absolute_url()
        oldfolder = self.folder.myfolder
        olddoc = self.folder.myfolder.mydoc
        self.folder.myfolder.MOVE(req, req.RESPONSE)
        self.assertEqual(oldfolder.order(), (0, 0, 1))                          # del
        self.assertEqual(self.subfolder.yourfolder.order(), (1, 0, 0))          # add
        self.assertEqual(olddoc.order(), (0, 0, 2))                             # del
        self.assertEqual(self.subfolder.yourfolder.mydoc.order(), (2, 0, 0))    # add

    def test_7_DELETE(self):
        # Test webdav DELETE
        req = self.app.REQUEST
        req['URL'] = '%s/myfolder' % self.folder.absolute_url()
        oldfolder = self.folder.myfolder
        olddoc = self.folder.myfolder.mydoc
        self.folder.myfolder.DELETE(req, req.RESPONSE)
        self.assertEqual(oldfolder.order(), (0, 0, 1))                          # del
        self.assertEqual(olddoc.order(), (0, 0, 2))                             # del


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCopySupport))
    suite.addTest(makeSuite(TestCopySupportSublocation))
    suite.addTest(makeSuite(TestCopySupportSublocationWithRecurse))
    return suite

if __name__ == '__main__':
    framework()

