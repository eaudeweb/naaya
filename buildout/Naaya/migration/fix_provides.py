"""
Strip broken __provides__ from all persistent objects in a ZODB Data.fs.

After a Python 2 -> Python 3 migration, pickled __provides__ attributes
may reference old-style classes (ExtensionClass) that zope.interface can't
handle. The declaration is rebuilt with only the marker interfaces (e.g. ISite).

Requires the patched zope.interface._normalizeargs (try/except TypeError)
so that objects with broken __provides__ can actually be loaded.

Usage:
    parts/circa/bin/interpreter fix_provides.py
"""

import logging
import transaction
import ZODB.FileStorage
import ZODB
from ZODB.serialize import ObjectWriter
from ZODB.utils import u64
from zope.interface import alsoProvides, directlyProvidedBy, implementedBy
from zope.interface.interface import InterfaceClass

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def marker_interfaces(obj):
    """Directly provided interfaces not implemented by the class (e.g. ISite)."""
    implemented = implementedBy(type(obj))
    return [iface for iface in directlyProvidedBy(obj).interfaces()
            if isinstance(iface, InterfaceClass)
            and not implemented.isOrExtends(iface)]


def fix_provides(datafs_path):
    storage = ZODB.FileStorage.FileStorage(datafs_path)
    db = ZODB.DB(storage)
    conn = db.open()
    root = conn.root()

    count = 0
    fixed = 0
    errors = 0
    skipped = []

    # Walk all objects reachable from root using ZODB's internal iteration
    # Use storage-level iteration to find all oids
    from ZODB.utils import p64
    next_oid = b'\x00' * 8
    while True:
        try:
            oid, tid, data, prev = storage.record_iternext(next_oid)
        except (TypeError, ValueError):
            break

        next_oid = p64(u64(oid) + 1)
        count += 1

        if count % 10000 == 0:
            logger.info(f"  Scanned {count} objects, fixed {fixed}, "
                        f"errors {errors}...")

        # Quick check: skip if no __provides__ in raw data
        if b'__provides__' not in data:
            continue

        # Try to load the object and remove __provides__
        try:
            obj = conn.get(oid)
            # Force loading the object state
            obj._p_activate()

            if '__provides__' in obj.__dict__:
                markers = marker_interfaces(obj)
                del obj.__provides__
                if markers:
                    alsoProvides(obj, *markers)
                obj._p_changed = True
                try:
                    ObjectWriter(obj).serialize(obj)
                except Exception as e:
                    # Other attributes refer to missing classes; leave it to migrate_zodb.py
                    obj._p_changed = False
                    obj._p_invalidate()
                    skipped.append(f'{u64(oid):#x} '
                                   f'({obj.__class__.__module__}.'
                                   f'{obj.__class__.__name__}): {e}')
                    continue
                fixed += 1
                if fixed <= 5 or markers:
                    oid_hex = f'{u64(oid):#x}'
                    logger.info(f"  Fixed oid {oid_hex} "
                                f"({obj.__class__.__module__}."
                                f"{obj.__class__.__name__}) kept "
                                f"{[i.__identifier__ for i in markers]}")
        except Exception as e:
            errors += 1
            if errors <= 5:
                oid_hex = f'{u64(oid):#x}'
                logger.info(f"  Error loading oid {oid_hex}: {e}")

        # Commit in batches to avoid excessive memory use
        if fixed > 0 and fixed % 500 == 0:
            logger.info(f"  Committing batch ({fixed} fixed so far)...")
            transaction.get().note('Strip broken __provides__ for Py3 migration')
            transaction.commit()

    # Final commit
    if fixed > 0:
        logger.info(f"  Final commit...")
        transaction.get().note('Strip broken __provides__ for Py3 migration')
        transaction.commit()

    logger.info(f"Done. Scanned {count} objects, "
                f"fixed {fixed}, errors {errors}, skipped {len(skipped)}.")
    for line in skipped:
        logger.info(f"  Skipped {line}")
    conn.close()
    db.close()


if __name__ == '__main__':
    import sys
    datafs = sys.argv[1]
    logger.info(f"Fixing __provides__ in {datafs}")
    fix_provides(datafs)
