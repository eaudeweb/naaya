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
# Copyright (C) European Environment Agency. All
# Rights Reserved.
#
# Author(s):
# Alexandru Ghica, Dragos Chirila - Finsiel Romania


#Python imports
from binascii import crc32
from copy import deepcopy

#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view

#Product imports
from Products.Finshare.Constants import *
from Products.Finshare.utils import utils

class DocVersioning(utils):
    """ """

    manage_options = (
        {'label' : ITEM_MANAGE_OPTION_VESIONS, 'action' : 'manage_versions_html'},
    )

    security = ClassSecurityInfo()

    def __init__(self):
        """ Constructor """
        self.__current_version_uid = None
        self.__versions = {}

    def __create_version(self, p_version_uid, p_version_data, p_downloadfilename, p_size, p_version):
        """ creates a version entry, a tuple of : data, current date, current authenticated user """
        self.__versions[p_version_uid] = (self.utGetTodayDate(), self.REQUEST.AUTHENTICATED_USER.getUserName(), p_version_data, p_downloadfilename, p_size, p_version)
        self.__current_version_uid = p_version_uid
        self._p_changed = 1

    def __get_version_data(self, p_version_uid):
        """ returns the data for a version entry """
        try: return (self.__versions[p_version_uid][2], self.__versions[p_version_uid][3], self.__versions[p_version_uid][4])
        except: return None
        
    def __delete_version(self, p_version_uid):
        """ deletes a version entry """
        del self.__versions[p_version_uid]
        self._p_changed = 1

    def __compare_current_version_data_with_data(self, p_version_data, p_data):
        """ crc32 it is used to compare data """
        return crc32(p_version_data) != crc32(p_data)

    def getVersions(self):
        """ returns the dictionary of versions """
        return self.__versions

    def getOlderVersions(self):
        """ returns the dictionary of older versions
            this means that current version is removed because
            it cointains the current content of the object """
        buf = deepcopy(self.__versions)
        try: del(buf[self.__current_version_uid])
        except: pass
        return buf

    def getCurrentVersionId(self):
        """ returns the current version id """
        return self.__current_version_uid
        
    def getVersion(self, p_version_uid=None):
        """ returns given version entry """
        return self.__get_version_data(p_version_uid)

    def __test_exist_version(self, p_version_number):
        """ test if version already exists """
        for id_version in self.__versions.keys():
            if p_version_number == self.__versions[id_version][5]: return id_version
        return 0

    def createVersion(self):
        """ creates a version entry """
        l_version_uid = self.utGenerateUID()
        l_exist_version = self.__test_exist_version(self.file_version)
        if l_exist_version:
            self.createHistory(HISTORY_EDIT_VERSION)
            self.__delete_version(l_exist_version)
            self.__create_version(l_exist_version, self.objectDataForVersion(), self.downloadfilename, self.size, self.file_version)
        else:
            self.createHistory(HISTORY_NEW_VERSION)
            self.__create_version(l_version_uid, self.objectDataForVersion(), self.downloadfilename, self.size, self.file_version)

    def delete_oldversion(self,p_version_uid):
        self.__delete_version(p_version_uid)
    ###########################################################################
    #   ABSTRACT METHODS                                                      #
    #   - must be implemented in classes that extends DocVersioning           #
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
    manage_versions_html = PageTemplateFile('zpt/DocFile/file_manage_versions', globals())

InitializeClass(DocVersioning)
