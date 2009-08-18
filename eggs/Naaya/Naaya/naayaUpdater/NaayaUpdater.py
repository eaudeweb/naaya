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
# Alec Ghica, Eau de Web
# Cornel Nitu, Eau de Web
# David Batranu, Eau de Web

#Python imports
import time
from os.path import join, isfile
import os
import sys
from OFS.History import html_diff
import copy
import types

from OFS.Folder import Folder
import Globals
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl.Permissions import view_management_screens
from AccessControl import ClassSecurityInfo

from Products.Naaya import NySite as NySite_module
from Products.Naaya.managers.skel_parser import skel_parser
from Products.naayaUpdater.utils import *
from Products.NaayaContent.discover import get_pluggable_content

from Products.naayaUpdater import update_scripts

UPDATERID = 'naaya_updates'
UPDATERTITLE = 'Update scripts for Naaya'
NAAYAUPDATER_PRODUCT_PATH = Globals.package_home(globals())

class NaayaUpdater(Folder):
    """NaayaUpdater class"""

    meta_type = 'Naaya Updater'
    icon = 'misc_/naayaUpdater/updater.jpg'
    update_scripts = {}

    def manage_options(self):
        """ """
        l_options = (
            {'label': 'Updates', 'action': 'index_html'},
            {'label':'Available content updates', 'action':'available_content_updates',},
            {'label':'Applied content updates', 'action':'applied_content_updates',},
            {'label': 'Layout updates', 'action': 'layout_updates'},
            {'label':'Contents', 'action':'manage_main',
             'help':('OFSP','ObjectManager_Contents.stx')},
         )
        return l_options

    security = ClassSecurityInfo()

    def __init__(self, id):
        """constructor"""
        self.id = id
        self.title = UPDATERTITLE
        self.pmeta_types = ['Naaya Site', 'CHM Site', 'EnviroWindows Site', 'SEMIDE Site', 'SMAP Site']
        self.refresh_updates_dict()

    def __bobo_traverse__(self, REQUEST, key):
        if hasattr(self, key):
            return getattr(self, key)
        if key in NaayaUpdater.update_scripts:
            return NaayaUpdater.update_scripts[key]().__of__(self)

    def refresh_updates_dict(self):
        NaayaUpdater.update_scripts = {}
        update_scripts.register_scripts(self)

    def register_update_script(self, key, update_script):
        NaayaUpdater.update_scripts[key] = update_script

    security.declareProtected(view_management_screens, 'get_updates') 
    def get_updates(self):
        return NaayaUpdater.update_scripts

    security.declareProtected(view_management_screens, 'get_update_script_url')
    def get_update_script_url(self, key):
        return self.absolute_url() + '/' + key

    security.declareProtected(view_management_screens, 'get_update_script_title')
    def get_update_script_title(self, key):
        return NaayaUpdater.update_scripts[key].title

    ###
    #General stuff
    ######
    security.declareProtected(view_management_screens, 'index_html')
    index_html = PageTemplateFile('zpt/updater_index', globals())

    security.declareProtected(view_management_screens, 'available_content_updates')
    available_content_updates = PageTemplateFile('zpt/available_content_updates', globals())

    security.declareProtected(view_management_screens, 'applied_content_updates')
    applied_content_updates = PageTemplateFile('zpt/applied_content_updates', globals())

    security.declareProtected(view_management_screens, 'layout_updates')
    layout_updates = PageTemplateFile('zpt/layout_updates', globals())

    security.declareProtected(view_management_screens, 'get_new_content_updates')
    def get_new_content_updates(self):
        updates = self.objectValues()
        for update in updates:
            if update.title_or_id() == 'This object from the naayaUpdater product is broken!':
                continue
            last_run = getattr(update, 'last_run', None)
            if last_run is None:
                yield update

    security.declareProtected(view_management_screens, 'get_applied_content_updates')
    def get_applied_content_updates(self):
        updates = self.objectValues()
        for update in updates:
            if update.title_or_id() == 'This object from the naayaUpdater product is broken!':
                continue
            last_run = getattr(update, 'last_run', None)
            if last_run is not None:
                yield update

    security.declareProtected(view_management_screens, 'run_content_updates')
    def run_content_updates(self, REQUEST=None, **kwargs):
        """ Run content updates"""
        if REQUEST:
            kwargs.update(REQUEST.form)
        uids = kwargs.get('uids', ())
        start = time.time()
        for uid in uids:
            update = getattr(self, uid, None)
            if update:
                update.update()
        stop = time.time()
        updates_no = len(uids)
        run_time = int(stop - start)
        message = 'Run %s update%s in %s second%s' % (
            updates_no,
            updates_no != 1 and 's' or '',
            run_time,
            run_time != 1 and 's' or ''
        )
        if REQUEST:
            REQUEST.RESPONSE.redirect('available_content_updates?manage_tabs_message=%s' % message)
        return message

    def _normalize_template(self, src):
        src = (src.strip().replace('\r', '')+'\n')
        if isinstance(src, unicode):
            src = src.encode('utf-8')
        return src

    security.declareProtected(view_management_screens, 'show_html_diff')
    def show_html_diff(self, source, target):
        """ """
        #return html_diff(source, target)
        import difflib
        from cStringIO import StringIO
        lines = lambda s: StringIO(self._normalize_template(s)).readlines()
        htmlquote = lambda s: s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        output = StringIO()
        output.write('<div style="font-family: monospace;">')
        for line in difflib.unified_diff(lines(source), lines(target)):
            if line.startswith('+'):
                cls = 'line_added'
            elif line.startswith('-'):
                cls = 'line_removed'
            elif line.startswith('@@'):
                cls = 'line_heading'
            else:
                cls = 'line_normal'
            output.write('<div class="%s">%s</div>\n' % (cls, htmlquote(line)))
        output.write('</div>')
        return output.getvalue()
        #return ''.join(htmlquote(s)+'<br/>' for s in difflib.unified_diff(lines(source), lines(target)))
        #return difflib.HtmlDiff().make_table(lines(source), lines(target))

    security.declareProtected(view_management_screens, 'get_fs_data')
    def get_fs_data(self, fpath):
        """ """
        return open(join(INSTANCE_HOME, fpath)).read()

    security.declareProtected(view_management_screens, 'show_diffTemplates')
    def show_diffTemplates(self, fpath, ppath):
        """ """
        zmi_obj = self.unrestrictedTraverse(ppath, None)
        fs_data = open(join(INSTANCE_HOME, fpath)).read()
        try:
            zmi_data = zmi_obj._body
        except AttributeError:
            try:
                zmi_data = zmi_obj.body
            except AttributeError:
                zmi_data = zmi_obj.document_src()
        return self.show_html_diff(zmi_data, fs_data)

    ###
    #See all modified forms
    ######
    security.declareProtected(view_management_screens, 'show_alldiff_html')
    show_alldiff_html = PageTemplateFile('zpt/show_alldiff', globals())

    security.declareProtected(view_management_screens, 'getAllModified')
    def getAllModified(self, meta_types, nonrecursive=True, forms=True, contentype_forms=False, portlets=False, layout=False):
        """ """
        root = self.getPhysicalRoot()
        meta_types = convertToList(meta_types)
        out_modified = []
        out_unmodified = []
        out_diff = 0

        if nonrecursive:
            for portal in self.get_root_ny_sites(root, meta_types):
                modified, unmodified, list_diff = self.get_modified_forms(portal)
                out_modified.extend(modified)
                out_unmodified.extend(unmodified)
                out_diff += list_diff
        else:
            portals_list = self.getPortals(root, meta_types)
            for portal in portals_list:
                modified, unmodified, list_diff = self.get_modified_forms(portal)
                out_modified.extend(modified)
                out_unmodified.extend(unmodified)
                out_diff += list_diff
        return out_modified, out_unmodified, out_diff



    ###
    #Overwritte Naaya forms
    ######
    security.declareProtected(view_management_screens, 'overwritte_forms_html')
    overwritte_forms_html = PageTemplateFile('zpt/overwritte_forms', globals())

    security.declareProtected(view_management_screens, 'quick_overwritte_forms_html')
    quick_overwritte_forms_html = PageTemplateFile('zpt/quick_overwritte_forms', globals())

    security.declareProtected(view_management_screens, 'diff_forms_html')
    diff_forms_html = PageTemplateFile('zpt/diff_forms', globals())

