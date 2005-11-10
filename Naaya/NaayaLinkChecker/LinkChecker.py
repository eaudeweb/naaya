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
# Portions created by EEA are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Contributor:
# Cornel Nitu, Finsiel Romania
#
# $Id: LinkChecker.py 3219 2005-03-15 10:23:28Z cupceant $
#

import string
import threading
import time

from OFS.ObjectManager import ObjectManager
from OFS.SimpleItem import SimpleItem
import Globals
from OFS.FindSupport import FindSupport
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
#try:
#    from Products.Xron import *
#    XRONinstalled=1
#except:
#    XRONinstalled=0
XRONinstalled=0
from Utils import UtilsManager
from CheckerThread import CheckerThread, logresults
import LogEntry

THREAD_COUNT = 4
def manage_addLinkChecker(self, id, title, REQUEST=None):
    "Add a LinkChecker"
    ob = LinkChecker(id, title)
    self._setObject(id,ob)

    # set proxy_roles for Xron methods
    checker_ob = getattr(self, id)
    if XRONinstalled:
        XronDTMLMethod.manage_addXronDTMLMethod(checker_ob,'runChecker','Run the LinkChecker',
            file = 'Content-Type: text/plain\n\n<dtml-with '+ checker_ob.id +'>\n<dtml-call automaticCheck>\n</dtml-with>',
            executeAt = checker_ob.umGetTodayDate() + 0.0021,
            periodDays = 0.0021)
    else: 
        checker_ob.manage_addDTMLMethod('runChecker','Run the URL checker',file = 'Content-Type: text/plain\n\n<dtml-with '+ checker_ob.id +'>\n<dtml-call automaticCheck>\n</dtml-with>')
    checker_ob.manage_addDTMLMethod('automatic_log','Logs of the automatic URL checkings',file = '<dtml-var standard_html_header>\n\n<h1>Automatic URL checker logs</h1>\n\n<dtml-var view_log>\n\n<dtml-var standard_html_footer>')

    getattr(checker_ob,'runChecker').manage_proxy(['Manager'])

    if REQUEST:
        return self.manage_main(self,REQUEST)

manage_addLinkCheckerForm = Globals.DTMLFile('dtml/LinkCheckerForm', globals())

