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
#$Id: EWGoogleSearchInterface.py 2741 2004-11-30 12:59:37Z finrocvs $

#Python imports
import re
import sys
import urllib
import operator

#Zope imports
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view

#Product imports
from constants import *
from Products.NaayaCore.constants import *
from Products.NaayaBase.constants import *
from Products.Naaya.constants import *
from Products.NaayaContent.NyURL.NyURL import METATYPE_OBJECT as METATYPE_NYURL
from Products.NaayaContent.NyURL.NyURL import PREFIX_OBJECT as PREFIX_NYURL
from Products.NaayaCore.managers.session_manager import session_manager
from Products.NaayaCore.managers.utils import utils
from managers.logitems_manager import logitems_manager
from managers.cacheitems_manager import cacheitems_manager

manage_addEWGoogleSearchInterface_html = PageTemplateFile('zpt/googlesearchinterface_manage_add', globals())
addEWGoogleSearchInterface_html = PageTemplateFile('zpt/googlesearchinterface_add', globals())
def addEWGoogleSearchInterface(self, title='', search_type='', REQUEST=None):
    """ """
    try: search_type = abs(int(search_type))
    except: search_type = 0
    ob = EWGoogleSearchInterface(EWGOOGLESEARCHINTERFACE_ID, title, search_type, self.absolute_url(1))
    self._setObject(EWGOOGLESEARCHINTERFACE_ID, ob)
    if REQUEST is not None:
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'googlesearchinterface_manage_add' or l_referer.find('googlesearchinterface_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'addEWGoogleSearchInterface_html':
            REQUEST.RESPONSE.redirect(self.absolute_url())

class EWGoogleSearchInterface(SimpleItem,
    utils,
    logitems_manager,
    cacheitems_manager):
    """ EWGoogleSearchInterface class """

    meta_type = METATYPE_EWGOOGLESEARCHINTERFACE
    icon = 'misc_/EnviroWindowsGoogleSearchInterface/EWGoogleSearchInterface.gif'

    manage_options = (
        SimpleItem.manage_options
    )

    security = ClassSecurityInfo()

    def __init__(self, id, title, search_type, automatic_folder):
        """ """
        self.id = id
        self.title = title
        self.search_type = search_type
        #preferences
        self.as_q = ''
        self.as_epq = ''
        self.as_oq = ''
        self.as_eq = ''
        self.filter = 1
        self.lr = ''
        self.as_ft = 'i'
        self.as_filetype = ''
        self.as_qdr = 'all'
        self.as_occt = 'any'
        self.as_dt = ''
        self.as_sitesearch = ''
        self.safe = 'images'
        #automatic
        self.automatic_as_q = ''
        self.automatic_as_epq = ''
        self.automatic_as_oq = ''
        self.automatic_as_eq = ''
        self.automatic_filter = 1
        self.automatic_lr = ''
        self.automatic_as_ft = 'i'
        self.automatic_as_filetype = ''
        self.automatic_as_qdr = 'all'
        self.automatic_as_occt = 'any'
        self.automatic_as_dt = ''
        self.automatic_as_sitesearch = ''
        self.automatic_safe = 'images'
        self.automatic_numberofresults = 10
        self.automatic_folder = automatic_folder
        session_manager.__dict__['__init__'](self)
        utils.__dict__['__init__'](self)
        logitems_manager.__dict__['__init__'](self)
        cacheitems_manager.__dict__['__init__'](self)

    def __setstate__(self, state):
        """ """
        EWGoogleSearchInterface.inheritedAttribute('__setstate__')(self, state)

    # API
    def getGoogleEngine(self):
        #returns the EWGoogleEngine object
        return self.unrestrictedTraverse(EWGOOGLEENGINE_ID, None)

    def get_automatic_folder_title_or_id(self):
        try: return self.unrestrictedTraverse(self.automatic_folder).title_or_id()
        except: return ''

    def automaticModeEnabled(self):
        #test if automatic mode is enabled
        return self.search_type == 1

    def getLanguagesList(self):
        #returns the list of languages (id, label)
        return DEFAULT_LANGUAGES_LIST

    def getFileTypesList(self):
        #returns the list of file types (id, label)
        return DEFAULT_FILETYPES_LIST

    def getUpdateDatesList(self):
        #returns the list of update dates (id, label)
        return DEFAULT_UPDATEDATES_LIST

    def getOccurrencesList(self):
        #returns the list of occurrences (id, label)
        return DEFAULT_OCCURRENCES_LIST

    def getLanguagesIndex(self):
        #get the languages list from an Index Terms object
        try: return self.getEWSite().getLanguages()
        except: return []

    # SITE ACTIONS
    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'savePreferences')
    def savePreferences(self, as_q='', as_epq='', as_oq='', as_eq='', filter='', lr='', as_ft='',
        as_filetype='', as_qdr='', as_occt='', as_dt='', as_sitesearch='', safe='', REQUEST=None):
        """ edit search preferences """
        #load form data
        try: filter = abs(int(filter))
        except: filter = 1
        #save data
        self.as_q = as_q
        self.as_epq = as_epq
        self.as_oq = as_oq
        self.as_eq = as_eq
        self.filter = filter
        self.lr = lr
        self.as_ft = as_ft
        self.as_filetype = as_filetype
        self.as_qdr = as_qdr
        self.as_occt = as_occt
        self.as_dt = as_dt
        self.as_sitesearch = as_sitesearch
        self.safe = safe
        self._p_changed = 1
        if REQUEST: REQUEST.RESPONSE.redirect('index_html')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'cacheGoogleSearchResult')
    def cacheGoogleSearchResult(self, gsi=None, REQUEST=None):
        """ cache selected items from google search result """
        #load form data
        if gsi is None: gsi = []
        else: gsi = self.utConvertToList(gsi)
        l_google_search_result = self.getGoogleSearchResult()[1]
        l_google_search_items = gsi
        for l_google_search_item in l_google_search_items:
            self.cacheGoogleSearchResultItem(l_google_search_result[int(l_google_search_item)])
        if REQUEST: self.REQUEST.RESPONSE.redirect('result_html')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'deleteGoogleCachedResult')
    def deleteGoogleCachedResult(self, REQUEST=None):
        """deletes the session variable"""
        l_cached_objects_ids = self.utConvertToList(REQUEST.get('delete_obj', []))
        self.delete_google_cached(l_cached_objects_ids)
        if REQUEST: self.REQUEST.RESPONSE.redirect('cache_html')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'updateGoogleCachedResult')
    def updateGoogleCachedResult(self, REQUEST=None):
        """ updates records from the session variable """
        #load form data
        l_item = int(REQUEST.get('item', ''))
        l_url = REQUEST.get('url', '')
        l_title = REQUEST.get('title', '')
        l_summary = REQUEST.get('summary', '')
        l_urlinfo = self.getURLContentInfo(l_url)
        l_contenttype = self.getInfoContentType(l_urlinfo)
        l_contentlength = self.getInfoContentLength(l_urlinfo)
        l_language = REQUEST.get('language', '')
        if l_contentlength: l_contentlength = int(float(l_contentlength)/1024)
        self.update_google_cached_result(l_item, l_url, l_title, l_summary, l_contenttype, l_contentlength, l_language)
        if REQUEST: REQUEST.RESPONSE.redirect('cache_html')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'saveAutomaticProperties')
    def saveAutomaticProperties(self, automatic_numberofresults='', automatic_folder='', REQUEST=None):
        """ """
        try: automatic_numberofresults = abs(int(automatic_numberofresults))
        except: automatic_numberofresults = 10
        self.automatic_numberofresults = automatic_numberofresults
        self.automatic_folder = automatic_folder
        self._p_changed = 1
        if REQUEST: REQUEST.RESPONSE.redirect('automatic_index_html')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'saveAutomaticPreferences')
    def saveAutomaticPreferences(self, as_q='', as_epq='', as_oq='', as_eq='', filter='', lr='', as_ft='',
        as_filetype='', as_qdr='', as_occt='', as_dt='', as_sitesearch='', safe='', REQUEST=None):
        """ edit automatic search preferences for automatic mode """
        try: filter = abs(int(filter))
        except: filter = 1
        self.automatic_as_q = as_q
        self.automatic_as_epq = as_epq
        self.automatic_as_oq = as_oq
        self.automatic_as_eq = as_eq
        self.automatic_filter = filter
        self.automatic_lr = lr
        self.automatic_as_ft = as_ft
        self.automatic_as_filetype = as_filetype
        self.automatic_as_qdr = as_qdr
        self.automatic_as_occt = as_occt
        self.automatic_as_dt = as_dt
        self.automatic_as_sitesearch = as_sitesearch
        self.automatic_safe = safe
        self._p_changed = 1
        if REQUEST: REQUEST.RESPONSE.redirect('automatic_index_html')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'saveAutomaticLog')
    def saveAutomaticLog(self, REQUEST=None):
        """ clears log """
        self.empty_logitems()
        if REQUEST: REQUEST.RESPONSE.redirect('automatic_log_html')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'changeShowHideButtonState')
    def changeShowHideButtonState(self, REQUEST):
        """ change state of Save preferences button """
        l_state = self.getShowHideButtonState()
        if l_state:
            self.setShowHideButtonState(0)
        else:
            self.setShowHideButtonState(1)
        if REQUEST: REQUEST.RESPONSE.redirect('index_html')

    def setShowHideButtonState(self, p_state):
        #set a value from session that tells us do show or hide the search preferences form
        return self.setSession('showhide_preferences_buttton', p_state)
    def getShowHideButtonState(self):
        #returns a value from session that tells us do show or hide the search preferences form
        return self.getSession('showhide_preferences_buttton', 1)

    def __buildGoogleQuery(self, p_as_q, p_as_epq, p_as_oq, p_as_eq, p_as_ft, p_as_filetype, p_as_qdr, p_as_occt, p_as_dt, p_as_sitesearch):
        """build query from a lot of parameters"""
        l_q = ''
        if p_as_occt == 'title':
            l_q += 'allintitle: '
        elif p_as_occt == 'body':
            l_q += 'allintext: '
        elif p_as_occt == 'url':
            l_q += 'allinurl:'
        elif p_as_occt == 'links':
            l_q += 'allinlinks:'
        if p_as_q != '':
            l_q += p_as_q
        if p_as_oq != '':
            l_tokens = re.split('[ |\t|\n]', p_as_oq)
            for l_token in l_tokens:
                l_q += ' ' + l_token + ' OR '
            l_q = l_q[:len(l_q)-4]
        if p_as_epq != '':
            l_q += ' ' + '"' + p_as_epq + '"'
        if p_as_eq != '':
            l_tokens = re.split('[ |\t|\n]', p_as_eq)
            for l_token in l_tokens:
                l_q += ' -' + l_token
        if p_as_sitesearch != '':
            if p_as_dt == 'i':
                l_q += ' site:' + p_as_sitesearch
            else:
                l_q += ' -site:' + p_as_sitesearch
        if p_as_filetype != '':
            if p_as_ft == 'i':
                l_q += ' filetype:' + p_as_filetype
            else:
                l_q += ' -filetype:' + p_as_filetype
        l_today = self.utGetTodayDate()
        if p_as_qdr == 'm3':
            l_lastdate = l_today - 92
            l_q += ' daterange:' + str(self.utGetJulianDayNumber(l_lastdate)) + '-' + str(self.utGetJulianDayNumber(l_today))
        elif p_as_qdr == 'm6':
            l_lastdate = l_today - 183
            l_q += ' daterange:' + str(self.utGetJulianDayNumber(l_lastdate)) + '-' + str(self.utGetJulianDayNumber(l_today))
        elif p_as_qdr == 'y':
            l_lastdate = l_today - 365
            l_q += ' daterange:' + str(self.utGetJulianDayNumber(l_lastdate)) + '-' + str(self.utGetJulianDayNumber(l_today))
        return l_q

    def __doGoogleSearch(self, p_q, p_start, p_maxResults, p_filter, p_restrict, p_safeSearch, p_language):
        """perform the search"""
        #do search
        l_googlesearchresults = (self.getMetaForEmptyResult(p_q), [])
        l_googleengine = self.getGoogleEngine()
        if l_googleengine:
            try:
                l_googlesearchresults = l_googleengine.doGoogleSearch(unicode(p_q, 'latin-1'), p_start, p_maxResults, p_filter, p_restrict, p_safeSearch, p_language, http_proxy=self.getSite().http_proxy)
            except:
                pass
            
        return l_googlesearchresults

    def buildGoogleQuery(self, REQUEST=None):
        #Build a query
        #load form data
        l_as_q = REQUEST.get('as_q', '')
        l_as_epq = REQUEST.get('as_epq', '')
        l_as_oq = REQUEST.get('as_oq', '')
        l_as_eq = REQUEST.get('as_eq', '')
        #start and max results
        l_start = 0
        #automatic filter
        l_filter = REQUEST.get('filter', self.filter)
        try:
            l_filter = int(l_filter)
        except:
            l_filter = 1
        #language
        l_lr = REQUEST.get('lr', self.lr)
        #file format
        l_as_ft = REQUEST.get('as_ft', self.as_ft)
        l_as_filetype = REQUEST.get('as_filetype', self.as_filetype)
        #date
        l_as_qdr = REQUEST.get('as_qdr', self.as_qdr)
        #occurences
        l_as_occt = REQUEST.get('as_occt', self.as_occt)
        #domain
        l_as_dt = REQUEST.get('as_dt', 'i')
        l_as_sitesearch = REQUEST.get('as_sitesearch', self.as_sitesearch)
        #safe search
        l_safe = REQUEST.get('safe', self.safe)
        if l_safe=='images':
            l_safe = 0
        else:
            l_safe = 1
        #build query
        l_q = self.__buildGoogleQuery(l_as_q, l_as_epq, l_as_oq, l_as_eq, l_as_ft, l_as_filetype, l_as_qdr, l_as_occt, l_as_dt, l_as_sitesearch)
        return (l_q, l_start, l_filter, l_safe, l_lr)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'doGoogleSearch')
    def doGoogleSearch(self, REQUEST=None):
        """ Perform a search """
        #query
        l_q, l_start, l_filter, l_safe, l_lr = self.buildGoogleQuery(REQUEST)
        #do search
        self.setGoogleSearchResult(self.__doGoogleSearch(l_q, l_start, DEFAULT_MAXRESULTS, l_filter, '', l_safe, l_lr))
        self.setGoogleSearchParameters(l_safe, l_lr)
        if REQUEST: REQUEST.RESPONSE.redirect('result_html')

    def doGoogleAutomaticSearch(self):
        """ Perform an automatic search and save results """
        # step 1: build query and set search parameters
        l_q = self.__buildGoogleQuery(self.automatic_as_q, self.automatic_as_epq, self.automatic_as_oq, self.automatic_as_eq, self.automatic_as_ft, self.automatic_as_filetype, self.automatic_as_qdr, self.automatic_as_occt, self.automatic_as_dt, self.automatic_as_sitesearch)
        l_start = 0
        l_filter = self.automatic_filter
        if self.automatic_safe=='images':
            l_safe = 0
        else:
            l_safe = 1
        l_lr = self.automatic_lr
        # step 2: perform search and cache results
        l_numberofsearches = operator.div(self.automatic_numberofresults, DEFAULT_MAXRESULTS)
        #perform first search
        l_results = []
        l_google_search = self.__doGoogleSearch(l_q, l_start, DEFAULT_MAXRESULTS, l_filter, '', l_safe, l_lr)
        l_google_search_result = l_google_search[1]
        l_results.extend(l_google_search_result)
        for i in range(1, l_numberofsearches):
            l_google_search = self.__doGoogleSearch(l_q, l_start + i*10 + 1, DEFAULT_MAXRESULTS, l_filter, '', l_safe, l_lr)
            l_google_search_result = l_google_search[1]
            l_results.extend(l_google_search_result)
        l_results = l_results[:self.automatic_numberofresults]
        # step 3: save cache
        #get folder object
        l_folder_obj = self.unrestrictedTraverse(self.automatic_folder, None)
        #build a dictionary with all Yaihaw URL objects locator property
        l_dict_locator = {}
        for obj in l_folder_obj.objectValues(METATYPE_NYURL):
            l_dict_locator[obj.locator] = ''
        #init errors list and number of saved records
        l_errors = []
        l_recordssaved = 0
        if l_folder_obj:
            for l_results_item in l_results:
                l_url = l_results_item.get('URL', '').encode('UTF-8')
                l_title = l_results_item.get('title', '').encode('UTF-8')
                l_summary = l_results_item.get('summary', '').encode('UTF-8')
                if not l_dict_locator.has_key(l_url):
                    #update dictionary with current url
                    l_dict_locator[l_url] = ''
                    #save as URL
                    l_id = self.utGenObjectId(l_title)
                    
                    #verify if the object already exists
                    try:
                        ob = l_folder_obj._getOb(l_id)
                        l_id = '%s-%s' % (l_id, self.utGenRandomId(5))
                    except AttributeError:
                        pass
                    
                    #set language to the currently selected portal language
                    l_language = ''
                    for lang in self.gl_get_languages_map():
                        if lang['selected'] == True:
                            l_language = lang['id']
                    res, error = self.__addEWURL(l_id, self.tmparseHTMLTags(l_title), l_summary, l_url, l_folder_obj, 1, l_language)
                    if res == 0:
                        l_errors.append((_ERROR_ADD_YIHAW_URL, error))
                    else:
                        #set approved flag to 0
                        l_ob = l_folder_obj._getOb(l_id)
                        l_ob.approveThis(0)
                        l_folder_obj.catalogNyObject(l_ob)
                        l_recordssaved += 1
        #create log item
        self.add_logitem_item(self.utGenRandomId(), self.utGetTodayDate(), len(l_results), l_recordssaved, l_errors)

    def getMetaForEmptyResult(self, p_query=''):
        #returns an meta data for an empty result
        l_metadata = {}
        l_metadata['documentFiltering'] = 0
        l_metadata['estimatedTotalResultsCount'] = 0
        l_metadata['estimateIsExact'] = 0
        l_metadata['directoryCategories'] = []
        l_metadata['searchTime'] = 0.0
        l_metadata['searchComments'] = ''
        l_metadata['searchQuery'] = p_query
        l_metadata['startIndex'] = 0
        l_metadata['endIndex'] = 0
        l_metadata['searchTips'] = ''
        return l_metadata

    def __nextpreviousGoogleSearchResult(self, p_range):
        """previous/next 10 results action"""
        #load search parameters from session
        l_metadata = self.getGoogleSearchResult()[0]
        l_parameters = self.getGoogleSearchParameters()
        l_q = l_metadata['searchQuery']
        l_start = l_metadata['startIndex'] + p_range
        l_filter = l_metadata['documentFiltering']
        l_safe = l_parameters.get('safe', 0)
        l_lr = l_parameters.get('lr', '')
        #do search
        return self.__doGoogleSearch(l_q, l_start, DEFAULT_MAXRESULTS, l_filter, '', l_safe, l_lr)

    def previousGoogleSearchResult(self, REQUEST=None):
        """previous 10 results action"""
        self.setGoogleSearchResult(self.__nextpreviousGoogleSearchResult(-11))
        if REQUEST: REQUEST.RESPONSE.redirect('result_html')

    def nextGoogleSearchResult(self, REQUEST=None):
        """ next 10 results action """
        self.setGoogleSearchResult(self.__nextpreviousGoogleSearchResult(9))
        if REQUEST: REQUEST.RESPONSE.redirect('result_html')

    def __saveGoogleCacheInFolder(self, REQUEST=None):
        """save selected cached items in folder"""
        #form data
        l_cached_objects_ids = self.utConvertToList(REQUEST.get('cached_obj', []))
        l_download_objects_ids = self.utConvertToList(REQUEST.get('download_obj', []))
        l_folder = REQUEST.get('folder', '')
        #get data from cache
        l_cache_result = self.getGoogleCachedResult()
        #get folder object
        l_folder_obj = self.unrestrictedTraverse(l_folder, None)
        #save in folder
        if l_folder_obj:
            for l_item in l_cached_objects_ids:
                l_cache_item = l_cache_result[int(l_item)]
                if l_item in l_download_objects_ids:
                    #save as FILE
                    self.__addEWFile(self.tmparseHTMLTags(l_cache_item.title), l_cache_item.summary, l_cache_item.url, l_folder_obj, l_cache_item.language)
                else:
                    #save as URL
                    self.__addEWURL('', self.tmparseHTMLTags(l_cache_item.title), l_cache_item.summary, l_cache_item.url, l_folder_obj, 0, l_cache_item.language)
        #delete items from cache
        self.delete_google_cached(l_cached_objects_ids)

    def saveGoogleCacheInFolder(self, REQUEST=None):
        """ """
        self.__saveGoogleCacheInFolder(REQUEST)
        if REQUEST: REQUEST.RESPONSE.redirect('cache_html')

    def formatExceptionInfo(self):
        """format an exception to a string"""
        return str(sys.exc_info()[1])

    def tmparseHTMLTags(self, expression):
        """ eliminate HTML tags from expression"""
        l_pattern = re.compile("<b>|</b>")
        return l_pattern.sub("",expression)

    def __addEWURL(self, p_id, p_title, p_description, p_url, p_container, p_automatic, p_language):
        #add an EWURL
        try:
            p_container.addNyURL(id=p_id, title=p_title, description=p_description, lang=p_language, locator=p_url)
            return (1, '')
        except:
            return (0, self.formatExceptionInfo())

    def __addEWFile(self, p_title, p_description, p_url, p_container, p_language):
        #add an EWFile
        try:
            p_container.addNyFile(title=p_title, description=p_description, lang=p_language, source='url', url=p_url)
            return 1
        except:
            return 0

    def setGoogleSearchResult(self, p_result):
        """set a session variable with google search results (meta, results)"""
        self.setSession('google_search_result', p_result)
    def getGoogleSearchResult(self):
        """get the session variable with google search results (meta, results)"""
        return self.getSession('google_search_result', (self.getMetaForEmptyResult(), []))

    def setGoogleSearchParameters(self, p_safe, p_lr):
        """set a session variable with search parameters"""
        l_parameters = {}
        l_parameters['safe'] = p_safe   #safe search
        l_parameters['lr'] = p_lr       #language
        self.setSession('google_search_parameters', l_parameters)
    def getGoogleSearchParameters(self):
        """get the session variable with search parameters"""
        return self.getSession('google_search_parameters', {})

    def hasPreviousButton(self):
        """returns true if there are some previous results"""
        return (self.getGoogleSearchResult()[0]['startIndex']>10)

    def hasNextButton(self):
        """returns true if there are some next results"""
        l_metadata = self.getGoogleSearchResult()[0]
        return ((l_metadata['endIndex']>=10) and (l_metadata['endIndex']<l_metadata['estimatedTotalResultsCount']))

    def getURLContentInfo(self, p_url):
        #get the informations about the content of an url
        l_urlclass = myURLOpener()
        l_engine = self.getGoogleEngine()
        if l_engine.http_proxy != '':
            l_urlclass.proxies['http'] = l_engine.http_proxy
        webPage = l_urlclass.open(p_url)
        return webPage.info()

    def getInfoContentType(self, p_info):
        #get the content type from mimetools
        return p_info.gettype()

    def getInfoContentLength(self, p_info):
        #get the content length from mimetools
        return p_info.getheader('Content-Length')

    def showDownloadAsFileButton(self, p_contenttype):
        #return true if is a file content type that has an entry in our dictionary
        return DEFAULT_CONTENTTYPES_DICTIONARY.has_key(p_contenttype)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'delete_google_interface')
    def delete_google_interface(self, REQUEST=None):
        """ """
        l_ob = self.unrestrictedTraverse(REQUEST['path'], None)
        if l_ob:
            l_ob.getParentNode().manage_delObjects(l_ob.id)
        return REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'trigger_google_interface')
    def trigger_google_interface(self, REQUEST=None):
        """ """
        l_ob = self.unrestrictedTraverse(REQUEST['path'], None)
        if l_ob:
            l_ob.doGoogleAutomaticSearch()
        return REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    # SITE FORMS
    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'menu_html')
    menu_html = PageTemplateFile('zpt/googlesearchinterface_menu', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'index_html')
    index_html = PageTemplateFile('zpt/googlesearchinterface_index', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'sitemap_html')
    sitemap_html = PageTemplateFile('zpt/googlesearchinterface_sitemap', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'result_html')
    result_html = PageTemplateFile('zpt/googlesearchinterface_result', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'cache_html')
    cache_html = PageTemplateFile('zpt/googlesearchinterface_cache', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'emptycache_html')
    emptycache_html = PageTemplateFile('zpt/googlesearchinterface_emptycache', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'automatic_properties_html')
    automatic_properties_html = PageTemplateFile('zpt/googlesearchinterface_automatic_properties', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'automatic_index_html')
    automatic_index_html = PageTemplateFile('zpt/googlesearchinterface_automatic_index', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'automatic_log_html')
    automatic_log_html = PageTemplateFile('zpt/googlesearchinterface_automatic_log', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'help_html')
    help_html = PageTemplateFile('zpt/googlesearchinterface_help', globals())

InitializeClass(EWGoogleSearchInterface)

class myURLOpener(urllib.FancyURLopener):
    """Create sub-class in order to overide error 206.  This error means a
       partial file is being sent, which is ok in this case.  Do nothing with this error.
    """
    def http_error_206(self, url, fp, errcode, errmsg, headers, data=None):
        pass
    
    def http_error_404(self, url, fp, errcode, errmsg, headers, data=None):
        pass
