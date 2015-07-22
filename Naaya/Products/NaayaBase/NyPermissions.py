"""
This module contains the class that implements permissions and rights checking.
"""

import logging

from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.Permissions import view
from Globals import InitializeClass
from zope.deprecation import deprecate

from naaya.i18n.constants import PERMISSION_TRANSLATE_PAGES
from Products.Naaya.constants import PERMISSION_ADD_FOLDER
from naaya.core.backport import all

from Products.NaayaBase.constants import *


log = logging.getLogger(__name__)

class NyPermissions(object):
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
                if not pc.has_key(k):
                    log.warning("%s appears as installed, although source files not on disk" % k)
                else:
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

    def checkPermissionRequestWebex(self):
        """ Check the permissions to request webex."""

        return self.checkPermission(PERMISSION_REQUEST_WEBEX)

    def checkPermissionCopyObjects(self, object_ids):
        """ Check the permissions to copy objects. """
        objects = [self[object_id] for object_id in object_ids]
        permissions = [x.checkPermissionCopyObject() for x in objects]

        return all(permissions)

    def checkPermissionRenameObjects(self, object_ids):
        """ Check the permissions to rename objects. """
        objects = [self[object_id] for object_id in object_ids]
        permissions = [x.checkPermissionRenameObject() for x in objects]

        return all(permissions)

    def checkPermissionCutObject(self):
        """ Check the permissions to cut objects."""

        return self.checkPermission(PERMISSION_COPY_OBJECTS) and \
            self.checkPermission(PERMISSION_DELETE_OBJECTS)

    def checkPermissionRenameObject(self):
        """ Check the permissions to rename an object."""

        return self.checkPermission(PERMISSION_COPY_OBJECTS) and \
            self.checkPermission(PERMISSION_DELETE_OBJECTS)

    def checkPermissionPasteObjects(self):
        """ Check the permissions to paste objects."""

        return self.checkPermissionAddObjects()

    def checkPermissionDeleteObjects(self, object_ids):
        """
        Some users need to delete their own items, although they do not have
        delete permission on parent.
        Check whether user can delete the sub objects with ids `object_ids`
        """
        if self.checkPermissionDeleteObject():
            # user can delete anything inside, if he can delete the container
            return True
        objects = [self[object_id] for object_id in object_ids]
        permissions = [x.checkPermissionDeleteObject() for x in objects]

        return all(permissions)

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

        return self.checkPermission(PERMISSION_DELETE_OBJECTS)

    def checkPermissionCopyObject(self):
        """ Check the permissions to copy a single object. The user must have
        the copy objects permission.

        """

        return self.checkPermission(PERMISSION_COPY_OBJECTS)

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

    def checkPermissionCreateUser(self):
        """ Check the permission to create a user """

        return self.checkPermission(PERMISSION_CREATE_USER)

    security.declareProtected(PERMISSION_SKIP_CAPTCHA, 'skip_captcha')
    def skip_captcha(self):
        """ bogus function used to register the SKIP_CAPTCHA permission"""

        pass

    security.declareProtected(PERMISSION_SKIP_APPROVAL,
                              'skip_approval_dummy_function')
    def skip_approval_dummy_function(self):
        """ dummy function used to register the SKIP_APPROVAL permission"""

        pass

    def checkAllowedToZipImport(self):
        """
        Not a regular Permission check.

        Check if user can use Zip Import to add a structure of folders
        and files in a location.
        Permission is granted if he is:
        * permitted to add Folders
        * permitted to add Files

        """
        # Bypass cross imports
        from naaya.content.bfile.permissions import PERMISSION_ADD_BFILE
        from naaya.content.file.permissions import PERMISSION_ADD_FILE

        return (self.checkPermission(PERMISSION_ADD_FOLDER) and
                (self.checkPermission(PERMISSION_ADD_FILE) or
                 self.checkPermission(PERMISSION_ADD_BFILE)
                )
               )

    def checkPermissionZipExport(self):
        """
        Allowed to export zip of contents? Used for Naaya Folder and Naaya
        Photo Folder.

        """
        return self.checkPermission(PERMISSION_ZIP_EXPORT)

    def checkPermissionReview(self):
        """ Can the user review consultations? """
        return self.checkPermission("Naaya - Review Consultation")


InitializeClass(NyPermissions)
