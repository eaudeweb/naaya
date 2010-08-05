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
# Agency (EEA). Portions created by Eau de Web are
# Copyright (C) European Environment Agency. All Rights Reserved.
#
# Authors:
#
# David Batranu, Eau de Web


#Python imports

#Zope imports
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from DateTime import DateTime

#Product imports
from message import addChatMessage
from constants import *

#Naaya imports
from Products.NaayaCore.managers.utils import utils


ut = utils()
manage_addChatArchive_html = PageTemplateFile('zpt/chatarchive_manage_add', globals())
def manage_addChatArchive(self, id='', title='', automatic=False, REQUEST=None):
    """ Creates a new ChatArchive instance"""
    username = self.getUserID()
    if automatic: title = '%s %s' % (ut.utShowFullDateTime(DateTime()), username)
    id = ut.utGenObjectId(title) or ut.utCleanupId(id)
    if not id or self._getOb(id, None): id = CHATTER_ARCHIVE_PREFIX + ut.utGenRandomId(6)
    ob = ChatArchive(id, title, automatic)
    self._setObject(id, ob)
    if REQUEST:
        return self.manage_main(self, REQUEST, update_menu=1)
    return ob.getId()


class ChatArchive(BTreeFolder2):
    """
    Contains message objects
    @param creation_date: log the creation date/time of this archive
    @param closing_date: log the closing date/time for this archive

    #TODO: log creation_date
    #TODO: log closing_date
    #TODO: automate the creation of daily archives
    """

    id = ''
    title = ''
    creation_date = None
    closing_date = None
    automatic = False
    last_msg_id = 0

    #Class metadata
    #Zope
    meta_type = CHATTER_ARCHIVE_META_TYPE
    security = ClassSecurityInfo()
    all_meta_types = {}

    def __init__(self, id, title, automatic=False):
        self.id = id
        self.title = title
        self.creation_date = DateTime()
        self.closing_date = None
        self.automatic = automatic
        self.last_msg_id = 0
        BTreeFolder2.__init__(self)


    security.declareProtected(CHATTER_VIEW_ROOM_PERMISSION, 'getChatArchive')
    def getChatArchive(self):
        """ Returns this Chat Archive instance """
        return self

    security.declareProtected(CHATTER_VIEW_ROOM_PERMISSION, 'get_firendly_title')
    def get_friendly_title(self):
        """ """
        if self.automatic: return ' '.join(self.title.split(' ')[:3])
        else: return self.title

    security.declareProtected(CHATTER_VIEW_ROOM_PERMISSION, 'get_creation_date')
    def get_creation_date(self):
        """ Returns the creation date of this archive """
        return self.creation_date

    security.declareProtected(CHATTER_VIEW_ROOM_PERMISSION, 'get_closing_date')
    def get_closing_date(self):
        """ Returns the closing date of this archive """
        return self.closing_date

    security.declareProtected(CHATTER_VIEW_ROOM_PERMISSION, 'listMessages')
    def listMessages(self, lastid=''):
        """ Returns a list of contained message objects """
        if lastid and lastid != self.last_msg_id:
            ret = []
            lastid = self.getIntFromId(lastid, CHATTER_MESSAGE_PREFIX)
            lastmsgid = self.getIntFromId(self.last_msg_id, CHATTER_MESSAGE_PREFIX)
            need = range(lastid + 1, lastmsgid + 1)
            for i in need:
                id = CHATTER_MESSAGE_PREFIX + str(i)
                ret.append(self._getOb(id))
            return ret
        if lastid and lastid == self.last_msg_id:
            return []
        if not lastid:
            return self.objectValues(CHATTER_MESSAGE_META_TYPE)

    security.declareProtected(CHATTER_VIEW_ROOM_PERMISSION, 'getSortedMessages')
    def getSortedMessages(self):
        """ returns all archive messages in order of submission """
        for message in ut.utSortObjsListByAttr(self.listMessages(), 'date_time', 0):
            yield message

    security.declareProtected(CHATTER_MANAGE_ROOM_PERMISSION, 'delMessages')
    def delMessages(self, messagelist=[]):
        """ Deletes a list of messages """
        #make use of manage_delObjects
        raise NotImplementedError

    security.declareProtected(CHATTER_VIEW_ROOM_PERMISSION, 'addMessage')
    def addMessage(self, user, msg):
        """ Adds a new message in this archive """
        if self.last_msg_id: last_int = int(self.last_msg_id[len(CHATTER_MESSAGE_PREFIX):])
        else: last_int = 0
        msgid = '%s%s' % (CHATTER_MESSAGE_PREFIX , ( last_int + 1 ))
        self.last_msg_id = addChatMessage(self, msgid, user, msg)

    security.declareProtected(CHATTER_VIEW_ROOM_PERMISSION, 'index_html')
    index_html = PageTemplateFile('zpt/chatarchive_index', globals())


    #Product
    security.declareProtected(CHATTER_VIEW_ROOM_PERMISSION, 'addChatMessage')
    addChatMessage = addChatMessage

InitializeClass(ChatArchive)
