#Python imports

#Zope imports

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript

class UpdateAddUseOpenzoom(UpdateScript):
    """ """
    title = 'Add use_openzoom property for GBIF media archive'
    creation_date = 'Aug 24, 2011'
    authors = ['Andrei Laza']

    def _update(self, portal):
        portal_catalog = portal.getCatalogTool()
        for brain in portal_catalog(meta_type='Naaya GBIF Media Folder'):
            folder = brain.getObject()
            if not hasattr(folder.aq_base, 'use_openzoom'):
                folder.use_openzoom = 0
                self.log.debug('Added property use_openzoom to %r',
                               folder.absolute_url())

        for brain in portal_catalog(meta_type='Naaya GBIF Photo'):
            photo = brain.getObject()
            if not hasattr(photo.aq_base, 'use_openzoom'):
                photo.use_openzoom = 0
                self.log.debug('Added property use_openzoom to %r',
                               photo.absolute_url())

        return True
