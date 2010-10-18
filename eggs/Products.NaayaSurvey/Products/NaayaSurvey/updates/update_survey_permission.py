from Products.NaayaSurvey.permissions import PERMISSION_EDIT_ANSWERS
from Products.naayaUpdater.updates import UpdateScript

class UpdatePermission(UpdateScript):
    """  """
    title='Update missing permission'
    description='Update missing PERMISSION_EDIT_ANSWERS in Naaya Survey'

    def _update(self, portal):
        """ """
        portal.manage_permission(PERMISSION_EDIT_ANSWERS,
                         ('Manager', 'Administrator', ), acquire=0)
        self.log.info("Added permission %r to %r", PERMISSION_EDIT_ANSWERS,
                                                    portal.absolute_url(1))
        return True
