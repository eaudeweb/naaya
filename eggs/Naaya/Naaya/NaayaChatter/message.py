#Python imports

#Zope imports
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from DateTime import DateTime

#Product imports
from constants import *

#Naaya imports
from Products.NaayaCore.managers.utils import utils


ut = utils()
def addChatMessage(self, id, user='', msg=''):
    """ Adds a new chat message """
    title =  '%s%s-%s' % (CHATTER_MESSAGE_PREFIX, user, msg)
    if not id or self._getOb(id, None):
        id = CHATTER_MESSAGE_PREFIX + ut.utGenRandomId(6)
    ob = message(id, title, user, msg)
    self._setObject(id, ob)
    return id


class message(Folder):
    """
    The chat message, stores a chat line 
    
    @param date_time: date and time posted
    @param user: the user id who sent this message
    @param msg: the submitted text message
    """
    id = ''
    title = ''
    date_time = None
    user = ''
    msg = ''

    def __init__(self, id, title, user, msg):
        self.id = id
        self.title = title
        self.date_time = DateTime()
        self.user = user
        self.msg = msg

    def get_posting_user(self):
        """ Returns the posting user id """
        return self.user

    def get_posting_time(self):
        """ Returns the time at whitch the message was posted """
        return self.date_time

    def get_msg(self):
        """ Returns the posted message"""
        return self.msg

    def get_date(self):
        """ """
        return self.date_time.Date()

    def get_time(self):
        """ """
        return self.date_time.Time()

    #Class metadata
    #Zope
    meta_type = CHATTER_MESSAGE_META_TYPE
    security = ClassSecurityInfo()
    all_meta_types = {}

InitializeClass(message)