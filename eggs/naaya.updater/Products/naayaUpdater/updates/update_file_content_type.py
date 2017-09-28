from AccessControl import ClassSecurityInfo

from Products.naayaUpdater.updates import UpdateScript

class UpdateFileContentType(UpdateScript):
    """ Update file content type if possible  """
    title = 'Update file content type'
    creation_date = 'Oct 18, 2011'
    authors = ['Andrei Laza']
    description = 'Update file content type if possible'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        portal_catalog = portal.getCatalogTool()
        for brain in portal_catalog(meta_type='Naaya File'):
            fileob = brain.getObject()
            self.log.debug('Content type for object %s at %s is %s' % (
                fileob.__name__, fileob.absolute_url(), fileob.content_type))

            if fileob.content_type == 'application/octet-stream':
                computed_ctype = fileob.get_data(as_string=False).getContentType()
                if computed_ctype != 'application/octet-stream':
                    self.log.debug('Changing content type to %s' % computed_ctype)
                    fileob.content_type = computed_ctype
                else:
                    self.log.debug('No content type found')
            else:
                self.log.debug('Not changing content type')

        return True
