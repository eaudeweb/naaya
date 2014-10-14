""" Naaya updater script """
__author__ = """Tiberiu Ichim"""

from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from StringIO import StringIO
import logging
import mimetypes
import os


class UpdateFixNyBlobFile(UpdateScript):
    """ Fix NyBloBFiles """
    title = 'Fix NyBlobFiles'
    creation_date = 'Oct 13, 2014'
    authors = ['Tiberiu Ichim']
    priority = PRIORITY['HIGH']
    description = ('Fix Blobs for NyBlobFiles')

    log = logging.getLogger('naaya.updater.fix_nyblobs')

    def get_content(self, folder, filename):
        path = os.path.join(folder, filename)
        with open(path) as f:
            content = f.read()
        sfile = StringIO(content)
        sfile.filename = filename
        try:
            ct = mimetypes.guess_type(filename)[0]
            if ct:
                sfile.headers = {'content-type': ct}
        except:
            self.log.info("Could not guess content type for %r", filename)

    def fix(self, obj):
        base = "/var/local/chmfiles/var/local/chm/var/files"
        relpath = obj.getPhysicalPath()[1:]
        abspath = os.path.join(base, '/'.join(relpath))
        if not os.path.exists(abspath):
            return

        versions = [f for f in os.listdir(abspath) if not f.endswith('.undo')]

        if len(versions) > 1:
            self.log.info("Skipping %s, too many files", obj.absolute_url())
            return

        for fname in versions:
            content = self.get_content(abspath, fname)
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
