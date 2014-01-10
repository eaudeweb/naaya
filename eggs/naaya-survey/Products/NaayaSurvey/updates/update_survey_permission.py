from Products.NaayaSurvey.permissions import PERMISSION_EDIT_ANSWERS
from Products.naayaUpdater.updates import UpdateScript
from AccessControl import ClassSecurityInfo
from AccessControl.Permission import Permission
from Products.NaayaSurvey.permissions import PERMISSION_VIEW_REPORTS
class UpdatePermission(UpdateScript):
    """  """
    title='Update missing permission'
    description='Update missing PERMISSION_EDIT_ANSWERS in Naaya Survey'

    def _update(self, portal):
        """ """
        portal.manage_permission(PERMISSION_EDIT_ANSWERS,
                         ('Manager', 'Administrator', ), acquire=0)
        self.log.info("Added permission %r to %r", PERMISSION_EDIT_ANSWERS,
                                                    portal.absolute_url(1))
        return True

class CorrectReportPermission(UpdateScript):
    """  """
    title = 'Remove anonymous from the view reports permission'
    description = ('Remove anonymous from the view reports permission '
                'and add Administrator, Manager and Owner')
    creation_date = 'Jan 10, 2014'
    authors = ['Valentin Dumitru']
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        view_reports_perm = Permission(PERMISSION_VIEW_REPORTS, (), portal)
        roles_with_view_reports = view_reports_perm.getRoles()
        if isinstance(roles_with_view_reports, list):
            acquire = 1
        else:
            acquire = 0
        if 'Anonymous' in roles_with_view_reports:
            #import pdb;pdb.set_trace()
            corrected_roles = set(role for role in roles_with_view_reports
                               if role != 'Anonymous')
            corrected_roles.update(['Administrator', 'Manager', 'Owner'])
            portal.manage_permission(PERMISSION_VIEW_REPORTS,
                    list(corrected_roles), acquire=acquire)
            self.log.debug('Anonymous role removed from permission')
        else:
            self.log.debug('Anonymous does not have the permission')
        return True
