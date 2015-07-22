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
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Eau de Web
# Dragos Chirila

#Python imports

#Zope imports
from OFS.Image import File
from AccessControl import ClassSecurityInfo

#Product imports
from Products.NaayaBase.NyVersioning import NyVersioning

class file_item(File, NyVersioning):
    """ """

    def __init__(self, id, title, file, precondition, content_type):
        """
        Constructor.
        """
        File.__dict__['__init__'](self, id, title, file, content_type, precondition)
        #"dirty" trick to get rid of the File's title property
        try: del self.id
        except: pass
        NyVersioning.__dict__['__init__'](self)

    security = ClassSecurityInfo()

    security.declarePrivate('objectDataForVersion')
    def objectDataForVersion(self):
        return (str(self.data), self.content_type)

    security.declarePrivate('objectDataForVersionCompare')
    def objectDataForVersionCompare(self):
        return str(self.data)

    security.declarePrivate('objectVersionDataForVersionCompare')
    def objectVersionDataForVersionCompare(self, p_version_data):
        return p_version_data[0]

    security.declarePrivate('versionForObjectData')
    def versionForObjectData(self, p_version_data=None):
        self.update_data(p_version_data[0], p_version_data[1], len(p_version_data[0]))
        self._p_changed = 1

    def handleUpload(self, source, file, url, parent):
        """
        Upload a file from disk or from a given URL.
        """
        if source=='file':
            if file != '':
                if hasattr(file, 'filename'):
                    if file.filename != '':
                        data, size = self._read_data(file)
                        content_type = self._get_content_type(file, data, self.__name__, 'application/octet-stream')
                        self.update_data(data, content_type, size)
                else:
                    self.update_data(file)
        elif source=='url':
            if url != '':
                l_data, l_ctype = parent.grabFromUrl(url)
                if l_data is not None:
                    self.update_data(l_data, l_ctype)
                    self.content_type = l_ctype
        self._p_changed = 1