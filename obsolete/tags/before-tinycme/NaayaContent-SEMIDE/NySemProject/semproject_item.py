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

class semproject_item(Implicit, NyProperties):
    """ """

    title =         LocalProperty('title')
    description =   LocalProperty('description')
    coverage =      LocalProperty('coverage')
    keywords =      LocalProperty('keywords')
    acronym =       LocalProperty('acronym')
    programme =     LocalProperty('programme')
    objectives =    LocalProperty('objectives')
    results =       LocalProperty('results')

    def __init__(self, title, description, coverage, keywords, sortorder, acronym,
        budget, programme, resourceurl, objectives, results, start_date,
        end_date, releasedate, lang, pr_number, subject):
        """
        Constructor.
        """
        self.save_properties(title, description, coverage, keywords, sortorder, acronym,
            budget, programme, resourceurl, objectives, results, start_date,
            end_date, releasedate, lang, pr_number, subject)
        NyProperties.__dict__['__init__'](self)

    def save_properties(self, title, description, coverage, keywords, sortorder, acronym,
        budget, programme, resourceurl, objectives, results, start_date,
        end_date, releasedate, lang, pr_number, subject):
        """
        Save item properties.
        """
        self._setLocalPropValue('title',        lang, title)
        self._setLocalPropValue('description',  lang, description)
        self._setLocalPropValue('coverage',     lang, coverage)
        self._setLocalPropValue('keywords',     lang, keywords)
        self._setLocalPropValue('acronym',      lang, acronym)
        self._setLocalPropValue('programme',    lang, programme)
        self._setLocalPropValue('objectives',   lang, objectives)
        self._setLocalPropValue('results',      lang, results)
        self.subject =      subject
        self.resourceurl =  resourceurl
        self.budget =       budget
        self.sortorder =    sortorder
        self.start_date =   start_date
        self.end_date =     end_date
        self.releasedate =  releasedate
        self.pr_number =    pr_number
