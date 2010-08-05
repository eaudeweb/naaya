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
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania
#
#
#
#$Id: EWGoogleEngine.py 2741 2004-11-30 12:59:37Z finrocvs $

#Python imports
import google

#Zope imports
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from AccessControl.Permissions import view_management_screens, view

#Product imports
from constants import *
from Products.NaayaCore.managers.utils import utils

class EWGoogleEngine(SimpleItem, utils):

    meta_type = METATYPE_EWGOOGLEENGINE
    icon = 'misc_/EnviroWindowsGoogleSearchInterface/EWGoogleEngine.gif'

    manage_options = (
        (
            {'label' : 'Properties', 'action' : 'manage_properties_html'},
        )
        +
        SimpleItem.manage_options
    )

    def __init__(self):
        #constructor
        self.id = EWGOOGLEENGINE_ID
        self.title = EWGOOGLEENGINE_TITLE
        self.license_key = None
        utils.__dict__['__init__'](self)

    #security stuff
    security = ClassSecurityInfo()

    # API
    def getEWGoogleEngine(self):
        #return this object
        return self

    def getEWGoogleSearchInterfaces(self, p_portal_obj):
        #return all EWGoogleSearchInterfaces from all the portal
        return [y for x,y in p_portal_obj.PrincipiaFind(p_portal_obj, obj_metatypes=[METATYPE_EWGOOGLESEARCHINTERFACE], search_sub=1)]

    def triggerAutomaticSearches(self):
        """ """
        l_root = self.utGetROOT()
        for l_item in l_root.PrincipiaFind(l_root, obj_metatypes=[METATYPE_EWGOOGLESEARCHINTERFACE], search_sub=1):
            l_ob_relative_url, l_ob = l_item
            if l_ob.automaticModeEnabled():
                l_ob.doGoogleAutomaticSearch()

    def doGoogleSearch(self, query, start = 0, maxResults = 10, filter = 1, restrict = '', safeSearch = 0, language = '', inputencoding = 'UTF-8', outputencoding = 'UTF-8', http_proxy=None):
        #doGoogleSearch
        google.setLicense(self.license_key)
        l_data = google.doGoogleSearch( query, start, maxResults, filter, restrict, safeSearch, language, inputencoding, outputencoding, self.license_key, http_proxy)
        l_meta = {
            'documentFiltering' : l_data.meta.documentFiltering,
            'searchComments' : l_data.meta.searchComments,
            'estimatedTotalResultsCount' : l_data.meta.estimatedTotalResultsCount,
            'estimateIsExact' : l_data.meta.estimateIsExact,
            'searchQuery' : l_data.meta.searchQuery,
            'startIndex' : l_data.meta.startIndex,
            'endIndex' : l_data.meta.endIndex,
            'searchTips' : l_data.meta.searchTips,
            'directoryCategories' : l_data.meta.directoryCategories,
            'searchTime' : l_data.meta.searchTime,
        }
        l_result = []
        for r in l_data.results:
            l_result.append(
                {
                    'URL' : r.URL,
                    'title' : r.title,
                    'snippet' : r.snippet,
                    'cachedSize' : r.cachedSize,
                    'relatedInformationPresent' : r.relatedInformationPresent,
                    'hostName' : r.hostName,
                    'directoryCategory' : r.directoryCategory,
                    'directoryTitle' : r.directoryTitle,
                    'summary' : r.summary,
                }
            )
        return (l_meta, l_result)

    def doSpellingSuggestion(self, phrase, http_proxy = None):
        #doSpellingSuggestion
        google.setLicense(self.license_key)
        return google.doSpellingSuggestion(phrase, self.license_key, http_proxy)

    def doGetCachedPage(self, url, http_proxy = None):
        #doGetCachedPage
        google.setLicense(self.license_key)
        return google.doGetCachedPage(url, http_proxy)

    # ZMI ACTIONS
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', license_key='', REQUEST=None):
        """ """
        self.title = title
        self.license_key = license_key
        self._p_changed = 1
        if REQUEST: REQUEST.RESPONSE.redirect('manage_properties_html?save=ok')

    # ZMI FORMS
    security.declareProtected(view_management_screens, 'manage_properties_html')
    manage_properties_html = PageTemplateFile('zpt/googleengine_manage_properties', globals())

InitializeClass(EWGoogleEngine)
