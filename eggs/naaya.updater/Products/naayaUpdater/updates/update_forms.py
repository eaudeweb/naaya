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
# Alexandru Plugaru, Eau de Web


#Python imports
import re
from os.path import join

#Zope imports
import zLOG
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Naaya imports
from Products.NaayaCore.LayoutTool.Template import Template
from Products.naayaUpdater.updates import UpdateScript

from Products.Naaya import NySite as NySite_module
from Products.Naaya.managers.skel_parser import skel_parser
from Products.NaayaCore.managers.utils import html_diff, normalize_template
from Products.naayaUpdater.utils import (convertLinesToList, convertToList,
    get_template_content, readFile, get_portals,
    get_portal, get_portal_path, get_contenttype_content)

class UpdateForms(UpdateScript):
    """ Update forms in portal_forms """
    title = 'Update forms'
    authors = ['Alex Morega', 'Alexandru Plugaru']
    creation_date = 'Jan 01, 2010'

    def _update(self, portal):
        self.log.debug('/'.join(portal.getPhysicalPath()))

        return True

    def get_report(self, forms, portals='', exclude=False, REQUEST=None):
        if not REQUEST.has_key('show_report'): # TODO: remove this
            return

        report = {}
        forms = convertLinesToList(forms)
        portals_list = get_portals(self)
        portals_custom = []

        if portals.strip():
            for portal_id in portals.split(','):
                portals_custom.append(portal_id.strip())

        for portal in portals_list:
            if portals_custom:
                if exclude and portal.id in portals_custom: continue
                elif not exclude and portal.id not in portals_custom: continue

            portal_path = '/'.join(portal.getPhysicalPath()[1:])
            portal_forms = portal.portal_forms
            if forms:
                forms_list_tmp = []
                for form_line in forms: #Search in ZMI and FS for template patterns
                    for form_id in self.find_templates(re.compile(form_line), portal):
                        if form_id not in forms_list_tmp: forms_list_tmp.append(form_id)
                forms_list = forms_list_tmp
                del(forms_list_tmp)
            else:
                forms_list = portal_forms.objectIds()
            deltas = []

            for form_id in forms_list:
                try:
                    form_fs = portal_forms._default_form(form_id)
                except KeyError, exc_error:
                    zLOG.LOG('Naaya Updater', zLOG.ERROR, '%s: %s' % (portal.id, exc_error))
                    continue
                form_zmi = portal_forms._getOb(form_id)
                if form_fs and form_zmi:
                    t1 = normalize_template(form_fs._text)
                    t2 = normalize_template(form_zmi._text)
                    delta = {
                        'physical_path': '/'.join(form_zmi.getPhysicalPath()[1:]),
                        'absolute_url': form_zmi.absolute_url(),
                        'id': form_zmi.getId(),
                        'title': form_zmi.title_or_id(),
                    }
                    if t1 == t2:
                        delta['result'] = 'identical'
                    else:
                        delta['result'] = 'different'

                        delta['diff'] = html_diff(form_fs._text, form_zmi._text)
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
            portal = get_portal(self, form_path[:form_path.find('portal_forms')])
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
            portal = get_portal(self, form_path[:form_path.find('portal_forms')])
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
        return get_contenttype_content(self, id, portal) #fall back to Naaya pluggable content types

    def get_fs_template_content(self, id, portal):
        """
            return the content of the filesystem template
        """
        portal_path = get_portal_path(self, portal)
        skel_handler, error = skel_parser().parse(readFile(join(portal_path, 'skel', 'skel.xml'), 'r'))
        if skel_handler.root.forms is not None:
            return readFile(join(portal_path, 'skel', 'forms', '%s.zpt' % id), 'r')

    def list_fs_templates(self, portal):
        """
            return the list of the filesystem templates
        """
        portal_path = get_portal_path(self, portal)
        skel_handler, error = skel_parser().parse(readFile(join(portal_path, 'skel', 'skel.xml'), 'r'))
        if skel_handler.root.forms is not None:
            return [f.id for f in skel_handler.root.forms.forms]

    def list_pluggable_templates(self, portal):
        """ get filesystem templates from pluggable content """
        return [ tpl for meta_type in portal.get_pluggable_metatypes() for tpl in portal.get_pluggable_item(meta_type).get('forms', None) ]

    def find_templates(self, pattern, portal):
        """ Find templates based on a rexp pattern from FS and ZMI """
        portal_forms = getattr(portal, 'portal_forms', None)
        forms_list = portal_forms.objectValues([Template.meta_type ,])
        for zmi_tpl in forms_list:
            if pattern.match(zmi_tpl.getId()):
                yield zmi_tpl.getId()
    manage_update = PageTemplateFile('zpt/update_forms', globals())
