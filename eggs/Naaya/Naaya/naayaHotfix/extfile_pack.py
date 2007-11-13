# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
# Alin Voinea, Eau de Web
""" Remove .undo files from disk. Use with zope pack
"""
import os
import sys
from threading import Thread
from Globals import INSTANCE_HOME

class ExtFilePack(Thread):
    """ Media Converter
    """
    def __init__(self, path):
        self._path = path
        Thread.__init__(self)

    def pack(self):
        """ os.walk in path and remove all .undo files"""
        os.path.walk(self._path, _pack, None)
        
    def run(self):
        """ Run pack"""
        return self.pack()

def _pack(arg, dirname, fnames):
    """ Use with os.path.walk to remove .undo files from disk."""
    for fname in fnames:
        if not fname.endswith(".undo"):
            continue
        path = os.path.join(dirname, fname)
        try:
            os.unlink(path)
        except OSError:
            continue

def pack_disk(path):
    extpack = ExtFilePack(path)
    extpack.start()
    extpack.join()
    return "Disk pack started"
