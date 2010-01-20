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
import traceback
from os.path import join

#Zope imports
from DateTime import DateTime
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from OFS.Folder import Folder

#Naaya imports
from Products.naayaUpdater.update_scripts import UpdateScript, PRIORITY
from Products.Naaya.managers.skel_parser import skel_parser

class UpdateMainSections(UpdateScript):
    """ Update portlet_maincategories  """
    id = 'update_main_sections'
    title = 'Update main sections portlet'
    #meta_type = 'Naaya Update Script'
    creation_date = DateTime('Jan 20, 2010')
    authors = ['David Batranu']
    #priority = PRIORITY['LOW']
    description = 'Renames portlet_mainsections so that the new-style portlet will be used. Also updates ep_collapse/ep_expand images.'
    #dependencies = []
    #categories = []

    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        self.update_portlet(portal, 'portlet_mainsections')
        self.update_images(portal, ['ep_expand.gif', 'ep_collapse.gif'])
        return True

    def update_portlet(self, portal, portlet_id):
        ptool = portal.getPortletsTool()
        if portlet_id not in ptool.objectIds():
            self.log.debug('%s does not exist in %s' % (portlet_id, portal.absolute_url(1)))
            return
        new_portlet_id = '%s_old-style' % portlet_id
        self.rename_object(ptool, portlet_id, new_portlet_id)

    def rename_object(self, container, old_id, new_id):
        try:
            container.manage_renameObjects([old_id], [new_id])
            self.log.debug('Renamed %s to %s' % (old_id, new_id))
        except Exception, e:
            self.log.error('Rename failed - "%s"' % str(e))
            self.log.error(traceback.format_exc())

    def get_schemes(self, portal):
        ltool = portal.getLayoutTool()
        for skin in ltool.objectValues('Naaya Skin'):
            for scheme in skin.objectValues('Naaya Scheme'):
                yield scheme

    def update_images(self, portal, images):
        for scheme in self.get_schemes(portal):
            for image in images:
                if image in scheme.objectIds():
                    self.update_image(scheme[image], self.get_image_file(portal, image))

    def get_skin_and_scheme_id(self, portal_path):
        skel = open(join(portal_path, 'skel', 'skel.xml'), 'rb')
        skel_handler, error = skel_parser().parse(skel.read())
        skel.close()
        skin = skel_handler.root.layout.default_skin_id
        scheme = skel_handler.root.layout.default_scheme_id
        return skin, scheme

    def get_image_file(self, portal, image_id):
        portal_path = self.get_portal_path(portal)
        skin_id, scheme_id = self.get_skin_and_scheme_id(portal_path)
        fs_layout = join(portal_path, 'skel', 'layout')
        fs_image = join(fs_layout, skin_id, scheme_id, image_id)
        return open(fs_image, 'rb').read()

    def update_image(self, image_ob, new_image_data):
        image_ob.update_data(new_image_data)
        self.log.debug('Updated %s' % image_ob.absolute_url(1))