#    security.declareProtected(view_management_screens, 'getPortalCreationDate')
#    def getPortalCreationDate(self, portal):
#        """ """
#        creation_date = portal.error_log.bobobase_modification_time()
#        for form in portal.getFormsTool().objectValues("Naaya Template"):
#            creation_date = minDate(form.bobobase_modification_time(), creation_date)
#        return creation_date


#------------------------------------------------------------------------------------------------- API

    security.declarePrivate('get_root_ny_sites')
    def get_root_ny_sites(self, context, meta_types):
        """ """
        return [portal for portal in context.objectValues(meta_types)]

    security.declarePrivate('get_modified_forms')
    def get_modified_forms(self, portal):
        """
            return the list of modified forms inside this portal ?????
        """
        EXCLUSION_FORMS_LIST = ['site_admin_comments', 'site_admin_network', 'site_external_search', 'site_admin_properties']
        modified = []   #modified forms list
        unmodified = [] #unmodified forms list

        forms_date_list = self.list_zmi_templates(portal)
        for f in self.list_zmi_templates(portal):
            if f.id not in EXCLUSION_FORMS_LIST:
                if f.bobobase_modification_time() > self.getFTCreationDate(portal):
                    modified.append(f)
                else:
                    unmodified.append(f)
        list_diff = len(forms_date_list) - len(modified) - len(EXCLUSION_FORMS_LIST)   #number of unmodified forms
        return modified, unmodified, list_diff

    security.declarePrivate('get_portal_path')
    def get_portal_path(self, portal):
        """
            return the portal path given the metatype
        """
        if isinstance(portal, types.ModuleType):
            m = portal
        else:
            if isinstance(portal, NySite_module.NySite):
                portal = portal.__class__
            m = sys.modules[portal.__module__]
        return os.path.dirname(m.__file__)

        metatype = portal.meta_type
        ppath = NAAYAUPDATER_PRODUCT_PATH.split(os.sep)[:-1]
        pname = metatype.split(' ')[0]
        if pname.lower() == 'chm': pname = 'CHM2'
        ppath.append(pname)
        return str(os.sep).join(ppath)


    security.declarePrivate('get_contenttype_content')
    def get_contenttype_content(self, id, portal):
        """
            return the content of the filesystem content-type template
        """
        portal_path = self.get_portal_path(portal)
        data_path = join(portal_path, 'skel', 'forms')

        for meta_type in portal.get_pluggable_metatypes():
            pitem = portal.get_pluggable_item(meta_type)
            #load pluggable item's data
            for frm in pitem['forms']:
                if id == frm:
                    frm_name = '%s.zpt' % frm
                    if isfile(join(data_path, frm_name)):
                        #load form from the 'forms' directory because it si customized
                        return readFile(join(data_path, frm_name), 'r')
                    else:
                        #load form from the pluggable meta type folder
                        return readFile(join(pitem['package_path'], 'zpt', frm_name), 'r')
                    break


    security.declarePrivate('list_zmi_templates')
    def list_zmi_templates(self, portal):
        """
            return the list of the ZMI templates
        """
        return portal.getFormsTool().objectValues("Naaya Template")


    security.declarePrivate('list_fs_templates')
    def list_fs_templates(self, portal):
        """
            return the list of the filesystem templates
        """
        portal_path = self.get_portal_path(portal)
        skel_handler, error = skel_parser().parse(readFile(join(portal_path, 'skel', 'skel.xml'), 'r'))
        if skel_handler.root.forms is not None:
            return [f.id for f in skel_handler.root.forms.forms]


    security.declarePrivate('get_fs_template_content')
    def get_fs_template_content(self, id, portal):
        """
            return the content of the filesystem template
        """
        portal_path = self.get_portal_path(portal)
        skel_handler, error = skel_parser().parse(readFile(join(portal_path, 'skel', 'skel.xml'), 'r'))
        if skel_handler.root.forms is not None:
            return readFile(join(portal_path, 'skel', 'forms', '%s.zpt' % id), 'r')


    security.declarePrivate('get_fs_template')
    def get_fs_template(self, id, portal):
        """
            return a filesystem template object given the id
        """
        if id in self.list_fs_templates(portal):
            return self.get_fs_template_content(id, portal)
        elif id in self.list_fs_templates(NySite_module):   #fall back to Naaya filesytem templates
            return self.get_fs_template_content(id, NySite_module)
        return self.get_contenttype_content(id, portal) #fall back to Naaya pluggable content types

    security.declarePrivate('get_fs_forms')
    def get_fs_forms(self, portal):
        """
            return a filesystem template object given the id
        """
        flist = {}
        #load contenttype forms
        for meta_type in portal.get_pluggable_metatypes():
            #chech if the meta_type is installed
            if portal.is_pluggable_item_installed(meta_type):
                item = portal.get_pluggable_item(meta_type)
                for f in item['forms']:
                    flist[f] = '%s/portal_forms/%s' % (portal.absolute_url(1), f)

        #load portal forms
        for f in self.list_fs_templates(NySite_module):
            flist[f] = '%s/portal_forms/%s' % (portal.absolute_url(1), f)
        for f in self.list_fs_templates(portal):
            flist[f] = '%s/portal_forms/%s' % (portal.absolute_url(1), f)

        return flist

