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
from os.path import join

#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Naaya imports
from Products.naayaUpdater.update_scripts import UpdateScript

from Products.Naaya import NySite as NySite_module
from Products.Naaya.managers.skel_parser import skel_parser
from Products.naayaUpdater.utils import (convertLinesToList, convertToList,
    get_template_content, normalize_template, html_diff, readFile)

class UpdateForms(UpdateScript):
    """ Update forms in portal_forms """
    id = 'update_forms'
    title = 'Update forms'
    authors = ['Alex Morega']

    def _update(self, portal):
        self.log.debug('/'.join(portal.getPhysicalPath()))

        return True

    def get_report(self, forms, all_forms=False, portals='', p_action='', REQUEST=None):
        if not REQUEST.has_key('show_report'): # TODO: remove this
            return

        report = {}
        forms_list = convertLinesToList(forms)
        portals_list = self.getPortals()
        portals_custom = []

        for portal_id in portals.split(','):
            portals_custom.append(portal_id.strip())

        for portal in portals_list:
            if p_action == 'ep' and portal.id in portals_custom: continue
            elif p_action != 'ep' and portal.id not in portals_custom: continue

            portal_path = '/'.join(portal.getPhysicalPath()[1:])
            if all_forms:
                forms_list = portal.portal_forms.objectIds()

            deltas = []
            for form_id in forms_list:
                form_path = '%s/portal_forms/%s' % (portal_path, form_id)
                form_fs = self.get_fs_template(form_id, portal)
                form_zmi_ob = self.get_zmi_template(form_path)
                if form_fs and form_zmi_ob:
                    form_zmi = get_template_content(form_zmi_ob)
                    t1 = normalize_template(form_fs)
                    t2 = normalize_template(form_zmi)
                    delta = {
                        'physical_path': '/'.join(form_zmi_ob.getPhysicalPath()[1:]),
                        'absolute_url': form_zmi_ob.absolute_url(),
                        'id': form_zmi_ob.getId(),
                        'title': form_zmi_ob.title_or_id(),
                    }
                    if t1 == t2:
                        delta['result'] = 'identical'
                    else:
                        delta['result'] = 'different'

                        delta['diff'] = html_diff(form_fs, form_zmi)
                    deltas.append(delta)

            if len(deltas) > 0:
                report[portal_path] = deltas
        return report

    def do_reload(self, fmod=[], fdel=[], forms='', REQUEST=None):
        """ reload portal forms """
        fmod = convertToList(fmod)
        fdel = convertToList(fdel)
        forms_list = convertLinesToList(forms)
        for form_path in fmod:
            portal = self.getPortal(form_path[:form_path.find('portal_forms')])
            form_id = form_path[form_path.find('portal_forms')+13:]
            form_ob = self.get_zmi_template(form_path)
            fs_content = self.get_fs_template(form_id, portal)
            try:
                if form_ob is None:
                    formstool_ob = portal.getFormsTool()
                    formstool_ob.manage_addTemplate(id=form_id, title='', file='')
                    form_ob = formstool_ob._getOb(form_id, None)
                form_ob.pt_edit(text=fs_content, content_type='')
                form_ob._p_changed = 1
            except Exception, error:
                print error
        for form_path in fdel:
            portal = self.getPortal(form_path[:form_path.find('portal_forms')])
            form_id = form_path[form_path.find('portal_forms')+13:]
            form_ob = self.get_zmi_template(form_path)
            form_ob.aq_parent.manage_delObjects([form_id])
        return REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_update')

    def get_zmi_template(self, path):
        """
            return a ZMI template object given the path
        """
        root = self.getPhysicalRoot()
        return root.unrestrictedTraverse(path, None)

    def get_fs_template(self, id, portal):
        """
            return a filesystem template object given the id
        """
        if id in self.list_fs_templates(portal):
            return self.get_fs_template_content(id, portal)
        elif id in self.list_fs_templates(NySite_module):   #fall back to Naaya filesytem templates
            return self.get_fs_template_content(id, NySite_module)
        return self.get_contenttype_content(id, portal) #fall back to Naaya pluggable content types

    def get_fs_template_content(self, id, portal):
        """
            return the content of the filesystem template
        """
        portal_path = self.get_portal_path(portal)
        skel_handler, error = skel_parser().parse(readFile(join(portal_path, 'skel', 'skel.xml'), 'r'))
        if skel_handler.root.forms is not None:
            return readFile(join(portal_path, 'skel', 'forms', '%s.zpt' % id), 'r')

    def list_fs_templates(self, portal):
        """
            return the list of the filesystem templates
        """
        portal_path = self.get_portal_path(portal)
        skel_handler, error = skel_parser().parse(readFile(join(portal_path, 'skel', 'skel.xml'), 'r'))
        if skel_handler.root.forms is not None:
            return [f.id for f in skel_handler.root.forms.forms]

    manage_update = PageTemplateFile('zpt/update_forms', globals())
