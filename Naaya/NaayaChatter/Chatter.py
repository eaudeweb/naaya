#Python imports
import re

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

    #Class metadata
    #Zope
    meta_type = CHATTER_META_TYPE
    security = ClassSecurityInfo()
    meta_types = ({'name':CHATTER_ROOM_META_TYPE, 'action':'manage_addChatRoom_html'}, )
    all_meta_types = meta_types

    def __init__(self, id, title):
        self.id = id
        self.title = title

    security.declareProtected(CHATTER_VIEW_PERMISSION, 'getChatter')
    def getChatter(self):
        """ Returns this Chatter instance """
        return self

    security.declareProtected(CHATTER_VIEW_PERMISSION, 'getChatter')
    def listRooms(self):
        """ Returns a list of contained ChatRoom objects """
        return self.objectValues(CHATTER_ROOM_META_TYPE)

    security.declareProtected(CHATTER_MANAGE_PERMISSION, 'getChatter')
    def delRooms(self, roomlist=[]):
        """ Deletes a list of chat rooms """
        #make use of manage_delObjects
        raise NotImplementedError

    security.declareProtected(CHATTER_ADD_ROOM_PERMISSION, 'getChatter')
    def addRoom(self, id='', title='', roles=[], user_list=[], private=0, REQUEST=None):
        """ Creates a new chat room """
        r_id = manage_addChatRoom(self, id, title, roles, user_list, private)
        if REQUEST:
            return self.REQUEST.RESPONSE.redirect(self.absolute_url())
        return r_id

    def getUserObj(self):
        return self.REQUEST.get('AUTHENTICATED_USER', None)

    def getUserID(self):
        return self.getUserObj().getUserName()

    def getIntFromId(self, id='', prefix=''):
        return int(id[len(prefix):])

    def linkifyURLS(self, string):
        def replace(match):
            txt = match.group('uri').replace('&amp;', '&')
            #if txt.startswith('http://'):
            if match.group('uri_proto'):
                uri = txt
            else:
                uri = 'http://' + txt
            return '<a href="%s">%s</a>' % (uri, txt)
        
        
        initial_lookbehind = r'(?<![\d\w\-])'
        host_component = r'[\w\d\-]+'
        host_port = r'\:\d+'
        path = r'/[^\s]*'
        get_params = r'\?[\w\d\=\%\&\;\-]*(?<!;)'
        
        regexp = r'(?P<uri>' \
                + initial_lookbehind \
                + r'((?P<uri_proto>\w+\://)|www\.)' \
                + host_component + r'(\.' + host_component + r')*' + r'('+ host_port + r')?' \
                + r'(' + path + r')?' \
                + r'(' + get_params + r')?' \
            + r')'
        
        return re.sub(regexp, replace, string)

    security.declareProtected(CHATTER_VIEW_PERMISSION, 'index_html')

    index_html = PageTemplateFile('zpt/chatter_index', globals())
    style_css = PageTemplateFile('zpt/style', globals())
    jquery_js = ImageFile('www/jquery.js', globals())
    room_js = ImageFile('www/room.js', globals())

    #Product
    security.declareProtected(CHATTER_ADD_ROOM_PERMISSION, 'manage_addChatRoom')
    security.declareProtected(CHATTER_ADD_ROOM_PERMISSION, 'manage_addChatRoom_html')

    manage_addChatRoom = manage_addChatRoom
    manage_addChatRoom_html = manage_addChatRoom_html

InitializeClass(Chatter)
