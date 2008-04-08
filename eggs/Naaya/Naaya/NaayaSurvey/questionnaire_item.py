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
# Alin Voinea, Eau de Web
from Acquisition import Implicit

#Product imports
from DateTime import DateTime
from Products.Localizer.LocalPropertyManager import LocalProperty
from Products.NaayaBase.NyProperties import NyProperties

class questionnaire_item(Implicit, NyProperties):
    """ """

    title = LocalProperty('title')
    description = LocalProperty('description')
    coverage = LocalProperty('coverage')
    keywords = LocalProperty('keywords')

    def __init__(self, title, description, coverage, keywords, 
                 sortorder, releasedate, expirationdate, lang):
        """
        Constructor.
        """
        self.save_properties(title, description, coverage, keywords, 
            sortorder, releasedate, expirationdate, lang)
        NyProperties.__dict__['__init__'](self)

    def save_properties(self, title='', description='', coverage='', 
                        keywords='', sortorder=100, 
                        releasedate=DateTime(), expirationdate=DateTime(),
                        notify_owner=True,
                        notify_respondents='LET_THEM_CHOOSE_YES',
                        lang=None, **kwargs):
        """
        Save item properties.
        """
        assert(notify_respondents in ('ALWAYS', 'NEVER', 'LET_THEM_CHOOSE_YES', 'LET_THEM_CHOOSE_NO'))
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('description', lang, description)
        self._setLocalPropValue('coverage', lang, coverage)
        self._setLocalPropValue('keywords', lang, keywords)
        self.sortorder = sortorder
        self.releasedate = releasedate
        self.expirationdate = expirationdate
        self.notify_owner = notify_owner
        self.notify_respondents = notify_respondents
