# Zope2 stuff
EditorRate = "Content Ratings: Editor Rate"
ViewEditorialRating = "Content Ratings: View Editorial Rating"
UserRate = "Content Ratings: User Rate"
ViewUserRating = "Content Ratings: View User Rating"

try:
    # Set some default roles for zope2
    import Products
    from AccessControl.Permission import _registeredPermissions
    from AccessControl.Permission import pname
    from Globals import ApplicationDefaultPermissions
    def setDefaultRoles(permission, roles):
        '''
        Sets the defaults roles for a permission.
        '''
        # XXX This ought to be in AccessControl.SecurityInfo.
        registered = _registeredPermissions
        if not registered.has_key(permission):
            registered[permission] = 1
            Products.__ac_permissions__=(
                Products.__ac_permissions__+((permission,(),roles),))
            mangled = pname(permission)
            setattr(ApplicationDefaultPermissions, mangled, roles)

    setDefaultRoles(EditorRate, ('Manager', 'Reviewer'))
    setDefaultRoles(ViewEditorialRating, ('Anonymous', 'Authenticated',))
    setDefaultRoles(UserRate, ('Anonymous', 'Authenticated',))
    setDefaultRoles(ViewUserRating, ('Anonymous','Authenticated',))
except ImportError:
    pass
