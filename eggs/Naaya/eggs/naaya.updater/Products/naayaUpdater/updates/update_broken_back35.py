from AccessControl import ClassSecurityInfo

from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from utils import physical_path

class UpdateBrokenBack35(UpdateScript):
    """ Removes a broken object from zodb """
    title = 'Remove zope.app.component.back35 from ZODB'
    creation_date = 'Apr 5, 2012'
    authors = ['Mihnea Simian']
    priority = PRIORITY['LOW']
    description = 'Removes the registrationManager broken object from sitemanager of portal'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        """
        We want to delete portal._sm['default'].registrationManager if existing.
        RegistrationManager was a class in zope.app.component.back35,
        module removed ages ago; not to be confused
        with deprecated zope.component.back35

        """
        sm_default = portal._sm['default']
        if hasattr(sm_default, 'registrationManager'):
            del sm_default.registrationManager
            self.log.debug("registrationManager property found and removed")
        else:
            self.log.debug("Skipped - no need to update.")

        return True
