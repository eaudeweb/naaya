from naaya.core.zope2util import permission_add_role
from Products.naayaUpdater.updates import UpdateScript

class UpdateOwnerPermissions(UpdateScript):
    """ """
    title = 'Update Owner permissions for Groupware sites'
    creation_date = 'Aug 02, 2011'
    authors = ['Andrei Laza']
    description = ('Add more permissions: edit, delete, copy, cut,'
                  ' add files, add comment, for the owners')

    def _update(self, portal):
        permissions = [
                "View",
                "Naaya - Copy content",
                "Naaya - Delete content",
                "Naaya - Edit content",
                "Add/Edit/Delete Naaya Forum Topic",
                "Edit/Delete Forum Message",
                "Add Naaya Forum Message",
                "Naaya - Add Naaya Event objects",
                "Naaya - Add Naaya Blob File objects",
                "Naaya - Add Naaya Folder objects",
                "Naaya - Add Naaya Document objects",
                "Naaya - Add Naaya Meeting objects",
                "Naaya - Add Naaya Media File objects",
                "Naaya - Add Naaya News objects",
                "Naaya - Add Naaya Photo",
                "Naaya - Add Naaya Pointer objects",
                "Naaya - Add Naaya URL objects",
                ]
        for p in permissions:
            permission_add_role(portal, p, 'Owner')
        self.log.debug('Done')
        return True
