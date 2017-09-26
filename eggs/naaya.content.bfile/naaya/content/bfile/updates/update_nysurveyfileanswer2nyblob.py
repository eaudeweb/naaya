""" Migrate storage of file answers from extfiles to
naaya.content.bfiles
"""

from Products.naayaUpdater.updates import UpdateScript
from naaya.content.bfile.NyBlobFile import make_blobfile
from datetime import datetime
from StringIO import StringIO


class UpdateSurveyFileAnswer2NyBlobFile(UpdateScript):
    title = 'Naaya Survey: Migrate file answers to Blobs'
    authors = ['Valentin Dumitru']
    creation_date = 'Nov 17, 2016'

    def _update(self, portal):

        brains = portal.portal_catalog(meta_type=['Naaya Survey Answer'])

        for brain in brains:
            try:
                obj = brain.getObject()
            except:
                self.log.warning(
                    "Couldn't get obj based on catalog information %s",
                    brain.getURL())
                continue

            for upload in obj.objectValues('ExtFile'):

                if upload is None:
                    continue

                if 'blob' in getattr(upload, 'meta_type', "").lower():
                    continue

                if upload.is_broken():
                    self.log.warning(
                        "\t BROKEN EXTFILE: Couldn't migrate extfile for "
                        "%s because of broken file", obj.absolute_url()
                    )
                    continue

                if upload.get_size():
                    data = upload.index_html()
                    sfile = StringIO(data)
                    self.log.debug('\t VERSION FILENAME: %s',
                                      '/'.join(upload.filename))
                    sfile.filename = upload.filename[-1]
                    sfile.headers = {
                        'content-type': upload.content_type}

                    bf = make_blobfile(sfile,
                                       title=upload.title,
                                       removed=False,
                                       timestamp=datetime.utcnow(),
                                       contributor='')

                    bf.filename = upload.id
                    bf.content_type = upload.content_type
                    bf.size = len(data)
                    upload._delete('/'.join(upload.filename))

                    setattr(obj, upload.id, bf)

                    self.log.info("Migrated %s bytes to bfile: %s" %
                                      (len(data), obj.absolute_url()))
                    obj._p_changed = True

        self.log.info('Migration done')

        return True

# vim: set ts=4 sw=4 ai et:
