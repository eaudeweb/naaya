#Python imports
import re

#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from OFS.Folder import Folder

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from utils import physical_path, list_folders_with_custom_index

class UpdateToStandardTemplateMacro(UpdateScript):
    """ Update custom indexes to use standard template macro """
    title = 'Update custom indexes to use standard template macro'
    creation_date = 'Dec 8, 2010'
    authors = ['Andrei Laza']
    priority = PRIORITY['LOW']
    description = 'Change custom indexes to use standard template macro instead of standard_html_header/footer'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        start = '<span tal:replace="structure here/standard_html_header" ?/>'
        end = '<span tal:replace="structure here/standard_html_footer" ?/>'

        replace_start = '<metal:block metal:define-macro="page" metal:extend-macro="here/standard_template_macro">\n\n<metal:block metal:fill-slot="body">'
        replace_end = '</metal:block>\n\n</metal:block>'

        self.log.debug(physical_path(portal))
        for folder in list_folders_with_custom_index(portal):
            folder.index.expand = 0

            tal = folder.index.read()
            tal = tal.strip()

            if re.search('^' + start, tal) is None:
                assert re.search(end + '$', tal) is None
                continue
            assert re.search(end + '$', tal) is not None

            t = 'matched folder: <a href="%(url)s/manage_main">%(text)s</a>'
            self.log.info(t % {'url': folder.absolute_url(),
                               'text': physical_path(folder)})

            tal = re.sub(start, replace_start, tal)
            tal = re.sub(end, replace_end, tal)

            folder.index.write(tal)
        return True
