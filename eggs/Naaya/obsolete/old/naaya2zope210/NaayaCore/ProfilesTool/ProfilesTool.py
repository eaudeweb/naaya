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
from AccessControl.Permissions import view_management_screens, view
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from Products.NaayaCore.constants import *
from Products.NaayaCore.managers.utils import utils
from Profile import manage_addProfile
from ProfileSheet import manage_addProfileSheet

def manage_addProfilesTool(self, REQUEST=None):
    """ """
    ob = ProfilesTool(ID_PROFILESTOOL, TITLE_PROFILESTOOL)
    self._setObject(ID_PROFILESTOOL, ob)
    if REQUEST: return self.manage_main(self, REQUEST, update_menu=1)


class ProfilesTool(Folder, utils):
    """ """

    meta_type = METATYPE_PROFILESTOOL
    icon = 'misc_/NaayaCore/ProfilesTool.gif'

    manage_options = (
        Folder.manage_options
        +
        (
            {'label': 'Control Panel', 'action': 'manage_controlpanel_html'},
        )
    )

    meta_types = ()
    all_meta_types = meta_types

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        """ """
        self.id = id
        self.title = title
        self.profiles_meta = {}

    #api
    def getProfiles(self): return self.objectValues(METATYPE_PROFILE)

    def getProfile(self, name=None):
        """
        Returns the profile for the given user. If the user is None
        the current AUTHENTICATED_USER is assumed. If no profile is found
        for the user then it will be created.
        """
        if name is None: name = self.REQUEST.AUTHENTICATED_USER.getUserName()
        name = self.utCleanupProfileId(name)
        profile_ob = self._getOb(name, None)
        if profile_ob is None:
            manage_addProfile(self, name, name)
            profile_ob = self._getOb(name, None)
        return profile_ob

    def getInstanceByIdentifier(self, identifier):
        """
        Returns an object by its identifier.
        """
        return self.utGetObject(identifier)

    security.declarePrivate('loadProfileSheets')
    def loadProfileSheets(self, profile_ob):
        """
        Given a profile object, it loads all needed sheets according
        with profile metadata definitions.
        """
        for k, v in self.profiles_meta.items():
            title = v['title']
            properties = v['properties']
            for x in v['instances']:
                instance_ob = self.getInstanceByIdentifier(x)
                sheet_id = instance_ob.getInstanceSheetId()
                manage_addProfileSheet(profile_ob, sheet_id, title, x)
                sheet_ob = profile_ob._getOb(sheet_id)
                for p in properties:
                    sheet_ob.manage_addProperty(p['id'], p['value'], p['type'])

    #zmi actions
    security.declareProtected(view_management_screens, 'manageAddProfileMeta')
    def manageAddProfileMeta(self, location='', REQUEST=None):
        """ """
        if location == '': ob = self.getSite()
        else: ob = self.getInstanceByIdentifier(location)
        if ob: ob.loadProfileMeta()
        if REQUEST:
            REQUEST.RESPONSE.redirect('%s/manage_controlpanel_html?save=ok' % self.absolute_url())

    security.declareProtected(view_management_screens, 'manageDeleteProfileInstanceMeta')
    def manageDeleteProfileInstanceMeta(self, meta_type='', location='', REQUEST=None):
        """ """
        v = self.profiles_meta.get(meta_type, None)
        if v:
            try:
                ob = self.getInstanceByIdentifier(location)
                if ob: ob.unloadProfileInstanceMeta()
                del self.profiles_meta[meta_type]
                self._p_changed = 1
            except:
                pass
        if REQUEST:
            REQUEST.RESPONSE.redirect('%s/manage_controlpanel_html?save=ok' % self.absolute_url())

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_controlpanel_html')
    manage_controlpanel_html = PageTemplateFile('zpt/profiles_controlpanel', globals())

InitializeClass(ProfilesTool)