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
# The Original Code is Naaya version 1.0
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
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from Products.NaayaCore.AuthenticationTool.plugBase import PlugBase

plug_name = 'plugUserFolder'
plug_doc = 'Plugin for User Folder'
plug_version = '1.0.0'
plug_object_type = 'User Folder'

class plugUserFolder(PlugBase):
    """ """

    meta_type = 'Plugin for user folder'

    def __init__(self):
        """ constructor """
        PlugBase.__dict__['__init__'](self)

    security = ClassSecurityInfo()

    security.declarePublic('interface_html')
    interface_html = PageTemplateFile('plugUserFolder', globals())

InitializeClass(plugUserFolder)
