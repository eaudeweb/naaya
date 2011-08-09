from Products.naayaUpdater.updates import UpdateScript

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
