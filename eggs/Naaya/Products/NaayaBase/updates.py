from AccessControl.Permission import Permission
from AccessControl.Permissions import view

from naaya.core.zope2util import permission_add_role
from Products.naayaUpdater.updates import UpdateScript, PRIORITY

class SkipApprovalPermission(UpdateScript):
    title = ('Set the "Naaya - Skip approval" permission '
             'based on the `submit_unapproved` setting')
    authors = ['Alex Morega']
    creation_date = 'Feb 21, 2011'

    def _update(self, portal):
        if not hasattr(portal.aq_base, 'submit_unapproved'):
            self.log.info("submit_unapproved flag already updated.")
            return True

        value = portal.submit_unapproved
        portal._set_submit_unapproved(value)
        self.log.info("submit_unapproved flag set to %r" % value)
        del portal.submit_unapproved
        return True
    
class HideSortOrderFromSchemas(UpdateScript):
    title = ('Hide the sortorder property from all schemas')
    authors = ['Valentin Dumitru']
    creation_date = 'Jul 19, 2011'

    def _update(self, portal):
        for schema in portal.portal_schemas.objectValues('Naaya Schema'):
            sortorder_property = getattr(schema, 'sortorder-property')
            sortorder_property.visible = False
            self.log.info("property hidden in schema %r" % schema.id)
        return True

class AddHelpTextOnNewsDescription(UpdateScript):
    title = ('Add a help text to the description property '
             'of News Items')
    authors = ['Valentin Dumitru']
    creation_date = 'Jul 19, 2011'

    def _update(self, portal):
        ny_news = getattr(portal.portal_schemas, 'NyNews', None)
        if ny_news:
            description = getattr(ny_news, 'description-property', None)
            if description and hasattr(description, 'help_text')\
                and not description.help_text:
                description.help_text = u'Keep this description short, about 50 words. Use the <strong>Details</strong> field below to add more information.'
                self.log.info("Help text updated")
        return True

class RestrictUnapproved(UpdateScript):
    """ """
    title = 'Restrict view for unapproved objects'
    creation_date = 'Oct 28, 2011'
    authors = ['Andrei Laza']
    priority = PRIORITY['HIGH']
    description = "Don't inherit view permission for unapproved objects"

    def _update(self, portal):
        catalog = portal.getCatalogTool()
        for brain in catalog(approved=0):
            obj = brain.getObject()
            permission = Permission(view, (), obj)
            roles = permission.getRoles()
            if isinstance(roles, list):
                obj.dont_inherit_view_permission()
                self.log.debug('restricted view permission for %s',
                                obj.absolute_url())
        return True

class SetPhotoFolderGalleryPermission(UpdateScript):
    title = ('Set Naaya Photo related permissions to administrators')
    authors = ['Valentin Dumitru']
    creation_date = 'Jan 18, 2012'

    def _update(self, portal):
        permissions = ["Naaya - Add Naaya Photo Folder",
                        "Naaya - Add Naaya Photo Gallery"]
        for permission in permissions:
            p = Permission(permission, (), portal)
            if 'Administrator' not in p.getRoles():
                permission_add_role(portal, permission, 'Administrator')
                self.log.debug('Added %s permission', permission)

        return True
