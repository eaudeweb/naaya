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

class search_tool:
    """ """

    def __init__(self):
        """ """
        pass

    def get_repository_sites(self, repo_server_url):
        transport = ProxiedTransport()
        transport.set_proxy(self.http_proxy)
        sites = {}
        #try to connect without proxy
        try:
            site = xmlrpclib.Server('%s/' % repo_server_url)
            sites = site.get_sites()
        except:
            #try to connect with proxy
            try:
                site = xmlrpclib.Server('%s/' % repo_server_url, transport=transport)
                sites = site.get_sites()
            except:
                pass
        return sites

    def external_ew_search(self, servers, query):
        results = []
        transport = ProxiedTransport()
        transport.set_proxy(self.http_proxy)
        for server in servers:
            #try to connect without proxy
            try:
                site = xmlrpclib.Server('%s/' % server)
                results.append(site.external_search(query))
            except:
                #try to connect with proxy
                try:
                    site = xmlrpclib.Server('%s/' % server, transport=transport)
                    results.append(site.external_search(query))
                except:
                    pass
        if results == []: results = [[]]
        return results

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

class ProxiedTransport(xmlrpclib.Transport):

    def set_proxy(self, proxy=None):
        self.proxy = proxy

    def make_connection(self, host):
        self.realhost = host
        import httplib
        return httplib.HTTP(self.proxy)

    def send_request(self, connection, handler, request_body):
        connection.putrequest("POST", 'http://%s%s' % (self.realhost, handler))

    def send_host(self, connection, host):
        connection.putheader('Host', self.realhost)
