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
This module contains the class that handles versioning for a single object.
"""

#Python imports
from binascii import crc32

#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view

#Product imports
from Products.NaayaCore.constants import *
from Products.NaayaCore.managers.utils import utils

class NyVersioning(utils):
    """
    Class that handles versioning for a single object.
    """

    manage_options = (
        {'label': 'Versions', 'action': 'manage_versions_html'},
    )

    security = ClassSecurityInfo()

    def __init__(self):
        """
        Initialize variables:

        B{__current_version_uid} - the id of the current version

        B{__versions} - a dictionary that stores versioned data
        """
        self.__current_version_uid = None
        self.__versions = {}

    def __create_version(self, p_version_uid, p_version_data, p_username):
        """
        Creates a version entry, a tuple of:
            - data
            - current date
            - current authenticated user
        @param p_version_uid: version unique identifier
        @param p_version_data: object data that is versioned
        """
        self.__versions[p_version_uid] = (self.utGetTodayDate(), p_username, p_version_data)
        self.__current_version_uid = p_version_uid
        self._p_changed = 1

    def __get_version_data(self, p_version_uid):
        """
        Returns the data for a version entry.
        @param p_version_uid: version unique identifier
        """
        try: return self.__versions[p_version_uid][2]
        except: return None

    def __delete_version(self, p_version_uid):
        """
        Deletes a version entry.
        @param p_version_uid: version unique identifier
        """
        if self.__versions.has_key(p_version_uid):
            del self.__versions[p_version_uid]
        self._p_changed = 1

    def __compare_current_version_data_with_data(self, p_version_data, p_data):
        """
        Compare a version data with some new data using crc32.
        @param p_version_data: version data
        @param p_data: new data
        """
        return crc32(p_version_data) != crc32(p_data)

    def getVersions(self):
        """
        Returns the dictionary of versions.
        """
        return self.__versions

    def setVersions(self, versions):
        """
        Set versions structure for current object.
        @param versions: dictionary with versions info
        """
        self.__versions = dict([(key, value) for key, value in versions.items()])
        self._p_changed = 1

    def getOlderVersions(self):
        """
        Returns the dictionary of older versions. This means that current
        version is removed because it cointains the current content of the
        object.
        """
        return dict([(key, value) for key, value in self.__versions.items()
                    if key != self.__current_version_uid])

    def getCurrentVersionId(self):
        """
        Returns the current version id.
        """
        return self.__current_version_uid

    def setCurrentVersionId(self, id):
        """
        Set the current version id.
        @param id: version unique identifier
        """
        self.__current_version_uid = id
        self._p_changed = 1

    def getVersion(self, p_version_uid=None):
        """
        Returns given version entry.
        @param p_version_uid: version unique identifier
        """
        return self.__get_version_data(p_version_uid)

    def copyVersions(self, target):
        """
        Copy all information about versions from the
        current object to the target object.
        @param target: target object
        """
        self.setCurrentVersionId(target.getCurrentVersionId())
        self.setVersions(target.getVersions())

    def createVersion(self, username):
        """
        Creates a version entry.
        """
        l_version_uid = self.utGenerateUID()
        if self.__current_version_uid is None:
            #no versions yet
            self.__create_version(l_version_uid, self.objectDataForVersion(), username)
        else:
            compare = self.objectVersionDataForVersionCompare(
                    self.__get_version_data(self.__current_version_uid))
            compare_index = getattr(compare, 'index_html', None)
            if compare_index:
                compare = compare_index()
            
            compare_with = self.objectDataForVersionCompare()
            compare_with_index = getattr(compare_with, 'index_html', None)
            if compare_with_index:
                compare_with = compare_with_index()
            
            #compare with current version
            if self.__compare_current_version_data_with_data(compare, compare_with):
                self.__create_version(l_version_uid, self.objectDataForVersion(), username)

    def objectDataForVersion(self):
        """
        Returns the data that will be stored in a version; it can be a
        property value or a list of properties or any structure.

        B{This method must be implemented.}
        """
        raise EXCEPTION_NOTIMPLEMENTED, 'objectDataForVersion'

    def objectDataForVersionCompare(self):
        """
        Rreturns the object property that is reprezentative for that object.
        It will support a crc32 comparation againts an older version
        in order to determine if is the same value.

        B{This method must be implemented.}
        """
        raise EXCEPTION_NOTIMPLEMENTED, 'objectDataForVersionCompare'

    def objectVersionDataForVersionCompare(self, p_version_data):
        """
        Returns the version piece that is reprezentative for a that version.
        It will support a crc32 comparation againts the object data
        in order to determine if is the same value.

        B{This method must be implemented.}

        @param p_version_data: version data
        """
        raise EXCEPTION_NOTIMPLEMENTED, 'objectVersionDataForVersionCompare'

    def versionForObjectData(self, p_version_data=None):
        """
        Restores the object data based on a version data.

        B{This method must be implemented.}

        @param p_version_data: version data
        """
        raise EXCEPTION_NOTIMPLEMENTED, 'versionForObjectData'

    def showVersionData(self, vid=None):
        """
        Given a version id, shows/returns the version data.

        B{This method must be implemented.}

        @param vid: version unique identifier
        """
        raise EXCEPTION_NOTIMPLEMENTED, 'showVersionData'

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_versions_html')
    manage_versions_html = PageTemplateFile('zpt/manage_versions', globals())

InitializeClass(NyVersioning)
