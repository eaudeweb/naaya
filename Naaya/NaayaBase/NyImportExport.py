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
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view

#Product imports
from Products.NaayaBase.constants import *

class NyImportExport:
    """ """

    manage_options = (
        {'label': 'Naaya Import/Export', 'action': 'manage_importexport_html'},
    )

    security = ClassSecurityInfo()

    def __init__(self):
        """ """
        pass

    #zmi actions
    security.declareProtected(view_management_screens, 'manage_import')
    def manage_import(self, source='file', file='', url='', REQUEST=None):
        """ - imports a site from an XML
            - it can be an uploaded XML file or the content grabbed from an url """
        if source=='file':
            if file != '':
                if hasattr(file, 'filename'):
                    if file.filename != '':
                        file = file.read()
                    else: file = ''
        elif source=='url':
            file, l_ctype = self.grabFromUrl(url) #upload from an url
        if file != '' and file != None:
            #import
            import_handler, error = self.getImportExportTool().parsenyexp(file)
            if import_handler is not None:
                for obj in import_handler.root.objects:
                    self.import_data(self, obj)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_importexport_html')

    security.declareProtected(view_management_screens, 'exportdata')
    def exportdata(self):
        """ - generates an XML with the site content
            - it can be imported into another site """
        r = []
        r.append('<?xml version="1.0" encoding="utf-8"?>')
        r.append('<export>')
        r.append(self.exportdata_custom())
        r.append('</export>')
        self.REQUEST.RESPONSE.setHeader('Content-Type', 'text/xml')
        self.REQUEST.RESPONSE.setHeader('Content-Disposition', 'attachment;filename=export.nyexp')
        return ''.join(r)

    ###########################################################################
    #   ABSTRACT METHODS
    #   - must be implemented in classes that extends NyImportExport
    ###########################################################################
    def exportdata_custom(self):
        #exports all the Naaya content in XML format under the current object
        raise EXCEPTION_NOTIMPLEMENTED, 'exportdata_custom'

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_importexport_html')
    manage_importexport_html = PageTemplateFile('zpt/manage_importexport', globals())

InitializeClass(NyImportExport)
