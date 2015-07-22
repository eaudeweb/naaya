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
#$Id: search_tool.py 3693 2005-05-23 09:13:47Z chiridra $

#Python imports
import xmlrpclib
from DateTime import DateTime

#Product imports
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
