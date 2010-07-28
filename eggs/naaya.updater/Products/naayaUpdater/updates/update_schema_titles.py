#Zope imports
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from Persistence.mapping import PersistentMapping

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript
from naaya.core.utils import path_in_site
from naaya.core.zope2util import exorcize_local_properties

class UpdateExample(UpdateScript):
    """ Convert any Schema widget title from LocalProperty to normal string """
    title = 'Convert schema widget titles to string'
    creation_date = 'Jun 8, 2010'
    authors = ['Alex Morega']
    description = ("Convert any Schema widget title from "
                   "LocalProperty to normal string")

    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        self.log.info('updating %r', portal)

        portal_schemas = portal['portal_schemas']
        for schema in portal_schemas.objectValues('Naaya Schema'):
            for widget in schema.objectValues():
                names = exorcize_local_properties(widget)
                if names is not None:
                    self.log.info('cleaned up %r: %r',
                                  path_in_site(widget), names)

        return True
