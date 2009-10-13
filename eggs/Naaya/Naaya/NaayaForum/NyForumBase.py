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
# The Original Code is Naaya version 1.0
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

"""
This module contains the base class of Naaya Forum.
"""

#Python imports

#Zope imports
from OFS.Folder import Folder
from AccessControl import ClassSecurityInfo, getSecurityManager
from Globals import InitializeClass

#Product imports
from constants import *
from Products.NaayaBase.NyAttributes import NyAttributes

class NyForumBase(NyAttributes):
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

    def manage_afterAdd(self, item, container):
        """
        This method is called, whenever _setObject in ObjectManager gets called.
        """
        Folder.inheritedAttribute('manage_afterAdd')(self, item, container)
        self.catalogNyObject(self)

    def manage_beforeDelete(self, item, container):
        """
        This method is called, when the object is deleted.
        """
        Folder.inheritedAttribute('manage_beforeDelete')(self, item, container)
        self.uncatalogNyObject(self)

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
        return getSecurityManager().checkPermission(p_permission, self) is not None

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