#        if id in self.list_fs_templates(portal):
#            return self.get_fs_template_content(id, portal)
#        elif id in self.list_fs_templates(NySite_module):   #fall back to Naaya filesytem templates
#            return self.get_fs_template_content(id, NySite_module)
#        return self.get_contenttype_content(id, portal) #fall back to Naaya pluggable content types


    security.declarePrivate('get_zmi_template')
    def get_zmi_template(self, path):
        """
            return a ZMI template object given the path
        """
        root = self.getPhysicalRoot()
        return root.unrestrictedTraverse(path, None)


    security.declarePrivate('get_template_content')
    def get_template_content(self, form):
        """
            return a template content given the object
        """
        try:
            return form._text
        except:
            return str(form.data)

#----------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------EXTERNAL

    security.declareProtected(view_management_screens, 'getPortal')
    def getPortal(self, ppath):
        """ """
        root = self.getPhysicalRoot()
        return root.unrestrictedTraverse(ppath)

    security.declareProtected(view_management_screens, 'getPortals')
    def getPortals(self, context=None, meta_types=None):
        """
            return the portals list
        """
        if context is None:
            context = self.getPhysicalRoot()
        if meta_types is None:
            meta_types = self.getPortalMetaTypes()
        res = []
        for portal in context.objectValues(meta_types):
            res.append(portal)
            if len(portal.objectValues(meta_types)) > 0:
                res.extend(self.getPortals(portal, meta_types))
        return res

    security.declareProtected(view_management_screens, 'getPortalMetaTypes')
    def getPortalMetaTypes(self):
        """ """
        return self.pmeta_types

    security.declareProtected(view_management_screens, 'generateFTCreationDate')
    def generateFTCreationDate(self, portal):
        """
            generate creation date
        """
        flist = [(f.bobobase_modification_time(), f) for f in self.list_zmi_templates(portal)]
        flist.sort()
        return flist[0][0]

    security.declareProtected(view_management_screens, 'testFTCreationDate')
    def testFTCreationDate(self, portal):
        """
            test PortalForms creation date
        """
        forms_tool = portal.getFormsTool()
        return hasattr(forms_tool, 'creation_date')

    security.declareProtected(view_management_screens, 'setFTCreationDate')
    def setFTCreationDate(self, portal):
        """
            set PortalForms creation date
        """
        forms_tool = portal.getFormsTool()
        if not self.testFTCreationDate(portal):
            forms_tool.creation_date = self.generateFTCreationDate(portal)
            forms_tool._p_changed = 1

    security.declareProtected(view_management_screens, 'getFTCreationDate')
    def getFTCreationDate(self, portal):
        """
            test PortalForms creation date
        """
        forms_tool = portal.getFormsTool()
        return getattr(forms_tool, 'creation_date', None)

    security.declareProtected(view_management_screens, 'diffTemplates')
    def diffTemplates(self, id, fpath, ppath):
        """ return the differences between the ZMI and the filesytem versions of the template"""
        portal = self.getPortal(ppath)
        fs = self.get_fs_template(id, portal)
        zmi = self.get_zmi_template(fpath)
        return self.show_html_diff(fs, self.get_template_content(zmi))


    security.declareProtected(view_management_screens, 'getReportModifiedForms')
    def getReportModifiedForms(self, ppath, REQUEST=None):
        """ overwritte Naaya portal forms """
        if REQUEST.has_key('show_report'):
            portal = self.getPortal(ppath)
            out_modified = []
            modified, unmodified, list_diff = self.get_modified_forms(portal)
            #check for modified
            buf = copy.copy(modified)
            for m in buf:
                zmi = self.get_fs_template(m.id, portal)
                if create_signature(self.get_template_content(m)) == create_signature(zmi):
                    modified.remove(m)
            #check for unmodified
            buf = copy.copy(unmodified)
            for m in buf:
                zmi = self.get_fs_template(m.id, portal)
                if create_signature(self.get_template_content(m)) == create_signature(zmi):
                    unmodified.remove(m)
            out_modified.extend(modified)
            return out_modified, len(unmodified)

    security.declareProtected(view_management_screens, 'reloadPortalForms')
    def reloadPortalForms(self, ppath, funmod=False, fmod=[], REQUEST=None):
        """ reload portal forms """
        portal = self.getPortal(ppath)
        fmods = convertToList(fmod)
        #modified forms
        for f in fmods:
            form_ob = self.get_zmi_template(f)
            fs_content = self.get_fs_template(form_ob.id, portal)
            try:
                form_ob.pt_edit(text=fs_content, content_type='')
            except Exception, error:
                print error
        #unmodified forms
        if funmod:
            modified, unmodified, list_diff = self.get_modified_forms(portal)
            all_forms = self.get_fs_forms(portal)
            for form_id, form_path in all_forms.items():
                if form_path not in [m.absolute_url(1) for m in modified]:
                    fs_content = self.get_fs_template(form_id, portal)
                    form_ob = self.get_zmi_template(form_path)
                    try:
                        if form_ob is None:
                            formstool_ob = portal.getFormsTool()
                            formstool_ob.manage_addTemplate(id=form_id, title='', file='')
                            form_ob = formstool_ob._getOb(form_id, None)
                        form_ob.pt_edit(text=fs_content, content_type='')
                        form_ob._p_changed = 1
                    except Exception, error:
                        print error

        return REQUEST.RESPONSE.redirect('%s/overwritte_forms_html?ppath=%s&show_report=1' % (self.absolute_url(), ppath))

    security.declareProtected(view_management_screens, 'formatDateTime')
    def formatDateTime(self, p_date):
        """ date is a DateTime object. This function returns a string 'dd month_name yyyy' """
        try: return p_date.strftime('%d/%m/%Y')
        except: return ''

    security.declareProtected(view_management_screens, 'setFTDateFormsPage')
    def setFTDateFormsPage(self, ppath, REQUEST=None):
        """
            Set creation date
        """
        portal = self.getPortal(ppath)
        self.setFTCreationDate(portal)
        return REQUEST.RESPONSE.redirect('%s/overwritte_forms_html?ppath=%s&show_report=1' % (self.absolute_url(), ppath))

    security.declareProtected(view_management_screens, 'getReportQuickModifiedForms')
    def getReportQuickModifiedForms(self, forms, all_forms=False, portals='', p_action='', REQUEST=None):
        """ """
        if not REQUEST.has_key('show_report'):
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

            res = []
            portal_path = '/'.join(portal.getPhysicalPath()[1:])
            if all_forms:
                forms_list = portal.portal_forms.objectIds()

            for form_id in forms_list:
                form_path = '%s/portal_forms/%s' % (portal_path, form_id)
                form_fs = self.get_fs_template(form_id, portal)
                form_zmi_ob = self.get_zmi_template(form_path)
                if form_fs and form_zmi_ob:
                    t1 = self._normalize_template(form_fs)
                    t2 = self._normalize_template(self.get_template_content(form_zmi_ob))
                    if t1 != t2:
                        res.append((form_zmi_ob, 'edit'))
                if form_fs and not form_zmi_ob:
                    res.append((form_id, 'add'))
            if len(res) > 0: report[portal_path] = res
        return report

    security.declareProtected(view_management_screens, 'reloadQuickPortalForms')
    def reloadQuickPortalForms(self, fmod=[], fdel=[], forms='', REQUEST=None):
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
        return REQUEST.RESPONSE.redirect('%s/quick_overwritte_forms_html' % (self.absolute_url()))

    security.declareProtected(view_management_screens, 'generateFormPath')
    def generateFormPath(self, form_id, portal):
        """ """
        return '%s/portal_forms/%s' % (portal.absolute_url(1), form_id)

    security.declareProtected(view_management_screens, 'generateFormPath')
    def updateBrokenDescription(self, portal_id='hazred'):
        """ update broken description """
        root = self.getPhysicalRoot()
        portal_ob = root._getOb(portal_id, None)
        if portal_ob is not None:
            items = portal_ob.getCatalogedObjects()
            for item in items:
                descr = item.getPropertyValue('description', 'en')
                try:
                    item.createProperty('description', html_decode(descr), 'en')
                    item._p_changed = 1
                except:
                    print item.absolute_url(0)
            return 'done'
        else:
            return 'portal %s not found' % portal_id



