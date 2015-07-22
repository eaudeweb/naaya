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
from OFS.Image import cookId
from AccessControl import ClassSecurityInfo

#Product imports
from Products.NaayaBase.NyFolderishVersioning import NyFolderishVersioning
from Products.NaayaBase.NyFSFile import NyFSFile

class file_item(NyFSFile, NyFolderishVersioning):
    """ """

    def __init__(self, id, title, file, precondition, content_type):
        """
        Constructor.
        """
        NyFSFile.__dict__['__init__'](self, id, title, file, content_type, precondition)
        #"dirty" trick to get rid of the File's title property
        try: del self.id
        except: pass
        NyFolderishVersioning.__dict__['__init__'](self)

    security = ClassSecurityInfo()
    #
    #override handlers
    #
    def getContentType(self):
        return self.get_data(as_string=False).getContentType()

    def _get_upload_file(self, source, file, url, parent):
        if source=='file':
            if file != '':
                if hasattr(file, 'filename'):
                    filename = cookId('', '', file)[0]
                    if filename != '':
                        data, size = self._read_data(file)
                        content_type = self._get_content_type(file, data, self.__name__, 'application/octet-stream')
                        return data, content_type, size, filename
                else:
                    return file, '', None, ''
        elif source=='url':
            if url != '':
                l_data, l_ctype = parent.grabFromUrl(url)
                if l_data is not None:
                    return l_data, l_ctype, None, ''
        return '', '', None, ''

    def handleUpload(self, source, file, url, parent):
        """
        Upload a file from disk or from a given URL.
        """
        data, ctype, size, filename = self._get_upload_file(source, file, url, parent)
        self.update_data(data, ctype, size, filename)
