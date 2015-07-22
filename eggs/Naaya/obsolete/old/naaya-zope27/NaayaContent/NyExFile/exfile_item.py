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
import warnings
from OFS.Folder import Folder

#Product imports
from Products.Localizer.LocalPropertyManager import LocalProperty
from Products.NaayaBase.NyProperties import NyProperties
from Products.NaayaContent.NyExFile.file_item import file_item

class exfile_item(Folder, NyProperties):
    """ """

    title = LocalProperty('title')
    description = LocalProperty('description')
    coverage = LocalProperty('coverage')
    keywords = LocalProperty('keywords')

    __files = {}

    def __init__(self, id, title, description, coverage, keywords, sortorder,
        file, precondition, releasedate, lang):
        """
        Constructor.
        """
        self.save_properties(title, description, coverage, keywords, sortorder,
                             releasedate, lang)
        Folder.__init__(self, id)
        NyProperties.__dict__['__init__'](self)

    # Backward compatible
    def _get_old_files(self):
        return self.__files

    def getFileItems(self):
        return self.objectItems('File')

    def copyFileItems(self, source, target):
        """ """
        if target.objectIds('File'):
            target.manage_delObjects(target.objectIds('File'))
        for lang, item in source.getFileItems():
            doc = file_item(lang, item.title, '', item.precondition, item.getContentType())
            target._setObject(lang, doc)
            doc = target._getOb(lang)
            doc.update_data(item.get_data(as_string=False))
            #doc.copyVersions(item)

    def getFileItem(self, lang=None):
        """ """
        if lang is None:
            lang = self.gl_get_selected_language()
        if not lang in self.objectIds():
            doc = file_item(lang, lang, None, '', '')
            self._setObject(lang, doc)
        return self._getOb(lang)

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
        if lang is None:
            lang = self.gl_get_selected_language()
        return self.getFileItem(lang).getContentType()

    def precondition(self, lang=None):
        """ """
        if lang is None: lang = self.gl_get_selected_language()
        try: return self.getFileItem(lang).precondition
        except: return ''

    def set_precondition(self, precondition, lang):
        """ """
        self.getFileItem(lang).precondition = precondition

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

    def handleUpload(self, source, file, url, lang=None):
        """
        Upload a file from disk or from a given URL.
        """
        if lang is None: lang = self.gl_get_selected_language()
        self.getFileItem(lang).handleUpload(source, file, url, self)

    def createversion(self, newdata, lang=None, **kwargs):
        """
        Creates a version.
        """
        if lang is None:
            lang = self.gl_get_selected_language()
        fileitem = self.getFileItem(lang)
        vdata = fileitem.get_data(as_string=False)
        if vdata.is_broken():
            return
        fileitem.createVersion(vdata, newdata, **kwargs)

    def getVersions(self, lang=None):
        """
        Returns the dictionary of older versions. This means that current
        version is removed because it cointains the current content of the
        object.
        """
        if lang is None:
            lang = self.gl_get_selected_language()
        fileitem = self.getFileItem(lang)
        return fileitem.getVersions()
