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
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens

#Product imports
from Products.NaayaCore.constants import *
from managers.import_parser import import_parser

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
        (
            {'label': 'Export', 'action': 'manage_export_html'},
            {'label': 'Import', 'action': 'manage_import_html'},
        )
        +
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

    #api
    def parsenyexp(self, p_nyexp):
        #parses a nyexp file and returns the result
        return import_parser().parse(p_nyexp)

    #zmi actions
    security.declareProtected(view_management_screens, 'exportsite')
    def exportsite(self):
        """ - generates an XML with the site content
            - it can be imported into another site """
        r = []
        r.append('<?xml version="1.0" encoding="utf-8"?>')
        r.append('<export>')
        for x in self.getSite().get_containers():
            r.append(x.export_this())
        r.append('</export>')
        self.REQUEST.RESPONSE.setHeader('Content-Type', 'text/xml')
        self.REQUEST.RESPONSE.setHeader('Content-Disposition', 'attachment;filename=exportsite.nyexp')
        return ''.join(r)

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_export_html')
    manage_export_html = PageTemplateFile('zpt/tool_export', globals())

    security.declareProtected(view_management_screens, 'manage_import_html')
    manage_import_html = PageTemplateFile('zpt/tool_import', globals())

InitializeClass(ImportExportTool)
