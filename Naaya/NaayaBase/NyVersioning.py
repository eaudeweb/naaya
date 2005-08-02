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
from binascii import crc32
from copy import deepcopy

#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view

#Product imports
from Products.NaayaCore.constants import *
from Products.NaayaCore.managers.utils import utils

class NyVersioning(utils):
    """ """

    manage_options = (
        {'label' : 'Versions', 'action' : 'manage_versions_html'},
    )

    security = ClassSecurityInfo()

    def __init__(self):
        """ """
        self.__current_version_uid = None
        self.__versions = {}

    def __create_version(self, p_version_uid, p_version_data):
        #creates a version entry, a tuple of : data, current date, current authenticated user
        self.__versions[p_version_uid] = (self.utGetTodayDate(), self.REQUEST.AUTHENTICATED_USER.getUserName(), p_version_data)
        self.__current_version_uid = p_version_uid
        self._p_changed = 1

    def __get_version_data(self, p_version_uid):
        #returns the data for a version entry
        try: return self.__versions[p_version_uid][2]
        except: return None
        
    def __delete_version(self, p_version_uid):
        #deletes a version entry
        raise EXCEPTION_NOTIMPLEMENTED

    def __compare_current_version_data_with_data(self, p_version_data, p_data):
        #crc32 it is used to compare data
        return crc32(p_version_data) != crc32(p_data)

    def getVersions(self):
        #returns the dictionary of versions
        return self.__versions

    def getOlderVersions(self):
        #returns the dictionary of older versions
        #this means that current version is removed because
        #it cointains the current content of the object
        buf = deepcopy(self.__versions)
        try: del(buf[self.__current_version_uid])
        except: pass
        return buf

    def getCurrentVersionId(self):
        #returns the current version id
        return self.__current_version_uid
        
    def getVersion(self, p_version_uid=None):
        #returns given version entry
        return self.__get_version_data(p_version_uid)

    def createVersion(self):
        #creates a version entry
        l_version_uid = self.utGenerateUID()
        if self.__current_version_uid is None:
            #no versions yet
            self.__create_version(l_version_uid, self.objectDataForVersion())
        else:
            #compare with current version
            if self.__compare_current_version_data_with_data(self.objectVersionDataForVersionCompare(self.__get_version_data(self.__current_version_uid)), self.objectDataForVersionCompare()):
                self.__create_version(l_version_uid, self.objectDataForVersion())

    ###########################################################################
    #   ABSTRACT METHODS
    #   - must be implemented in classes that extends NyVersioning
    ###########################################################################
    def objectDataForVersion(self):
        #returns the data that will be stored in a version
        # can be a property value or a list of properties or any structure
        raise EXCEPTION_NOTIMPLEMENTED, 'objectDataForVersion'

    def objectDataForVersionCompare(self):
        #returns the object property that is reprezentative for that object
        #it will support a crc32 comparation againts an older version
        #in order to determine if is the same value
        raise EXCEPTION_NOTIMPLEMENTED, 'objectDataForVersionCompare'

    def objectVersionDataForVersionCompare(self, p_version_data):
        #returns the version piece that is reprezentative for a that version
        #it will support a crc32 comparation againts the object data
        #in order to determine if is the same value
        raise EXCEPTION_NOTIMPLEMENTED, 'objectVersionDataForVersionCompare'

    def versionForObjectData(self, p_version_data=None):
        #restores the object data based on a version data
        raise EXCEPTION_NOTIMPLEMENTED, 'versionForObjectData'

    def showVersionData(self, vid=None):
        #given a version id, shows/returns the version data
        raise EXCEPTION_NOTIMPLEMENTED, 'showVersionData'

    ###########################
    #         ZMI FORMS       #
    ###########################
    security.declareProtected(view_management_screens, 'manage_versions_html')
    manage_versions_html = PageTemplateFile('zpt/manage_versions', globals())

InitializeClass(NyVersioning)
