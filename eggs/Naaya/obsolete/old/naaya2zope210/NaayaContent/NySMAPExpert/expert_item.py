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
# The Initial Owner of the Original Code is SMAP Clearing House.
# All Rights Reserved.
#
# Authors:
#
# Alexandru Ghica, Eau de Web
# Cornel Nitu, Eau de Web
# Miruna Badescu, Eau de Web
# Alex Morega, Eau de Web

#Python imports

#Zope imports
from OFS.Image import File, cookId
#Product imports
from Products.NaayaBase.NyContentType import NyContentData

class expert_item(NyContentData, File):
    """ """

    def __init__(self, id, title, file, precondition, content_type):
        """
        Constructor.
        """
        File.__dict__['__init__'](self, id, title, file, content_type, precondition)
        #"dirty" trick to get rid of the File's title property
        try: del self.title
        except: pass
        try: del self.id
        except: pass
        NyContentData.__init__(self)

    def handleUpload(self, file):
        """
        Upload a file from disk.
        """
        if file != '':
            if hasattr(file, 'filename'):
                if file.filename != '':
                    data, size = self._read_data(file)
                    content_type = self._get_content_type(file, data, self.__name__, 'application/octet-stream')
                    self.update_data(data, content_type, size)
            else:
                self.update_data(file)
        self._p_changed = 1
        return cookId('', '', file)[0]
