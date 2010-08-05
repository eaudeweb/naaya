#The contents of this file are subject to the Mozilla Public
#License Version 1.1 (the "License"); you may not use this file
#except in compliance with the License. You may obtain a copy of
#the License at http://www.mozilla.org/MPL/
#
#Software distributed under the License is distributed on an "AS
#IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
#implied. See the License for the specific language governing
#rights and limitations under the License.
#
#The Original Code is "EWGeoMap"
#
#The Initial Owner of the Original Code is European Environment
#Agency (EEA).  Portions created by Finsiel Romania and Eau de Web 
#are Copyright (C) 2000 by European Environment Agency.  All
#Rights Reserved.
#
#Contributor(s):
#  Original Code: 
#        Cornel Nitu (Eau de Web)
#        Bogdan Grama (Finsiel Romania)
#        Iulian Iuga (Finsiel Romania)
#  Porting to Naaya: 
#        Cornel Nitu (Eau de Web)


#Python imports

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

#Product imports

class symbol_item:
    """ """

    def __init__(self, id, title, description, picture):
        """Constructor"""
        self.id = id
        self.title = title
        self.description = description
        self.picture = picture

    def setPicture(self, picture):
        """ """
        if picture != '':
            if hasattr(picture, 'filename'):
                if picture.filename != '':
                    content = picture.read()
                    if content != '':
                        self.picture = content
                        self._p_changed = 1
            else:
                self.picture = picture
                self._p_changed = 1

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

InitializeClass(symbol_item)

class symbols_tool:
    """ """

    def __init__(self):
        """ """
        self.__symbol_collection = {}

    def __addSymbol(self, id, title, description, picture):
        """ """
        obj = symbol_item(id, title, description, None)
        obj.setPicture(picture)
        self.__symbol_collection[id] = obj

    def __updateSymbol(self, id, title, description, picture):
        """ """
        try: obj = self.__symbol_collection[id]
        except: pass
        else:
            obj.title = title
            obj.description = description
            obj.setPicture(picture)

    def __deleteSymbol(self, id):
        """ """
        try: del(self.__symbol_collection[id])
        except: pass

    def getSymbolsList(self):
        """Get a list with all objects"""
        try: return self.__symbol_collection.values()
        except: return []

    def getSymbolsIds(self):
        """Get a list with all objects' ids """
        try: return [x.id for x in self.__symbol_collection.values()]
        except: return []

    def getSymbol(self, id):
        """Get an object"""
        try: return self.__symbol_collection[id]
        except: return None

    def getSymbolData(self, id):
        """ """
        ob = self.getSymbol(id)
        if ob is not None:
            return {'action': 'update', 'id': ob.id, 'title': ob.title,
                'description': ob.description, 'picture': ob.picture}
        else:
            return {'action': 'add', 'id': '', 'title': '',
                'description': '', 'picture': None}

    def getSymbolTitle(self, id):
        """Get title"""
        try: return self.__symbol_collection[id].title
        except: return id

    def getSymbolZPicture(self, id, REQUEST=None):
        """Get picture stream in zope interface """
        try:
            return self.__symbol_collection[id].picture
        except: return None

    def getSymbolPicture(self, id, REQUEST=None):
        """Get picture stream"""
        try:
            REQUEST.RESPONSE.setHeader('Content-Type', 'image/jpeg')
            REQUEST.RESPONSE.setHeader('Content-Disposition', 'inline; filename="%s.jpg"' % id)
            return self.__symbol_collection[id].picture
        except: return None

    def addSymbol(self, id, title, description, picture):
        """ """
        self.__addSymbol(id, title, description, picture)
        self._p_changed = 1

    def updateSymbol(self, id, title, description, picture):
        """ """
        self.__updateSymbol(id, title, description, picture)
        self._p_changed = 1

    def deleteSymbol(self, ids):
        """ """
        map(self.__deleteSymbol, ids)
        self._p_changed = 1
