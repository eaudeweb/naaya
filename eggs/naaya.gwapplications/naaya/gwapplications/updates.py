from Products.naayaUpdater.updates import UpdateScript

class ChangeLDAPSourceTitle(UpdateScript):
    title = 'Change LDAP source title'
    authors = ['Andrei Laza']
    creation_date = 'Mar 08, 2011'

    def _update(self, portal):
        sources = portal.acl_users.getSources()
        for s in sources:
            if s.title == 'LDAP':
                s.title = 'Eionet'
                self.log.debug('Changed source name to %s' % s.title)
        return True
