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

class semmultimedia_item(Implicit, NyProperties):
    """ """

    title =         LocalProperty('title')
    description =   LocalProperty('description')
    coverage =      LocalProperty('coverage')
    keywords =      LocalProperty('keywords')
    creator =       LocalProperty('creator')
    source =        LocalProperty('source')


    def __init__(self, title, description, coverage, keywords, sortorder, creator, creator_email, 
            rights, type_multimedia, source, source_link, subject, relation, file_link, 
            file_link_local, format, releasedate, lang):
        """
        Constructor.
        """
        self.save_properties(title, description, coverage, keywords, sortorder, creator, creator_email, 
            rights, type_multimedia, source, source_link, subject, relation, file_link, file_link_local, 
            format, releasedate, lang)
        NyProperties.__dict__['__init__'](self)


    def save_properties(self, title, description, coverage, keywords, sortorder, creator, creator_email, rights,
            type_multimedia, source, source_link, subject, relation, file_link, file_link_local, 
            format, releasedate, lang):
        """ Save item properties. """
        self._setLocalPropValue('title',        lang, title)
        self._setLocalPropValue('description',  lang, description)
        self._setLocalPropValue('coverage',     lang, coverage)
        self._setLocalPropValue('keywords',     lang, keywords)
        self._setLocalPropValue('source',       lang, source)
        self._setLocalPropValue('creator',      lang, creator)
        self.sortorder =        sortorder
        self.creator_email =    creator_email
        self.rights =           rights
        self.type_multimedia =  type_multimedia
        self.source_link =      source_link
        self.subject =          subject
        self.relation =         relation
        self.file_link =        file_link
        self.file_link_local =  file_link_local
        self.format =           format
        self.releasedate =      releasedate






