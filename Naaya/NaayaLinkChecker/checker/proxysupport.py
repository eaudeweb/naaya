
import urllib
from _exceptions import ProxyError

class ProxySupport:
    """
    Get support for proxying
    """

    def set_proxy (self, proxy):
        """
        Parse given proxy information and store parsed values.
        Note that only http:// proxies are supported, both for ftp://
        and http:// URLs.
        """

        self.proxy = proxy
        if not self.proxy:
            return

        if self.proxy[:7].lower() != "http://":
            raise ProxyError, "Proxy value %r must start with 'http://'." % self.proxy

        self.proxy = urllib.splittype(self.proxy)   #xxx sa vedem ce se intampla
