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
