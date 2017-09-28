#Python imports

#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from OFS.Folder import Folder

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from utils import physical_path, list_folders_with_custom_index

class UpdateFolderListingMacro(UpdateScript):
    """ Update folder listing macro """
    title = ' Update folder listing macro '
    creation_date = 'Dec 8, 2010'
    authors = ['Andrei Laza']
    priority = PRIORITY['LOW']
    description = 'Update the way folder listing macro is used in folder indexes'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        t = '%(info)s folder: <a href="%(url)s/manage_main">%(text)s</a>'

        old_macro_start = '<metal:block use-macro="here/folder_listing/macros/content">'
        new_macro_start = '<metal:block use-macro="python:here.getFormsTool().getForm(\'folder_listing\').macros[\'listing\']">'

        self.log.debug(physical_path(portal))
        for folder in list_folders_with_custom_index(portal):
            tal = folder.index.read()
            if tal.find(new_macro_start) != -1:
                self.log.info(t % {'info': 'already uses new folder listing macro',
                                   'url': folder.absolute_url(),
                                   'text': physical_path(folder)})
                continue

            if tal.find(old_macro_start) == -1:
                self.log.info(t % {'info': 'not using folder listing macro',
                                   'url': folder.absolute_url(),
                                   'text': physical_path(folder)})
                continue

            self.log.info(t % {'info': 'replacing folder listing macro',
                               'url': folder.absolute_url(),
                               'text': physical_path(folder)})

            tal = tal.replace(old_macro_start, new_macro_start)
            folder.index.write(tal)

        custom_folder_index = portal.portal_forms._getOb('folder_index', default=None)
        if custom_folder_index is None:
            return True

        tal = custom_folder_index.read()
        if tal.find(new_macro_start) != -1:
            self.log.info('folder index already uses new folder listing macro')
            return True

        if tal.find(old_macro_start) == -1:
            self.log.info('folder index not using folder listing macro')
            return True

        self.log.info('folder index replacing folder listing macro')
        tal = tal.replace(old_macro_start, new_macro_start)
        custom_folder_index.write(tal)
        return True
