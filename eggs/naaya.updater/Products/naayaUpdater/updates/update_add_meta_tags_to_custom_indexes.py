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

class UpdateAddMetaTagsToCustomIndexes(UpdateScript):
    """ Add meta information to custom indexes """
    title = 'Add meta information to custom indexes'
    creation_date = 'Dec 8, 2010'
    authors = ['Andrei Laza']
    priority = PRIORITY['LOW']
    description = 'Add meta information to custom indexes'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        t = '%(info)s folder: <a href="%(url)s/manage_main">%(text)s</a>'
        pt_start = '<metal:block metal:define-macro="page" metal:extend-macro="here/standard_template_macro">'
        old_meta_slot = '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" ?/>'
        meta_slot_start = '<metal:block fill-slot="meta">'
        meta_slot = '''
<metal:block fill-slot="meta">
    <meta tal:define="description here/description;
                      content python:here.html2text(description);"
          tal:condition="content"
          tal:attributes="content content" name="description" />
    <meta tal:condition="here/keywords"
          tal:attributes="content here/keywords" name="keywords" />
    <meta tal:attributes="content here/contributor" name="author" />
    <meta tal:attributes="content here/gl_get_selected_language"
          name="dc.language" />
    <meta tal:attributes="content string:${here/title} | ${here/site_title}"
          name="title" />
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
</metal:block>
'''

        self.log.debug(physical_path(portal))
        for folder in list_folders_with_custom_index(portal):
            tal = folder.index.read()
            if re.search(meta_slot_start, tal) is not None:
                self.log.info(t % {'info': 'already has meta slot',
                                   'url': folder.absolute_url(),
                                   'text': physical_path(folder)})
                continue

            if re.search('^' + pt_start, tal) is None and re.search(old_meta_slot, tal) is None:
                self.log.info(t % {'info': 'not using standard template macro and no old meta slot',
                                    'url': folder.absolute_url(),
                                    'text': physical_path(folder)})
                continue

            self.log.info(t % {'info': 'matched',
                               'url': folder.absolute_url(),
                               'text': physical_path(folder)})

            if re.search(old_meta_slot, tal) is not None:
                # replace only first occurance, remove the others
                tal = re.sub(old_meta_slot, meta_slot, tal, count=1)
                tal = re.sub(old_meta_slot, '', tal)
            elif re.search('^' + pt_start, tal) is not None:
                tal = re.sub(pt_start, '%s\n%s' % (pt_start, meta_slot), tal)
            folder.index.write(tal)
        return True
