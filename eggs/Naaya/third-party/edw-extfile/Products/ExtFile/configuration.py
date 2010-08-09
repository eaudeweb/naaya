
import os
import sys
import logging
import mimetypes
import ConfigParser

SITE_INI = os.path.join(INSTANCE_HOME, 'etc', 'extfile.ini')
EXAMPLE_INI = os.path.join(os.path.dirname(__file__), 'extfile.ini')

event_log = logging.getLogger('ExtFile')

# Legacy constants
FLAT = 0
SYNC_ZODB = 1
SLICED = 2
SLICED_REVERSE = 3
SLICED_HASH = 4
CUSTOM = 5
NORMALIZE = 0
KEEP = 1
PHYSICAL = 0
VIRTUAL = 1
DISABLED = 0
ENABLED = 1
ZOPEID = 0
MIMETYPE_APPEND = 1
MIMETYPE_REPLACE = 2
BACKUP_ON_DELETE = 0
ALWAYS_BACKUP = 1
NO_PREVIEW = 0
GENERATE = 1
UPLOAD_NORESIZE = 2
UPLOAD_RESIZE = 3


class Configuration(dict):

    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value

    def __init__(self):
        # Some defaults
        self.dirlock_sleep_seconds = 0.1
        self.dirlock_sleep_count = 10
        self.unknown_types = ('application/octet-stream', 'text/plain',
                              'text/x-unknown-content-type')
        self.load()

    def load(self):
        file = SITE_INI
        if not os.path.exists(file):
            file = EXAMPLE_INI

        event_log.info("Using configuration file %s", file)
        self.loadfile(file)

    def loadfile(self, file):
        global REPOSITORY_PATH, REPOSITORY_UMASK, REPOSITORY
        global NORMALIZE_CASE, ZODB_PATH, SLICE_WIDTH, SLICE_DEPTH
        global CUSTOM_METHOD, FILE_FORMAT, REPOSITORY_EXTENSIONS
        global COPY_OF_PROTECTION, UNDO_POLICY

        parser = ConfigParser.ConfigParser()
        parser.read(file)

        section = 'repository'
        self.location = filter(None, parser.get(section, 'location').replace('\\', '/').split('/'))
        self.umask = int(parser.get(section, 'umask'), 8)
        self.mode = parser.get(section, 'mode')
        self.case = parser.get(section, 'case')
        self.zodb_path = parser.get(section, 'zodb-path')
        self.slice_width = parser.getint(section, 'slice-width')
        self.slice_depth = parser.getint(section, 'slice-depth')
        self.custom_method = parser.get(section, 'custom-method')
        self.file_format = parser.get(section, 'file-format')
        self.extensions = parser.get(section, 'extensions')
        self.copy_of_protection = parser.get(section, 'copy-of-protection')
        self.undo_policy = parser.get(section, 'undo-policy')

        section = 'mimetypes'
        self.mimetypes_override_map = {}
        for type, ext in parser.items(section):
            type = type.lower()
            mimetypes.add_type(type, ext)
            self.mimetypes_override_map[type] = ext

        # This section is optional
        section = 'dirlock'
        if parser.has_section(section):
            for key, value in parser.items(section):
                if key == 'sleep-seconds':
                    self.dirlock_sleep_seconds = parser.getfloat(section, 'sleep-seconds')
                elif key == 'sleep-count':
                    self.dirlock_sleep_count = parser.getint(section, 'sleep-count')

        # Translate to legacy configuration
        REPOSITORY_PATH = self.location
        REPOSITORY_UMASK = self.umask

        if self.mode == 'flat':
            REPOSITORY = FLAT
        elif self.mode == 'sync-zodb':
            REPOSITORY = SYNC_ZODB
        elif self.mode == 'sliced':
            REPOSITORY = SLICED
        elif self.mode == 'sliced-reverse':
            REPOSITORY = SLICED_REVERSE
        elif self.mode == 'sliced-hash':
            REPOSITORY = SLICED_HASH
        elif self.mode == 'custom':
            REPOSITORY = CUSTOM

        if self.case == 'normalize':
            NORMALIZE_CASE = NORMALIZE
        elif self.case == 'keep':
            NORMALIZE_CASE = KEEP

        if self.zodb_path == 'physical':
            ZODB_PATH = PHYSICAL
        elif self.zodb_path == 'virtual':
            ZODB_PATH = VIRTUAL

        SLICE_WIDTH = self.slice_width
        SLICE_DEPTH = self.slice_depth
        CUSTOM_METHOD = self.custom_method
        FILE_FORMAT = self.file_format

        if self.extensions == 'zope-id':
            REPOSITORY_EXTENSIONS = ZOPEID
        elif self.extensions == 'mimetype-append':
            REPOSITORY_EXTENSIONS = MIMETYPE_APPEND
        elif self.extensions == 'mimetype-replace':
            REPOSITORY_EXTENSIONS = MIMETYPE_REPLACE

        if self.copy_of_protection == 'protect':
            COPY_OF_PROTECTION = ENABLED
        elif self.copy_of_protection == 'allow':
            COPY_OF_PROTECTION = DISABLED

        if self.undo_policy == 'backup-on-delete':
            UNDO_POLICY = BACKUP_ON_DELETE
        elif self.undo_policy == 'always-backup':
            UNDO_POLICY = ALWAYS_BACKUP


config = Configuration()
load = config.load
loadfile = config.loadfile

