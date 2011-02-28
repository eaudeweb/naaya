#Python imports

#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from OFS.Folder import Folder

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from utils import physical_path

class UpdateNotifyOnErrorsEmail(UpdateScript):
    """ Update notify on errors check to erros email address """
    title = 'Update notify on errors email'
    creation_date = 'Feb 28, 2011'
    authors = ['Andrei Laza']
    priority = PRIORITY['LOW']
    description = ' Update notify on errors check to erros email address.'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        if hasattr(portal.aq_base, 'notify_on_errors'):
            self.log.debug('Found attribute "notify_on_errors"')
            if portal.notify_on_errors:
                portal.notify_on_errors_email = portal.administrator_email
                self.log.debug('Copied value from administrator_email')
            else:
                portal.notify_on_errors_email = ''
                self.log.debug('Errors email is left blank')
            del portal.notify_on_errors
        else:
            self.log.debug('Could not find attribute "notify_on_errors"')
            self.log.debug('No need to update');
        return True

