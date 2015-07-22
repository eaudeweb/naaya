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
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

#Python imports

#Zope imports
from Acquisition import Implicit

#Product imports
from Products.Localizer.LocalPropertyManager    import LocalProperty
from Products.NaayaBase.NyProperties            import NyProperties

class semevent_item(Implicit, NyProperties):
    """ """

    contact_person =    LocalProperty('contact_person')
    creator =           LocalProperty('creator')
    title =             LocalProperty('title')
    keywords =          LocalProperty('keywords')
    description =       LocalProperty('description')
    source =            LocalProperty('source')
    coverage =          LocalProperty('coverage')
    organizer =         LocalProperty('organizer')
    address =           LocalProperty('address')
    duration =          LocalProperty('duration')
    file_link =         LocalProperty('file_link')
    file_link_copy =    LocalProperty('file_link_copy')

    def __init__(self, title, description, coverage, keywords, sortorder,
        creator, creator_email, topitem, event_type, source, source_link,
        file_link, file_link_copy, subject, relation, organizer, duration,
        geozone, address, start_date, end_date, event_status, contact_person,
        contact_email, contact_phone, working_langs, releasedate, lang):
        """
        Constructor.
        """
        self.save_properties(title, description, coverage, keywords, sortorder,
            creator, creator_email, topitem, event_type, source, source_link,
            file_link, file_link_copy, subject, relation, organizer, duration,
            geozone, address, start_date, end_date, event_status, contact_person,
            contact_email, contact_phone, working_langs, releasedate, lang)
        NyProperties.__dict__['__init__'](self)


    def save_properties(self, title, description, coverage, keywords, sortorder,
        creator, creator_email, topitem, event_type, source,
        source_link, file_link, file_link_copy, subject, relation, organizer,
        duration, geozone, address, start_date, end_date, event_status,
        contact_person, contact_email, contact_phone, working_langs, releasedate, lang):
        """
        Save item properties.
        """
        self._setLocalPropValue('title',            lang, title)
        self._setLocalPropValue('description',      lang, description)
        self._setLocalPropValue('coverage',         lang, coverage)
        self._setLocalPropValue('keywords',         lang, keywords)
        self._setLocalPropValue('contact_person',   lang, contact_person)
        self._setLocalPropValue('creator',          lang, creator)
        self._setLocalPropValue('source',           lang, source)
        self._setLocalPropValue('organizer',        lang, organizer)
        self._setLocalPropValue('duration',         lang, duration)
        self._setLocalPropValue('address',          lang, address)
        self._setLocalPropValue('file_link',        lang, file_link)
        self._setLocalPropValue('file_link_copy',   lang, file_link_copy)
        self.contact_email =    contact_email
        self.contact_phone =    contact_phone
        self.working_langs =    working_langs
        self.sortorder =        sortorder
        self.creator_email =    creator_email
        self.topitem =          topitem
        self.event_type =       event_type
        self.source_link =      source_link
        self.subject =          subject
        self.relation =         relation
        self.geozone =          geozone
        self.start_date =       start_date
        self.end_date =         end_date
        self.event_status =     event_status
        self.releasedate =      releasedate
