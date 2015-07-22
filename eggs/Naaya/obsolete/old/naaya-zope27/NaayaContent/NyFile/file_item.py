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

#Product imports
from Products.Localizer.LocalPropertyManager import LocalProperty
from Products.NaayaBase.NyProperties import NyProperties
from Products.NaayaBase.NyFSFile import NyFSFile

class file_item(NyProperties, NyFSFile):
    """ """

    title = LocalProperty('title')
    description = LocalProperty('description')
    coverage = LocalProperty('coverage')
    keywords = LocalProperty('keywords')

    def __init__(self, id, title, description, coverage, keywords, sortorder,
        file, precondition, releasedate, lang):
        """
        Constructor.
        """
        NyFSFile.__init__(self, id, title, file, '', precondition)
        #"dirty" trick to get rid of the File's title property
        try: del self.title
        except: pass
        try: del self.id
        except: pass
        self.save_properties(title, description, coverage, keywords, sortorder,
            releasedate, lang)
        NyProperties.__init__(self)

    def del_file_title(self):
        """
        Removes the File's object 'title' property.
        We are using a LocalProperty 'title'.
        """
        try: del self.title
        except: pass
        self._p_changed = 1

    def save_properties(self, title, description, coverage, keywords, sortorder,
        releasedate, lang):
        """
        Save item properties.
        """
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('description', lang, description)
        self._setLocalPropValue('coverage', lang, coverage)
        self._setLocalPropValue('keywords', lang, keywords)
        self.sortorder = sortorder
        self.releasedate = releasedate

    def getContentType(self):
        """Returns file content-type"""
        data = self.get_data(as_string=False)
        ctype = data.getContentType()
        if not ctype:
            return getattr(self, 'content_type', '')
        return ctype

    def _get_upload_file(self, source, file, url):
        """ grab file from disk or from a given url.
        Returns data, content_type, size, filename
        """
        if source=='file':
            if file != '':
                if hasattr(file, 'filename'):
                    filename = cookId('', '', file)[0]
                    if filename != '':
                        data, size = self._read_data(file)
                        content_type = self._get_content_type(file, data,
                            self.__name__, 'application/octet-stream')
                        return data, content_type, size, filename
                else:
                    return file, '', None, ''
        elif source=='url':
            if url != '':
                l_data, l_ctype = self.grabFromUrl(url)
                if l_data is not None:
                    return l_data, l_ctype, None, ''
        return '', '', None, ''

    def handleUpload(self, source, file, url):
        """
        Upload a file from disk or from a given URL.
        """
        data, ctype, size, filename = self._get_upload_file(source, file, url)
        self.update_data(data, ctype, size, filename)
