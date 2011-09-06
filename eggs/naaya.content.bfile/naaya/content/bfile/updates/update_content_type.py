#python imports
import mimetypes

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript, PRIORITY

class UpdateContentType(UpdateScript):
    title = 'Update content_type for bfiles with content_type=None'
    creation_date = 'Sep 09, 2011'
    authors = ['Andrei Laza']
    priority = PRIORITY['HIGH']

    def _update(self, portal):
        catalog = portal.portal_catalog
        for brain in catalog(meta_type='Naaya Blob File'):
            bfile = brain.getObject()
            versions = [v for v in bfile._versions if not v.removed]
            for v in versions:
                if v.content_type is not None:
                    self.log.debug('No need to update %r (%s)',
                                   v, bfile.absolute_url())
                    continue

                v.content_type = mimetypes.guess_type(v.filename)[0]
                if v.content_type is not None:
                    self.log.info('Updated %r (%s)', v, bfile.absolute_url())
                    continue

                v.content_type = 'application/octet-stream'
                self.log.info('Using default content_type for %r (%s)',
                              v, bfile.absolute_url())
        return True
