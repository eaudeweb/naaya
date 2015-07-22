"""There are certain actions performed by users that need to be logged.
Actions such as ``Role requests``, support requests, etc.
This module implements a persistent container for logging this type of
actions for future reference. Usually this type of actions were just e-mail
notifications. Note that the container is not intended to be used as a logger
for all user actions. Some other storage methods should be researched for that.

Example usage::

    >>> from Products.Naaya.action_logger import ActionLogger
    >>> logger = ActionLogger()
    >>> logger.create(message="Some log")
    1
    >>> logger[1]
    <Products.Naaya.action_logger.ActionLogItem object at 0xb75bd6ec>
    >>> logger[1].message
    'Some log'


Database size: creating many records uses about 600 bytes for each record,
plus whatever is taken up by custom data added to the record. This is
counted after a pack; before packing, expect 3 or 4 times that size, because
of btree reshuffling overhead.
"""

from BTrees.IOBTree import IOBTree
from Persistence import Persistent
from DateTime import DateTime

from zope import interface
from interfaces import IActionLogItem, IActionLogger

class ActionLogger(Persistent):
    """ ``IActionLogItem`` container. This is used in `Products.Naaya.NySite`
    site manager."""

    interface.implements(IActionLogger)

    def __init__(self):
        super(ActionLogger, self).__init__()
        self.container = IOBTree()

    def append(self, log):
        """ Add an ``IActionLog``"""

        assert IActionLogItem in interface.providedBy(log), (
            "%s must implementation of IActionLogItem" % log)
        try:
            new_id = self.container.maxKey() + 1
        except ValueError:
            new_id = 1
        self.container[new_id] = log
        return new_id

    def create(self, **kw):
        """ Convenience function """

        log = ActionLogItem(**kw)
        return self.append(log)

    def items(self, type=None):
        """ Return container items filtered by type"""
        if type is None:
            return self.container.items()
        return filter(lambda (log_id, log): log.type == type,
                            self.container.items())

    def __iter__(self):
        return self.container.iteritems()

    def __getitem__(self, key):
        return self.container[key]

    def __delitem__(self, key):
        del self.container[key]

    def __len__(self):
        return len(self.container)

class ActionLogItem(Persistent):
    """ Action log base class"""

    interface.implements(IActionLogItem)

    def __init__(self, type=None, created_datetime=None, **kw):
        """ Type attribute is used to filter types of logs. """
        if created_datetime is None:
            created_datetime = DateTime()
        assert isinstance(created_datetime, DateTime)

        self.__dict__.update(kw)
        self.type = type
        self.created_datetime = created_datetime

    def __repr__(self):
        return u"<%s %r>" % (self.__class__.__name__, self.__dict__)
