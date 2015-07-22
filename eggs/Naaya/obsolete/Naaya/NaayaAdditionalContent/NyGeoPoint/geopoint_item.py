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
# Agency (EEA). Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Eau de Web

#Python import

#Zope imports
from Acquisition import Implicit

#Product imports
from Products.Localizer.LocalPropertyManager import LocalProperty
from Products.NaayaBase.NyProperties import NyProperties

class geopoint_item(Implicit, NyProperties):
    """ """

    title = LocalProperty('title')
    description = LocalProperty('description')
    coverage = LocalProperty('coverage')
    keywords = LocalProperty('keywords')

    def __init__(self, title, description, coverage, keywords, sortorder, lon_cardinal, lon_ds, lon_ms, 
        lon_ss, lat_cardinal, lat_ds, lat_ms, lat_ss, geo_type, url, pointer, releasedate, lang):
        """
        Constructor.
        """
        self.save_properties(title, description, coverage, keywords, sortorder, lon_cardinal, lon_ds, lon_ms, 
        lon_ss, lat_cardinal, lat_ds, lat_ms, lat_ss, geo_type, url, pointer, releasedate, lang)
        NyProperties.__dict__['__init__'](self)

    def save_properties(self, title, description, coverage, keywords, sortorder, lon_cardinal, lon_ds, lon_ms, 
        lon_ss, lat_cardinal, lat_ds, lat_ms, lat_ss, geo_type, url, pointer, releasedate, lang):
        """
        Save item properties.
        """
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('description', lang, description)
        self._setLocalPropValue('coverage', lang, coverage)
        self._setLocalPropValue('keywords', lang, keywords)
        self.lon_cardinal = lon_cardinal
        self.lon_ds = lon_ds
        self.lon_ms = lon_ms
        self.lon_ss = lon_ss
        self.lat_cardinal = lat_cardinal
        self.lat_ds = lat_ds
        self.lat_ms = lat_ms
        self.lat_ss = lat_ss
        self.geo_type = geo_type
        self.url = url
        self.pointer = pointer
        self.sortorder = sortorder
        self.releasedate = releasedate