import queue
from queue import Full, Empty

class SharedSet(queue.Queue):
    """ This extends queue.Queue BUT breaks its contract of defined order !!
    The elements in this collection, while benefiting from locking and timeouts
    as queue.Queue, unlike it, will get elements in random order."""
    def _init(self, maxsize):
        self.queue = set()

    def _get(self):
        return self.queue.pop()

    def _put(self, item):
        self.queue.add(item)

    def __init__(self, maxsize=0):
        queue.Queue.__init__(self, maxsize)
