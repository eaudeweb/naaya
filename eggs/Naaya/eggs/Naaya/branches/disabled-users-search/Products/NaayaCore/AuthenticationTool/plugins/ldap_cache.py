import logging
from time import time
import cPickle as pickle
from zope.component import queryUtility

log = logging.getLogger('naaya.core.auth.ldap')
_raise_if_not_found = object()

class Cache(object):
    """
    Store LDAP user information in-memory for quick access.

    Data is stored in a `dict` keyed by user DN (the complete ID of the
    user's LDAP record). Values are pickles of dictionaries containing a
    user's information and are unpickled on demand. This is done to save
    memory.
    """

    def __init__(self):
        self.timestamp = None
        self.users = {}
        self._last_update = None

    def _store_dump(self, dump_stream):
        users = dict( (dn, pickle.dumps(record, pickle.HIGHEST_PROTOCOL))
                      for (dn, record) in dump_stream )
        self.users = users

    def update(self):
        """
        Update the LDAP cache.

        First make sure we're not called more often than 8 minutes. Then
        see if the `naaya.ldapdump` datastore is present. If so, ask for
        the timestamp of the most recent dump, and if it's newer than
        what we have, load it.
        """
        now = time()
        if now - (60*8) < self._last_update: # 8 minute cooldown
            return
        self._last_update = now

        try:
            from naaya.ldapdump.interfaces import IDumpReader
        except ImportError:
            return
        dump_reader = queryUtility(IDumpReader, default=None)
        if dump_reader is None:
            return

        timestamp = dump_reader.latest_timestamp()
        if not (timestamp > self.timestamp):
            return

        log.debug("fetching ldap user dump, timestamp is %s ...", timestamp)

        time0 = time()
        self._store_dump(dump_reader.get_dump())
        self.timestamp = timestamp

        log.info("got ldap users dump: %d records, %.3f seconds",
                  len(self.users), (time() - time0))

    def get(self, user_dn, default=_raise_if_not_found):
        """
        Retrieve a record from this cache. Raises KeyError if record not found.
        """
        if self.timestamp is None:
            try:
                self.update()
            except Exception, e:
                log.exception("Update failed for empty cache")
                # behave as cache miss
                if default is _raise_if_not_found:
                    raise
                else:
                    return default

        try:
            record = self.users[user_dn]
        except KeyError:
            if default is _raise_if_not_found:
                raise
            else:
                return default
        else:
            return pickle.loads(record)

    def has(self, user_dn):
        """ Check if the cache has a record for the specified `user_dn` """
        if self.timestamp is None:
            self.update()

        return user_dn in self.users

_cache = Cache()
get = _cache.get
has = _cache.has

def update(*args):
    """ event handler that updates the ldap user cache """
    try:
        _cache.update()
    except:
        log.exception("Error when trying to update the LDAP user cache")
