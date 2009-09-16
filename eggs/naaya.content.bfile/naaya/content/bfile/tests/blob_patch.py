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
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alex Morega, Eau de Web


"""
patch ZopeTestCase to use blob storage
"""

import tempfile, shutil, atexit
from ZODB.DB import DB
from ZODB.blob import BlobStorage

blob_dir = tempfile.mkdtemp()
print "NAAYA BLOB: monkey-patching ZODB; using temp folder:", blob_dir
orig__init__ = DB.__init__
def new__init__(self, storage, *args, **kwargs):
    storage = BlobStorage(blob_dir, storage)
    orig__init__(self, storage, *args, **kwargs)
DB.__init__ = new__init__

def cleanup_blob_dir(*args, **kwargs):
    print "NAAYA BLOB: cleaning up temp folder", blob_dir
    shutil.rmtree(blob_dir)
atexit.register(cleanup_blob_dir)
