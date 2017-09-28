#Python imports
import re

#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from OFS.Folder import Folder

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from utils import physical_path
from update_add_portlets_onerror_to_custom_indexes import add_onerror_to_portlets_in_tal

class UpdateAddPortletsOnerrorToStandardTemplate(UpdateScript):
    """ Add on error to portlets in standard template """
    title = ' Add on error to portlets in standard template '
    creation_date = 'Dec 9, 2010'
    authors = ['Andrei Laza']
    priority = PRIORITY['LOW']
    description = ' Add on error to portlets in standard template '
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        t = '%(info)s: <a href="%(url)s/manage_main">current skin standard template</a>'

        self.log.debug(physical_path(portal))
        standard_template = get_standard_template(portal)
        tal = standard_template.read()
        tal, strs = add_onerror_to_portlets_in_tal(tal)
        if strs:
            self.log.info(t % {'info': ','.join(strs),
                               'url': standard_template.absolute_url()})
            standard_template.write(tal)
        return True

def get_standard_template(portal):
    return portal.getLayoutTool().getCurrentSkin().standard_template

