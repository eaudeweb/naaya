""" Naaya updater script """
__author__ = """Tiberiu Ichim"""

from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from StringIO import StringIO
import logging
import os


class UpdateFixNyBlobFile(UpdateScript):
    """ Fix NyBloBFiles """
    title = 'Fix NyBlobFiles'
    creation_date = 'Oct 13, 2014'
    authors = ['Tiberiu Ichim']
    priority = PRIORITY['HIGH']
    description = ('Fix Blobs for NyBlobFiles')

    def get_content(self, folder, filename):
        path = os.path.join(folder, filename)
        with open(path) as f:
            content = f.read()
        sfile = StringIO(content)
        sfile.filename = filename
        raise ValueError ("Content type extraction not yet implemented")
        sfile.headers = {'content-type': ''}

    def get_extfiles(self, obj):
        base = "/var/local/chmfiles/var/files"
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

    def fix(self, obj):
        pass

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
