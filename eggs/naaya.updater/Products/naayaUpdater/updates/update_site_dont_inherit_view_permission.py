#Python imports

#Zope imports
from AccessControl import ClassSecurityInfo
from AccessControl.Permission import Permission
from AccessControl.Permissions import view

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript

class DontInheritViewPermission(UpdateScript):
    """ Remove view permission inheritance for sites """
    title = 'Remove view permission inheritance for sites'
    creation_date = 'Oct 17, 2011'
    authors = ['Andrei Laza']
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        view_perm = Permission(view, (), portal)
        roles_with_view = view_perm.getRoles()
        if tuple is type(roles_with_view):
            self.log.debug('No need to update')
        else:
            view_perm.setRoles(tuple(roles_with_view))
            self.log.debug('Removed view permission inheritance for the site')
        return True
