#Python imports

#Zope imports
from OFS.Folder import Folder
from App.ImageFile import ImageFile
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view

#Product imports
from ChatRoom import manage_addChatRoom, manage_addChatRoom_html
from constants import *

#Naaya imports
from Products.NaayaCore.managers.utils import utils



ut = utils()
manage_addChatter_html = PageTemplateFile('zpt/chatter_manage_add', globals())
def manage_addChatter(self, id='', title='', REQUEST=None):
    """ Creates a new Chatter instance"""
    id = ut.utGenObjectId(title) or ut.utCleanupId(id)
    if not id or self._getOb(id, None):
        id = CHATTER_PREFIX + ut.utGenRandomId(6)
    ob = Chatter(id, title)
    self._setObject(id, ob)
    if REQUEST:
        return self.manage_main(self, REQUEST, update_menu=1)

class Chatter(Folder):
    """ Contains chat rooms """

    id = ''
    title = ''

    def __init__(self, id, title):
        self.id = id
        self.title = title

    def getChatter(self):
        """ Returns this Chatter instance """
        return self

    def listRooms(self):
        """ Returns a list of contained ChatRoom objects """
        return self.objectValues(CHATTER_ROOM_META_TYPE)

    def delRooms(self, roomlist=[]):
        """ Deletes a list of chat rooms """
        #make use of manage_delObjects
        raise NotImplementedError

    def addRoom(self, id='', title='', roles=[], user_list=[], REQUEST=None):
        """ Creates a new chat room """
        manage_addChatRoom(self, id, title, roles, user_list)
        if REQUEST:
            self.REQUEST.RESPONSE.redirect(self.absolute_url())

    def getUserID(self, REQUEST):
        if REQUEST:
            return REQUEST.AUTHENTICATED_USER.getUserName()
        else:
            return 'no-user'

    def getIntFromId(self, id='', prefix=''):
        return int(id[len(prefix):])

    index_html = PageTemplateFile('zpt/chatter_index', globals())
    style_css = PageTemplateFile('zpt/style', globals())
    jquery_js = ImageFile('www/jquery.js', globals())

    #Class metadata
    #Zope
    meta_type = CHATTER_META_TYPE
    security = ClassSecurityInfo()
    meta_types = ({'name':CHATTER_ROOM_META_TYPE, 'action':'manage_addChatRoom_html'}, )
    all_meta_types = meta_types


    #Product
    manage_addChatRoom = manage_addChatRoom
    manage_addChatRoom_html = manage_addChatRoom_html

InitializeClass(Chatter)