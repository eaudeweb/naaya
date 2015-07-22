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

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from Products.NaayaCore.constants import *
import Scheme
import Template

manage_addSkinForm = PageTemplateFile('zpt/skin_add', globals())
def manage_addSkin(self, id='', title='', content=None, REQUEST=None):
    """ """
    if content is None or content == '':
        ob = Skin(id, title)
        self._setObject(id, ob)
        if content == '':
            #create default empty templates
            self._getOb(id).createSkinFiles()
    else:
        self.manage_clone(self._getOb(content), id)
        ob = self._getOb(id)
        ob.title = title
        ob._p_changed = 1
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class Skin(Folder):
    """ """

    meta_type = METATYPE_SKIN
    icon = 'misc_/NaayaCore/Skin.gif'

    manage_options = (
        Folder.manage_options
    )

    security = ClassSecurityInfo()

    meta_types = (
        {'name': METATYPE_SCHEME, 'action': 'manage_addSchemeForm'},
        {'name': METATYPE_TEMPLATE, 'action': 'manage_addTemplateForm'},
    )
    all_meta_types = meta_types

    manage_addSchemeForm = Scheme.manage_addSchemeForm
    manage_addScheme = Scheme.manage_addScheme
    manage_addTemplateForm = Template.manage_addTemplateForm
    manage_addTemplate = Template.manage_addTemplate

    def __init__(self, id, title):
        """ """
        self.id = id
        self.title = title

    security.declarePrivate('createSkinFiles')
    def createSkinFiles(self):
        #Creates the default template files with empty content
        self.manage_addTemplate('site_header', 'Portal standard HTML header')
        self.manage_addTemplate('site_footer', 'Portal standard HTML footer')
        self.manage_addTemplate('portlet_left_macro', 'Macro for left portlets')
        self.manage_addTemplate('portlet_center_macro', 'Macro for center portlets')
        self.manage_addTemplate('portlet_right_macro', 'Macro for right portlets')

    #api
    def getSchemes(self): return self.objectValues(METATYPE_SCHEME)
    def getTemplateById(self, p_id): return self._getOb(p_id)

InitializeClass(Skin)
