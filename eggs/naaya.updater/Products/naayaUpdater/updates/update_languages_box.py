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
import re
from os.path import join

#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from OFS.Folder import Folder

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from Products.naayaUpdater.utils import get_portal_path
from Products.Naaya.managers.skel_parser import skel_parser

updated_line = '<tal:block replace="structure here/languages_box"/>'
style_control_string = "bg-lang-btns.gif"
new_languages_style=\
"""
/* change language links */
#language {
    float:right;
    margin-right: 0.7em;
    white-space: nowrap !important;
    color: #333;
    /*padding: 0.3em 0.2em 0 0;*/
    position: relative;
    padding-top: 0.1em;
}
#language span {
    font-size:0.75em;
}
body #language a {
    display: block;
    width: 31px;
    height: 23px;
    line-height: 23px;
    font-size: 11px !important;
    color: #000;
    text-decoration: none;
    text-transform: capitalize;
    text-align: center;
    font-weight: normal;
    float: left;
    border: none;
    padding: 0;
}
#language form{
    display:inline;
}
#language a {
    background: url("bg-lang-btns.gif") no-repeat bottom left;
}
#language a:hover, #language a.current {
    background: url("bg-lang-btns.gif") no-repeat top left;
}
"""

class UpdateLanguagesBox(UpdateScript):
    """ Update languages_box script  """
    title = 'Update languages box to display language links inline'
    creation_date = 'Jan 11, 2010'
    authors = ['David Batranu']
    description = ('This update will modify standard_template'
                   'for the new languages_box display.')
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        ltool = portal.getLayoutTool()
        skin = ltool.getCurrentSkin()
        if 'standard_template' in skin.objectIds():
            self.update_standard_template(skin['standard_template'])
        else:
            self.log.debug('Skipping, standard_template not customised')
        self.add_image_to_current_skin(portal)
        self.remove_old_language_style(ltool)
        self.append_new_language_style(ltool)
        return True

    def add_image_to_current_skin(self, portal):
        ltool = portal.getLayoutTool()
        scheme = ltool.getCurrentSkinScheme()
        image = 'bg-lang-btns.gif'
        if image in scheme.objectIds():
            self.log.debug('Image exists in current scheme')
            return
        scheme.manage_addProduct['OFSP'].manage_addImage(id=image, file=None)
        self.update_image(scheme[image], self.get_image_file(portal, image))
        self.log.debug('Added image to skin')

    def remove_old_language_style(self, ltool):
        style = ltool.getCurrentSkinScheme()['style']
        input = style.read()
        if style_control_string in input:
            self.log.debug('Style seems updated. Skipping remove.')
            return
        output = re.sub(r'[^\n{}]*#language[^\n{]*{[^}]*}\n?\r?',
                        '', input, re.DOTALL)
        style.pt_edit(text=output, content_type="text/html")
        self.log.debug('Removed old language style')

    def append_new_language_style(self, ltool):
        style = ltool.getCurrentSkinScheme()['style']
        input = style.read()
        if style_control_string in input:
            self.log.debug('Style seems updated. Skipping append.')
            return
        output = input + new_languages_style
        style.pt_edit(text=output, content_type="text/html")
        self.log.debug('Appended new language style')

    def update_standard_template(self, template):
        content = template.document_src()
        if updated_line in content:
            self.log.debug('Update not needed for standard_template.')
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

    def get_skin_and_scheme_id(self, portal_path):
        skel = open(join(portal_path, 'skel', 'skel.xml'), 'rb')
        skel_handler, error = skel_parser().parse(skel.read())
        skel.close()
        skin = skel_handler.root.layout.default_skin_id
        scheme = skel_handler.root.layout.default_scheme_id
        return skin, scheme

    def get_image_file(self, portal, image_id):
        portal_path = get_portal_path(self, portal)
        skin_id, scheme_id = self.get_skin_and_scheme_id(portal_path)
        fs_layout = join(portal_path, 'skel', 'layout')
        fs_image = join(fs_layout, skin_id, scheme_id, image_id)
        return open(fs_image, 'rb').read()

    def update_image(self, image_ob, new_image_data):
        image_ob.update_data(new_image_data)
        self.log.debug('Updated %s' % image_ob.absolute_url(1))
