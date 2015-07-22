"""
TMRegistry and ProxyTM

Use case
--------

Persistent objects (ExtFiles) need to participate in ZODB transactions.
ExtFiles perform all operations using temporary files which are saved on
commit or deleted on abort.

Constraints
-----------

- TransactionManagers (TM) must not be persistent themselves, i.e. must
  not have a _p_jar attribute.

- We have to make sure the ExtFile's _abort is called *before* the ZODB
  destroys the attributes of the persistent object.

Solution
--------

- ProxyTM is a subclass of TM.TM that keeps a (hard) reference to the
  (wrapped) persistent object it manages. Calls to _begin, _finish, and
  _abort are forwarded to the target object.

- TMRegistry is a module-level container for ProxyTMs. It creates and
  holds ProxyTMs keyed by (target_id, thread_id).

- ExtFiles implement _finish and _abort and register with the machinery
  by calling TM.register(self).

- On commit (or abort) the ProxyTM notifies its target object and removes
  itself from the registry.

Hacks
-----

- We manipulate the transaction's _resources attribute directly. This is
  to guarantee the ProxyTM is processed before other resources. There may
  be a way to achieve this using official APIs only, but I can't seem to
  find one.

"""

from Shared.DC.ZRDB.TM import TM
from Acquisition import aq_base
from thread import get_ident
from Products.ExtFile import transaction


class TMRegistry:

    def __init__(self):
        self._tms = {}

    def getid(self, target):
        return (id(aq_base(target)), get_ident())

    def register(self, target):
        if not self.contains(target):
            id = self.getid(target)
            tm = ProxyTM(target)
            tm._register()
            self._tms[id] = tm
            return 1
        return 0

    def remove(self, target):
        if self.contains(target):
            id = self.getid(target)
            del self._tms[id]
            return 1
        return 0

    def contains(self, target):
        id = self.getid(target)
        return self._tms.has_key(id)

    def get(self, target):
        id = self.getid(target)
        return self._tms.get(id)

    def __len__(self):
        return len(self._tms)

    def count(self):
        return len(self)


class ProxyTM(TM):

    def __init__(self, target):
        self._target = target

    def _register(self):
        TM._register(self)
        # XXX Make sure we are called before the
        # persistent ExtFile object is destroyed.
        t = transaction.get()
        if hasattr(t, '_resources'):
            r = t._resources.pop()
            t._resources.insert(0, r)

    def _begin(self):
        return self._target._begin()

    def _finish(self):
        if registry.remove(self._target):
            return self._target._finish()

    def _abort(self):
        if registry.remove(self._target):
            return self._target._abort()


registry = TMRegistry()
register = registry.register
remove = registry.remove
contains = registry.contains
count = registry.count

