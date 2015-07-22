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
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

#Python imports
from os.path import join

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
import Products
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from Products.NaayaCore.constants import *
from managers.combosync_tool import combosync_tool
import Skin

def manage_addLayoutTool(self, REQUEST=None):
    """ """
    ob = LayoutTool(ID_LAYOUTTOOL, TITLE_LAYOUTTOOL)
    self._setObject(ID_LAYOUTTOOL, ob)
    self._getOb(ID_LAYOUTTOOL).loadDefaultData()
    if REQUEST:
        return self.manage_main(self, REQUEST, update_menu=1)

class LayoutTool(Folder, combosync_tool):
    """ """

    meta_type = METATYPE_LAYOUTTOOL
    icon = 'misc_/NaayaCore/LayoutTool.gif'

    manage_options = (
        Folder.manage_options[:1]
        +
        (
            {'label': 'Layout', 'action': 'manage_layout_html'},
        )
        +
        Folder.manage_options[3:]
    )

    meta_types = (
        {'name': METATYPE_SKIN, 'action': 'manage_addSkinForm', 'permission': PERMISSION_ADD_NAAYACORE_TOOL },
    )
    def all_meta_types(self, interfaces=None):
        """ """
        y = []
        additional_meta_types = ['Image', 'File']
        for x in Products.meta_types:
            if x['name'] in additional_meta_types:
                y.append(x)
        y.extend(self.meta_types)
        return y

    manage_addSkinForm = Skin.manage_addSkinForm
    manage_addSkin = Skin.manage_addSkin

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        """ """
        self.id = id
        self.title = title
        self.__current_skin_id = None
        self.__current_skin_scheme_id = None
        combosync_tool.__dict__['__init__'](self)

    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self):
        """ """
        pass

    def getSkinsList(self): return self.objectValues(METATYPE_SKIN)
    def getCurrentSkinId(self): return self.__current_skin_id
    def getCurrentSkinSchemeId(self): return self.__current_skin_scheme_id
    def getCurrentSkin(self): return self._getOb(self.__current_skin_id)
    def getCurrentSkinScheme(self): return self._getOb(self.__current_skin_id)._getOb(self.__current_skin_scheme_id)
    def getCurrentSkinSchemes(self):
        try: return self._getOb(self.getCurrentSkinId()).getSchemes()
        except: return []

    def getSkinFilesPath(self):
        return '%s/%s' % (self._getOb(self.__current_skin_id).absolute_url(), self.getCurrentSkinSchemeId())

    def getDataForLayoutSettings(self):
        l_data = []
        for l_skin in self.getSkinsList():
            l_schemes = []
            for l_scheme in l_skin.getSchemes():
                l_schemes.append((l_scheme.title_or_id(), l_scheme.id))
            l_data.append((l_skin.id, l_skin.title_or_id(), l_schemes))
        return (self.__current_skin_id, self.getCurrentSkinSchemeId(), l_data)

    def getContent(self, p_context={}, p_page=None):
        l_skin = self._getOb(self.__current_skin_id)
        p_context['skin_files_path'] = '%s/%s' % (l_skin.absolute_url(), self.getCurrentSkinSchemeId())
        return l_skin._getOb(p_page)(p_context)

    def getNaayaContentStyles(self):
        ny_content = self.get_pluggable_content()
        res = []
        for v in ny_content.values():
            if v.has_key('additional_style'):
                style = v['additional_style']
                res.append(style)
        return '\n'.join(res)

    #zmi actions
    security.declareProtected(view_management_screens, 'manageLayout')
    def manageLayout(self, theMasterList='', theSlaveList='', REQUEST=None):
        """ """
        self.__current_skin_id = theMasterList
        self.__current_skin_scheme_id = theSlaveList
        self._p_changed = 1
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_layout_html')

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_layout_html')
    manage_layout_html = PageTemplateFile('zpt/layout_layout', globals())

InitializeClass(LayoutTool)
