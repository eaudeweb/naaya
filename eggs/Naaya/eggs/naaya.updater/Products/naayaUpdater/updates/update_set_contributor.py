from AccessControl import ClassSecurityInfo

from Products.naayaUpdater.updates import UpdateScript

class SetContributor(UpdateScript):
    """ Set contributor if None """
    title = 'Set contributor if None'
    creation_date = 'Oct 18, 2011'
    authors = ['Andrei Laza']
    description = 'Updates the contributor from the owner role if contributor is None.'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        portal_catalog = portal.getCatalogTool()
        for brain in portal_catalog():
            item = brain.getObject()
            if not hasattr(item.aq_base, 'contributor'):
                continue
            if item.contributor is not None:
                continue
            self.log.debug('%s has None "contributor"' % item.absolute_url())
            item.contributor = item.getOwner().name
            self.log.debug('new owner is %s' % item.contributor)
        return True
