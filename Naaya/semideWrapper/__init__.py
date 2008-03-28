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
from Products.NaayaContent.NySemNews.NySemNews import METATYPE_OBJECT as METATYPE_NYSEMNEWS
from Products.NaayaContent.NySemEvent.NySemEvent import METATYPE_OBJECT as METATYPE_NYSEMEVENT
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

def getDuplicatesInFolder(self):
    """
    Builds a disctionary with objects URLs that are potential duplicates:
    - news are duplicates if news.title and news.coverage are identical
    - events are duplicates if event.start_date and events.coverage are identical
    """
    seen = {}
    result = []
    for item in self.objectValues(METATYPE_NYSEMNEWS):
        marker = (item.title, item.coverage)
        if marker in seen:
            result.append(item)
            result.append(seen[marker])
            continue
        seen[marker] = item
    return result
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
        self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
        REQUEST.RESPONSE.redirect('%s/basketofapprovals_duplicates_html' % self.absolute_url())
NyFolder.processDuplicateContent = processDuplicateContent

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
        self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
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
security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'folder_basketofapprovals_published')
security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'folder_basketofapprovals_duplicates')
security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'processPublishedContent')

security.apply(NyFolder)
InitializeClass(NyFolder)
