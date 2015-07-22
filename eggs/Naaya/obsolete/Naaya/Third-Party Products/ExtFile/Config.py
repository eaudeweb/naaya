#
# Configuration for the ExtFile/ExtImage filesystem repository
#

# Repository location and umask

REPOSITORY_PATH = ['var','files']  # Path to files below INSTANCE_HOME.
REPOSITORY_UMASK = 022


# Repository directory structure

FLAT = 0                # All files reside in a single directory.
SYNC_ZODB = 1           # Directories copy the ZODB folder structure.
SLICED = 2              # Sliced directories from ZOPEID.
SLICED_REVERSE = 3      # Sliced directories from reverse ZOPEID.
SLICED_HASH = 4         # Sliced directories from hash of ZOPEID.
CUSTOM = 5              # Call CUSTOM_METHOD to determine directories.
                        # The CUSTOM feature requires Zope >= 2.7.8.

REPOSITORY = SLICED_HASH

NORMALIZE = 0           # Normalize case of directory names.
KEEP = 1                # Keep case of directory names (backward compatibility).

NORMALIZE_CASE = KEEP

PHYSICAL = 0            # SYNC_ZODB uses physical path (recommended).
VIRTUAL = 1             # SYNC_ZODB uses path relative to virtual root (backward compatibility).

ZODB_PATH = VIRTUAL

SLICE_WIDTH = 1         # SLICED* uses this many characters per slice.
SLICE_DEPTH = 2         # SLICED* goes this many slices (directories) deep.

CUSTOM_METHOD = 'getExtFilePath'
                        # CUSTOM calls this method passing the object's path
                        # and ZOPEID as arguments (where path depends on
                        # the ZODB_PATH setting). The method must return a
                        # list of directory names.


# Repository file name handling

# %u=user, %p=path, %n=file name, %e=file extension, %c=counter, %t=time
FILE_FORMAT = "%n%c%e"

DISABLED = 0            # Allow file names to begin with 'copy_of_'.
ENABLED = 1             # Remove 'copy_of_' prefixes from file names.

COPY_OF_PROTECTION = ENABLED


# Repository file extension handling

ZOPEID = 0              # Use ZOPEID (even if it doesn't include an extension).
MIMETYPE_APPEND = 1     # Append extension to ZOPEID according to mimetype.
MIMETYPE_REPLACE = 2    # Remove extension from ZOPEID, then append mime extension.

REPOSITORY_EXTENSIONS = MIMETYPE_REPLACE


# Repository undo policy

BACKUP_ON_DELETE = 0    # Create a .undo copy only when a file is deleted.
ALWAYS_BACKUP = 1       # Create a .undo copy (and a new filename) whenever
                        # a file is uploaded or otherwise modified.

UNDO_POLICY = BACKUP_ON_DELETE

