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
import copy
import types

from OFS.Folder import Folder
import Globals
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl.Permissions import view_management_screens
from AccessControl import ClassSecurityInfo

from Products.Naaya import NySite as NySite_module
from Products.naayaUpdater.utils import *
try:
    from naaya.content.base.discover import get_pluggable_content
except ImportError:
    from Products.NaayaContent.discover import get_pluggable_content

from Products.naayaUpdater import update_scripts
from Products.Naaya.interfaces import INySite

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

    def update_ids(self):
        return sorted(NaayaUpdater.update_scripts.keys())

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
        return html_diff(zmi_data, fs_data)


#------------------------------------------------------------------------------------------------- API

    security.declarePrivate('get_root_ny_sites')
    def get_root_ny_sites(self, context, meta_types):
        """ """
        return [portal for portal in context.objectValues(meta_types)]

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
        res = []
        for ob in context.objectValues():
            if not INySite.providedBy(ob):
                continue
            if meta_types is not None and ob.meta_type not in meta_types:
                continue
            res.append(ob)
            res.extend(self.getPortals(ob, meta_types))
        return res

    security.declareProtected(view_management_screens, 'getPortalMetaTypes')
    def getPortalMetaTypes(self):
        """ """
        return self.pmeta_types

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
