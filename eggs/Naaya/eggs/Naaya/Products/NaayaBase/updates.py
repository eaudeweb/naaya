from Products.naayaUpdater.updates import UpdateScript
from Products.NaayaBase.constants import PERMISSION_SKIP_APPROVAL
from naaya.core.zope2util import permission_add_role

class SkipApprovalPermission(UpdateScript):
    title = ('Set the "Naaya - Skip approval" permission '
             'based on the `submit_unapproved` setting')
    authors = ['Alex Morega']
    creation_date = 'Feb 21, 2011'

    def _update(self, portal):
        if portal.submit_unapproved:
            # note: we leave the `submit_unapproved` flag in place, instead
            # of cleaning it up, in case the update script is run several
            # times.
            self.log.info("Administrator submissions will remain unapproved.")
        else:
            permission_add_role(portal, PERMISSION_SKIP_APPROVAL,
                                'Administrator')
            self.log.info("Administrator will skip approval workflow.")
        return True
