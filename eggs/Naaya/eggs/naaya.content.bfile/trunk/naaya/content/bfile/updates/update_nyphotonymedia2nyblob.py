""" Migrate storage of photos and media files from extfiles to
naaya.content.bfiles
"""

from OFS.Image import getImageInfo
from Products.naayaUpdater.updates import UpdateScript


class UpdateNyPhotoNyMedia2NyBlobFile(UpdateScript):
    title = 'PhotoArchive and MediaFiles: Migrate ExtFiles to Blobs'
    authors = ['Tiberiu Ichim']
    creation_date = 'Oct 10, 2014'

    def _update(self, portal):

        brains = portal.portal_catalog(meta_type=['Naaya Photo',
                                                  'Naaya Media File'])

        for brain in brains:
            obj = brain.getObject()
            self.log.info("Migrating object %s", obj.absolute_url())
            for extfile in obj.objectValues('ExtFile'):
                self.log.info("Migrating extfile %s", extfile.absolute_url())
                data = extfile.index_html()
                filename = extfile.id
                obj.manage_delObjects([filename])
                child_id = obj.manage_addFile(filename)
                child = obj._getOb(child_id)
                child.content_type, child.width, child.height = getImageInfo(
                    data)
                blob = child.open_write()
                blob.write(data)
                blob.seek(0)
                blob.close()
                child.size = len(data)
                self.log.info('Migrated to bfile: %s' % child)

        self.log.info('Migration done')

        return True
