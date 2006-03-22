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
from OFS.Image import File

#Product imports
from Products.Localizer.LocalPropertyManager import LocalProperty
from Products.NaayaBase.NyProperties import NyProperties
from file_item import file_item

class exfile_item(NyProperties):
    """ """

    title = LocalProperty('title')
    description = LocalProperty('description')
    coverage = LocalProperty('coverage')
    keywords = LocalProperty('keywords')

    def __init__(self, id, title, description, coverage, keywords, sortorder,
        file, precondition, content_type, downloadfilename, releasedate, lang):
        """
        Constructor.
        """
        self.__files = {}
        self.__files[lang] = file_item(id, title, file, content_type, precondition)
        self.save_properties(title, description, coverage, keywords, sortorder,
            downloadfilename, releasedate, lang)
        NyProperties.__dict__['__init__'](self)

    def file_for_lang(self, lang):
        """ """
        return self.__files.get(lang, None)

    def save_properties(self, title, description, coverage, keywords, sortorder,
        downloadfilename, releasedate, lang):
        """
        Save item properties.
        """
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('description', lang, description)
        self._setLocalPropValue('coverage', lang, coverage)
        self._setLocalPropValue('keywords', lang, keywords)
        self.sortorder = sortorder
        self.downloadfilename = downloadfilename
        self.releasedate = releasedate

    def handleUpload(self, source, file, url, lang):
        """
        Upload a file from disk or from a given URL.
        """
        if not self.__files.has_key(lang):
            self.__files[lang] = file_item(self.id, self.title, '', '', '')
        self.__files[lang].handleUpload(source, file, url)
        self._p_changed = 1