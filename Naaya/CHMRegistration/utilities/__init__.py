import os
import tempfile
import csv

from AccessControl import getSecurityManager

class tmpfile:

    def __init__(self, data):
        self.fname = tempfile.mktemp()
        writer = csv.writer(open(self.fname,'wb'))
        for row in data:
            writer.writerow(row)

    def __str__(self): return self.fname
    __repr__ = __str__

    def __del__(self):
        os.unlink(self.fname)


def checkPermission(permission, object):
    """  Generic function to check a given permission on the current object. """
    return getSecurityManager().checkPermission(permission, object)