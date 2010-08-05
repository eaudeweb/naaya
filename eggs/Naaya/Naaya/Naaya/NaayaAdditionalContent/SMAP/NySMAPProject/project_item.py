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
# The Initial Owner of the Original Code is SMAP Clearing House.
# All Rights Reserved.
#
# Authors:
#
# Alexandru Ghica
# Cornel Nitu
# Miruna Badescu

#Python imports

#Zope imports
from Acquisition import Implicit

#Product imports
from Products.Localizer.LocalPropertyManager import LocalProperty
from Products.NaayaBase.NyProperties import NyProperties

class project_item(Implicit, NyProperties):
    """ """

    title = LocalProperty('title')
    description = LocalProperty('description')
    coverage = LocalProperty('coverage')
    keywords = LocalProperty('keywords')
    contact = LocalProperty('contact')
    donor = LocalProperty('donor')
    links = LocalProperty('links')
    organisation = LocalProperty('organisation')
    location = LocalProperty('location')

    def __init__(self, title, description, coverage, keywords, country, contact,
        donor, links, organisation, location, main_issues, tools, budget,
        timeframe, priority_area, focus, sortorder ,releasedate, lang):
        """
        Constructor.
        """
        self.save_properties(title, description, coverage, keywords, country, contact,
                        donor, links, organisation, location, main_issues, tools, budget,
                        timeframe, priority_area, focus, sortorder ,releasedate, lang)
        NyProperties.__dict__['__init__'](self)

    def save_properties(self, title, description, coverage, keywords, country, contact,
        donor, links, organisation, location, main_issues, tools, budget,
        timeframe, priority_area, focus, sortorder ,releasedate, lang):
        """
        Save item properties.
        """
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('description', lang, description)
        self._setLocalPropValue('coverage', lang, coverage)
        self._setLocalPropValue('keywords', lang, keywords)
        self._setLocalPropValue('contact', lang, contact)
        self._setLocalPropValue('donor', lang, donor)
        self._setLocalPropValue('links', lang, links)
        self._setLocalPropValue('organisation', lang, organisation)
        self._setLocalPropValue('location', lang, location)
        self.country = country
        self.main_issues = main_issues
        self.tools = tools
        self.budget = budget
        self.timeframe = timeframe
        self.priority_area = priority_area
        self.focus = focus
        self.sortorder = sortorder
        self.releasedate = releasedate