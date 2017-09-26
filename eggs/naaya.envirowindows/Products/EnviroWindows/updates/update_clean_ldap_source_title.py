from Products.naayaUpdater.updates import UpdateScript

class CleanLDAPSourceTitle(UpdateScript):
    title = 'Change LDAP source title (remove last "users" part)'
    authors = ['Andrei Laza']
    creation_date = 'Mar 09, 2011'

    def _update(self, portal):
        sources = portal.acl_users.getSources()
        for s in sources:
            if s.title.endswith(' users') or s.title.endswith(' Users'):
                s.title = s.title[:-6]
                self.log.debug('Changed source name to %s' % s.title)
            else:
                self.log.debug('Source name is %s' % s.title)
        return True

