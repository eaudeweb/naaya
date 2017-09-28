from AccessControl import ClassSecurityInfo
from zope.app.component import interfaces, site

from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from Products.Naaya.interfaces import IActionLogger
from Products.Naaya.action_logger import ActionLogger

class UpdateAddLocalSiteManager(UpdateScript):
    """ Add local site manager """
    title = 'Add site manager to all naaya sites'
    creation_date = 'Mar 08, 2011'
    authors = ['Alexandru Plugaru']
    description = 'Adds a local site manager to naaya site'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):

        def add_action_logger(sm):
            #Register Action Logger utility
            try:
                sm.getUtility(IActionLogger)
            except:
                sm.registerUtility(ActionLogger(), IActionLogger)
                self.log.debug('Added action logger utility to %s' %
                           portal.absolute_url())
            else:
                self.log.debug('Already has action logger')

        if interfaces.ISite.providedBy(portal) is True:
            self.log.debug("Already has site manager")
            add_action_logger(portal.getSiteManager())
            return True

        if interfaces.IPossibleSite.providedBy(portal) is False:
            self.log.error('Failed to add manager to %s'
                           % portal.absolute_url())
            return False

        sm = site.LocalSiteManager(portal)
        site.SiteManagerContainer.setSiteManager.im_func(portal, sm)
        portal.setSiteManager(sm)
        self.log.debug('Added site manager to %s' % portal.absolute_url())
        add_action_logger(sm)
        return True
