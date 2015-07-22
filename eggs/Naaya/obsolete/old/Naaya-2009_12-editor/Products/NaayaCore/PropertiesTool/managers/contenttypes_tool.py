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

#Python imports

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

#Product imports

class ContentType:
    """Defines a ContentType. Properties:
        - id : generated unique id
        - title : string
    """

    def __init__(self, p_id, p_title, p_picture):
        """Constructor"""
        self.id = p_id
        self.title = p_title
        self.picture = p_picture

    def setPicture(self, p_picture):
        """ """
        if p_picture != '':
            if hasattr(p_picture, 'filename'):
                if p_picture.filename != '':
                    l_read = p_picture.read()
                    if l_read != '':
                        self.picture = l_read
                        self._p_changed = 1
            else:
                self.picture = p_picture
                self._p_changed = 1

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

InitializeClass(ContentType)

class contenttypes_tool:
    """This class is responsable with ContentType management.
        All the data is stored in a dictionary like structure:
            - key: object's id
            - value: object
    """

    def __init__(self):
        """Constructor"""
        self.__contenttype_dictionary = {}

    def __createContentType(self, p_id, p_title, p_picture):
        """Add"""
        obj = ContentType(p_id, p_title, None)
        obj.setPicture(p_picture)
        self.__contenttype_dictionary[p_id] = obj

    def __modifyContentType(self, p_id, p_title, p_picture):
        """Modify"""
        try: obj = self.__contenttype_dictionary[p_id]
        except: pass
        else:
            obj.title = p_title
            obj.setPicture(p_picture)

    def __deleteContentType(self, p_id):
        """Delete"""
        try: del(self.__contenttype_dictionary[p_id])
        except: pass

    def getContentTypesList(self):
        """Get a list with all objects"""
        try: return self.__contenttype_dictionary.values()
        except: return []

    def getContentType(self, id):
        """Get an object"""
        try: return self.__contenttype_dictionary[id]
        except: return None

    def getContentTypeTitle(self, id):
        """Get title"""
        try: return self.__contenttype_dictionary[id].title
        except: return id

    def getContentTypePicture(self, id):
        """Get picture stream"""
        try: return self.__contenttype_dictionary[id].picture
        except: return self.__contenttype_dictionary['application/octet-stream'].picture

    def createContentType(self, p_id, p_title, p_picture):
        """Add from console"""
        self.__createContentType(p_id, p_title, p_picture)
        self._p_changed = 1

    def modifyContentType(self, p_id, p_title, p_picture):
        """Modify"""
        self.__modifyContentType(p_id, p_title, p_picture)
        self._p_changed = 1

    def deleteContentType(self, p_ids):
        """Delete"""
        map(self.__deleteContentType, p_ids)
        self._p_changed = 1

    def getContentTypeData(self, p_id):
        """ """
        obj = self.getContentType(p_id)
        if obj is not None:
            return ['update', obj.id, obj.title, obj.picture]
        else:
            return ['add', '', '', None]
