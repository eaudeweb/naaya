""" Remove .undo files from disk. Use with zope pack
"""
import os
import sys
import logging
from threading import Thread

# Config custom logger
LOG_ROOT = os.path.join(os.environ['CLIENT_HOME'], 'log')
if not os.path.isdir(LOG_ROOT):
    os.mkdir(LOG_ROOT)
LOG_FILE = os.path.join(LOG_ROOT, 'packing.log')

logging.basicConfig()
_handler = logging.FileHandler(LOG_FILE)
_formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
_handler.setFormatter(_formatter)

logger = logging.getLogger('naayaHotfix.extfile_pack')
logger.setLevel(logging.DEBUG)
logger.handlers = [_handler]
logger.propagate = 0

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
        new_fname = fname.replace('.undo', '.old')
        new_path = os.path.join(dirname, new_fname)
        try:
            os.rename(path, new_path)
        except Exception, err:
            logger.debug('[RENAME ERROR] %s %s => %s', err, path, new_path)
            continue
        else:
            logger.debug('[RENAME OK] %s => %s', path, new_path)

def pack_disk(path):
    logger.debug('Disk pack started')
    extpack = ExtFilePack(path)
    extpack.start()
    extpack.join()
    return "Disk pack started"
