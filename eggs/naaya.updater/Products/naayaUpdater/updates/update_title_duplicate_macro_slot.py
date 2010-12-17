#Python imports

#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from OFS.Folder import Folder

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from utils import physical_path

class UpdateSlotTitle(UpdateScript):
    """ Update slot title """
    title = 'Update slot title'
    creation_date = 'Dec 17, 2010'
    authors = ['Andrei Laza']
    priority = PRIORITY['HIGH']
    description = 'Modify slot name in standard template and fill slot in page templates from "title" to "header-title".'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        self.log.debug(physical_path(portal))
        objects = portal.ZopeFind(portal, obj_metatypes=['Page Template', 'Naaya Template'], search_sub=1)

        original1 = '<metal:block fill-slot="title">'
        original2 = '<metal:block metal:fill-slot="title">'

        target = '<metal:block metal:fill-slot="header-title">'

        t_found = 'Found duplicate title slot in: <a href="%(url)s/manage_main">%(text)s</a>'
        t_notfound = 'Not found %(text)s'

        for obj_id, obj in objects:
            tal = obj.read()

            ret = False
            if tal.find(original1) != -1:
                tal = tal.replace(original1, target)
                ret = True
            if tal.find(original2) != -1:
                tal = tal.replace(original2, target)
                ret = True

            if ret:
                self.log.info(t_found % {'url': '%s' % obj.absolute_url(),
                                   'text': '%s:%s' % (physical_path(obj), obj.meta_type) })
            else:
                self.log.info(t_notfound % {'url': '%s' % obj.absolute_url(),
                                   'text': '%s:%s' % (physical_path(obj), obj.meta_type) })


            obj.write(tal)

        return True
