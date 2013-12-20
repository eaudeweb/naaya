import xmlrpclib
from DateTime import DateTime

from xmlrpc_tool import ProxiedTransport

class search_tool:
    """ """

    def __init__(self):
        """ """
        pass

    def external_get_items_age(self, search_list, age):
        """ """
        if len(search_list)==0:
            return 0
        items_old=0
        for item in search_list:
            items_old = items_old + self.external_get_item_age(item['time'], age)
        return (items_old*100)/len(search_list)

    def external_get_item_age(self, item, age):
        """ """
        item_date = DateTime(item)
        current_date = DateTime()
        difference = current_date-item_date
        if difference >= age*30:
            return 1
        return 0

    def internal_get_items_age(self, search_list, age):
        """ comments here """
        if len(search_list) == 0:
            return 0
        items_old = 0
        for item in search_list:
            items_old = items_old + self.internal_get_item_age(item.bobobase_modification_time(), age)
        return (items_old*100)/len(search_list)

    def internal_get_item_age(self, item, age):
        """ comments here """
        item_date = item
        current_date = DateTime()
        difference = current_date - item_date
        if difference >= age*30:
            return 1
        return 0
