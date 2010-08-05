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

class contact_item(Implicit, NyProperties):
    """ """

    title = LocalProperty('title')
    description = LocalProperty('description')
    coverage = LocalProperty('coverage')
    keywords = LocalProperty('keywords')
    personaltitle = LocalProperty('personaltitle')
    jobtitle = LocalProperty('jobtitle')
    firstname = LocalProperty('firstname')
    lastname = LocalProperty('lastname')
    department = LocalProperty('department')
    organisation = LocalProperty('organisation')
    postaladdress = LocalProperty('postaladdress')

    def __init__(self, title, description, coverage, keywords, sortorder, personaltitle, 
            firstname, lastname, jobtitle, department, organisation, postaladdress, phone, 
            fax, cellphone, email, webpage, releasedate, lang):
        """
        Constructor.
        """
        self.save_properties(title, description, coverage, keywords, sortorder, personaltitle, 
            firstname, lastname, jobtitle, department, organisation, postaladdress, phone, fax, 
            cellphone, email, webpage, releasedate, lang)
        NyProperties.__dict__['__init__'](self)

    def save_properties(self, title, description, coverage, keywords, sortorder, 
        personaltitle, firstname, lastname, jobtitle, department, organisation,
        postaladdress, phone, fax, cellphone, email, webpage, releasedate, lang):
        """
        Save item properties.
        """
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('description', lang, description)
        self._setLocalPropValue('coverage', lang, coverage)
        self._setLocalPropValue('keywords', lang, keywords)
        self._setLocalPropValue('personaltitle', lang, personaltitle)
        self._setLocalPropValue('jobtitle', lang, jobtitle)
        self._setLocalPropValue('firstname', lang, firstname)
        self._setLocalPropValue('lastname', lang, lastname)
        self._setLocalPropValue('department', lang, department)
        self._setLocalPropValue('organisation', lang, organisation)
        self._setLocalPropValue('postaladdress', lang, postaladdress)
        self.phone = phone
        self.fax = fax
        self.cellphone = cellphone
        self.email = email
        self.webpage = webpage
        self.sortorder = sortorder
        self.releasedate = releasedate