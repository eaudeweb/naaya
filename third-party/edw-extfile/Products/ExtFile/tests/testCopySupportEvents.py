#
# Tests CopySupport events
#

from Testing import ZopeTestCase

from Products.ExtFile import testing
import transaction

from OFS.SimpleItem import SimpleItem
from OFS.Folder import Folder

from zope import interface

copymove_perms = ['Copy or Move', 'View management screens', 'Add Folders',
                  'Add Documents, Images, and Files', 'Delete objects']


class EventLogger(object):
    def __init__(self):
        self.reset()
    def reset(self):
        self._called = []
    def trace(self, ob, event):
        self._called.append((ob.getId(), event.__class__.__name__))
    def called(self):
        return self._called

eventlog = EventLogger()


class ITestItem(interface.Interface):
    pass

class TestItem(SimpleItem):
    interface.implements(ITestItem)
    def __init__(self, id):
        self.id = id


class ITestFolder(interface.Interface):
    pass

class TestFolder(Folder):
    interface.implements(ITestFolder)
    def __init__(self, id):
        self.id = id
    def _verifyObjectPaste(self, object, validate_src=1):
        pass # Always allow


class TestCopySupport(ZopeTestCase.ZopeTestCase):
    '''Tests the order in which events are fired'''

    layer = testing.EventLayer

    def afterSetUp(self):
        # A folder that does not verify pastes
        self.folder._setObject('folder', TestFolder('folder'))
        self.folder = getattr(self.folder, 'folder')
        # The subfolder we are going to copy/move to
        self.folder._setObject('subfolder', TestFolder('subfolder'))
        self.subfolder = getattr(self.folder, 'subfolder')
        # The document we are going to copy/move
        self.folder._setObject('mydoc', TestItem('mydoc'))
        # Set some permissions
        self.setPermissions(copymove_perms)
        # Need _p_jars
        transaction.savepoint(1)
        # Reset event log
        eventlog.reset()

    def test_1_Clone(self):
        # Test clone
        self.subfolder.manage_clone(self.folder.mydoc, 'mydoc')
        self.assertEqual(eventlog.called(),
            [('mydoc', 'ObjectCopiedEvent'),
             ('mydoc', 'ObjectWillBeAddedEvent'),
             ('mydoc', 'ObjectAddedEvent'),
             ('subfolder', 'ContainerModifiedEvent'),
             ('mydoc', 'ObjectClonedEvent')]
        )

    def test_2_CopyPaste(self):
        # Test copy/paste
        cb = self.folder.manage_copyObjects(['mydoc'])
        self.subfolder.manage_pasteObjects(cb)
        self.assertEqual(eventlog.called(),
            [('mydoc', 'ObjectCopiedEvent'),
             ('mydoc', 'ObjectWillBeAddedEvent'),
             ('mydoc', 'ObjectAddedEvent'),
             ('subfolder', 'ContainerModifiedEvent'),
             ('mydoc', 'ObjectClonedEvent')]
        )

    def test_3_CutPaste(self):
        # Test cut/paste
        cb = self.folder.manage_cutObjects(['mydoc'])
        self.subfolder.manage_pasteObjects(cb)
        self.assertEqual(eventlog.called(),
            [('mydoc', 'ObjectWillBeMovedEvent'),
             ('mydoc', 'ObjectMovedEvent'),
             ('folder', 'ContainerModifiedEvent'),
             ('subfolder', 'ContainerModifiedEvent')]
        )

    def test_4_Rename(self):
        # Test rename
        self.folder.manage_renameObject('mydoc', 'yourdoc')
        self.assertEqual(eventlog.called(),
            [('mydoc', 'ObjectWillBeMovedEvent'),
             ('yourdoc', 'ObjectMovedEvent'),
             ('folder', 'ContainerModifiedEvent')]
        )

    def test_5_COPY(self):
        # Test webdav COPY
        req = self.app.REQUEST
        req.environ['HTTP_DEPTH'] = 'infinity'
        req.environ['HTTP_DESTINATION'] = '%s/subfolder/mydoc' % self.folder.absolute_url()
        self.folder.mydoc.COPY(req, req.RESPONSE)
        self.assertEqual(eventlog.called(),
            [('mydoc', 'ObjectCopiedEvent'),
             ('mydoc', 'ObjectWillBeAddedEvent'),
             ('mydoc', 'ObjectAddedEvent'),
             ('subfolder', 'ContainerModifiedEvent'),
             ('mydoc', 'ObjectClonedEvent')]
        )

    def test_6_MOVE(self):
        # Test webdav MOVE
        req = self.app.REQUEST
        req.environ['HTTP_DEPTH'] = 'infinity'
        req.environ['HTTP_DESTINATION'] = '%s/subfolder/mydoc' % self.folder.absolute_url()
        self.folder.mydoc.MOVE(req, req.RESPONSE)
        self.assertEqual(eventlog.called(),
            [('mydoc', 'ObjectWillBeMovedEvent'),
             ('mydoc', 'ObjectMovedEvent'),
             ('folder', 'ContainerModifiedEvent'),
             ('subfolder', 'ContainerModifiedEvent')]
        )

    def test_7_DELETE(self):
        # Test webdav DELETE
        req = self.app.REQUEST
        req['URL'] = '%s/mydoc' % self.folder.absolute_url()
        self.folder.mydoc.DELETE(req, req.RESPONSE)
        self.assertEqual(eventlog.called(),
            [('mydoc', 'ObjectWillBeRemovedEvent'),
             ('mydoc', 'ObjectRemovedEvent'),
             ('folder', 'ContainerModifiedEvent')]
        )


