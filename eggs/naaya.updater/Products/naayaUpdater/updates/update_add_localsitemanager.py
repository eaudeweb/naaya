from AccessControl import ClassSecurityInfo
from zope.app.component import interfaces, site

from Products.naayaUpdater.updates import UpdateScript, PRIORITY

class UpdateAddLocalSiteManager(UpdateScript):
    """ Add local site manager """
    title = 'Add site manager to all naaya sites'
    creation_date = 'Mar 08, 2011'
    authors = ['Alexandru Plugaru']
    description = 'Adds a local site manager to naaya site'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):

        if interfaces.ISite.providedBy(portal) is True:
            self.log.debug("%s is already a site" % portal.absolute_url())

        if interfaces.IPossibleSite.providedBy(portal) is False:
            self.log.error('Failed to add manager to %s' % portal.absolute_url())
            return False

        sm = site.LocalSiteManager(portal)
        site.SiteManagerContainer.setSiteManager.im_func(self, sm)
        portal.setSiteManager(sm)
        self.log.debug('Added site manager to %s' % portal.absolute_url())
        return True
