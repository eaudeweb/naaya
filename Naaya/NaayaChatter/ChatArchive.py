#Python imports

#Zope imports
from OFS.Folder import Folder
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
    username = self.getUserID(REQUEST)
    if automatic: title = '%s %s' % (ut.utShowFullDateTime(DateTime()), username)
    id = ut.utGenObjectId(title) or ut.utCleanupId(id)
    if not id or self._getOb(id, None): id = CHATTER_ARCHIVE_PREFIX + ut.utGenRandomId(6)
    ob = ChatArchive(id, title, automatic)
    self._setObject(id, ob)
    if REQUEST:
        return self.manage_main(self, REQUEST, update_menu=1)
    return ob.getId()


class ChatArchive(Folder):
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

    def __init__(self, id, title, automatic=False):
        self.id = id
        self.title = title
        self.creation_date = DateTime()
        self.closing_date = None
        self.automatic = automatic
        self.last_msg_id = 0

    def getChatArchive(self):
        """ Returns this Chat Archive instance """
        return self

    def get_creation_date(self):
        """ Returns the creation date of this archive """
        return self.creation_date

    def get_closing_date(self):
        """ Returns the closing date of this archive """
        return self.closing_date

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

    def delMessages(self, messagelist=[]):
        """ Deletes a list of messages """
        #make use of manage_delObjects
        raise NotImplementedError

    def addMessage(self, user, msg):
        """ Adds a new message in this archive """
        if self.last_msg_id: last_int = int(self.last_msg_id[len(CHATTER_MESSAGE_PREFIX):])
        else: last_int = 0
        msgid = '%s%s' % (CHATTER_MESSAGE_PREFIX , ( last_int + 1 ))
        self.last_msg_id = addChatMessage(self, msgid, user, msg)

    index_html = PageTemplateFile('zpt/chatarchive_index', globals())

    #Class metadata
    #Zope
    meta_type = CHATTER_ARCHIVE_META_TYPE
    security = ClassSecurityInfo()
    all_meta_types = {}


    #Product
    addChatMessage = addChatMessage

InitializeClass(ChatArchive)