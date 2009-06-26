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
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cristian Romanescu, Eau de Web
from os.path import join, isfile
import md5

from Products.naayaUpdater.updates import nyUpdateLogger as logger
from Products.naayaUpdater.NaayaContentUpdater import NaayaContentUpdater
from Products.naayaUpdater.updates import nyUpdateLogger as logger
from Products.NaayaCore.LayoutTool.Template import Template
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl.Permissions import view_management_screens
from AccessControl import ClassSecurityInfo

from Globals import InitializeClass
from Products.Naaya.managers.skel_parser import skel_parser
from difflib import ndiff, IS_CHARACTER_JUNK, IS_LINE_JUNK
from Products.Naaya.constants import *
try:
    from Products.EnviroWindows.constants import ENVIROWINDOWS_PRODUCT_PATH
except ImportError: pass
try:
    from Products.SMAP.constants import SMAP_PRODUCT_PATH
except ImportError: pass
try:
    from Products.CHM2.constants import CHM2_PRODUCT_PATH
except ImportError: pass
            
from Products.NaayaCore.managers.utils import file_utils
from Products.NaayaCore.LayoutTool.Skin import Skin

class SiteUpdateSummary:
    """
    """
    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")


    def __init__(self):
        """ """
        self.forms_status = {}
        self.skins_status = {}
        self.ob = None


    def getName(self):
        """ """
        return self.ob.id


    def getSiteObject(self):
        return self.ob


    def getFormsStatus(self):
        """ """
        return self.forms_status

    def getSkinsStatus(self):
        """ """
        return self.skins_status

    def isUpdateNeeded(self):
        return 1 in self.forms_status.values() or 1 in self.skins_status.values()

InitializeClass(SiteUpdateSummary)
    

