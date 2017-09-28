
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo


class link_item:
    """ """

    def __init__(self, id, title, description, url, relative, permission, order):
        self.id = id
        self.title = title
        self.description = description
        self.url = url
        self.relative = relative
        self.permission = permission
        self.order = order

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

InitializeClass(link_item)

class links_manager:
    """ """

    def __init__(self):
        """ """
        self.__links_collection = {}

    #security stuff
    security = ClassSecurityInfo()

    def __add_link_item(self, id, title, description, url, relative, permission, order):
        #create a new item
        item = link_item(id, title, description, url, relative, permission, order)
        self.__links_collection[id] = item

    def __update_link_item(self, id, title, description, url, relative, permission, order):
        #modify an item
        try:
            item = self.__links_collection[id]
        except:
            pass
        else:
            item.title = title
            item.description = description
            item.url = url
            item.relative = relative
            item.permission = permission
            item.order = order

    def __delete_link_item(self, id):
        #delete an item
        try: del(self.__links_collection[id])
        except: pass

    #api
    def get_links_collection(self):
        #get the collection
        return self.__links_collection

    def get_links_list(self):
        #get a list with all items
        try: return self.utSortObjsListByAttr(self.__links_collection.values(), 'order', 0)
        except: return []

    def get_link_item(self, id):
        #get an item
        try: return self.__links_collection[id]
        except: return None

    def get_link_item_data(self, id):
        #get an item data
        item = self.get_link_item(id)
        if item is not None:
            return ['update', item.id, item.title, item.description, item.url, item.relative, item.permission, item.order]
        else:
            return ['add', '', '', '', '', 0, '', '0']

    def add_link_item(self, id, title, description, url, relative, permission, order):
        #create a new item
        self.__add_link_item(id, title, description, url, relative, permission, order)
        self._p_changed = 1

    def update_link_item(self, id, title, description, url, relative, permission, order):
        #modify an item
        self.__update_link_item(id, title, description, url, relative, permission, order)
        self._p_changed = 1

    def delete_link_item(self, ids):
        #delete 1 or more items
        map(self.__delete_link_item, ids)
        self._p_changed = 1

InitializeClass(links_manager)