class TestCopySupportSublocation(ZopeTestCase.ZopeTestCase):
    '''Tests the order in which events are fired'''

    layer = testing.EventLayer

    def afterSetUp(self):
        # A folder that does not verify pastes
        self.folder._setObject('folder', TestFolder('folder'))
        self.folder = getattr(self.folder, 'folder')
        # The subfolder we are going to copy/move to
        self.folder._setObject('subfolder', TestFolder('subfolder'))
        self.subfolder = getattr(self.folder, 'subfolder')
        # The folder we are going to copy/move
        self.folder._setObject('myfolder', TestFolder('myfolder'))
        self.myfolder = getattr(self.folder, 'myfolder')
        # The "sublocation" inside our folder we are going to watch
        self.myfolder._setObject('mydoc', TestItem('mydoc'))
        # Set some permissions
        self.setPermissions(copymove_perms)
        # Need _p_jars
        transaction.savepoint(1)
        # Reset event log
        eventlog.reset()

    def assertEqual(self, first, second, msg=None):
        # XXX: Compare sets as the order of event handlers cannot be
        #      relied on between objects.
        if not set(first) == set(second):
            raise self.failureException(
                (msg or '%r != %r' % (first, second)))

    def test_1_Clone(self):
        # Test clone
        self.subfolder.manage_clone(self.folder.myfolder, 'myfolder')
        self.assertEqual(eventlog.called(),
            [('myfolder', 'ObjectCopiedEvent'),
             ('mydoc', 'ObjectCopiedEvent'),
             ('myfolder', 'ObjectWillBeAddedEvent'),
             ('mydoc', 'ObjectWillBeAddedEvent'),
             ('myfolder', 'ObjectAddedEvent'),
             ('mydoc', 'ObjectAddedEvent'),
             ('subfolder', 'ContainerModifiedEvent'),
             ('myfolder', 'ObjectClonedEvent'),
             ('mydoc', 'ObjectClonedEvent')]
        )

    def test_2_CopyPaste(self):
        # Test copy/paste
        cb = self.folder.manage_copyObjects(['myfolder'])
        self.subfolder.manage_pasteObjects(cb)
        self.assertEqual(eventlog.called(),
            [('myfolder', 'ObjectCopiedEvent'),
             ('mydoc', 'ObjectCopiedEvent'),
             ('myfolder', 'ObjectWillBeAddedEvent'),
             ('mydoc', 'ObjectWillBeAddedEvent'),
             ('myfolder', 'ObjectAddedEvent'),
             ('mydoc', 'ObjectAddedEvent'),
             ('subfolder', 'ContainerModifiedEvent'),
             ('myfolder', 'ObjectClonedEvent'),
             ('mydoc', 'ObjectClonedEvent')]
        )

    def test_3_CutPaste(self):
        # Test cut/paste
        cb = self.folder.manage_cutObjects(['myfolder'])
        self.subfolder.manage_pasteObjects(cb)
        self.assertEqual(eventlog.called(),
            [('myfolder', 'ObjectWillBeMovedEvent'),
             ('mydoc', 'ObjectWillBeMovedEvent'),
             ('myfolder', 'ObjectMovedEvent'),
             ('mydoc', 'ObjectMovedEvent'),
             ('folder', 'ContainerModifiedEvent'),
             ('subfolder', 'ContainerModifiedEvent')]
        )

    def test_4_Rename(self):
        # Test rename
        self.folder.manage_renameObject('myfolder', 'yourfolder')
        self.assertEqual(eventlog.called(),
            [('myfolder', 'ObjectWillBeMovedEvent'),
             ('mydoc', 'ObjectWillBeMovedEvent'),
             ('yourfolder', 'ObjectMovedEvent'),
             ('mydoc', 'ObjectMovedEvent'),
             ('folder', 'ContainerModifiedEvent')]
        )

    def test_5_COPY(self):
        # Test webdav COPY
        req = self.app.REQUEST
        req.environ['HTTP_DEPTH'] = 'infinity'
        req.environ['HTTP_DESTINATION'] = '%s/subfolder/myfolder' % self.folder.absolute_url()
        self.folder.myfolder.COPY(req, req.RESPONSE)
        self.assertEqual(eventlog.called(),
            [('myfolder', 'ObjectCopiedEvent'),
             ('mydoc', 'ObjectCopiedEvent'),
             ('myfolder', 'ObjectWillBeAddedEvent'),
             ('mydoc', 'ObjectWillBeAddedEvent'),
             ('myfolder', 'ObjectAddedEvent'),
             ('mydoc', 'ObjectAddedEvent'),
             ('subfolder', 'ContainerModifiedEvent'),
             ('myfolder', 'ObjectClonedEvent'),
             ('mydoc', 'ObjectClonedEvent')]
        )

    def test_6_MOVE(self):
        # Test webdav MOVE
        req = self.app.REQUEST
        req.environ['HTTP_DEPTH'] = 'infinity'
        req.environ['HTTP_DESTINATION'] = '%s/subfolder/myfolder' % self.folder.absolute_url()
        self.folder.myfolder.MOVE(req, req.RESPONSE)
        self.assertEqual(eventlog.called(),
            [('myfolder', 'ObjectWillBeMovedEvent'),
             ('mydoc', 'ObjectWillBeMovedEvent'),
             ('myfolder', 'ObjectMovedEvent'),
             ('mydoc', 'ObjectMovedEvent'),
             ('folder', 'ContainerModifiedEvent'),
             ('subfolder', 'ContainerModifiedEvent')]
        )

    def test_7_DELETE(self):
        # Test webdav DELETE
        req = self.app.REQUEST
        req['URL'] = '%s/myfolder' % self.folder.absolute_url()
        self.folder.myfolder.DELETE(req, req.RESPONSE)
        self.assertEqual(eventlog.called(),
            [('myfolder', 'ObjectWillBeRemovedEvent'),
             ('mydoc', 'ObjectWillBeRemovedEvent'),
             ('myfolder', 'ObjectRemovedEvent'),
             ('mydoc', 'ObjectRemovedEvent'),
             ('folder', 'ContainerModifiedEvent')]
        )


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCopySupport))
    suite.addTest(makeSuite(TestCopySupportSublocation))
    return suite

