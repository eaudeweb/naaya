from AccessControl import ClassSecurityInfo
from AccessControl.Permission import Permission
from AccessControl.Permissions import view

from Products.naayaUpdater.updates import UpdateScript, PRIORITY


class UpdateViewPermission(UpdateScript):
    """ Setting view permission for Anonymous, portal_layout  """
    title = 'Set view for Anonymous on portal_layout'
    creation_date = 'Apr 17, 2012'
    authors = ['Mihnea Simian']
    priority = PRIORITY['LOW']
    description = 'Sets view permission for Anonymous on portal_layout.'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        layout_tool = portal.getLayoutTool()
        view_perm = Permission(view, (), layout_tool)
        if 'Anonymous' not in view_perm.getRoles():
            view_perm.setRoles(['Anonymous',])
            self.log.info("View Permission set for Anonymous on portal_layout.")
        else:
            self.log.info("Already has it, nothing to do.")
        return True
