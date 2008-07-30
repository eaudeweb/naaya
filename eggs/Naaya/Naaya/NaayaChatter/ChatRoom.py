#Python imports

#Zope imports
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from DateTime import DateTime
from time import time

#Product imports
from ChatArchive import manage_addChatArchive, manage_addChatArchive_html
from constants import *

#Naaya imports
from Products.NaayaCore.managers.utils import utils


ut = utils()
manage_addChatRoom_html = PageTemplateFile('zpt/chatroom_manage_add', globals())
def manage_addChatRoom(self, id='', title='', roles='', user_list='', REQUEST=None):
    """ Creates a new ChatRoom instance"""
    creator = self.getUserID()
    user_list = user_list.split(' ')
    id = ut.utGenObjectId(title) or ut.utCleanupId(id)
    if not id or self._getOb(id, None):
        id = CHATTER_ROOM_PREFIX + ut.utGenRandomId(6)
    ob = ChatRoom(id, title, roles, user_list, creator)
    self._setObject(id, ob)
    ob = self._getOb(id)
    ob.setRoomRoles()
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
    users_online = None

    #Class metadata
    #Zope
    meta_type = CHATTER_ROOM_META_TYPE
    security = ClassSecurityInfo()
    meta_types = ({'name':CHATTER_ARCHIVE_META_TYPE, 'action':'manage_addChatArchive_html'}, )
    all_meta_types = meta_types

    def __init__(self, id, title, roles, user_list, creator):
        self.id = id
        self.title = title
        self.roles = roles
        self.user_list = user_list
        self.previous_archive = ''
        self.latest_archive = ''
        self.releasedate = DateTime()
        self.creator = creator
        self.users_online = None

    security.declareProtected(CHATTER_VIEW_ROOM_PERMISSION, 'getChatRoom')
    def getChatRoom(self):
        """ Returns this Chat Room instance """
        return self

    security.declareProtected(CHATTER_MANAGE_ROOM_PERMISSION, 'setRoomRoles')
    def setRoomRoles(self):
        """ Give the owner local role to the user_list and assign view permissions to that role """
        roles = self.roles
        roles.append('Owner')
        for userid in self.user_list:
            self.manage_setLocalRoles(userid, ['Owner'])
        self.manage_permission(CHATTER_VIEW_ROOM_PERMISSION, roles)
        self.manage_permission(CHATTER_VIEW_ARCHIVE_PERMISSION, roles)
        self.manage_permission(CHATTER_VIEW_MESSAGE_PERMISSION, roles)
        self.manage_permission(CHATTER_ADD_MESSAGE_PERMISSION, roles)

    security.declareProtected(CHATTER_VIEW_ROOM_PERMISSION, 'get_friendlyDate')
    def get_friendlyDate(self):
        return ut.utShowFullDateTime(self.releasedate)

    security.declareProtected(CHATTER_VIEW_ROOM_PERMISSION, 'get_latest_archive')
    def get_latest_archive(self):
        """ Returns the active archive object """
        return self._getOb(self.latest_archive)

    security.declareProtected(CHATTER_VIEW_ROOM_PERMISSION, 'get_previous_archive')
    def get_previous_archive(self):
        """ Returns the previous archive object """
        return self._getOb(self.previous_archive)

    security.declareProtected(CHATTER_MANAGE_ROOM_PERMISSION, 'update_latest_previous')
    def update_latest_previous(self, id=''):
        """ Update the latest and previous archive properties """
        if id:
            self.previous_archive = self.latest_archive
            self.latest_archive = id

    security.declareProtected(CHATTER_VIEW_ROOM_PERMISSION, 'listArchives')
    def listArchives(self):
        """ Returns a list of contained message archive objects """
        return self.objectValues(CHATTER_ARCHIVE_META_TYPE)

    security.declareProtected(CHATTER_MANAGE_ROOM_PERMISSION, 'delArchive')
    def delArchive(self, archlist=[]):
        """ Deletes a list of archives """
        raise NotImplementedError

    security.declareProtected(CHATTER_MANAGE_ROOM_PERMISSION, 'addArchive')
    def addArchive(self, title='', automatic=False, REQUEST=None):
        """ Creates a new chat archive """
        #TODO: allow users to create own archives
        if automatic: self.update_latest_previous(manage_addChatArchive(self, automatic=automatic))
        else: manage_addChatArchive(self, title=title)

    security.declareProtected(CHATTER_VIEW_ROOM_PERMISSION, 'getOpenArchives')
    def getOpenArchives(self):
        """ Returns archives without a closing date """
        return [arch for arch in self.listArchives() if not arch.get_closing_date()]

    security.declareProtected(CHATTER_VIEW_ROOM_PERMISSION, 'checkArchive')
    def checkArchive(self, arch=None):
        """ Returns True if the archive was automatically created today """
        return arch.automatic and arch.get_creation_date().Date() == DateTime().Date()

    security.declareProtected(CHATTER_MANAGE_ROOM_PERMISSION, 'closeArchives')
    def closeArchives(self):
        """ Close expired automatic archives """
        today = DateTime()
        archives = self.getOpenArchives()
        for arch in archives:
            if arch.automatic and arch.get_creation_date().Date() != today.Date():
                arch.closing_date = today
        return self.getOpenArchives()

    security.declareProtected(CHATTER_VIEW_ROOM_PERMISSION, 'checkArchives')
    def checkArchives(self):
        """ Returns the latest automatic archive """
        archives = self.closeArchives()
        if archives: return [arch for arch in archives if self.checkArchive(arch)][0]
        else:
            self.addArchive(automatic=True)
            return self.get_latest_archive()

    security.declareProtected(CHATTER_ADD_MESSAGE_PERMISSION, 'submitMessage')
    def submitMessage(self, msg=''):
        """ Submits the chat message to the latest archive for handling """
        if msg:
            user = self.getUserID()
            self.checkArchives().addMessage(user, msg)

    security.declareProtected(CHATTER_VIEW_ROOM_PERMISSION, 'getSortedMessages')
    def getSortedMessages(self, lastid=''):
        """ Returns missing messages starting from lastid """
        latest = self._getOb(self.latest_archive, None)
        for message in ut.utSortObjsListByAttr(latest.listMessages(lastid), 'date_time', 0):
            yield message

    security.declareProtected(CHATTER_VIEW_ROOM_PERMISSION, 'updateOnlineUsers')
    def updateOnlineUsers(self):
        """ Update the users online list """
        user = self.getUserID()
        now = time()
        try:
            self.users_online[user] = now
        except:
            self.users_online = {}
            self.users_online[user] = now

    security.declareProtected(CHATTER_VIEW_ROOM_PERMISSION, 'messages_html')
    def messages_html(self, lastid=''):
        """ Returns missing messages"""
        self.updateOnlineUsers()
        return self.messages(lastid=lastid)

    security.declareProtected(CHATTER_VIEW_ROOM_PERMISSION, 'getOnlineUsers')
    def getOnlineUsers(self):
        """ Get the online user list """
        now = time()
        return [k for k, v in self.users_online.items() if int(now - v) < 60]

    security.declareProtected(CHATTER_VIEW_ROOM_PERMISSION, 'messages')
    security.declareProtected(CHATTER_VIEW_ROOM_PERMISSION, 'index_html')
    security.declareProtected(CHATTER_VIEW_ROOM_PERMISSION, 'online_users_html')

    messages = PageTemplateFile('zpt/messages_html', globals())
    index_html = PageTemplateFile('zpt/chatroom_index', globals())
    online_users_html = PageTemplateFile('zpt/online_users_html', globals())

    #Product
    security.declareProtected(CHATTER_ADD_ARCHIVE_PERMISSION, 'manage_addChatArchive')
    security.declareProtected(CHATTER_ADD_ARCHIVE_PERMISSION, 'manage_addChatArchive_html')

    manage_addChatArchive = manage_addChatArchive
    manage_addChatArchive_html = manage_addChatArchive_html

InitializeClass(ChatRoom)