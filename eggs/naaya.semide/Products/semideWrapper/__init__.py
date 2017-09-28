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
# Agency (EEA).  Portions created by Eau de Web Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Eau de Web Romania
from Products import Naaya

from Products.Naaya.NyFolder import NyFolder
from AccessControl import ClassSecurityInfo
from Products.NaayaBase.constants import PERMISSION_PUBLISH_OBJECTS, MESSAGE_SAVEDCHANGES
from Products.Naaya.constants import METATYPE_FOLDER
from naaya.content.semide.news.semnews_item import METATYPE_OBJECT as METATYPE_NYSEMNEWS
from naaya.content.semide.event.semevent_item import METATYPE_OBJECT as METATYPE_NYSEMEVENT
from Globals import InitializeClass

security = ClassSecurityInfo()

def getFolders(self): 
    return [x for x in self.objectValues(METATYPE_FOLDER) if x.submitted==1]
NyFolder.getFolders = getFolders

def hasContent(self): 
    return (len(self.getObjects()) > 0) or (len(self.objectValues(METATYPE_FOLDER)) > 0)
NyFolder.hasContent = hasContent

def getPublishedFolders(self): 
    return self.utSortObjsListByAttr([x for x in self.objectValues(METATYPE_FOLDER) if x.approved==1 and x.submitted==1], 'sortorder', 0)
NyFolder.getPublishedFolders = getPublishedFolders

security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'basketofapprovals_published_html')
def basketofapprovals_published_html(self, REQUEST=None, RESPONSE=None):
    """ """
    return self.getFormsTool().getContent({'here': self}, 'folder_basketofapprovals_published')
NyFolder.basketofapprovals_published_html = basketofapprovals_published_html

security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'basketofapprovals_duplicates_html')
def basketofapprovals_duplicates_html(self, REQUEST=None, RESPONSE=None):
    """ """
    return self.getFormsTool().getContent({'here': self}, 'folder_basketofapprovals_duplicates')
NyFolder.basketofapprovals_duplicates_html = basketofapprovals_duplicates_html

def _getDuplicatesInFolder(self, meta_type, attrs):
    """Returns an iterater with duplicate objects.

        Items with equal attrs are considered duplicated.
        @param meta_type: meta type to check
        @type meta_type: string or list (the same as for objectValues)
        @param attrs: sequence of attributes that need to be equal to consider the objects duplicate
        @type params: sequence of strings
        @rtype: iterator
    """
    all_items = {}
    for item in self.objectValues(meta_type):
        marker = tuple([getattr(item, attr) for attr in attrs]) # TODO Python 2.4: generator comprehension
        L = all_items.get(marker, None)
        if L is None:
            L = all_items[marker] = []
        L.append(item)
    for items in all_items.values():
        if len(items) < 2:
            continue
        for item in items:
            yield item
NyFolder._getDuplicatesInFolder = _getDuplicatesInFolder

def getDuplicatesInFolder(self):
    """Returns a list of duplicate news and events that are potential duplicates.

        - news are duplicates if news.title and news.coverage are identical
        - events are duplicates if event.start_date and events.coverage are identical
    """
    L = list(self._getDuplicatesInFolder(METATYPE_NYSEMNEWS, ('title', 'coverage')))
    L.extend(self._getDuplicatesInFolder(METATYPE_NYSEMEVENT, ('start_date', 'coverage')))
    return L
NyFolder.getDuplicatesInFolder = getDuplicatesInFolder

def processDuplicateContent(self, delids=[], REQUEST=None):
    """
    Process the published content inside this folder.
    Objects with ids in delids will be deleted.
    """
    for id in self.utConvertToList(delids):
        try: self._delObject(id)
        except: pass
    if REQUEST:
        self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
        REQUEST.RESPONSE.redirect('%s/basketofapprovals_duplicates_html' % self.absolute_url())
NyFolder.processDuplicateContent = processDuplicateContent

def getItemDuplicates(self, orig):
    """ Returns the duplicate(s) of the original found in this context"""
    data = {METATYPE_NYSEMNEWS: ('title', 'coverage'), METATYPE_NYSEMEVENT: ('start_date', 'coverage')}
    all_items = {}
    attrs = data[orig.meta_type]

    for item in self.objectValues(orig.meta_type):
        marker = tuple([getattr(item, attr) for attr in attrs])
        L = all_items.get(marker, None)
        if L is None:
            L = all_items[marker] = []
        L.append(item)
    for items in all_items.values():
        if len(items) < 2:
            continue
        if orig in items:
            items.remove(orig)
            return items
    return []
NyFolder.getItemDuplicates = getItemDuplicates

def processPublishedContent(self, appids=[], delids=[], REQUEST=None):
    """
    Process the published content inside this folder.
    Objects with ids in appids list will be unapproved.
    Objects with ids in delids will be deleted.
    """
    for id in self.utConvertToList(appids):
        try:
            ob = self._getOb(id)
            ob.approveThis(0, None)
            self.recatalogNyObject(ob)
        except:
            pass
    for id in self.utConvertToList(delids):
        try: self._delObject(id)
        except: pass
    if REQUEST:
        self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
        REQUEST.RESPONSE.redirect('%s/basketofapprovals_published_html' % self.absolute_url())
NyFolder.processPublishedContent = processPublishedContent

def getSortedPublishedContent(self, skey='', rkey=0):
    return self.utSortObjsListByAttr(self.getPublishedContent(), skey, rkey)
NyFolder.getSortedPublishedContent = getSortedPublishedContent

def getSortedPendingContent(self, skey='', rkey=0):
    return self.utSortObjsListByAttr(self.getPendingContent(), skey, rkey)
NyFolder.getSortedPendingContent = getSortedPendingContent

def getSortedDuplicateContent(self, skey='', rkey=0):
    return self.utSortObjsListByAttr(self.getDuplicatesInFolder(), skey, rkey)
NyFolder.getSortedDuplicateContent = getSortedDuplicateContent

security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'processDuplicateContent')
security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'getDuplicatesInFolder')
security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'basketofapprovals_published_html')
security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'basketofapprovals_duplicates_html')
security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'processPublishedContent')

security.apply(NyFolder)
InitializeClass(NyFolder)