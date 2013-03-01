from AccessControl import ClassSecurityInfo

from naaya.core.utils import force_to_unicode

from Products.naayaUpdater.updates import UpdateScript
from utils import get_standard_template

class MigrateGwCommonCss(UpdateScript):
    """ Migrate gw_common_css from Naaya style to Naaya Disk file """
    title = 'Migrate gw_common_css from Naaya style to Naaya Disk file'
    creation_date = 'Feb 28, 2013'
    authors = ['Mihai Tabara']
    description = 'Migrate gw_common_css from Naaya style to Naaya Disk file'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        layout_tool = portal.getLayoutTool()
        curr_scheme = layout_tool.getCurrentSkinScheme()

        common_css = curr_scheme._getOb('gw_common_css', None)
        if common_css:
            if common_css.meta_type == 'Naaya Style':
                curr_scheme.manage_delObjects(common_css.id)
                curr_scheme.manage_addDiskFile(pathspec='naaya.groupware:skel/layout/groupware/eionet/gw_common.css')
                self.log.debug('Css object migrated successfully')
            else:
                self.log.debug('Css object already migrated')
        else:
            self.log.debug('Css object not found')

        curr_skin = layout_tool.getCurrentSkin()
        if 'standard_template' in curr_skin.objectIds():
            template = curr_skin['standard_template']
            content = template.document_src()
            if content.find('gw_common.css') != -1:
                self.log.debug('Standard template already updated')
            else:
                new_content = content.replace('gw_common_css', 'gw_common.css')
                new_content = new_content.encode('utf-8')
                template.pt_edit(text=new_content, content_type='')
                self.log.debug('Standard template successfully updated')
        else:
            self.log.debug('Standard template not found')

        return True