#layout updates
    security.declareProtected(view_management_screens, 'updateStyle')
    def updateStyle(self, target_portals=[], style_name='', class_name='', scheme_ids=[], style_declaration=[], REQUEST=None):
        """ update specified class name in given style """
        if 'all_portals' in target_portals or not target_portals:
            portals = self.getPortals()
        else:
            portals = [self.getPortal(portal) for portal in target_portals]

        for portal in portals:
            schemes = portal.getLayoutTool().getCurrentSkinSchemes()
            for scheme in schemes:
                if not scheme_ids or scheme.getId() in scheme_ids:
                    style_ob = getattr(scheme, style_name)
                    style = style_ob.read()
                    if not style_declaration:
                        #if no new selector style was submitted, return the first occurence of the given selector
                        return self.getCSSRuleText(self.makeCSSSheet(style), class_name)
                    #edit style
                    new_style = self.editCSS(style, class_name, style_declaration)
                    #commit changes
                    self.commitCSS(style_ob, new_style._pprint())
        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect('%s/layout_updates?save=ok' % (self.absolute_url()))

    security.declareProtected(view_management_screens, 'editCSS')
    def editCSS(self, style, class_name, style_declaration):
        """ make changes to the CSSSheet and return it"""
        ob_sheet = self.makeCSSSheet(style)
        ob_rule = self.findCSSRule(ob_sheet, class_name)
        if not ob_rule:
            ob_rule = self.makeCSSRule(class_name)
            self.addCSSRuleToSheet(ob_sheet, ob_rule)
        new_dec = self.makeCSSDeclaration(style_declaration)
        ob_rule.style = new_dec
        return ob_sheet

    security.declareProtected(view_management_screens, 'commitCSS')
    def commitCSS(self, ny_style=None, new_style=''):
        """ write changes to the Naaya Scheme """
        new_style = new_style.encode('utf-8')
        ny_style.pt_edit(text=new_style, content_type='text/html')

    security.declareProtected(view_management_screens, 'findCSSRule')
    def findCSSRule(self, sheet=None, string=''):
        """ returns the selector object """
        from cssutils.cssstylerule import StyleRule
        rules = sheet.getRules()
        for rl in rules:
            if isinstance(rl, StyleRule) and rl.selectorText == u'%s' % string:
                return rl

    security.declareProtected(view_management_screens, 'getCSSRuleText')
    def getCSSRuleText(self, sheet=None, string=''):
        """ returns the selector text """
        ob_rule = self.findCSSRule(sheet, string)
        if ob_rule:
            return ob_rule.cssText
        else:
            return 'CSS Rule does not exist in specified style.'

    security.declareProtected(view_management_screens, 'makeCSSSheet')
    def makeCSSSheet(self, style=''):
        """ creates the cssutils css sheet from the given style string """
        #disable file debugging
        import logging
        from cssutils.cssparser import CSSParser
        log = logging.getLogger('parser')
        hndl = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)s\t%(message)s')
        hndl.setFormatter(formatter)
        log.addHandler(hndl)
        log.setLevel(logging.NOTSET)   #for debugging set to DEBUG

        ob = CSSParser(log=log)
        ob.parseString(style)
        return ob.getStyleSheet()

    security.declareProtected(view_management_screens, 'makeCSSRule')
    def makeCSSRule(self, selector=''):
        """ creates a new CSS Rule with the given selector text """

        from cssutils.cssstylerule import StyleRule
        ob_rule = StyleRule()
        ob_rule.selectorText = selector
        return ob_rule

    security.declareProtected(view_management_screens, 'addCSSRuleToSheet')
    def addCSSRuleToSheet(self, sheet=None, rule=None):
        """ appends the given rule to the specified sheet"""

        sheet.addRule(rule)

    security.declareProtected(view_management_screens, 'makeCSSDeclaration')
    def makeCSSDeclaration(self, style_declaration=[]):
        """ creates a selector body with the passed properties and values"""
        from cssutils.cssstyledeclaration import StyleDeclaration
        dc = StyleDeclaration()
        for dec in style_declaration:
            n, v = dec.split(':')
            n, v = self.cleanCSSValues(n, v)
            dc.setProperty(n, v)
        return dc

    security.declareProtected(view_management_screens, 'editCSSProperty')
    def editCSSProperty(self, rule=None, name='', value=''):
        """ changes a style property from a selector body """
        style_dec = rule.style
        style_dec.setProperty(name, value)

    security.declareProtected(view_management_screens, 'removeCSSProperty')
    def removeCSSProperty(self, rule=None, name=''):
        """ removes a style property from a selector body """
        style_dec = rule.style
        style_dec.removeProperty(name)

    security.declareProtected(view_management_screens, 'cleanCSSValues')
    def cleanCSSValues(self, n='', v=''):
        """ """
        if n.endswith(' '): n = n[:-1]
        if v.startswith(' '): v = v[1:]
        if v.endswith(';'): v = v[:-1]
        return n, v


Globals.InitializeClass(NaayaUpdater)

