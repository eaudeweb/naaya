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
#$Id: cacheitems_manager.py 2719 2004-11-29 17:08:51Z finrocvs $

#Python imports

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

#Product imports
from Products.EnviroWindowsGoogleSearchInterface.constants import *
from Products.NaayaCore.managers.session_manager import session_manager

class cacheitem_item:
    """ """

    def __init__(self, url, title, snippet, cachedSize, relatedInformationPresent, hostName,
        directoryCategory, directoryTitle, summary, contenttype, contentlength, language):
        self.url = url
        self.title = title
        self.snippet = snippet
        self.cachedSize = cachedSize
        self.relatedInformationPresent = relatedInformationPresent
        self.hostName = hostName
        self.directoryCategory = directoryCategory
        self.directoryTitle = directoryTitle
        self.summary = summary
        self.contenttype = contenttype
        self.contentlength = contentlength
        self.language = language
        self.edited = 0

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

InitializeClass(cacheitem_item)

class cacheitems_manager(session_manager):
    """ """

    def __init__(self):
        pass

    def getGoogleCachedResult(self):
        #get the session variable with google cached results
        return self.getSession(SESSION_GOOGLE_CACHED_RESULT, [])

    def getGoogleCachedResultUrls(self):
        #get the session variable with google cached results
        return [item.url for item in self.getSession(SESSION_GOOGLE_CACHED_RESULT, [])]

    def getGoogleCachedResultLength(self):
        #get the length of session variable with google cached results
        return len(self.getSession(SESSION_GOOGLE_CACHED_RESULT, []))

    def setGoogleCachedResult(self, p_result):
        #puts the p_result list on the session
        self.setSession(SESSION_GOOGLE_CACHED_RESULT, p_result)

    def addGoogleCachedResult(self, p_result):
        #adds an item to the list from the session
        l_cache = self.getGoogleCachedResult()
        l_cache.append(p_result)
        self.setGoogleCachedResult(l_cache)

    def createGoogleCacheItem(self, p_google_search_result_item):
        #takes a dictionary of properties and returns an cacheitem
        l_url = p_google_search_result_item.get('URL', '').encode('UTF-8')
        l_title = p_google_search_result_item.get('title', '').encode('UTF-8')
        l_snippet = p_google_search_result_item.get('snippet', '').encode('UTF-8')
        l_cachedSize = p_google_search_result_item.get('cachedSize', '').encode('UTF-8')
        l_relatedInformationPresent = p_google_search_result_item.get('relatedInformationPresent', '')
        l_hostName = p_google_search_result_item.get('hostName', '').encode('UTF-8')
        l_directoryCategory = p_google_search_result_item.get('directoryCategory', '')
        l_directoryTitle = p_google_search_result_item.get('directoryTitle', '').encode('UTF-8')
        l_summary = p_google_search_result_item.get('summary', '').encode('UTF-8')
        l_urlinfo = self.getURLContentInfo(l_url)
        l_contenttype = self.getInfoContentType(l_urlinfo)
        l_contentlength = self.getInfoContentLength(l_urlinfo)
        
        #set language to the currently selected portal language
        l_language = ''
        for lang in self.gl_get_languages_map():
            if lang['selected'] == True:
                l_language = lang['id']
                
        if l_contentlength: l_contentlength = int(float(l_contentlength)/1024)
        return cacheitem_item(l_url, l_title, l_snippet, l_cachedSize, l_relatedInformationPresent, l_hostName, l_directoryCategory, l_directoryTitle, l_summary, l_contenttype, l_contentlength, l_language)

    def cacheGoogleSearchResultItem(self, p_google_search_result_item):
        #caches an item
        self.addGoogleCachedResult(self.createGoogleCacheItem(p_google_search_result_item))

    def delete_google_cached(self, p_cached_objects_ids):
        #deletes cache from session
        l_cached_objects = self.getGoogleCachedResult()
        l_new_cache = []
        for i in range(len(l_cached_objects)):
            if str(i) not in p_cached_objects_ids:
                l_new_cache.append(l_cached_objects[i])
        self.setGoogleCachedResult(l_new_cache)

    def empty_cache(self):
        #deletes all cached data
        self.setGoogleCachedResult([])

    def update_google_cached_result(self, p_item, p_url, p_title, p_summary, p_contenttype, p_contentlength, p_language):
        #updates records from the session variable
        l_cached_list = self.getGoogleCachedResult()
        l_cached_item = l_cached_list[p_item]
        l_cached_item.url = p_url
        l_cached_item.title = p_title
        l_cached_item.summary = p_summary
        l_cached_item.contenttype = p_contenttype
        l_cached_item.contentlength = p_contentlength
        l_cached_item.edited = 1
        l_cached_item.language = p_language
        l_cached_item._p_changed = 1
