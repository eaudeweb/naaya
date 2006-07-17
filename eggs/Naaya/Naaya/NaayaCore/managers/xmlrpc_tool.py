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
import xmlrpclib

#Zope imports

#Product imports

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

class XMLRPCConnector:
    """ """

    def __init__(self, http_proxy):
        """ """
        self.http_proxy = http_proxy

    def __call__(self, url, method, *args):
        """ """
        transport = ProxiedTransport()
        transport.set_proxy(self.http_proxy)
        #try to connect without proxy
        try:
            server = xmlrpclib.Server('%s/' % url)
            return getattr(server, method)(*args)
        except:
            #try to connect with proxy
            try:
                server = xmlrpclib.Server('%s/' % url, transport=transport)
                return getattr(server, method)(*args)
            except:
                return None
