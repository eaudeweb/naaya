from Products.naayaUpdater.updates import UpdateScript, PRIORITY

class RemovePredifinedLatestUploads(UpdateScript):
    """ """
    title = 'Remove predefined_latest_uploads'
    creation_date = 'Oct 20, 2011'
    authors = ['Andrei Laza']
    priority = PRIORITY['LOW']
    description = ('Remove predefined_latest_uploads from CHMSites')

    def _update(self, portal):
        if hasattr(portal.aq_base, 'predefined_latest_uploads'):
            del portal.predefined_latest_uploads
            self.log.debug("removed portal.predefined_latest_uploads")
        else:
            self.log.debug("No need to remove portal.predefined_latest_uploads")

        portlets = portal.portal_portlets
        if portlets.hasObject('portlet_latestrelevantuploads_rdf'):
            portlets.manage_delObjects('portlet_latestrelevantuploads_rdf')
            self.log.debug("removed portlet_latestrelevantuploads_rdf")
        else:
            self.log.debug("No need to remove portlet_latestrelevantuploads_rdf")

        syndication = portal.portal_syndication
        if syndication.hasObject('latestrelevantuploads_rdf'):
            syndication.manage_delObjects('latestrelevantuploads_rdf')
            self.log.debug("removed latestrelevantuploads_rdf channel")
        else:
            self.log.debug("No need to remove latestrelevantuploads_rdf channel")

        return True
