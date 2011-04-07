from Products.naayaUpdater.updates import UpdateScript
from Products.NaayaBase.constants import PERMISSION_SKIP_APPROVAL
from naaya.core.zope2util import permission_add_role

class SkipApprovalPermission(UpdateScript):
    title = ('Set the "Naaya - Skip approval" permission '
             'based on the `submit_unapproved` setting')
    authors = ['Alex Morega']
    creation_date = 'Feb 21, 2011'

    def _update(self, portal):
        if not hasattr(portal.aq_base, 'submit_unapproved'):
            self.log.info("submit_unapproved flag already updated.")
            return True

        value = portal.submit_unapproved
        portal._set_submit_unapproved(value)
        self.log.info("submit_unapproved flag set to %r" % value)
        del portal.submit_unapproved
        return True
