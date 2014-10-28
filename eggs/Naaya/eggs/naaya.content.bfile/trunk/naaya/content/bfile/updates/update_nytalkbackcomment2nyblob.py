""" Migrate storage of photos and media files from extfiles to
naaya.content.bfiles
"""

#from OFS.Image import getImageInfo
from Products.naayaUpdater.updates import UpdateScript


class UpdateNyTalkbackComment2NyBlobFile(UpdateScript):
    title = 'naaya.content.talkback: Migrate Comment file attachment to Blobs'
    authors = ['Tiberiu Ichim']
    creation_date = 'Oct 27, 2014'

    def _update(self, portal):

        brains = portal.portal_catalog(meta_type='Naaya TalkBack Consultation')

        for brain in brains:
            obj = brain.getObject()
            self.log.info("Migrating object %s", obj.absolute_url())
            for section in obj.objectValues('Naaya TalkBack Consultation Section'):
                for para in section.objectValues():
                    for comment in para.objectValues():
                        if not hasattr(comment, '_ext_file'):
                            continue

                        if comment._ext_file.get_size():
                            data = comment._ext_file.index_html()
                            blob = comment._bfile.open_write()
                            blob.write(data)
                            blob.seek(0)
                            blob.close()
                            comment._bfile.size = len(data)
                            comment._p_changed = True
                            comment._bfile._p_changed = True
                            self.log.info("Migrated %s bytes to bfile: %s" %
                                          (len(data), comment.absolute_url()))

                        comment._ext_file._delete(
                            '/'.join(comment._ext_file.filename))

                        del comment._ext_file
                        self.log.info("Removed _ext_file for %s" %
                                      comment.absolute_url())

        self.log.info('Migration done')

        return True
