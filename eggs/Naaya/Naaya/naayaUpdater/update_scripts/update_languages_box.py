# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA). Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# David Batranu, Eau de Web


#Python imports

#Zope imports
from DateTime import DateTime
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from OFS.Folder import Folder

#Naaya imports
from Products.naayaUpdater.update_scripts import UpdateScript, PRIORITY

updated_line = '<tal:block replace="structure here/languages_box"/>'

class UpdateLanguagesBox(UpdateScript):
    """ Update languages_box script  """
    id = 'update_languages_box'
    title = 'Update languages box to display language links inline'
    #meta_type = 'Naaya Update Script'
    creation_date = DateTime('Jan 11, 2010')
    authors = ['David Batranu']
    #priority = PRIORITY['LOW']
    description = ('This update will modify standard_template'
                   'for the new languages_box display.')
    #dependencies = []
    #categories = []

    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        ltool = portal.getLayoutTool()
        skin = ltool.getCurrentSkin()
        if 'standard_template' in skin.objectIds():
            self.update_standard_template(skin['standard_template'])
        else:
            self.log.debug('Skipping, standard_template not customised')
        return True

    def update_standard_template(self, template):
        content = template.document_src()
        if updated_line in content:
            self.log.debug('Update not needed.')
            return
        lines = content.split('\n')
        start_index = None
        end_index = None
        i = -1
        #find out where the language div begins
        for line in lines:
            i = i + 1
            if line.strip() == '<div id="language">':
                start_index = i
                break

        #and where it ends
        for line in lines[start_index:]:
            i = i + 1
            if line.strip() == '</div>':
                end_index = i
                break

        #if both indexes are present
        if start_index and end_index:
            #build new 'languages' line
            new_line = [updated_line]
            #add proper indent to the line that is about to be inserted
            new_line[0] = self.get_indent(lines[end_index]) + new_line[0]
            #replace old language div with the new code
            new_content = lines[:start_index] + new_line + lines[end_index:]
            new_content = '\n'.join(new_content)
            new_content = new_content.encode('utf-8')
            template.pt_edit(text=new_content, content_type='')
            self.log.debug('Updated standard_template')
        else:
            self.log.debug('Cannot update standard_template')

    def get_indent(self, string):
        return string.split('<')[0]
