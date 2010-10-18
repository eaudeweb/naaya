from Products.naayaUpdater.updates import UpdateScript, PRIORITY

class UpdatePortalProfiles(UpdateScript):
    title='Update empty portal_profiles from NySite'
    descrtiption = 'Remove no longer needed portal_profiles from NySite'
    priority = PRIORITY['HIGH']
    creation_date = 'Oct 15, 2010'
    authors = ['Alexandru Plugaru']

    def _update(self, portal):
        """ """
        if hasattr(portal, 'portal_profiles'):
            if len(portal.portal_profiles.objectValues()) == 0:
                self.log.info("Removed: %r",
                              portal.portal_profiles.absolute_url())
                portal.manage_delObjects('portal_profiles')
            else:
                self.log.info("Not empty: %r",
                              portal.portal_profiles.absolute_url())
        return True
