#Python imports

#Zope imports
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from DateTime import DateTime

#Product imports
from ChatArchive import manage_addChatArchive, manage_addChatArchive_html
from constants import *

#Naaya imports
from Products.NaayaCore.managers.utils import utils


ut = utils()
manage_addChatRoom_html = PageTemplateFile('zpt/chatroom_manage_add', globals())
def manage_addChatRoom(self, id='', title='', roles='', user_list='', REQUEST=None):
    """ Creates a new ChatRoom instance"""
    creator = self.getUserID(REQUEST)
    id = ut.utGenObjectId(title) or ut.utCleanupId(id)
    if not id or self._getOb(id, None):
        id = CHATTER_ROOM_PREFIX + ut.utGenRandomId(6)
    ob = ChatRoom(id, title, roles, user_list, creator)
    self._setObject(id, ob)
    ob = self._getOb(id)
    ob.addArchive(automatic=True)
    if REQUEST:
        return self.manage_main(self, REQUEST, update_menu=1)


class ChatRoom(Folder):
    """
    Contains chat archives
    
    @param roles: the list of user roles that are allowed in the chat room
    @param user_list: the list of users that are allowd in the chat room
    @param previous_archive: log the previously created archive
    @param latest_archive: log the last created archive
    """

    id = ''
    title = ''
    roles = None # list expected
    user_list = None # list expected
    previous_archive = ''
    latest_archive = ''
    releasedate = ''
    creator = ''

    def __init__(self, id, title, roles, user_list, creator):
        self.id = id
        self.title = title
        self.roles = roles
        self.user_list = user_list
        self.previous_archive = ''
        self.latest_archive = ''
        self.releasedate = DateTime()
        self.creator = creator

    def getChatRoom(self):
        """ Returns this Chat Room instance """
        return self

    def get_friendlyDate(self):
        return ut.utShowFullDateTime(self.releasedate)

    def get_latest_archive(self):
        """ Returns the active archive object """
        return self._getOb(self.latest_archive)

    def get_previous_archive(self):
        """ Returns the previous archive object """
        return self._getOb(self.previous_archive)

    def update_latest_previous(self, id=''):
        """ Update the latest and previous archive properties """
        if id:
            self.previous_archive = self.latest_archive
            self.latest_archive = id

    def listArchives(self):
        """ Returns a list of contained message archive objects """
        return self.objectValues(CHATTER_ARCHIVE_META_TYPE)

    def delArchive(self, archlist=[]):
        """ Deletes a list of archives """
        raise NotImplementedError

    def addArchive(self, title='', automatic=False, REQUEST=None):
        """ Creates a new chat archive """
        #TODO: allow users to create own archives
        if automatic: self.update_latest_previous(manage_addChatArchive(self, automatic=automatic))
        else: manage_addChatArchive(self, title=title)

    def getOpenArchives(self):
        """ Returns archives without a closing date """
        return [arch for arch in self.listArchives() if not arch.get_closing_date()]

    def checkArchive(self, arch=None):
        """ Returns True if the archive was automatically created today """
        return arch.automatic and arch.get_creation_date().Date() == DateTime().Date()

    def closeArchives(self):
        """ Close expired automatic archives """
        today = DateTime()
        archives = self.getOpenArchives()
        for arch in archives:
            if arch.automatic and arch.get_creation_date().Date() != today.Date():
                arch.closing_date = today
        return self.getOpenArchives()

    def checkArchives(self):
        """ Returns the latest automatic archive """
        archives = self.closeArchives()
        if archives: return [arch for arch in archives if self.checkArchive(arch)][0]
        else:
            self.addArchive(automatic=True)
            return self.get_latest_archive()

    def submitMessage(self, msg='', REQUEST=None):
        """ Submits the chat message to the latest archive for handling """
        if msg:
            user = self.getUserID(REQUEST)
            self.checkArchives().addMessage(user, msg)

    def getSortedMessages(self, lastid=''):
        """ """
        latest = self._getOb(self.latest_archive, None)
        for message in ut.utSortObjsListByAttr(latest.listMessages(lastid), 'date_time'):
            yield message

    def messages_html(self, lastid=''):
        """ """
        return self.messages(lastid=lastid)

    messages = PageTemplateFile('zpt/xml_messages', globals())
    index_html = PageTemplateFile('zpt/chatroom_index', globals())

    #Class metadata
    #Zope
    meta_type = CHATTER_ROOM_META_TYPE
    security = ClassSecurityInfo()
    meta_types = ({'name':CHATTER_ARCHIVE_META_TYPE, 'action':'manage_addChatArchive_html'}, )
    all_meta_types = meta_types


    #Product
    manage_addChatArchive = manage_addChatArchive
    manage_addChatArchive_html = manage_addChatArchive_html

InitializeClass(ChatRoom)