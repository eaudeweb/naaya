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
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo

#Product imports
from Products.NaayaCore.constants import *

def manage_addImportExportTool(self, REQUEST=None):
    """ """
    ob = ImportExportTool(ID_IMPORTEXPORTTOOL, TITLE_IMPORTEXPORTTOOL)
    self._setObject(ID_IMPORTEXPORTTOOL, ob)
    self._getOb(ID_IMPORTEXPORTTOOL).loadDefaultData()
    if REQUEST:
        return self.manage_main(self, REQUEST, update_menu=1)

class ImportExportTool(SimpleItem):
    """ """

    meta_type = METATYPE_IMPORTEXPORTTOOL
    icon = 'misc_/NaayaCore/ImportExportTool.gif'

    manage_options = (
        SimpleItem.manage_options
    )

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        """ """
        self.id = id
        self.title = title

    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self):
        #load default stuff
        pass

InitializeClass(ImportExportTool)
