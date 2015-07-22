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

class ref_item:
    """ """

    def __init__(self, id, title):
        self.id = id
        self.title = title

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

InitializeClass(ref_item)

class ref_manager:
    """ """

    def __init__(self):
        """ """
        self.__collection = {}

    #security stuff
    security = ClassSecurityInfo()

    def __add_item(self, id, title):
        #create a new item
        item = ref_item(id, title)
        self.__collection[id] = item

    def __update_item(self, id, title):
        #modify an item
        try:
            item = self.__collection[id]
        except:
            pass
        else:
            item.title = title

    def __delete_item(self, id):
        #delete an item
        try: del(self.__collection[id])
        except: pass

    #api
    def get_collection(self):
        #get the collection
        return self.__collection

    def get_list(self):
        #get a list with all items
        try: return self.utSortObjsListByAttr(self.__collection.values(), 'title', 0)
        except: return []

    def get_item(self, id):
        #get an item
        try: return self.__collection[id]
        except: return None

    def get_item_data(self, id):
        #get an item data
        item = self.get_item(id)
        if item is not None:
            return ['update', item.id, item.title]
        else:
            return ['add', '', '']

    def add_item(self, id, title):
        #create a new item
        self.__add_item(id, title)
        self._p_changed = 1

    def update_item(self, id, title):
        #modify an item
        self.__update_item(id, title)
        self._p_changed = 1

    def delete_item(self, ids):
        #delete 1 or more items
        map(self.__delete_item, ids)
        self._p_changed = 1

InitializeClass(ref_manager)
