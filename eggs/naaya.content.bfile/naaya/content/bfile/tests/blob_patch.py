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

import tempfile
import shutil

import Globals
from ZODB.blob import BlobStorage

def patch_testing_db():
    # first, make sure the DB has been set up
    from Testing import ZopeTestCase

    # then, patch it
    db = Globals.DB
    orig_storage = db._storage
    blob_dir = tempfile.mkdtemp()
    db._storage = BlobStorage(blob_dir, orig_storage)

    # provide a cleanup function, return it as callback
    def cleanup():
        db._storage = orig_storage
        shutil.rmtree(blob_dir)

    return cleanup
