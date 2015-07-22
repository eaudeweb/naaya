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
import Products
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from Products.NaayaCore.constants import *
import Style

manage_addSchemeForm = PageTemplateFile('zpt/scheme_add', globals())
def manage_addScheme(self, id='', title='', REQUEST=None):
    """ """
    ob = Scheme(id, title)
    self._setObject(id, ob)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class Scheme(Folder):
    """ """

    meta_type = METATYPE_SCHEME
    icon = 'misc_/NaayaCore/Scheme.gif'

    manage_options = (
        Folder.manage_options
    )

    security = ClassSecurityInfo()

    meta_types = (
        {'name': METATYPE_STYLE, 'action': 'manage_addStyle_html', 'permission': PERMISSION_ADD_NAAYACORE_TOOL },
    )
    def all_meta_types(self, interfaces=None):
        """ """
        y = []
        additional_meta_types = ['Image']
        for x in Products.meta_types:
            if x['name'] in additional_meta_types:
                y.append(x)
        y.extend(self.meta_types)
        return y

    #constructors
    manage_addStyle_html = Style.manage_addStyle_html
    manage_addStyle = Style.manage_addStyle

    def __init__(self, id, title):
        """ """
        self.id = id
        self.title = title

InitializeClass(Scheme)
