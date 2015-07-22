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
# Alin Voinea, Eau de Web
"""
This module contains the class that handles versioning for a single object.
"""

from binascii import crc32
from OFS.Folder import Folder

class NyFolderishVersioning:
    """ File versioning
    """
    def __init__(self):
        self.versions = Folder('versions')
    #
    # Private interface
    #
    def _add_version(self, vdata, **kwargs):
        """ Add version by id (vid) if not exists or update existing one with
        given (v)data and keywords
        """
        vid = self.utCleanupId(vdata.getId())
        vdata.id = vid
        versions = self._get_versions_container()
        if vid not in versions.objectIds():
            versions._setObject(vid, vdata)
        else:
            version = versions._getOb(vid)
            version.manage_upload(vdata.index_html(), vdata.getContentType())
        version = versions._getOb(vid)
        for key, value in kwargs.items():
            setattr(version, key, value)

    def _delete_version(self, vid=None):
        """ Delete version by given version id (vid).
        If vid is not provided delete all versions.
        """
        versions = self._get_versions_container()
        if not vid:
            # Delete all
            versions.manage_delObjects(versions.objectIds())
        if vid in versions.objectIds():
            versions.manage_delObjects([vid, ])

    def _get_versions_container(self):
        """ If versions container not exists create and return it
        """
        if not 'versions' in self.__dict__.keys():
            self.versions = Folder('versions')
        return self.versions

    def _get_version(self, vid=None):
        """ Returns version by given v(id) or None if not exists.
        If v(id) is not provided returns a list of all versions.
        """
        versions = self._get_versions_container()
        if not vid:
            return versions.objectValues()
        return versions._getOb(vid, None)

    def _compare_versions(self, vdata1, vdata2):
        """ Compare 2 versions data.
        """
        if getattr(vdata1, 'index_html', None):
            vdata1 = vdata1.index_html()
        if getattr(vdata2, 'index_html', None):
            vdata2 = vdata2.index_html()
        if not isinstance(vdata1, str):
            vdata1 = str(vdata1)
        if not isinstance(vdata2, str):
            vdata2 = str(vdata2)
        return crc32(vdata1) != crc32(vdata2)
    #
    # Public interface
    #
    def createVersion(self, vdata, newdata, **kwargs):
        """ Create version from given data or default
        """
        # Same content
        if not self._compare_versions(vdata, newdata):
            return
        self._add_version(vdata, **kwargs)

    def getVersionsContainer(self):
        """ If versions container not exists create and return it
        """
        return self._get_versions_container()

    def getVersion(self, version_id):
        """ Return version by given id
        """
        if not version_id:
            return None
        return self._get_version(version_id)

    def getVersions(self):
        """ Return all versions
        """
        return self._get_version()

    def deleteVersions(self, version_ids):
        """ Not implemented as it's not required, yet.
        """
        pass
