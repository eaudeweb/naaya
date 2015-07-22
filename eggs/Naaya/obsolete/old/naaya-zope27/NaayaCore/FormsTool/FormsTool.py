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

"""
This module contains the class that implements a container
for Naaya CMF common forms (page templates).

This is a core tool of the Naaya CMF.
Every portal B{must} have an object of this type inside.
"""

#Python imports

#Zope imports
from Globals import InitializeClass
from OFS.Folder import Folder
from AccessControl import ClassSecurityInfo

#Product imports
from Products.NaayaCore.constants import *
from Products.NaayaCore.LayoutTool.Template import manage_addTemplateForm, manage_addTemplate

def manage_addFormsTool(self, REQUEST=None):
    """
    Class that implements the tool.
    """
    ob = FormsTool(ID_FORMSTOOL, TITLE_FORMSTOOL)
    self._setObject(ID_FORMSTOOL, ob)
    self._getOb(ID_FORMSTOOL).loadDefaultData()
    if REQUEST:
        return self.manage_main(self, REQUEST, update_menu=1)

class FormsTool(Folder):
    """
    Class that implements a container for forms.
    """

    meta_type = METATYPE_FORMSTOOL
    icon = 'misc_/NaayaCore/FormsTool.gif'

    manage_options = (
        Folder.manage_options
    )

    meta_types = (
        {'name': METATYPE_TEMPLATE, 'action': 'manage_addTemplateForm'},
    )
    all_meta_types = meta_types

    manage_addTemplateForm = manage_addTemplateForm
    manage_addTemplate = manage_addTemplate

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        """
        Initialize variables.
        """
        self.id = id
        self.title = title

    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self):
        """
        Creates default stuff.
        I{(Nothing for the moment.)}
        """
        pass

    def getForm(self, form_id):
        """
        Backported getForm
        Fetches a Naaya form
        """
        return self._getOb(form_id)

    def getContent(self, p_context={}, p_page=None):
        """
        Renders the given form and return the result.
        @param p_context: extra parameters for the ZPT
        @type p_context: dictionary
        @param p_page: the id of the ZPT
        @type p_page: string
        """
        p_context['skin_files_path'] = self.getLayoutTool().getSkinFilesPath()
        return self._getOb(p_page)(p_context)

InitializeClass(FormsTool)
