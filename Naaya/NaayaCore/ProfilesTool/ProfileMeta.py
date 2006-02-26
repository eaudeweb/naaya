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
from os.path import join

#Zope imports
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

#Product imports
from Products.NaayaBase.constants import *
from managers.profilemeta_parser import profilemeta_parser

class ProfileMeta:
    """
    """

    security = ClassSecurityInfo()

    def __init__(self):
        """ """
        pass

    security.declarePrivate('_loadProfileMeta')
    def _loadProfileMeta(self, meta_type, module_path):
        """
        """
        profilemeta_path = join(module_path, 'profilemeta.xml')
        profilemeta_handler, error = profilemeta_parser().parse(self.futRead(profilemeta_path, 'r'))
        if profilemeta_handler is not None:
            if profilemeta_handler.root is not None:
                profiles_tool = self.getProfilesTool()
                print profilemeta_handler.root.title
                for p in profilemeta_handler.root.properties:
                    print p.id, p.type, p.mode
        else:
            raise Exception, EXCEPTION_PARSINGFILE % (profilemeta_path, error)

InitializeClass(ProfileMeta)
