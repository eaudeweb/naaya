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
# Alex Morega, Eau de Web


#Python imports

#Zope imports

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript


class UpdateGeotaggedContent(UpdateScript):
    """ Update reinstall content types script  """
    title = 'Update portlet layout'
    authors = ['Alex Morega']
    creation_date = 'Jan 01, 2010'

    def _update(self, portal):
        self.log.debug('/'.join(portal.getPhysicalPath()))

        update_portlets_data(portal, self.log)

        for ob_path, delta_list in zpt_patches.iteritems():
            try:
                obj = portal.unrestrictedTraverse(ob_path)
            except:
                self.log.debug('Skipped %s - NotFound' % ob_path)
                continue
            update_zpt(obj, delta_list, self.log)

        try:
            header = portal.portal_layout.getCurrentSkin().site_header
            update_zpt(header, site_header_patches, self.log)
            self.log.debug('Updated site_header')
        except AttributeError:
            self.log.debug('Skipped site_header - NotFound')
        return True


def update_portlets_data(portal, log):
    site_prefix = '/'.join(portal.getPhysicalPath()[1:]) + '/'
    portal_portlets = portal._getOb('portal_portlets')

    repr(portal_portlets) # force ZODB to load the __dict__ of portal_portlets

    if '_portlet_layout' not in portal_portlets.__dict__:
        log.debug('no _portlet_layout dictionary; creating it')
        portal_portlets._portlet_layout = {}

    for portlet_id in portal.__dict__.get(
      '_portlets_manager__center_portlets_ids', []):
        log.debug('center portlet "%s" at "" no inherit' % portlet_id)
        portal_portlets.assign_portlet('', 'center', portlet_id, False)

    for portlet_id in portal.__dict__.get(
      '_portlets_manager__left_portlets_ids', []):
        log.debug('left portlet "%s" at ""' % portlet_id)
        portal_portlets.assign_portlet('', 'left', portlet_id, True)

    for folder_path, portlet_ids in portal.__dict__.get(
      '_portlets_manager__right_portlets_locations', {}).iteritems():
        if folder_path.startswith(site_prefix):
            fixed_folder_path = folder_path[len(site_prefix):]
            log.debug('location "%s" starts with site prefix; changing to  "%s"'
                    % (folder_path, fixed_folder_path))
            folder_path = fixed_folder_path
        for portlet_id in portlet_ids:
            log.debug('right portlet "%s" at "%s"' % (portlet_id, folder_path))
            portal_portlets.assign_portlet(folder_path, 'right', portlet_id, False)

    portal.__dict__['_portlets_manager__left_portlets_ids'] = []
    portal.__dict__['_portlets_manager__center_portlets_ids'] = []
    portal.__dict__['_portlets_manager__right_portlets_locations'] = {}
    portal._p_changed = 1

zpt_patches = {
    'portal_portlets/portlet_administration': [{
        'removed': ('<li tal:condition="canPublish"><a tal:attributes="'
            'href string:${site_url}/admin_leftportlets_html"'
            ' title="Arrange portlets around the site" i18n:attributes="title"'
            ' i18n:translate="">Arrange</a></li>'),
        'added': ('<li tal:condition="canPublish"><a tal:attributes="'
            'href string:${site_url}/portal_portlets/admin_layout"'
            ' title="Arrange portlet layout" i18n:attributes="title"'
            ' i18n:translate="">Arrange</a></li>'),
    }],
    'portal_forms/folder_index': [{
        'removed': ('<div id="center_content" tal:attributes="style'
            ' python:test(len(here.get_right_portlets_locations_objects(here))>0,'
            ' \'width: 78%;; overflow-x: auto;;\', \'\')">'),
        'added': ('<div id="center_content" tal:attributes="style'
            ' python:test(len(here.portal_portlets.get_portlets_for_obj(here,'
            ' \'right\'))>0, \'width: 78%;; overflow-x: auto;;\', \'\')">'),
    }, {
        'removed': ('</div>\r\n<div id="right_port">'),
        'added': ('</div>\r\n\r\n<tal:block tal:repeat="item python:here.portal_portlets.'
            'get_portlets_for_obj(here, \'center\')">\n'
            '\t<span tal:replace="structure python:item({\'here\': here,'
            ' \'portlet_macro\': \'portlet_center_macro\'})" />\r\n'
            '</tal:block>\r\n\r\n\r\n<div id="right_port">'),
    }, {
        'removed': ('<tal:block tal:repeat="item python:here.'
            'get_right_portlets_locations_objects(here)">'),
        'added': ('<tal:block tal:repeat="item python:here.'
            'portal_portlets.get_portlets_for_obj(here, \'right\')">'),
    }],
}
site_header_patches = [{
        'removed': ('<div id="container" tal:attributes="style'
            ' python:test(len(here.get_right_portlets_locations_objects(here))'
            ' or here.meta_type == here.get_constant(\'METATYPE_FOLDER\'), \'\','
            ' \'background: none\')">'),
        'added': ('<div id="container" tal:attributes="style'
            ' python:test(len(here.portal_portlets.get_portlets_for_obj(here,'
            ' \'right\')) or here.meta_type == here.get_constant(\'METATYPE_FOLDER\'),'
            ' \'\', \'background: none\')">'),
    }, {
        'removed': ('<tal:block tal:repeat="item here/get_left_portlets_objects">'),
        'added': ('<tal:block tal:repeat="item python:here.'
            'portal_portlets.get_portlets_for_obj(here, \'left\')">'),
    }]

def update_zpt(obj, delta_list, log):
    obj_path = '/'.join(obj.getPhysicalPath())

    new_text = obj._text
    for delta in delta_list:
        new_text = new_text.replace(delta['removed'], delta['added'])

    if new_text == obj._text:
        return

    log.debug('updating "%s"' % obj_path)
    obj.pt_edit(text=new_text.encode('utf-8'), content_type='')

