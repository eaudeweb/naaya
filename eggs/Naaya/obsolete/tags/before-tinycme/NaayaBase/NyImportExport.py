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
This module contains the class that implements import/export functionality
using Naaya XML format.
"""

#Python imports

#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view

#Product imports
from constants import *
from managers.import_parser import import_parser

class NyImportExport:
    """
    Class that implements import/export functionality.
    It is an I{abstract class} in the sense that a set of functions are not
    implemented.
    """

    manage_options = (
        {'label': 'Naaya Import/Export', 'action': 'manage_importexport_html'},
    )

    security = ClassSecurityInfo()

    #zmi actions
    security.declareProtected(view_management_screens, 'manage_import')
    def manage_import(self, source='file', file='', url='', REQUEST=None):
        """
        Import data from an uploaded XML file.
        @param source: from where the file is uploaded, disk or URL
        @type source: string - I{file} or I{url}
        @param file: uploaded file from the disk
        @param url: the URL from where the file will be grabbed
        @param REQUEST: I{optional} parameter to do the redirect
        """
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
            import_handler, error = import_parser().parse(file)
            if import_handler is not None:
                for object in import_handler.root.objects:
                    self.import_data(object)
            else:
                raise Exception, EXCEPTION_PARSINGFILE % ('', error)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_importexport_html')

    security.declareProtected(view_management_screens, 'exportdata')
    def exportdata(self):
        """
        Generetes an XML with the object content.
        @return: a downloadable Naaya XML file
        """
        r = []
        ra = r.append
        ra('<?xml version="1.0" encoding="utf-8"?>')
        ra('<export xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="%s">' % self.nyexp_schema)
        ra(self.exportdata_custom())
        ra('</export>')
        self.REQUEST.RESPONSE.setHeader('Content-Type', 'text/xml')
        self.REQUEST.RESPONSE.setHeader('Content-Disposition', 'attachment;filename=%s.nyexp' % self.id)
        return ''.join(r)

    security.declarePrivate('exportdata_custom')
    def exportdata_custom(self):
        """
        Exports all the Naaya content of the object in XML format.

        B{This method must be implemented.}
        """
        raise EXCEPTION_NOTIMPLEMENTED, 'exportdata_custom'

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_importexport_html')
    manage_importexport_html = PageTemplateFile('zpt/manage_importexport', globals())

InitializeClass(NyImportExport)
