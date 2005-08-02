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
# The Original Code is EEAWebUpdate version 0.1
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by CMG and Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

#Python imports

#Zope imports
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from Products.NaayaCore.AuthenticationTool.plugBase import PlugBase

plug_name = 'plugLDAPUserFolder'
plug_doc = 'Plugin for LDAPUserFolder'
plug_version = '1.0.0'
plug_object_type = 'LDAPUserFolder'


class plugLDAPUserFolder(PlugBase):
    """ """

    meta_type = 'Plugin for user folder'

    def __init__(self):
        """ constructor """
        PlugBase.__dict__['__init__'](self)

    security = ClassSecurityInfo()

    def getLDAPSchema(self, acl_folder):
        """ returns the schema for a LDAPUserFolder """
        return acl_folder.getLDAPSchema()

    def findLDAPUsers(self, acl_folder, params, term):
        """ search for users in LDAP """
        try: return acl_folder.findUser(search_param=params, search_term=term)
        except: return ()

    security.declarePublic('interface_html')
    interface_html = PageTemplateFile('plugLDAPUserFolder', globals())


InitializeClass(plugLDAPUserFolder)