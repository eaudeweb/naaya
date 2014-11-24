""" Migrate storage of publications from extfile to bfile """

from Products.naayaUpdater.updates import UpdateScript
from StringIO import StringIO
from naaya.content.bfile.NyBlobFile import make_blobfile


class UpdateNyPublication2NyBlobFile(UpdateScript):
    title = 'Publication: Migrate ExtFiles to Blobs'
    authors = ['Tiberiu Ichim']
    creation_date = '2014-11-22'

    def _update(self, portal):

        brains = portal.portal_catalog(meta_type=['Naaya Publication'])

        for brain in brains:
            fobj = brain.getObject()
            self.log.info("Migrating object %s", fobj.absolute_url())

            if not hasattr(fobj, '_ext_file'):
                continue

            if fobj._ext_file.is_broken():
                self.log.warning(
                    "\t BROKEN EXTFILE: Couldn't migrate extfile for "
                    "%s because of broken file", fobj.absolute_url()
                )
                continue

            if fobj._ext_file.get_size():
                data = fobj._ext_file.index_html()

                out = StringIO()
                out.write(data)
                out.seek(0)
                fobj._bfile = make_blobfile(
                    out, filename=fobj._ext_file.id,
                    content_type=fobj._ext_file.content_type)
                fobj._p_changed = True

                self.log.info("Migrated %s bytes to bfile: %s" %
                                    (len(data), fobj.absolute_url()))

                fobj._ext_file._delete('/'.join(fobj._ext_file.filename))

                del fobj._ext_file
                self.log.info("Removed _ext_file for %s" % fobj.absolute_url())
                self.log.info('Migrated to bfile: %s' % fobj.absolute_url())

        self.log.info('Migration done')

        return True
