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

class semtextlaws_item(Implicit, NyProperties):
    """ """

    title =                 LocalProperty('title')
    description =           LocalProperty('description')
    coverage =              LocalProperty('coverage')
    keywords =              LocalProperty('keywords')
    source =                LocalProperty('source')
    official_journal_ref =  LocalProperty('official_journal_ref')

    def __init__(self, title, description, coverage, keywords, sortorder, source, source_link,
            subject, relation, geozone, file_link, file_link_local, official_journal_ref, type_law,
            original_language, statute, releasedate, lang):
        """
        Constructor.
        """
        self.save_properties(title, description, coverage, keywords, sortorder, source, source_link,
            subject, relation, geozone, file_link, file_link_local, official_journal_ref, type_law,
            original_language, statute, releasedate, lang)
        NyProperties.__dict__['__init__'](self)

    def save_properties(self, title, description, coverage, keywords, sortorder, source, source_link,
            subject, relation, geozone, file_link, file_link_local, official_journal_ref, type_law,
            original_language, statute, releasedate, lang):
        """ Save item properties. """
        self._setLocalPropValue('title',                lang, title)
        self._setLocalPropValue('description',          lang, description)
        self._setLocalPropValue('coverage',             lang, coverage)
        self._setLocalPropValue('keywords',             lang, keywords)
        self._setLocalPropValue('source',               lang, source)
        self._setLocalPropValue('official_journal_ref', lang, official_journal_ref)
        self.sortorder =            sortorder
        self.source_link =          source_link
        self.subject =              subject
        self.relation =             relation
        self.geozone =              geozone
        self.file_link =            file_link
        self.file_link_local =      file_link_local
        self.type_law =             type_law
        self.original_language =    original_language
        self.statute =              statute
        self.releasedate =          releasedate