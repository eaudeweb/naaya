""" Migrate storage of photos and media files from extfiles to
naaya.content.bfiles
"""

from Products.naayaUpdater.updates import UpdateScript


class UpdateSurveyAttachment2NyBlobFile(UpdateScript):
    title = 'Naaya Survey: Migrate survey attachment to Blobs'
    authors = ['Tiberiu Ichim']
    creation_date = 'Oct 28, 2014'

    def _update(self, portal):

        brains = portal.portal_catalog(meta_type=['Naaya Mega Survey'])

        for brain in brains:
            obj = brain.getObject()
            self.log.info("Migrating object %s", obj.absolute_url())
            for attach in obj.objectValues('Naaya Survey Attachment'):
                self.log.info("Migrating survey attachment %s",
                              attach.absolute_url())
                for fobj in attach.objectValues():
                    if not getattr(fobj, '_ext_file'):
                        continue

                    if fobj._ext_file.get_size():
                        data = fobj._ext_file.index_html()

                        blob = fobj._bfile.open_write()
                        blob.write(data)
                        blob.seek(0)
                        blob.close()
                        fobj._bfile.filename = fobj._ext_file.id
                        fobj._bfile.content_type = fobj._ext_file.content_type
                        fobj._bfile.size = len(data)
                        fobj._p_changed = True
                        fobj._bfile._p_changed = True

                        self.log.info("Migrated %s bytes to bfile: %s" %
                                          (len(data), fobj.absolute_url()))

                        del fobj._ext_file
                        self.log.info("Removed _ext_file for %s" %
                                      fobj.absolute_url())

                        self.log.info('Migrated to bfile: %s' %
                                      fobj.absolute_url())

        self.log.info('Migration done')

        return True
