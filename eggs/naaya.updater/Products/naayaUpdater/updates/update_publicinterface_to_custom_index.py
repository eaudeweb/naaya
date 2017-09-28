#Python imports

#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from OFS.Folder import Folder

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from utils import physical_path

class UpdatePublicInterfaceToCustomIndex(UpdateScript):
    """ Update NyFolder publicinterface to custom_index """
    title = 'Update NyFolder publicinterface to custom_index'
    creation_date = 'Dec 14, 2010'
    authors = ['Andrei Laza']
    priority = PRIORITY['LOW']
    description = 'Update NyFolder publicinterface to custom_index.'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        self.log.debug(physical_path(portal))
        catalog = portal.getCatalogTool()

        for brain in catalog(meta_type='Naaya Folder'):
            folder = brain.getObject()
            folder = folder.aq_base
            self.convert_publicinterface_to_custom_index(folder)
        return True

    def convert_publicinterface_to_custom_index(self, folder):
        if hasattr(folder, 'publicinterface'):
            self.log.debug('%s has publicinterface', physical_path(folder))
            if folder.publicinterface:
                self.log.debug('%s has custom index', physical_path(folder))
                folder.custom_index = 'local:index'
            del folder.publicinterface

