import transaction
from Acquisition import aq_base
from OFS.Image import File, Image

from naaya.core.blobofs import to_blob
from Products.naayaUpdater.updates import UpdateScript, PRIORITY


class UpdateOFSDataToBlobs(UpdateScript):
    """ Move the data of OFS Images and Files from Data.fs to blobs """
    title = 'Move OFS Image and File data to blobs'
    authors = ['Valentin Dumitru']
    creation_date = 'Oct 12, 2026'
    priority = PRIORITY['LOW']
    description = ('Replaces plain OFS Images and Files (editor uploads, '
                   'layout images, attachments) with BlobImage/BlobFile '
                   'objects keeping the same id and properties. '
                   'Pack the database afterwards to reclaim the space.')

    def _walk(self, container):
        for ob in container.objectValues():
            yield container, ob
            if hasattr(aq_base(ob), 'objectValues'):
                yield from self._walk(ob)

    def _update(self, portal):
        converted = size = 0
        for container, ob in self._walk(portal):
            if type(aq_base(ob)) not in (Image, File):
                continue
            ob_id = ob.getId()
            new = to_blob(aq_base(ob))
            # same id and meta_type: replace the attribute, keep _objects
            container._setOb(ob_id, new)
            converted += 1
            size += new.size or 0
            self.log.debug('%s/%s', container.absolute_url(1), ob_id)
            if converted % 100 == 0:
                transaction.savepoint(optimistic=True)
                portal._p_jar.cacheGC()
        self.log.info('Converted %d Images/Files, %.1f MB', converted,
                      size / 1e6)
        return True
