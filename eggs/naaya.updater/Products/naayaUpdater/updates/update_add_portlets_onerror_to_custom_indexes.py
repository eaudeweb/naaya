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

        self.log.debug(physical_path(portal))
        for folder in list_folders_with_custom_index(portal):
            tal = folder.index.read()

            tal, strs = add_onerror_to_portlets_in_tal(tal)
            if strs == []:
                self.log.info(t % {'info': 'no match',
                                   'url': folder.absolute_url(),
                                   'text': physical_path(folder)})
            else:
                self.log.info(t % {'info': ','.join(strs) + ' portlet(s)',
                                   'url': folder.absolute_url(),
                                   'text': physical_path(folder)})
                folder.index.write(tal)
        return True

def add_onerror_to_portlets_in_tal(tal):
    left = '<(tal:block|span)\s+(tal:)?(content|replace)="structure python:item\\(\\{\'here\': here, \'portlet_macro\': \'portlet_left_macro\'\\}\\)" ?/>'
    center = '<(tal:block|span)\s+(tal:)?(content|replace)="structure python:item\\(\\{\'here\': here, \'portlet_macro\': \'portlet_center_macro\'\\}\\)" ?/>'
    right = '<(tal:block|span)\s+(tal:)?(content|replace)="structure python:item\\(\\{\'here\': here, \'portlet_macro\': \'portlet_right_macro\'\\}\\)" ?/>'

    span_left_new = '<span\s+(tal:)?(content|replace)="structure python:item\\(\\{\'here\': here, \'portlet_macro\': \'portlet_left_macro\'\\}\\)" on-error="python:here.log_page_error\\(error\\)" />'
    span_center_new = '<span\s+(tal:)?(content|replace)="structure python:item\\(\\{\'here\': here, \'portlet_macro\': \'portlet_center_macro\'\\}\\)" on-error="python:here.log_page_error\\(error\\)" />'
    span_right_new = '<span\s+(tal:)?(content|replace)="structure python:item\\(\\{\'here\': here, \'portlet_macro\': \'portlet_right_macro\'\\}\\)" on-error="python:here.log_page_error\\(error\\)" />'

    left_new = '<tal:block content="structure python:item({\'here\': here, \'portlet_macro\': \'portlet_left_macro\'})" on-error="python:here.log_page_error(error)" />'
    center_new = '<tal:block content="structure python:item({\'here\': here, \'portlet_macro\': \'portlet_center_macro\'})" on-error="python:here.log_page_error(error)" />'
    right_new = '<tal:block content="structure python:item({\'here\': here, \'portlet_macro\': \'portlet_right_macro\'})" on-error="python:here.log_page_error(error)" />'

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

    if re.search(span_left_new, tal):
        tal = re.sub(span_left_new, left_new, tal)
        strs.append('span_left_new')
    if re.search(span_center_new, tal):
        tal = re.sub(span_center_new, center_new, tal)
        strs.append('span_center_new')
    if re.search(span_right_new, tal):
        tal = re.sub(span_right_new, right_new, tal)
        strs.append('span_right_new')
    return tal, strs

