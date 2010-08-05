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

    #Class metadata
    #Zope
    meta_type = CHATTER_MESSAGE_META_TYPE
    security = ClassSecurityInfo()
    all_meta_types = {}

    def __init__(self, id, title, user, msg):
        self.id = id
        self.title = title
        self.date_time = DateTime()
        self.user = user
        self.msg = msg

    security.declareProtected(CHATTER_VIEW_ROOM_PERMISSION, 'get_posting_user')
    def get_posting_user(self):
        """ Returns the posting user id """
        return self.user

    security.declareProtected(CHATTER_VIEW_ROOM_PERMISSION, 'get_posting_time')
    def get_posting_time(self):
        """ Returns the time at whitch the message was posted """
        return self.date_time

    security.declareProtected(CHATTER_VIEW_ROOM_PERMISSION, 'get_msg')
    def get_msg(self):
        """ Returns the posted message"""
        msg = ut.utXmlEncode(self.msg)
        msg = self.linkifyURLS(msg)
        return msg

    security.declareProtected(CHATTER_VIEW_ROOM_PERMISSION, 'get_date')
    def get_date(self):
        """ """
        return self.date_time.Date()

    security.declareProtected(CHATTER_VIEW_ROOM_PERMISSION, 'get_time')
    def get_time(self):
        """ """
        return self.date_time.Time()

InitializeClass(message)
