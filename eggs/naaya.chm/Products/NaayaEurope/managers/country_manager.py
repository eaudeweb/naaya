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
# Dragos Chirila, Finsiel Romania

#Python imports

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

#Product imports

class country_item:
    """ """

    def __init__(self, id, title, organisation, contact, state, url, host, cbd_url):
        self.id = id
        self.title = title
        self.organisation = organisation
        self.contact = contact
        self.state = state
        self.url = url
        self.host = host
        self.cbd_url = cbd_url

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

InitializeClass(country_item)

class country_manager:
    """ """

    def __init__(self):
        """ """
        self.__collection = {}

    #security stuff
    security = ClassSecurityInfo()

    def __add_item(self, id, title, organisation, contact, state, url, host, cbd_url):
        #create a new item
        item = country_item(id, title, organisation, contact, state, url, host, cbd_url)
        self.__collection[id] = item

    def __update_item(self, id, title, organisation, contact, state, url, host, cbd_url):
        #modify an item
        try:
            item = self.__collection[id]
        except:
            pass
        else:
            item.title = title
            item.organisation = organisation
            item.contact = contact
            item.state = state
            item.url = url
            item.host = host
            item.cbd_url = cbd_url

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
        return self.__collection.values()

    def get_sorted_list(self):
        #return a list with all items sorted by title ascendent
        l = [(self.getEuropeCountryTitle(x.id), x) for x in self.__collection.values()]
        l.sort()
        return [x[1] for x in l]

    def get_item(self, id):
        #get an item
        try: return self.__collection[id]
        except: return None

    def get_item_data(self, id):
        #get an item data
        item = self.get_item(id)
        if item is not None:
            return ['update', item.id, item.title, item.organisation, item.contact, item.state, item.url, item.host, item.cbd_url]
        else:
            return ['add', '', '', '', '', 1, '', '', '']

    def add_item(self, id, title, organisation, contact, state, url, host, cbd_url):
        #create a new item
        self.__add_item(id, title, organisation, contact, state, url, host, cbd_url)
        self._p_changed = 1

    def update_item(self, id, title, organisation, contact, state, url, host, cbd_url):
        #modify an item
        self.__update_item(id, title, organisation, contact, state, url, host, cbd_url)
        self._p_changed = 1

    def delete_item(self, ids):
        #delete 1 or more items
        map(self.__delete_item, ids)
        self._p_changed = 1

InitializeClass(country_manager)
