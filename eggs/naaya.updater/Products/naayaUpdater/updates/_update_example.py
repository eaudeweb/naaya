from AccessControl import ClassSecurityInfo

from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from utils import physical_path

class UpdateExample(UpdateScript):
    """ Update example script  """
    title = 'Example of update script'
    creation_date = 'Aug 1, 2010'
    authors = ['Jane Doe']
    priority = PRIORITY['LOW']
    description = 'This is an example, change this description when implementing an update.'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        self.log.debug(physical_path(portal))
        return True
