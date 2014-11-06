""" Naaya updater script """
__author__ = """Tiberiu Ichim"""

from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from StringIO import StringIO
from os.path import join, isfile, isdir, exists
import hashlib
import logging
import mimetypes
import os
import re

finder = re.compile('.*\.(\d+)\.*.*$')
inter  = lambda x:int((finder.findall(x) or ['0'])[0])
sorter = lambda x, y:cmp(inter(x), inter(y))


def hashfile(fpath, blocksize=65536):
    hasher = hashlib.md5()
    with open(fpath) as afile:
        buf = afile.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(blocksize)
    return hasher.digest()


class UpdateFixNyBlobFile(UpdateScript):
    """ Fix NyBloBFiles """
    title = 'Fix NyBlobFiles'
    creation_date = 'Oct 13, 2014'
    authors = ['Tiberiu Ichim']
    priority = PRIORITY['HIGH']
    description = ('Fix Blobs for NyBlobFiles')

    log = logging.getLogger('naaya.updater.fix_nyblobs')

    def get_content(self, folder, filename):
        path = join(folder, filename)
        with open(path) as f:
            content = f.read()
        sfile = StringIO(content)
        if filename.endswith('.undo'):
            filename = filename[:-5]
        sfile.filename = filename
        try:
            ct = mimetypes.guess_type(filename)[0]
            if ct:
                sfile.headers = {'content-type': ct}
        except:
            self.log.warning("Could not guess content type for %r", filename)
        return sfile

    def fix(self, obj):
        base = "/var/local/chmfiles/var/local/chm/var/files"
        relpath = obj.getPhysicalPath()[1:]
        abspath = join(base, '/'.join(relpath))
        if not exists(abspath):
            # try to see if the lowercase version exists
            cp = list(relpath)
            cp[-1] = cp[-1].lower()
            abspath = join(base, '/'.join(cp))
            if not exists(abspath):
                self.log.warning("Could not find path %r for %r", abspath, obj.absolute_url())
                return

        #versions = [f for f in os.listdir(abspath) if not f.endswith('.undo')]
        # We treat .undo files the same way extfile does, which is to take it into consideration
        # if not other file is found there
        site_lang = obj.getSite().gl_get_default_language()

        versions = [(abspath, f) for f in os.listdir(abspath)
                            if isfile(join(abspath, f))]

        lang_counter = 0
        for lang in obj.getSite().gl_get_languages():
            lpath = join(abspath, lang)
            if exists(lpath) and isdir(lpath):
                lang_counter += 1
                versions.extend([(lpath, f) for f in os.listdir(lpath)
                                if isfile(join(lpath, f))])

        if len(versions) > 1:
            # see if the files have the same content, in which
            # case we can upload one version of that file
            hashes = set([hashfile(join(fpath, filename))
                                for (fpath, filename) in versions])
            if len(hashes) == 1:
                versions = versions[:1]
            else:
                # we try take the file for the main language
                lang_path = join(abspath, site_lang)
                if os.path.exists(lang_path):
                    versions = [(lang_path, f) for f in os.listdir(lang_path)
                                    if isfile(join(lang_path, f))]
                    if len(versions) > 1:
                        hashes = set([hashfile(join(fpath, filename))
                                            for (fpath, filename) in versions])
                        if len(hashes) == 1:
                            versions = versions[:1]
                        else:
                            # TODO: take files from here
                            if len(lang_counter) == 1:
                                _versions = sorted(versions, sorter)
                                for fpath, filename in _versions:
                                    content = self.get_content(fpath, filename)
                                    obj._save_file(content, contributor='')
                                    self.log.info("Added a file for %r", obj.absolute_url())
                                return
                            self.log.warning("Skipping %s, too many files", obj.absolute_url())
                            return
                    self.log.info("Using the files from the default language path %s", site_lang)
                else:
                    # TODO: take files from here
                    # add the versions for each file
                    # order the files by version

                    self.log.warning("Skipping %s, too many files", obj.absolute_url())
                    return

        for fpath, filename in versions:
            content = self.get_content(fpath, filename)
            obj._save_file(content, contributor='')
            self.log.info("Added a file for %r", obj.absolute_url())

    def _update(self, portal):
        """ Run updater
        """

        ctool = portal.portal_catalog
        brains = set(ctool(meta_type='Naaya Blob File'))

        self.log.debug('Updating %s files in %s',
                       len(brains), portal.absolute_url(1))

        for brain in brains:
            doc = brain.getObject()
            if len(doc._versions) > 0:
                continue
            self.log.debug('Fixing file: %s' % doc.absolute_url(1))
            self.fix(doc)

        return True
