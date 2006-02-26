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
from ProfileSheet import manage_addProfileSheet

class ProfileMeta:
    """
    """

    security = ClassSecurityInfo()

    def __init__(self):
        """ """
        pass

    security.declarePrivate('_loadProfileMeta')
    def _loadProfileMeta(self, module_path):
        """
        """
        instance_url = self.absolute_url(1)
        print self.id, self.meta_type, instance_url
        profilemeta_path = join(module_path, 'profilemeta.xml')
        profilemeta_handler, error = profilemeta_parser().parse(self.futRead(profilemeta_path, 'r'))
        if profilemeta_handler is not None:
            if profilemeta_handler.root is not None:
                profiles_tool = self.getProfilesTool()
                #add entry in profiles tool
                if not profiles_tool.profiles_meta.has_key(self.meta_type):
                    profiles_tool.profiles_meta[self.meta_type] = {
                        'title': profilemeta_handler.root.title,
                        'properties': [],
                        'instances': []
                    }
                    psa = profiles_tool.profiles_meta[self.meta_type]['properties'].append
                    for p in profilemeta_handler.root.properties:
                        psa({'id': p.id, 'type': p.type, 'mode': p.mode})
                if instance_url not in profiles_tool.profiles_meta[self.meta_type]['instances']:
                    #update profile meta instances list
                    profiles_tool.profiles_meta[self.meta_type]['instances'].append(instance_url)
                    profiles_tool._p_chanaged = 1
                    #update all existing profiles
                    sheet_id = self.getInstanceSheetId(instance_url)
                    for profile_ob in profiles_tool.getProfiles():
                        manage_addProfileSheet(profile_ob, '%s at %s' % (profilemeta_handler.root.title, instance_url))
            print profiles_tool.profiles_meta
        else:
            raise Exception, EXCEPTION_PARSINGFILE % (profilemeta_path, error)

    security.declarePrivate('loadProfileMeta')
    def loadProfileMeta(self):
        """
        Loads profile metadata and updates existing profiles.
        """
        raise EXCEPTION_NOTIMPLEMENTED

InitializeClass(ProfileMeta)
