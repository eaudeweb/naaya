"""
This module contains the class that implements permissions and rights checking.
"""

from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.Permissions import view
from Globals import InitializeClass
from zope.deprecation import deprecate
from constants import *

class NyPermissions:
    """ Class that implements permissions and rights checking."""

    security = ClassSecurityInfo()

    def getObjectOwner(self):
        """ Returns the name of the user that owns the object."""
        o = None
        o = self.owner_info()
        if hasattr(o, "has_key") and o.has_key('id'):
            o = o['id']
        return o

    def checkPermission(self, p_permission):
        """ Check `p_permission` for the current object"""

        return getSecurityManager().checkPermission(p_permission, self)

    def checkPermissionView(self):
        """ Check the access to the current object."""

        return self.checkPermission(view)

    def checkPermissionAdministrate(self):
        """ Check the access to the administrative area."""

        return self.checkPermission(PERMISSION_ADMINISTRATE)

    def checkPermissionValidateObjects(self):
        """ Check the access to objects validation area."""

        return self.checkPermission(PERMISSION_VALIDATE_OBJECTS)

    def checkPermissionTranslatePages(self):
        """ Check the access to translations area."""

        return self.checkPermission(PERMISSION_TRANSLATE_PAGES)

    def checkPermissionAddObjects(self):
        """ Check the permissions to add different types of objects."""

        #check folder
        p = self.checkPermissionAddFolders(self)
        if not p:
            #check pluggable content
            pc = self.get_pluggable_content()
            for k in self.get_pluggable_installed_meta_types():
                p = p or self.checkPermission(pc[k]['permission'])
                if p: break
        return p

    def checkPermissionEditObjects(self):
        """ Check the permissions to edit different type of objects."""

        return self.checkPermission(PERMISSION_EDIT_OBJECTS)

    @deprecate('`glCheckPermissionPublishObjects` is deprecated. Use '
               '`checkPermissionSkipApproval` instead.')
    def glCheckPermissionPublishObjects(self):
        """ """

        return self.checkPermissionSkipApproval()

    def checkPermissionPublishDirect(self):
        """
        Check the permissions to publish objects without fill the CAPTCHA.

        """

        return self.checkPermission(PERMISSION_PUBLISH_DIRECT)

    def checkPermissionPublishObjects(self):
        """ Check the permissions to publish objects."""

        return self.checkPermission(PERMISSION_PUBLISH_OBJECTS)

    def checkPermissionCopyObjects(self):
        """ Check the permissions to copy objects."""

        return self.checkPermission(PERMISSION_COPY_OBJECTS)

    def checkPermissionCutObjects(self):
        """ Check the permissions to cut objects."""

        return self.checkPermission(PERMISSION_COPY_OBJECTS) and \
            self.checkPermission(PERMISSION_DELETE_OBJECTS)

    def checkPermissionPasteObjects(self):
        """ Check the permissions to paste objects."""

        return self.checkPermissionAddObjects()

    def checkPermissionDeleteObjects(self):
        """ Check the permissions to delete objects."""

        return self.checkPermission(PERMISSION_DELETE_OBJECTS)

    def checkPermissionEditObject(self):
        """ Check the permissions to edit a single object. The user must have
        the edit objects permission and to be the object's owner or to have
        the publish permission.

        """

        return self.checkPermissionEditObjects()

    def checkPermissionDeleteObject(self):
        """ Check the permissions to delete a single object. The user must have
        the delete objects permission and to be the object's owner or to have
        the publish permission.

        """

        return self.checkPermissionDeleteObjects()

    def checkPermissionCopyObject(self):
        """ Check the permissions to copy a single object. The user must have
        the copy objects permission.

        """

        return self.checkPermissionCopyObjects()

    def checkPermissionBulkDownload(self):
        """ Check if the user can access the bulk download functionality"""

        return self.checkPermission(PERMISSION_BULK_DOWNLOAD)

    def checkPermissionSkipCaptcha(self):
        """
        Check the permission to skip Captcha testing
        """

        return self.checkPermission(PERMISSION_SKIP_CAPTCHA)

    def checkPermissionSkipApproval(self):
        """ Check the permission to skip Captcha testing"""

        return self.checkPermission(PERMISSION_SKIP_APPROVAL)

    security.declareProtected(PERMISSION_SKIP_CAPTCHA, 'skip_captcha')
    def skip_captcha(self):
        """ bogus function used to register the SKIP_CAPTCHA permission"""

        pass

    security.declareProtected(PERMISSION_SKIP_APPROVAL,
                              'skip_approval_dummy_function')
    def skip_approval_dummy_function(self):
        """ dummy function used to register the SKIP_APPROVAL permission"""

        pass

InitializeClass(NyPermissions)
