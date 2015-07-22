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
from copy import deepcopy

#Zope imports
from Acquisition import Implicit

#Product imports
from Products.Localizer.LocalPropertyManager import LocalProperty
from Products.NaayaBase.NyProperties import NyProperties
from Products.NaayaContent.NyExFile.file_item import file_item

class exfile_item(Implicit, NyProperties):
    """ """

    title = LocalProperty('title')
    description = LocalProperty('description')
    coverage = LocalProperty('coverage')
    keywords = LocalProperty('keywords')
    downloadfilename = LocalProperty('downloadfilename')


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

    def getFileItems(self): return self.__files
    def setFileItems(self, files):
        self.__files = files
        self._p_changed = 1

    def copyFileItems(self, source, target):
        """ """
        files = {}
        for k, v in source.getFileItems().items():
            files[k] = file_item(v.getId(), v.title, '', v.precondition, v.content_type)
            files[k].update_data(v.get_data(as_string=False))
            files[k].content_type = v.content_type
            files[k].precondition = v.precondition
            files[k].copyVersions(v)
        target.setFileItems(files)

    def getFileItem(self, lang=None):
        """ """
        if lang is None: lang = self.gl_get_selected_language()
        if not self.__files.has_key(lang):
            self.__files[lang] = file_item('', '', '', '', '')
            self._p_changed = 1
        return self.__files[lang]
    
    def getFileItemData(self, lang=None, as_string=False):
        fileitem = self.getFileItem(lang)
        return fileitem.get_data(as_string=as_string)

    def size(self, lang=None):
        """ """
        if lang is None: lang = self.gl_get_selected_language()
        try: return self.getFileItem(lang).size
        except: return 0

    def get_size(self, lang=None):
        """ """
        if lang is None: lang = self.gl_get_selected_language()
        try: return self.getFileItem(lang).size
        except: return 0

    def content_type(self, lang=None):
        """ """
        if lang is None: lang = self.gl_get_selected_language()
        return self.getFileItem(lang).content_type
        #try: 
        #except: return 'application/octet-stream'

    def precondition(self, lang=None):
        """ """
        if lang is None: lang = self.gl_get_selected_language()
        try: return self.getFileItem(lang).precondition
        except: return ''

    def set_content_type(self, content_type, lang):
        """ """
        try: self.getFileItem(lang).content_type = content_type
        except: pass

    def set_precondition(self, precondition, lang):
        """ """
        try: self.getFileItem(lang).precondition = precondition
        except: pass

    def save_properties(self, title, description, coverage, keywords, sortorder,
        downloadfilename, releasedate, lang):
        """
        Save item properties.
        """
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('description', lang, description)
        self._setLocalPropValue('coverage', lang, coverage)
        self._setLocalPropValue('keywords', lang, keywords)
        self._setLocalPropValue('downloadfilename', lang, downloadfilename)
        self.sortorder = sortorder
        self.releasedate = releasedate

    def handleUpload(self, source, file, url, lang=None):
        """
        Upload a file from disk or from a given URL.
        """
        if lang is None: lang = self.gl_get_selected_language()
        self.getFileItem(lang).handleUpload(source, file, url, self)

    def createversion(self, username, lang=None):
        """
        Creates a version.
        """
        if lang is None: lang = self.gl_get_selected_language()
        self.getFileItem(lang).createVersion(username)

    def getOlderVersions(self, lang=None):
        """
        Returns the dictionary of older versions. This means that current
        version is removed because it cointains the current content of the
        object.
        """
        if lang is None: lang = self.gl_get_selected_language()
        try: return self.getFileItem(lang).getOlderVersions()
        except: return []
