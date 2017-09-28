import Queue
from Queue import Full, Empty

class SharedSet(Queue.Queue):
    """ This extends Queue.Queue BUT breaks its contract of defined order !!
    The elements in this collection, while benefiting from locking and timeouts
    as Queue.Queue, unlike it, will get elements in random order."""
    def _init(self, maxsize):
        self.queue = set()

    def _get(self):
        return self.queue.pop()

    def _put(self, item):
        self.queue.add(item)

    def __init__(self, maxsize=0):
        Queue.Queue.__init__(self, maxsize)

