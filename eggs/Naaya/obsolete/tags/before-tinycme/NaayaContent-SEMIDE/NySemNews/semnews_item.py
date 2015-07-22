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

class semnews_item(Implicit, NyProperties):
    """ """

    contact_person  = LocalProperty('contact_person')
    contact_email   = LocalProperty('contact_email')
    contact_phone   = LocalProperty('contact_phone')
    creator         = LocalProperty('creator')
    rights          = LocalProperty('rights')
    title           = LocalProperty('title')
    source          = LocalProperty('source')
    keywords        = LocalProperty('keywords')
    description     = LocalProperty('description')
    coverage        = LocalProperty('coverage')
    file_link       = LocalProperty('file_link')
    file_link_local = LocalProperty('file_link_local')


    def __init__(self, creator, creator_email, contact_person, contact_email,
            contact_phone, rights, title, news_type, file_link, file_link_local, source, source_link,
            keywords, description, subject, relation, coverage, news_date, working_langs, sortorder, releasedate, lang):

                
        """
        Constructor.
        """
        self.save_properties(creator, creator_email, contact_person, contact_email,
            contact_phone, rights, title, news_type, file_link, file_link_local, source, source_link,
            keywords, description, subject, relation, coverage, news_date, working_langs, sortorder, releasedate, lang)
        NyProperties.__dict__['__init__'](self)

    def save_properties(self, creator, creator_email, contact_person, contact_email,
            contact_phone, rights, title, news_type, file_link, file_link_local, source, source_link,
            keywords, description, subject, relation, coverage, news_date, working_langs, sortorder, releasedate, lang):
        """
        Save item properties.
        """
        self._setLocalPropValue('creator',          lang, creator)
        self._setLocalPropValue('contact_person',   lang, contact_person)
        self._setLocalPropValue('contact_email',    lang, contact_email)
        self._setLocalPropValue('contact_phone',    lang, contact_phone)
        self._setLocalPropValue('rights',           lang, rights)
        self._setLocalPropValue('title',            lang, title)
        self._setLocalPropValue('source',           lang, source)
        self._setLocalPropValue('keywords',         lang, keywords)
        self._setLocalPropValue('description',      lang, description)
        self._setLocalPropValue('coverage',         lang, coverage)
        self._setLocalPropValue('file_link',        lang, file_link)
        self._setLocalPropValue('file_link_local',  lang, file_link_local)
        self.creator_email =    creator_email
        self.working_langs =    working_langs
        self.news_type =        news_type
        self.source_link =      source_link
        self.subject =          subject
        self.relation =         relation
        self.news_date =        news_date
        self.sortorder =        sortorder
        self.releasedate =      releasedate
