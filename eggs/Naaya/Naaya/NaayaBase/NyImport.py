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
from Products.NaayaCore.constants import *

class NyImport:
    """ """

    manage_options = (
        {'label': 'Naaya Import', 'action' : 'manage_import_html'},
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
                    print obj.id, obj.meta_type
                    self.import_object(self, obj)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_import_html')

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_import_html')
    manage_import_html = PageTemplateFile('zpt/manage_import', globals())

InitializeClass(NyImport)
