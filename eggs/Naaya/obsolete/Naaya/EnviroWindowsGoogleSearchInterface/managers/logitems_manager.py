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
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania
#
#
#
#$Id: logitems_manager.py 2727 2004-11-30 07:36:49Z finrocvs $

#Python imports

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

#Product imports

class logitem_item:
    """ """

    def __init__(self, id, date, resultsfound, resultssaved, errors):
        self.id = id
        self.date = date
        self.resultsfound = resultsfound
        self.resultssaved = resultssaved
        self.errors = errors

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

InitializeClass(logitem_item)

class logitems_manager:
    """ """

    def __init__(self):
        self.__logitems_collection = {}

    def __add_logitem_item(self, id, date, resultsfound, resultssaved, errors):
        #create a new item
        item = logitem_item(id, date, resultsfound, resultssaved, errors)
        self.__logitems_collection[id] = item

    def __delete_logitem_item(self, id):
        #delete an item
        try: del(self.__logitems_collection[id])
        except: pass

    #api
    def get_logitems_collection(self):
        #get the collection
        return self.__logitems_collection

    def get_logitems_list(self):
        #get a list with all items
        return self.utSortObjsListByAttr(self.__logitems_collection.values(), 'date', 1)

    def get_logitem_item(self, id):
        #get an item
        try: return self.__logitems_collection[id]
        except: return None

    def add_logitem_item(self, id, date, resultsfound, resultssaved, errors):
        #create a new item
        self.__add_logitem_item(id, date, resultsfound, resultssaved, errors)
        self._p_changed = 1

    def delete_logitem_item(self, ids):
        #delete 1 or more items
        map(self.__delete_logitem_item, ids)
        self._p_changed = 1

    def empty_logitems(self):
        #remove all items
        self.__logitems_collection = {}
        self._p_changed = 1
