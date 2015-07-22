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

    def getInstanceIdentifier(self):
        """
        Returns a value that identifies this instance.
        """
        return '/'.join(self.getPhysicalPath())

    def getInstanceSheetId(self):
        """
        Generate an UID based on instance url. This UID is the id of the
        profile sheet associated with the instance.
        """
        return self.utGenerateUID(self.getInstanceIdentifier())

    security.declarePrivate('_loadProfileMeta')
    def _loadProfileMeta(self, module_path):
        """
        """
        instance_identifier = self.getInstanceIdentifier()
        profilemeta_path = join(module_path, 'profilemeta.xml')
        profilemeta_handler, error = profilemeta_parser().parse(self.futRead(profilemeta_path, 'r'))
        if profilemeta_handler is not None:
            if profilemeta_handler.root is not None:
                profiles_tool = self.getProfilesTool()
                entry_title = 'Profile at %s' % instance_identifier
                #add entry in profiles tool
                if not profiles_tool.profiles_meta.has_key(self.meta_type):
                    profiles_tool.profiles_meta[self.meta_type] = {
                        'title': entry_title,
                        'properties': [],
                        'instances': []
                    }
                    psa = profiles_tool.profiles_meta[self.meta_type]['properties'].append
                    for p in profilemeta_handler.root.properties:
                        psa({'id': p.id, 'value': p.value, 'type': p.type})
                if instance_identifier not in profiles_tool.profiles_meta[self.meta_type]['instances']:
                    #update profile meta instances list
                    profiles_tool.profiles_meta[self.meta_type]['instances'].append(instance_identifier)
                    profiles_tool._p_changed = 1
                    #update all existing profiles
                    sheet_id = self.getInstanceSheetId()
                    for profile_ob in profiles_tool.getProfiles():
                        manage_addProfileSheet(profile_ob, sheet_id, entry_title, instance_identifier)
                        sheet_ob = profile_ob._getOb(sheet_id)
                        for p in profilemeta_handler.root.properties:
                            sheet_ob.manage_addProperty(p.id, p.value, p.type)
        else:
            raise Exception, EXCEPTION_PARSINGFILE % (profilemeta_path, error)

    security.declarePrivate('loadProfileMeta')
    def loadProfileMeta(self):
        """
        Loads profile metadata and updates existing profiles. Must be implemented.
        """
        raise EXCEPTION_NOTIMPLEMENTED

    security.declarePrivate('unloadProfileInstanceMeta')
    def unloadProfileInstanceMeta(self):
        """
        Remove profile entry for this instance.
        """
        instance_identifier = self.getInstanceIdentifier()
        sheet_id = self.getInstanceSheetId()
        profiles_tool = self.getProfilesTool()
        #remove instance entry from profile metadata
        try: profiles_tool.profiles_meta[self.meta_type]['instances'].remove(instance_identifier)
        except: pass
        for profile_ob in profiles_tool.getProfiles():
            try: profile_ob.manage_delObjects([sheet_id])
            except: pass
        profiles_tool._p_changed = 1

    def _processProfileProperties(self, REQUEST, kwargs):
        """
        Try to extract values for profile defined properties.
        """
        profiles_tool = self.getProfilesTool()
        properties = {}
        #process properties
        for p in profiles_tool.profiles_meta[self.meta_type]['properties']:
            v = None
            if REQUEST: v = REQUEST.get(p['id'], None)
            if v is None: v = kwargs.get(p['id'], None)
            properties[p['id']] = v
        return properties

    security.declarePrivate('_profilesheet')
    def _profilesheet(self, name, properties):
        """
        Updates the profile of the given user.
        """
        profile_ob = self.getProfilesTool().getProfile(name)
        sheet_ob = profile_ob._getOb(self.getInstanceSheetId(), None)
        if sheet_ob:
            for k, v in properties.items():
                sheet_ob._updateProperty(k, v)

    def profilesheet(self, name, REQUEST=None, **kwargs):
        """
        Updates the profile of the given user. Must be implemented.
        """
        raise EXCEPTION_NOTIMPLEMENTED

    #site pages
    def profilesheet_html(self, REQUEST=None, RESPONSE=None):
        """
        View for instance associated sheet. Must be implemented.
        """
        raise EXCEPTION_NOTIMPLEMENTED

InitializeClass(ProfileMeta)
