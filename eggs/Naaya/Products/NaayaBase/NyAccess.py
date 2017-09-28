from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from AccessControl.Permission import Permission
from AccessControl.ImplPython import rolesForPermissionOn
from AccessControl.Permissions import change_permissions
from Products.NaayaBase.constants import MESSAGE_SAVEDCHANGES
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

class NyAccess(SimpleItem):
    security = ClassSecurityInfo()

    title = "Edit permissions"

    def __init__(self, id, permissions):
        assert isinstance(permissions, dict) # old code used a list here
        self.id = id
        self.permissions = permissions

    security.declareProtected(change_permissions, 'getObject')
    def getObject(self):
        """ Returns the object NyAccess is associated to """

        return self.aq_inner.aq_parent

    security.declareProtected(change_permissions, 'getObjectParent')
    def getObjectParent(self):
        """ Returns the parent of the object """

        return self.getObject().aq_inner.aq_parent

    security.declareProtected(change_permissions, 'sortedPermissions')
    def sortedPermissions(self):
        """ """

        return sorted(self.permissions.keys())

    security.declareProtected(change_permissions, 'getValidRoles')
    def getValidRoles(self):
        """ """

        roles_to_remove = ['Owner', 'Manager']
        return [role for role in self.getObject().validRoles()
                        if role not in roles_to_remove]

    security.declareProtected(change_permissions, 'getPermissionsWithAcquiredRoles')
    def getPermissionsWithAcquiredRoles(self):
        """ Return the permissions which acquire roles from their parents """

        ret = []
        for permission in self.permissions:
            permission_object = Permission(permission, (), self.getObject())
            if isinstance(permission_object.getRoles(), list):
                ret.append(permission)
        return ret

    security.declareProtected(change_permissions, 'getPermissionAcquiredMapping')
    def getPermissionAcquiredMapping(self):
        """ """

        parent = self.getObjectParent()
        acquiring_permissions = self.getPermissionsWithAcquiredRoles()
        mapping = {}
        for permission in self.permissions:
            if permission in acquiring_permissions:
                mapping[permission] = rolesForPermissionOn(permission, parent)
            else:
                mapping[permission] = []
        return mapping

    security.declareProtected(change_permissions, 'getPermissionMapping')
    def getPermissionMapping(self):
        """ Return the permission mapping for the object """

        mapping = {}
        for permission in self.permissions:
            permission_object = Permission(permission, (), self.getObject())
            mapping[permission] = permission_object.getRoles()
        return mapping

    security.declareProtected(change_permissions, 'setPermissionMapping')
    def setPermissionMapping(self, mapping):
        """
        Change the permission mapping for the object.
        This leaves the other permissions (not in mapping.keys()) unchanged
        """

        for permission in mapping:
            permission_object = Permission(permission, (), self.getObject())
            permission_object.setRoles(mapping[permission])

    security.declareProtected(change_permissions, 'savePermissionMapping')
    def savePermissionMapping(self, REQUEST, known_roles=[]):
        """
        This is called from index_html
        calls setPermissionMapping after converting the arguments
        """

        # consistency checks
        assert isinstance(known_roles, list)
        assert set(self.getValidRoles()) == set(known_roles)

        for permission in self.permissions:
            if permission in REQUEST.form:
                assert isinstance(REQUEST.form[permission], list)
            if ('acquires'+permission) in REQUEST.form:
                assert REQUEST.form['acquires'+permission] == 'on'

        # make the mapping
        mapping = {}
        for permission in self.permissions:
            roles = []

            if permission in REQUEST.form:
                roles = REQUEST.form[permission]

            if ('acquires'+permission) not in REQUEST.form:
                # manager role added when roles not acquired from parents
                roles = tuple(roles + ['Manager'])

            mapping[permission] = roles

        #save the mapping
        self.setPermissionMapping(mapping)

        # return to index_html
        self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES,
                                 date=self.utGetTodayDate())
        return REQUEST.RESPONSE.redirect(self.absolute_url())

    security.declareProtected(change_permissions, 'index_html')
    index_html = PageTemplateFile('zpt/ny_access', globals())
