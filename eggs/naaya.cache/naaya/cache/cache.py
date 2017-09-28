""" Naaya cache module based on plone.memoize """

import time

from plone.memoize import ram, volatile


class SelfClearingRAMCacheAdapter(ram.RAMCacheAdapter):
    """
    Constructing the key based on time is not enough; we also have to
    clear the old values, to free up the memory.
    Since we can't change the maxAge for global Zope RAMCache,
    we are going to store a cleanup timestamp in the cache itself,
    and check it on each new cache write.

    We could use a local RAMCache, but plone.memoize only let's you
    negotiate it based on function you are going to use it for,
    which is not helpful for general use.

    """

    def __init__(self, ramcache, globalkey, cleanup_interval=84600):
        self.cleanup_interval = cleanup_interval
        self.last_cleanup = time.time()
        ram.RAMCacheAdapter.__init__(self, ramcache, globalkey)

    def __setitem__(self, key, value):
        last_cleanup = self.ramcache.query(self.globalkey, {'key': "last-cleanup"}, 0)
        not_cleaned_for = time.time() - last_cleanup
        if not_cleaned_for >= self.cleanup_interval:
            self.ramcache.invalidate(self.globalkey)
            self.ramcache.set(time.time(), self.globalkey, key={'key': "last-cleanup"})
        ram.RAMCacheAdapter.__setitem__(self, key, value)

def store_in_cache_with_timeout(timeout):
    def store_in_cache(fun, *args, **kwargs):
        key = '%s.%s' % (fun.__module__, fun.__name__)
        return SelfClearingRAMCacheAdapter(ram.global_cache, key, timeout)
    return store_in_cache

def timed(timeout):
    def get_timed_key(func, *args, **kw):
        key = (args, frozenset(kw.items()), time.time() // timeout)
        return key
    return volatile.cache(get_timed_key,
                          get_cache=store_in_cache_with_timeout(timeout))