class CustomContentUpdater(NaayaContentUpdater):
    """ This update applies to process of moving forms to disk]
    It will set all the forms as customized (so they will still be loaded from ZODB)
    for existing sites. Users then should "manually" mark existing forms
    to be loaded from disk if they do not differ from their disk counterparts.
    """
    forms_on_disk = {}
    forms_paths = {}
    patterns = ('-', '+', '?')

    security = ClassSecurityInfo()

    security.declareProtected(view_management_screens, 'index_html')
    index_html = PageTemplateFile('zpt/update_forms_to_disk', globals())


    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Update Naaya Layout Tool'
        self.description = 'Mark existing forms as "customized" so they will be still loaded from ZODB until manually checked. Click on portal name to see details of the update.'
        self.update_meta_type = ''


    def _list_updates(self):
        ids = ()
        if self.REQUEST:
            ids = self.REQUEST.form.get('ids', ())
        """ Return all portals that need update"""
        utool = self.aq_inner.aq_parent
        portals = utool.getPortals()
        for portal in portals:
            if ids and portal.id not in ids:
                continue
            yield portal


    def _update(self):
        updates = self._list_updates()
        for update in updates:
            formstool_ob = update.getFormsTool()
            layouttool_ob = update.getLayoutTool()
            self._load_forms(update)
            children = formstool_ob.objectValues()
            for child in children:
                if isinstance(child, Template) and not hasattr(child, 'path'):
                    if self.forms_on_disk.has_key(child.id):
                        iDiff = ndiff(child._text.splitlines(), 
                                      self.forms_on_disk[ child.id ].splitlines(), 
                                      IS_LINE_JUNK, IS_CHARACTER_JUNK)
                        differs = False
                        for line in iDiff:
                            if line[ 0 ] in self.patterns:
                                differs = True
                                break
                        if differs:
                            #We have differences
                            child.setPath(self.forms_paths[ child.id ])
                            child.setCustomized(True)
                            form_url = '%s/%s/manage_workspace' % (formstool_ob.absolute_url(), child.id)
                            logger.warn("[%s]Form '%s' (%s) differs from disk version" % (update.id, child.id, form_url))
                            print "[%s]['%s'] * (%s) differs from disk version" % (update.id, child.id, form_url)
                        else:
                            #Identical forms
                            child.setPath(self.forms_paths[ child.id ])
                            child.setCustomized(False, False)
                            logger.info("[%s]Form '%s' identical with disk version" % (update.id, child.id))
                            print "[%s]['%s'] identical with disk version" % (update.id, child.id)
                    else:
                        #Mark as customized anyway, it has no disk correspondent
                        child.setPath(None)
                        child.setCustomized(True)
                        logger.warn("[%s]Form '%s' is not on disk, marked as customized" % (update.id, child.id))
                        print "[%s]['%s'] * is not on disk, marked as customized" % (update.id, child.id)

            #We get all the defined skins and enumerate their Template object child which needs update
            layout_children = layouttool_ob.objectValues()
            for layout_child in layout_children:
                subchildren = layout_child.objectValues()
                if isinstance(layout_child, Skin):
                    for subchild in subchildren:
                        if isinstance(subchild, Template) and not hasattr(child, 'path'):
                            if self.forms_on_disk.has_key(subchild.id):
                                iDiff = ndiff(subchild._text.splitlines(), 
                                              self.forms_on_disk[ subchild.id ].splitlines(), 
                                              IS_LINE_JUNK, IS_CHARACTER_JUNK)
                                differs = False
                                for line in iDiff:
                                    if line[ 0 ] in self.patterns:
                                        differs = True
                                        break
                                if differs:
                                    #We have differences
                                    subchild.setPath(self.forms_paths[ subchild.id ])
                                    subchild.setCustomized(True)
                                    form_url = '%s/%s/manage_workspace' % (formstool_ob.absolute_url(), subchild.id)
                                    logger.warn("[%s][Skins]Form '%s' (%s) differs from disk version" % (update.id, subchild.id, form_url))
                                    print "[%s][Skins]['%s'] * (%s) differs from disk version" % (update.id, subchild.id, form_url)
                                else:
                                    #Identical forms
                                    subchild.setPath(self.forms_paths[ subchild.id ])
                                    subchild.setCustomized(False, False)
                                    logger.info("[%s][Skins]Form '%s' identical with disk version" % (update.id, subchild.id))
                                    print "[%s][Skins]['%s'] identical with disk version" % (update.id, subchild.id)
                            else:
                                #Mark as customized anyway, it has no disk correspondent
                                subchild.setPath(None)
                                subchild.setCustomized(True)
                                logger.warn("[%s][Skins]Form '%s' is not on disk, marked as customized" % (update.id, subchild.id))
                                print "[%s][Skins]['%s'] * is not on disk, marked as customized" % (update.id, subchild.id)


    def buildUpdateSummary(self):
        """Update summary displayed in naayaUpdater"""
        updates = self._list_updates()
        ret = []
        summary = None
        for update in updates:
            formstool_ob = update.getFormsTool()
            layouttool_ob = update.getLayoutTool()
            summary = SiteUpdateSummary()
            summary.ob = update
            self._load_forms(update)
            children = formstool_ob.objectValues()
            for child in children:
                if isinstance(child, Template) and not hasattr(child, 'path'):
                    if self.forms_on_disk.has_key(child.id):
                        iDiff = ndiff(child._text.splitlines(), 
                                      self.forms_on_disk[ child.id ].splitlines(), 
                                      IS_LINE_JUNK, IS_CHARACTER_JUNK)
                        differs = False
                        for line in iDiff:
                            if line[ 0 ] in self.patterns:
                                differs = True
                                break
                        if differs:
                            summary.getFormsStatus()[child.id] = 1 #We have differences
                        else:
                            summary.getFormsStatus()[child.id] = 0 #Identical forms
                    else:
                        #Mark as customized anyway, it has no disk correspondent
                        summary.getFormsStatus()[child.id] = 1

            #We get all the defined skins and enumerate their Template object child which needs update
            layout_children = layouttool_ob.objectValues()
            for layout_child in layout_children:
                subchildren = layout_child.objectValues()
                if isinstance(layout_child, Skin):
                    for subchild in subchildren:
                        if isinstance(subchild, Template) and not hasattr(child, 'path'):
                            if self.forms_on_disk.has_key(subchild.id):
                                iDiff = ndiff(subchild._text.splitlines(), 
                                              self.forms_on_disk[ subchild.id ].splitlines(), 
                                              IS_LINE_JUNK, IS_CHARACTER_JUNK)
                                differs = False
                                for line in iDiff:
                                    if line[ 0 ] in self.patterns:
                                        differs = True
                                        break
                                if differs:
                                    summary.getSkinsStatus()[subchild.id] = 1 #We have differences
                                else:
                                    summary.getSkinsStatus()[subchild.id] = 0 #Identical forms
                            else:
                                #Mark as customized anyway, it has no disk correspondent
                                summary.getSkinsStatus()[subchild.id] = 1
            ret.append(summary)
        return ret


    def _load_forms(self, nySite):
        """
        We load forms from skel to find a match on existing forms from 
        portal_forms based on form's name since before this, forms didn't have 
        information about where its content originated from. Now is stored on 
        form.path field
        """
        self.forms_on_disk.clear()
        self.forms_paths.clear()
        skel_path = ''
        
        if nySite.meta_type == 'Naaya Site':
            skel_path = join(NAAYA_PRODUCT_PATH, 'skel')
        elif nySite.meta_type == 'EnviroWindows Site':
            skel_path = join(ENVIROWINDOWS_PRODUCT_PATH, 'skel')
        elif nySite.meta_type == 'SMAP Site':
            skel_path = join(SMAP_PRODUCT_PATH, 'skel')
        elif nySite.meta_type == 'CHM Site':
            skel_path = join(CHM2_PRODUCT_PATH, 'skel')

        self._load_skeleton(join(NAAYA_PRODUCT_PATH, 'skel'), nySite)
        #If site is not Naaya, additionally load & override Naaya's forms 
        #with product's form
        if nySite.meta_type != 'Naaya Site':
            self._load_skeleton(skel_path, nySite)


    def _load_skeleton(self, skel_path, nySite):
        skel_file = join(skel_path, 'skel.xml')
        skel_handler, error = skel_parser().parse(open(skel_file, 'r').read())
        if error:
            zLOG.LOG('NySite.loadSkeleton', zLOG.ERROR, error)
        if skel_handler is not None:
            #load forms from Naaya
            if skel_handler.root.forms is not None:
                for form in skel_handler.root.forms.forms:
                        f_path = join(skel_path, 'forms', '%s.zpt' % form.id)
                        content = open(f_path).read()
                        self.forms_on_disk[ form.id ] = content
                        self.forms_paths[ form.id ] = f_path 
            #load forms from pluggable content types
            if skel_handler.root.pluggablecontenttypes is not None:
                for pluggablecontenttype in skel_handler.root.pluggablecontenttypes.pluggablecontenttypes:
                    try: action = abs(int(pluggablecontenttype.action)) 
                    except: action = 1
                    if action == 1:
                        data_path = join(nySite.get_data_path(), 'skel', 'forms')
                        meta_type = pluggablecontenttype.meta_type
                        pitem = nySite.get_pluggable_item(meta_type)
                        for frm in pitem['forms']:
                            if isfile(join(data_path, frm)):
                                f_path = join(data_path, "%s.zpt" % frm)
                            else:
                                f_path = join(pitem['package_path'], 'zpt', "%s.zpt" % frm)
                            content = open(f_path).read()
                            self.forms_on_disk[ frm ] = content
                            self.forms_paths[ frm ] = f_path
            #load templates from skins
            if skel_handler.root.layout is not None:
                layouttool_ob = nySite.getLayoutTool()
                for skin in skel_handler.root.layout.skins:
                    for template in skin.templates:
                        f_path = join(skel_path, 'layout', skin.id, '%s.zpt' % template.id)
                        content = open(f_path, 'r').read()
                        self.forms_on_disk[ template.id ] = content
                        self.forms_paths[ template.id ] = f_path
        logger.info("Loaded %s forms from %s" % (len(self.forms_on_disk), skel_file))


def register(uid):
    return CustomContentUpdater(uid)