class LinkChecker(ObjectManager, SimpleItem, UtilsManager):
    """ Link checker is meant to check the links to remote websites """
    meta_type="LinkChecker"
    #catalog_name = "Catalog"
    security = ClassSecurityInfo()
    manage_options = (ObjectManager.manage_options[0],) + \
          ({'label' : 'Properties', 'action' : 'manage_properties'},
          {'label' : 'View', 'action' : 'index_html'},
          {'label' : 'Logs', 'action' : 'log_html'},) + SimpleItem.manage_options

    manage_addLogEntry = LogEntry.manage_addLogEntry

    index_html = Globals.DTMLFile("dtml/LinkChecker_index", globals())
    manage_properties = Globals.DTMLFile("dtml/LinkChecker_edit", globals())
    style_html = Globals.DTMLFile("dtml/LinkChecker_style", globals())
    log_html = Globals.DTMLFile("dtml/LinkChecker_log", globals())
    view_log = Globals.DTMLFile("dtml/LinkChecker_logForm",globals())

    def __init__(self, id, title='',objectMetaType={}, proxy='', batch_size=10):
        "initialize a new instance of LinkChecker"
        self.id = id
        self.title = title
        self.objectMetaType = objectMetaType
        self.proxy = proxy
        self.batch_size = int(batch_size)
        self.use_catalog = 0
        self.catalog_name = ''
        UtilsManager.__dict__['__init__'](self)

    security.declareProtected(view_management_screens, 'manage_edit')
    def manage_edit(self, proxy, batch_size, catalog_name='', REQUEST=None):
        """Edits the summary's characteristics"""
        self.proxy = proxy
        self.batch_size = int(batch_size)
        if REQUEST is not None:
            if REQUEST.has_key('use_catalog'):
                self.use_catalog = 1
                self.catalog_name = catalog_name
            else:
                self.use_catalog = 0
                self.catalog_name = ''
            REQUEST.RESPONSE.redirect('manage_properties')
        else:
            self.use_catalog = 1
            self.catalog_name = catalog_name

    def getObjectMetaTypes(self):
        """Get all added meta types"""
        return self.objectMetaType.keys()

    security.declarePrivate('findObjects')
    def findObjects(self):
        """ """
        results = []
        meta_types = self.getObjectMetaTypes()
        if meta_types == []:
            return []
        if self.use_catalog == 1:
            catalog_obj = self.unrestrictedTraverse(self.catalog_name)
            objects_founded = catalog_obj({'meta_type':meta_types})
            for obj in objects_founded:
                obj = catalog_obj.getobject(obj.data_record_id_)
                if string.find(obj.absolute_url(),'Control_Panel') == -1:
                    results.append(obj)
        else:
            objects_founded = FindSupport().ZopeFind(self.umGetROOT(), obj_metatypes=meta_types, search_sub=1)
            for obj in objects_founded:
                if string.find(obj[1].absolute_url(),'Control_Panel') == -1:
                    results.append(obj[1])
        return results

    security.declarePrivate('processObjects')
    def processObjects(self):
        """Get a list of 'findObjects' results and for each result:
            - gets all specified properties
            - parse the content of each property and extract links
            - save results into a dictionary like {'obj_url':[list_of_links]}
        """
        results = {}
        objects_founded = self.findObjects()
        for obj in objects_founded:
            properties = self.getProperties(obj.meta_type)
            for property in properties:
                try:
                    value = getattr(obj, property)
                except:
                    pass #Invalid property
                else:
                    links = self.parseUrls(value)
                    results_entry = results.get(obj.absolute_url(1), [])
                    results_entry.extend(self.umConvertToList(links))
                    results[obj.absolute_url(1)] = results_entry
        return results

    security.declareProtected('Run Automatic Check', 'automaticCheck')
    def automaticCheck(self):
        """ """
        links_dict = {}
        links_list = []
        links_dict = self.processObjects()
        for link_value in links_dict.values():
            links_list.extend(link_value)
        links_ListLock = threading.Lock()
        checker_ThreadList = []
        for thread in range(0,THREAD_COUNT):
            NewThread = CheckerThread(links_list, links_ListLock, proxy=self.proxy)
            NewThread.setName(thread)
            checker_ThreadList.append(NewThread)
            results = NewThread.start()
        for thread in range(0,THREAD_COUNT):
            checker_ThreadList[thread].join()
        log_entries = self.prepareLog(links_dict, logresults)
        self.manage_addLogEntry(self.REQUEST.AUTHENTICATED_USER.getUserName(), time.localtime(), log_entries)
        return

    security.declareProtected('Run Manual Check', 'manualCheck')
    def manualCheck(self, start, stop):
        """ """
        #build a list with all links
        links_dict = self.processObjects()
        l_temp_list = []
        for link_value in links_dict.values():
            for link_item in link_value:
                if not link_item in l_temp_list:
                    l_temp_list.append(link_item)
        links_list = l_temp_list[start-1:stop-1]
        #start threads
        links_ListLock = threading.Lock()
        checker_ThreadList = []
        for thread in range(0,THREAD_COUNT):
            NewThread = CheckerThread(links_list, links_ListLock, proxy=self.proxy)
            NewThread.setName(thread)
            checker_ThreadList.append(NewThread)
            results = NewThread.start()
        for thread in range(0,THREAD_COUNT):
            checker_ThreadList[thread].join()
        return self.prepareLog(links_dict, logresults, 0)

    security.declarePrivate('prepareLog')
    def prepareLog(self, links_dict, logresults, manual=0):
        """ """
        saveinlog = []
        for key in links_dict.keys():
            object = self.unrestrictedTraverse(key)
            for link in links_dict[key]:
                errorcode = logresults.get(link, None)
                if errorcode != 'OK' or manual == 1:
                    saveinlog.append((object.getId(), object.meta_type, object.absolute_url(1), object.icon, '', link, 1, errorcode))
        return saveinlog

    def getProperties(self, metatype):
        """Get all added meta types"""
        return self.objectMetaType[metatype]

    def hasMetaType(self, meta_type):
        """Is this meta_type in our list"""
        return self.objectMetaType.has_key(meta_type)

    def getObjectMetaTypes(self):
        """Get all added meta types"""
        return self.objectMetaType.keys()

    security.declareProtected(view_management_screens, 'manage_addMetaType')
    def manage_addMetaType(self, MetaType=None, REQUEST=None):
        """Add a new meta type to list"""
        if MetaType is None:
            addmetatype = REQUEST.get('objectMetaType', '')
        else:
            addmetatype = MetaType
        if addmetatype != '':
            if addmetatype not in self.objectMetaType.keys():
                self.objectMetaType[addmetatype] = []
                self._p_changed = 1
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect('manage_properties')

    security.declareProtected(view_management_screens,'manage_delMetaType')
    def manage_delMetaType(self, REQUEST=None):
        """Delete meta types from list"""
        delmetatype = REQUEST.get('objectMetaType', [])
        for metatype in self.umConvertToList(delmetatype):
            try:
                del(self.objectMetaType[metatype])
            except:
                pass
        self._p_changed = 1
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect('manage_properties')

    security.declareProtected(view_management_screens, 'manage_addProperty')
    def manage_addProperty(self, MetaType=None, Property=None, REQUEST=None):
        """Add a new property for a meta type"""
        if MetaType is None:
            editmetatype = REQUEST.get('editmetatype', '')
            addobjectproperty = REQUEST.get('objectProperty', '')
        else:
            editmetatype = MetaType
            addobjectproperty = Property
        if self.hasMetaType(editmetatype):
            # valid meta type - add property
            listproperties = self.objectMetaType[editmetatype]
            if addobjectproperty != '':
                if addobjectproperty not in listproperties:
                    listproperties.append(addobjectproperty)
                    self.objectMetaType[editmetatype] = listproperties
                    self._p_changed = 1
            if REQUEST is not None:
                REQUEST.RESPONSE.redirect('manage_properties?editmetatype=' + self.umURLEncode(editmetatype) + '#property')

    security.declareProtected(view_management_screens, 'manage_delProperty')
    def manage_delProperty(self, REQUEST=None):
        """Delete properties for a meta type"""
        editmetatype = REQUEST.get('editmetatype', '')
        delobjectproperty = REQUEST.get('objectProperty', [])
        if self.hasMetaType(editmetatype):
            # valid meta type - add property
            listproperties = self.objectMetaType[editmetatype]
            for property in self.umConvertToList(delobjectproperty):
                listproperties.remove(property)
            self.objectMetaType[editmetatype] = listproperties
            self._p_changed = 1
            if REQUEST is not None:
                REQUEST.RESPONSE.redirect('manage_properties?editmetatype=' + self.umURLEncode(editmetatype) + '#property')

    def getLogEntries(self):
        """Returns a list with all 'LogEntry' objects"""
        return self.objectValues('LogEntry')

    def getLocation(self, p_url):
        """get the parent object related to the object with given url"""
        try:
            return self.unrestrictedTraverse(p_url, None).aq_parent
        except:
            return None

Globals.default__class_init__(LinkChecker)
