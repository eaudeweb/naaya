from Products.naayaUpdater.updates import UpdateScript

class UpdateOwnerEditPermissions(UpdateScript):
    """ """
    title = 'Update Owner edit permissions for Groupware sites'
    creation_date = 'Nov 09, 2012'
    authors = ['Cornel Nitu']
    description = ('Add edit, copy and delete permissions for the owners')

    def _update(self, portal):
        if portal.can_edit_own_content():
            portal._set_edit_own_content(edit_own_content=True)
            self.log.debug('Done')
        else:
            self.log.debug("Owners cannot edit their own content on this portal.")
        return True
