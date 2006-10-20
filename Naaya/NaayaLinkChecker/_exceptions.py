from exceptions import Exception

class ProxyError(Exception):
    """
        Invalid proxies might raise TypeError in urllib2,
        so make sure to stop checking at this point, not later.
    """
    pass