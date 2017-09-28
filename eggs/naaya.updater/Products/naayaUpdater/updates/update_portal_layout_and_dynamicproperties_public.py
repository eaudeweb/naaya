#Python imports

#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from AccessControl.Permission import Permission
from OFS.Folder import Folder

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript, PRIORITY

class UpdatePortalLayoutAndDynamicPropertiesPublic(UpdateScript):
    """ Make portal layout and portal dynamic properties public """
    title = ' Make portal layout and portal dynamic properties public '
    creation_date = 'Dec 13, 2010'
    authors = ['Andrei Laza']
    priority = PRIORITY['LOW']
    description = 'Make portal layout and portal dynamic properties public.'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        layout_permission = Permission(view, (), portal.portal_layout)
        layout_permission.setRoles(portal.validRoles())

        dyn_permission = Permission(view, (), portal.portal_dynamicproperties)
        dyn_permission.setRoles(portal.validRoles())
        self.log.info('Done')
        return True
