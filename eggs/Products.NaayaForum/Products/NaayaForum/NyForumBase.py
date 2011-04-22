"""
This module contains the base class of Naaya Forum.
"""
from AccessControl import ClassSecurityInfo, getSecurityManager
from Globals import InitializeClass

from constants import *
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyBase import NyBase

class NyForumBase(NyAttributes, NyBase):
    """
    The base class of Naaya Forum. It implements basic functionality
    common to all classes.
    """

    def __init__(self):
        """
        Constructor.
        """
        pass

    security = ClassSecurityInfo()

    def _objectkeywords(self, lang):
        """
        Builds the object keywords from common multilingual properties.
        @param lang: the index language
        @type lang: string
        """
        v = [self.title, self.description]
        return u' '.join(v)

    security.declarePrivate('objectkeywords')
    def objectkeywords(self, lang):
        """
        For each portal language an index I{objectkeywords}_I{lang} is created.
        Process the keywords for the specific catalog index.

        B{This method can be overwritten by some types of objects if additonal
        properties values must be considered as keywords.}
        @param lang: the index language
        @type lang: string
        """
        return self._objectkeywords(lang)

    def checkPermission(self, p_permission):
        """
        Generic function to check a given permission on the current object.
        @param p_permission: permissions name
        @type p_permission: string
        @return:
            - B{1} if the current user has the permission
            - B{None} otherwise
        """
        return bool(getSecurityManager().checkPermission(p_permission, self))

    def checkPermissionAddForum(self):
        """
        Check the permission to add forum topics.
        """
        return self.checkPermission(PERMISSION_ADD_FORUM)

    def checkPermissionAddForumTopic(self):
        """
        Check the permission to add forum topics.
        """
        return self.checkPermission(PERMISSION_MODIFY_FORUMTOPIC)

    def checkPermissionModifyForumTopic(self):
        """
        Check the access to edit/delete a forum topic.
        """
        return self.checkPermission(PERMISSION_MODIFY_FORUMTOPIC)

    def checkPermissionAddForumMessage(self):
        """
        Check the permission to add forum messages.
        """
        return self.checkPermission(PERMISSION_ADD_FORUMMESSAGE)

    def checkPermissionModifyForumMessage(self):
        """
        Check the permission to edit/delete a forum message.
        """
        return self.checkPermission(PERMISSION_MODIFY_FORUMMESSAGE)

InitializeClass(NyForumBase)
