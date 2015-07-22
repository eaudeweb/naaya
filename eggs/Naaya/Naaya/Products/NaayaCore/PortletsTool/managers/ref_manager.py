
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo


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

    def get_list(self, sort_attr='title'):
        #get a list with all items
        try: return self.utSortObjsListByAttr(self.__collection.values(), sort_attr, 0)
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
