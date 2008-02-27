#
# Tests TMRegistry and ProxyTM
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

from OFS.SimpleItem import SimpleItem
from Products.ExtFile import transaction
from Products.ExtFile.TM import TMRegistry, registry
from Products.ExtFile.TM import ProxyTM


class Target(SimpleItem):
    begin_called = 0
    finish_called = 0
    abort_called = 0
    def _begin(self):
        self.begin_called = 1
    def _finish(self):
        self.finish_called = 1
    def _abort(self):
        self.abort_called = 1

def tr():
    t = transaction.get()
    if hasattr(t, '_objects'):
        return t._objects   # ZODB <= 3.2
    elif hasattr(t, '_resources'):
        return t._resources # ZODB >= 3.4


class TestTMRegistry(ZopeTestCase.TestCase):

    def afterSetUp(self):
        self.reg = TMRegistry()

    def testRegister(self):
        self.assertEqual(len(self.reg), 0)
        self.reg.register(Target())
        self.assertEqual(len(self.reg), 1)
        self.reg.register(Target())
        self.assertEqual(len(self.reg), 2)

    def testCount(self):
        self.assertEqual(self.reg.count(), 0)
        self.reg.register(Target())
        self.assertEqual(self.reg.count(), 1)
        self.reg.register(Target())
        self.assertEqual(self.reg.count(), 2)

    def testContains(self):
        target1, target2 = Target(), Target()
        self.reg.register(target1)
        self.reg.register(target2)
        self.failUnless(self.reg.contains(target1))
        self.failUnless(self.reg.contains(target2))

    def testRemove(self):
        target1, target2 = Target(), Target()
        self.reg.register(target1)
        self.reg.register(target2)
        self.reg.remove(target1)
        self.reg.remove(target2)
        self.failIf(self.reg.contains(target1))
        self.failIf(self.reg.contains(target2))

    def testGet(self):
        target1 = Target()
        self.reg.register(target1)
        tm = self.reg.get(target1)
        self.failUnless(isinstance(tm, ProxyTM))
        self.assertEqual(target1, tm._target)


class TestProxyTM(ZopeTestCase.Sandboxed, ZopeTestCase.TestCase):

    def testRegister(self):
        tm = ProxyTM(Target())
        self.assertEqual(len(tr()), 0)
        tm._register()
        self.assertEqual(len(tr()), 1)
        try:
            self.assertEqual(tr()[0].manager, tm)
        except AttributeError:
            pass # ZODB <= 3.2

    def testLastRegisteredComesFirst(self):
        tm1, tm2 = ProxyTM(Target()), ProxyTM(Target())
        tm1._register()
        tm2._register()
        self.assertEqual(len(tr()), 2)
        # Now make sure that tm2 comes first in the
        # transaction's _resources list
        try:
            self.assertEqual(tr()[0].manager, tm2)
            self.assertEqual(tr()[1].manager, tm1)
        except AttributeError:
            pass # ZODB <= 3.2

    def testBeginIsForwarded(self):
        target = Target()
        registry.register(target)
        tm = registry.get(target)
        tm._begin()
        self.failUnless(target.begin_called)

    def testFinishIsForwarded(self):
        target = Target()
        registry.register(target)
        tm = registry.get(target)
        tm._finish()
        self.failUnless(target.finish_called)
        # _finish removes the TM from the registry
        self.failIf(registry.contains(target))

    def testAbortIsForwarded(self):
        target = Target()
        registry.register(target)
        tm = registry.get(target)
        tm._abort()
        self.failUnless(target.abort_called)
        # _abort removes the TM from the registry
        self.failIf(registry.contains(target))

    def testCommitCallsFinish(self):
        target = Target()
        registry.register(target)
        transaction.commit()
        self.failUnless(target.finish_called)
        # _finish removes the TM from the registry
        self.failIf(registry.contains(target))

    def testAbortCallsAbort(self):
        target = Target()
        registry.register(target)
        transaction.abort()
        self.failUnless(target.abort_called)
        # _abort removes the TM from the registry
        self.failIf(registry.contains(target))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTMRegistry))
    suite.addTest(makeSuite(TestProxyTM))
    return suite

if __name__ == '__main__':
    framework()

