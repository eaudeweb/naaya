#Python imports
import re

#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from OFS.Folder import Folder

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from update_list_custom_objects import (list_folders_with_custom_index,
                                        physical_path)

class UpdateAddPortletsOnerrorToCustomIndexes(UpdateScript):
    """ Add on error to portlets in custom indexes """
    title = ' Add on error to portlets in custom indexes '
    creation_date = 'Dec 9, 2010'
    authors = ['Andrei Laza']
    priority = PRIORITY['LOW']
    description = ' Add on error to portlets in custom indexes '
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        t = '%(info)s folder: <a href="%(url)s/manage_main">%(text)s</a>'

        left = '<(tal:block|span)\s+(tal:)?(content|replace)="structure python:item\\(\\{\'here\': here, \'portlet_macro\': \'portlet_left_macro\'\\}\\)" ?/>'
        center = '<(tal:block|span)\s+(tal:)?(content|replace)="structure python:item\\(\\{\'here\': here, \'portlet_macro\': \'portlet_center_macro\'\\}\\)" ?/>'
        right = '<(tal:block|span)\s+(tal:)?(content|replace)="structure python:item\\(\\{\'here\': here, \'portlet_macro\': \'portlet_right_macro\'\\}\\)" ?/>'

        left_new = '<tal:block content="structure python:item({\'here\': here, \'portlet_macro\': \'portlet_left_macro\'})" on-error="python:here.log_page_error(error)" />'
        center_new = '<tal:block content="structure python:item({\'here\': here, \'portlet_macro\': \'portlet_center_macro\'})" on-error="python:here.log_page_error(error)" />'
        right_new = '<tal:block content="structure python:item({\'here\': here, \'portlet_macro\': \'portlet_right_macro\'})" on-error="python:here.log_page_error(error)" />'

        self.log.debug(physical_path(portal))
        for folder in list_folders_with_custom_index(portal):
            tal = folder.index.read()
            if (re.search(left, tal) is None and re.search(center, tal) is None
                and re.search(right, tal) is None):
                self.log.info(t % {'info': 'no match',
                                   'url': folder.absolute_url(),
                                   'text': physical_path(folder)})
                continue

            strs = []
            if re.search(left, tal):
                tal = re.sub(left, left_new, tal)
                strs.append('left')
            if re.search(center, tal):
                tal = re.sub(center, center_new, tal)
                strs.append('center')
            if re.search(right, tal):
                tal = re.sub(right, right_new, tal)
                strs.append('right')
            self.log.info(t % {'info': ','.join(strs) + ' portlet(s)',
                               'url': folder.absolute_url(),
                               'text': physical_path(folder)})
            folder.index.write(tal)
        return True

