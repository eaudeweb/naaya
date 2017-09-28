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
from os.path import join

#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from OFS.Folder import Folder

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from Products.naayaUpdater.utils import get_portal_path
from Products.NaayaCore.LayoutTool import Template
from Products.Naaya.managers.skel_parser import skel_parser


class UpdateExample(UpdateScript):
    """ Adds standard_template and renames old site_header and site_footer """
    title = 'Update to standard_template'
    creation_date = 'Dec 14, 2009'
    authors = ['David Batranu']
    description = 'Adds standard_template and renames old site_header and site_footer'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        ltool = portal.getLayoutTool()
        standard_template = self.get_fs_template(portal)
        self.log.debug('<span style="color: green">Default skin: %s</span>' % ltool.getCurrentSkinId())
        for skin in ltool.getSkinsList():
            if hasattr(skin.aq_base, 'standard_template'):
                self.log.debug('`%s` has standard_template' % skin.getId())
                continue
            self.update_skin(skin, standard_template)
            self.rename_old(skin)
        return True

    def rename_old(self, skin):
        try:
            skin.manage_renameObjects(['site_header', 'site_footer'],
                                      ['site_header_old', 'site_footer_old'])
            self.log.debug(('Renamed `site_header` and `site_footer`'
                            ' to `site_header_old` and `site_footer_old`.'))
        except:
            self.log.debug(('An error has occured while renaming'
                           ' old header and footer on `%s`.') % skin.getId())

    def update_skin(self, skin, standard_template):
        add_template = Template.manage_addTemplate
        add_template(skin, 'standard_template', 'Portal standard template')
        skin['standard_template'].pt_edit(standard_template, 'text/html')
        self.log.debug('Added standard_template in `%s` skin' % skin.getId())

    def get_skin_id(self, portal_path):
        skel = open(join(portal_path, 'skel', 'skel.xml'), 'rb')
        skel_handler, error = skel_parser().parse(skel.read())
        skel.close()
        return skel_handler.root.layout.default_skin_id

    def get_fs_template(self, portal):
        portal_path = get_portal_path(self, portal)
        skin_id = self.get_skin_id(portal_path)
        fs_layout = join(portal_path, 'skel', 'layout')
        fs_template = join(fs_layout, skin_id, 'standard_template.zpt')
        return open(fs_template, 'rb').read()
