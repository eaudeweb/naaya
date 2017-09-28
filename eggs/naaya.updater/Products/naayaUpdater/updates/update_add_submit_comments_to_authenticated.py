#Python imports

#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from AccessControl.Permission import Permission

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript, PRIORITY

class UpdateAddSubmitCommentsToAuthenticated(UpdateScript):
    """ Update add submit comments permission to authenticated users  """
    title = 'Update add submit comments to authenticated'
    creation_date = 'Mar 1, 2011'
    authors = ['Andrei Laza']
    priority = PRIORITY['LOW']
    description = 'Update add submit comments permission to authenticated users.'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        permission = Permission('Naaya - Add comments for content', (), portal)
        roles = permission.getRoles()
        if 'Authenticated' in roles:
            self.log.debug("Portal doesn't need update")
            self.log.debug("Authenticated users can already add comments")
            return True

        if isinstance(roles, tuple):
            roles = tuple(list(roles) + ['Authenticated'])
        else:
            roles = roles + ['Authenticated']
        permission.setRoles(roles)
        return True



