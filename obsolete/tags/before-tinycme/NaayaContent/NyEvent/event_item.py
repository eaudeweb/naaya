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

class event_item(Implicit, NyProperties):
    """ """

    title = LocalProperty('title')
    description = LocalProperty('description')
    coverage = LocalProperty('coverage')
    keywords = LocalProperty('keywords')
    location = LocalProperty('location')
    location_address = LocalProperty('location_address')
    host = LocalProperty('host')
    details = LocalProperty('details')

    def __init__(self, title, description, coverage, keywords, sortorder,
        location, location_address, location_url, start_date, end_date, host,
        agenda_url, event_url, details, topitem, event_type, contact_person,
        contact_email, contact_phone, contact_fax, releasedate, lang):
        """
        Constructor.
        """
        self.save_properties(title, description, coverage, keywords, sortorder,
            location, location_address, location_url, start_date, end_date,
            host, agenda_url, event_url, details, topitem, event_type,
            contact_person, contact_email, contact_phone, contact_fax,
            releasedate, lang)
        NyProperties.__dict__['__init__'](self)


    def save_properties(self, title, description, coverage, keywords, sortorder,
        location, location_address, location_url, start_date, end_date, host,
        agenda_url, event_url, details, topitem, event_type, contact_person,
        contact_email, contact_phone, contact_fax, releasedate, lang):
        """
        Save item properties.
        """
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('description', lang, description)
        self._setLocalPropValue('coverage', lang, coverage)
        self._setLocalPropValue('keywords', lang, keywords)
        self._setLocalPropValue('location', lang, location)
        self._setLocalPropValue('location_address', lang, location_address)
        self._setLocalPropValue('host', lang, host)
        self._setLocalPropValue('details', lang, details)
        self.sortorder = sortorder
        self.location_url = location_url
        self.start_date = start_date
        self.end_date = end_date
        self.agenda_url = agenda_url
        self.event_url = event_url
        self.topitem = topitem
        self.event_type = event_type
        self.contact_person = contact_person
        self.contact_email = contact_email
        self.contact_phone = contact_phone
        self.contact_fax = contact_fax
        self.releasedate = releasedate
