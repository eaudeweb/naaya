from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from AccessControl.Permission import Permission


class SetReviewerPermission(UpdateScript):
    """ Set reviewers to have 'Naaya - Review TalkBack Consultation'
        permission"""
    title = 'Review TalkBack permission for reviewer role'
    creation_date = 'Oct 22, 2015'
    authors = ['Valentin Dumitru']
    priority = PRIORITY['LOW']
    description = ("Set reviewers to have "
                   "'Naaya - Review TalkBack Consultation' permission")

    def _update(self, portal):
        review_perm = Permission('Naaya - Review TalkBack Consultation',
                                 (), portal)
        for role in ['Administrator', 'Owner', 'Reviewer']:
            roles = review_perm.getRoles()
            if role not in roles:
                roles.append(role)
                review_perm.setRoles(roles)
                self.log.info("Review Permission set for %s on %s" %
                              (role, portal.absolute_url()))
        return True
