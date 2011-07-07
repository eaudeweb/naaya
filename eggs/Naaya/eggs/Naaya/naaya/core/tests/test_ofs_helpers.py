import unittest
from mock import Mock
from zope import interface
from OFS.SimpleItem import SimpleItem
from OFS.Folder import Folder

class OfsHelpersTest(unittest.TestCase):

    def test_walk_basic(self):
        from naaya.core.zope2util import ofs_walk
        fol = Folder('fol').__of__(Folder('root'))

        self.assertEqual(list(ofs_walk(fol)), [])

        item = SimpleItem('item')
        fol._setObject('item', item)
        self.assertEqual(list(ofs_walk(fol)), [item])

        fol2 = Folder('fol2')
        fol._setObject('fol2', fol2)
        self.assertEqual(list(ofs_walk(fol)), [item, fol2])

        item2 = SimpleItem('item2')
        fol2._setObject('item2', item2)
        self.assertEqual(list(ofs_walk(fol)), [item, fol2, item2])

    def test_restrict_output(self):
        from naaya.core.zope2util import ofs_walk
        fol = Folder('fol').__of__(Folder('root'))
        fol2 = Folder('fol2')
        item = SimpleItem('item')
        fol._setObject('item', item)
        fol._setObject('fol2', fol2)
        class IMyItem(interface.Interface): pass
        class IMyItem2(interface.Interface): pass

        # we call with 2 interfaces to make sure "OR" logic is applied
        walk = lambda: list(ofs_walk(fol, [IMyItem, IMyItem2]))

        self.assertEqual(walk(), [])

        interface.alsoProvides(item, IMyItem)
        self.assertEqual(walk(), [item])

        interface.alsoProvides(fol2, IMyItem)
        self.assertEqual(walk(), [item, fol2])

    def test_restrict_traversal(self):
        from naaya.core.zope2util import ofs_walk
        fol = Folder('fol').__of__(Folder('root'))
        fol2 = Folder('fol2')
        item = SimpleItem('item')
        item2 = SimpleItem('item2')
        fol._setObject('item', item)
        fol._setObject('fol2', fol2)
        fol2._setObject('item2', item2)
        class IMyContainer(interface.Interface): pass
        class IMyCont2(interface.Interface): pass

        # we call with 2 interfaces to make sure "OR" logic is applied
        walk = lambda: list(ofs_walk(fol, containers=[IMyContainer, IMyCont2]))

        self.assertEqual(walk(), [item, fol2])

        interface.alsoProvides(fol2, IMyContainer)
        self.assertEqual(walk(), [item, fol2, item2])

    def test_always_traverse_root(self):
        from naaya.core.zope2util import ofs_walk
        fol = Folder('fol').__of__(Folder('root'))
        fol2 = Folder('fol2')
        item = SimpleItem('item')
        item2 = SimpleItem('item2')
        fol._setObject('item', item)
        fol._setObject('fol2', fol2)
        fol2._setObject('item2', item2)

        self.assertEqual(list(ofs_walk(fol, containers=[])), [item, fol2])
