import xmlrpclib
import string
import httplib
from base64 import encodestring

class BasicAuthTransport(xmlrpclib.Transport):
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password
        self.verbose = None
        self.has_ssl = httplib.__dict__.has_key("HTTPConnection")

    def request(self, host, handler, request_body, verbose=None):
        # issue XML-RPC request
        if self.has_ssl:
            if host.startswith("https:"): h = httplib.HTTPSConnection(host)
            else: h = httplib.HTTPConnection(host)
        else: h = httplib.HTTP(host)

        h.putrequest("POST", handler)

        # required by HTTP/1.1
        if not self.has_ssl: # HTTPConnection already does 1.1
            h.putheader("Host", host)
        h.putheader("Connection", "close")

        # required by XML-RPC
        h.putheader("User-Agent", self.user_agent)
        h.putheader("Content-Type", "text/xml")
        h.putheader("Content-Length", str(len(request_body)))

        # basic auth
        if self.username is not None and self.password is not None:
            h.putheader("AUTHORIZATION", "Basic %s" % string.replace(
                    encodestring("%s:%s" % (self.username, self.password)),
                    "\012", ""))
        h.endheaders()

        if request_body: h.send(request_body)
        if self.has_ssl:
            response = h.getresponse()
            if response.status != 200:
                raise xmlrpclib.ProtocolError(host + handler,
                                              response.status,
                                              response.reason,
                                              response.msg)
            file = response.fp
        else:
            errcode, errmsg, headers = h.getreply()
            if errcode != 200:
                raise xmlrpclib.ProtocolError(host + handler, errcode, errmsg, headers)

            file = h.getfile()

        return self.parse_response(file)

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

    def __init__(self, http_proxy, uid='', pwd=''):
        """ """
        self.http_proxy = http_proxy
        self.uid = uid
        self.pwd = pwd

    def __call__(self, url, method, *args):
        """ """
        transport = ProxiedTransport()
        transport.set_proxy(self.http_proxy)
        #try to connect without proxy
        try:
            if self.uid and self.pwd:
                server = xmlrpclib.Server('%s/' % url, BasicAuthTransport(self.uid, self.pwd))
            else:
                server = xmlrpclib.Server('%s/' % url)
            return getattr(server, method)(*args)
        except:
            #try to connect with proxy
            try:
                if self.uid and self.pwd:
                    server = xmlrpclib.Server('%s/' % url, BasicAuthTransport(self.uid, self.pwd), transport=transport)
                else:
                    server = xmlrpclib.Server('%s/' % url, transport=transport)
                return getattr(server, method)(*args)
            except:
                return None