from Products.naayaUpdater.updates import UpdateScript
from Persistence.mapping import PersistentMapping

class AddValidateEmails(UpdateScript):
    title = 'NySite: Add email validation'
    authors = ['Daniel Baragan']
    creation_date = 'Dec 4, 2013'

    def _update(self, portal):
        self.log.debug('Patching %s objects' % portal.getId())

        if getattr(portal, 'checked_emails', None) is None:
            setattr(portal, 'checked_emails', PersistentMapping())
        else:
            self.log.debug('Skipping new-version/patched portal object at %s' %
                            portal.absolute_url(1))
        return True

