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
# Alexandru Ghica, Finsiel Romania

#Python imports

#Zope imports
from Acquisition import Implicit

#Product imports
from Products.Localizer.LocalPropertyManager    import LocalProperty
from Products.NaayaBase.NyProperties            import NyProperties

class semfieldsite_item(Implicit, NyProperties):
    """ """

    title =             LocalProperty('title')
    description =       LocalProperty('description')
    coverage =          LocalProperty('coverage')
    keywords =          LocalProperty('keywords')
    fieldsite_rb =      LocalProperty('fieldsite_rb')
    fieldsite_loc =     LocalProperty('fieldsite_loc')

    def __init__(self, title, description, coverage, keywords, sortorder,
        fieldsite_rb, fieldsite_loc, releasedate, lang):
        """
        Constructor.
        """
        self.save_properties(title, description, coverage, keywords, sortorder,
            fieldsite_rb, fieldsite_loc, releasedate, lang)
        NyProperties.__dict__['__init__'](self)

    def save_properties(self, title, description, coverage, keywords, sortorder,
        fieldsite_rb, fieldsite_loc, releasedate, lang):
        """
        Save item properties.
        """
        self._setLocalPropValue('title',            lang, title)
        self._setLocalPropValue('description',      lang, description)
        self._setLocalPropValue('coverage',         lang, coverage)
        self._setLocalPropValue('keywords',         lang, keywords)
        self._setLocalPropValue('fieldsite_rb',     lang, fieldsite_rb)
        self._setLocalPropValue('fieldsite_loc',    lang, fieldsite_loc)
        self.sortorder =    sortorder
        self.releasedate =  releasedate
