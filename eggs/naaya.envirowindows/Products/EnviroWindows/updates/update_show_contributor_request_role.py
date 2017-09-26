from Products.naayaUpdater.updates import UpdateScript

class ShowContributorRequestRole(UpdateScript):
    title = 'Localize show_contributor_request_role widget'
    authors = ['Andrei Laza']
    creation_date = 'Dec 15, 2011'

    def _update(self, portal):
        schema = portal.portal_schemas.NyFolder
        prop = schema['show_contributor_request_role-property']
        if not prop.localized:
            prop.localized = True
            self.log.debug('Localizing show_contributor_request_role')
        else:
            self.log.debug('Nothing to update')
        return True
