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
# The Initial Owner of the Original Code is EMWIS/SEMIDE.
# Code created by Finsiel Romania are
# Copyright (C) EMWIS/SEMIDE. All Rights Reserved.
#
# Authors:
#
# Dragos Chirila, Finsiel Romania

#Python imports

#Zope imports
from Acquisition import Implicit

#Product imports
from Products.Localizer.LocalPropertyManager    import LocalProperty
from Products.NaayaBase.NyProperties            import NyProperties

class semorganisation_item(Implicit, NyProperties):
    """ """

    title =             LocalProperty('title')
    description =       LocalProperty('description')
    coverage =          LocalProperty('coverage')
    keywords =          LocalProperty('keywords')
    address =           LocalProperty('address')
    contact_title =     LocalProperty('contact_title')
    contact_firstname = LocalProperty('contact_firstname')
    contact_lastname =  LocalProperty('contact_lastname')
    contact_position =  LocalProperty('contact_position')


    def __init__(self, title, description, coverage, keywords, sortorder,
        org_type, address, org_url, contact_title, contact_firstname,
        contact_lastname, contact_position, contact_email, contact_phone,
        contact_fax, org_coord, releasedate, lang):
        """
        Constructor.
        """
        self.save_properties(title, description, coverage, keywords, sortorder,
            org_type, address, org_url, contact_title, contact_firstname,
            contact_lastname, contact_position, contact_email, contact_phone,
            contact_fax, org_coord, releasedate, lang)
        NyProperties.__dict__['__init__'](self)

    def save_properties(self, title, description, coverage, keywords, sortorder,
        org_type, address, org_url, contact_title, contact_firstname,
        contact_lastname, contact_position, contact_email, contact_phone,
        contact_fax, org_coord, releasedate, lang):
        """
        Save item properties.
        """
        self._setLocalPropValue('title',                lang, title)
        self._setLocalPropValue('description',          lang, description)
        self._setLocalPropValue('coverage',             lang, coverage)
        self._setLocalPropValue('keywords',             lang, keywords)
        self._setLocalPropValue('address',              lang, address)
        self._setLocalPropValue('contact_title',        lang, contact_title)
        self._setLocalPropValue('contact_firstname',    lang, contact_firstname)
        self._setLocalPropValue('contact_lastname',     lang, contact_lastname)
        self._setLocalPropValue('contact_position',     lang, contact_position)
        self.sortorder =        sortorder
        self.org_type =         org_type
        self.org_url =          org_url
        self.contact_email =    contact_email
        self.contact_phone =    contact_phone
        self.contact_fax =      contact_fax
        self.org_coord =        org_coord
        self.releasedate =      releasedate
