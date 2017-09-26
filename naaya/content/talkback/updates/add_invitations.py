from Products.naayaUpdater.updates import UpdateScript

from naaya.content.talkback.invitations import InvitationsContainer

class AddInvitations(UpdateScript):
    title = 'Fix AttributeError: invitations'
    authors = ['Andrei Laza']
    creation_date = 'Nov 04, 2011'

    def _update(self, portal):
        query = {'meta_type': ['Naaya TalkBack Consultation']}
        for brain in portal.getCatalogTool()(**query):
            consultation = brain.getObject()
            if hasattr(consultation.aq_base, 'invitations'):
                continue

            consultation.invitations = InvitationsContainer('invitations')
            self.log.debug('Updated %s', consultation.absolute_url())
        return True
