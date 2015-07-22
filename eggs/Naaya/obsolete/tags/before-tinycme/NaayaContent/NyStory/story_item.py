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
from Acquisition import Implicit

#Product imports
from Products.Localizer.LocalPropertyManager import LocalProperty
from Products.NaayaBase.NyProperties import NyProperties

class story_item(Implicit, NyProperties):
    """ """

    title = LocalProperty('title')
    description = LocalProperty('description')
    coverage = LocalProperty('coverage')
    keywords = LocalProperty('keywords')
    body = LocalProperty('body')
    source = LocalProperty('source')

    def __init__(self, title, description, coverage, keywords, sortorder, body,
        topitem, resourceurl, source, releasedate, frontpicture, lang):
        """
        Constructor.
        """
        self.save_properties(title, description, coverage, keywords, sortorder,
            body, topitem, resourceurl, source, releasedate, frontpicture, lang)
        NyProperties.__dict__['__init__'](self)

    def save_properties(self, title, description, coverage, keywords, sortorder,
        body, topitem, resourceurl, source, releasedate, frontpicture, lang):
        """
        Save item properties.
        """
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('description', lang, description)
        self._setLocalPropValue('coverage', lang, coverage)
        self._setLocalPropValue('keywords', lang, keywords)
        self._setLocalPropValue('body', lang, body)
        self.sortorder = sortorder
        self.topitem = topitem
        self.resourceurl = resourceurl
        self._setLocalPropValue('source', lang, source)
        self.releasedate = releasedate
        self.frontpicture = frontpicture

    def setFrontPicture(self, p_picture):
        """
        Upload the front page picture.
        """
        if p_picture != '':
            if hasattr(p_picture, 'filename'):
                if p_picture.filename != '':
                    l_read = p_picture.read()
                    if l_read != '':
                        self.frontpicture = l_read
                        self._p_changed = 1
            else:
                self.frontpicture = p_picture
                self._p_changed = 1

    def delFrontPicture(self):
        """
        Delete the front page picture.
        """
        self.frontpicture = None
        self._p_changed = 1
