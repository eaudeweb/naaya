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

#Python imports

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

#Product imports

class networkportal_item:
    """ """

    def __init__(self, id, title, url, langs):
        """ """
        self.id = id
        self.title = title
        self.url = url
        self.langs = langs

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

InitializeClass(networkportal_item)

class networkportals_manager:
    """ """

    def __init__(self):
        """ """
        self.__networkportals_collection = {}

    def __add_networkportal_item(self, id, title, url, langs):
        #create a new item
        item = networkportal_item(id, title, url, langs)
        self.__networkportals_collection[id] = item

    def __edit_networkportal_item(self, id, title, url, langs):
        #modify an item
        try:
            item = self.__networkportals_collection[id]
        except:
            pass
        else:
            item.title = title
            item.url = url
            item.langs = langs

    def __delete_networkportal_item(self, id):
        #delete an item
        try: del(self.__networkportals_collection[id])
        except: pass

    #api
    def get_networkportals_collection(self):
        #get the collection
        return self.__networkportals_collection

    def get_networkportals_list(self):
        #get a list with all items
        return self.__networkportals_collection.values()

    def get_networkportal_item(self, id):
        #get an item
        try: return self.__networkportals_collection[id]
        except: return None

    def get_networkportal_title(self, id):
        #get the title of an item
        try: return self.__networkportals_collection[id].title
        except: return ''

    def get_networkportal_langs_map(self):
        #returns a list of tuples (lang id, lalg label) from
        #all network portals
        d = {}
        for x in self.__networkportals_collection.values():
            for l in x.langs:
                d[l] = ''
        return zip(d.keys(), map(self.gl_get_language_name, d.keys()))

    def get_networkportal_langs(self, id):
        #returns a comma separated string with languages labels
        try: return ', '.join(map(self.gl_get_language_name, self.__networkportals_collection[id].langs))
        except: return ''

    def get_networkportal_item_data(self, id):
        #get an item data
        item = self.get_networkportal_item(id)
        if item is not None: 
            return ['edit', item.id, item.title, item.url, item.langs]
        else:
            return ['add', '', '', '', []]

    def add_networkportal_item(self, id, title, url, langs):
        #create a new item
        self.__add_networkportal_item(id, title, url, langs)
        self._p_changed = 1

    def edit_networkportal_item(self, id, title, url, langs):
        #modify an item
        self.__edit_networkportal_item(id, title, url, langs)
        self._p_changed = 1

    def delete_networkportal_item(self, ids):
        #delete 1 or more items
        map(self.__delete_networkportal_item, ids)
        self._p_changed = 1
