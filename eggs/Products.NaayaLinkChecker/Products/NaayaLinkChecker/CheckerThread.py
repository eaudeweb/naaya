from http.client import InvalidURL
from queue import Empty
import socket
import ssl
from threading import Thread
import time
from types import *

import urllib.request

class CheckerThread(Thread):
    """Thread for checking URLs.

        URLs with unsupported protocols will be considered OK.
    """

    def __init__(self, urls, logresults, proxy):
        """CheckerThread constructor.

            @param urls: a queue of URLs to check
            @type urls: Queue of strings
            @param proxy: proxy
        """
        Thread.__init__(self)
        self.urls = urls
        self.logresults = logresults
        self.proxy = proxy

    def _isSupported(self, url):
        """Returns True if the protocol from url is supported, False otherwise"""
        for i in 'http:', 'https:', 'ftp', 'gopher:':
            if url.startswith(i):
                return True
        return False

    def run(self):
        while True:
            try:
                url = self.urls.get_nowait()
                if not self._isSupported(url):
                    self.logresults[url] = 'OK'
                    continue
            except Empty:
                break
            result = check_link(url, self.proxy)
            self.logresults[url] = str(result)


def check_link(url, proxy=''):
    handlers = []
    if proxy:
        handlers.append(urllib.request.ProxyHandler({'http': proxy, 'https': proxy}))
    opener = urllib.request.build_opener(*handlers)
    opener.addheaders = [('User-Agent', 'Naaya Link Checker')]
    try:
        resp = opener.open(url, timeout=20)
        resp.close()
        return 'OK'
    except IOError as e:
        if getattr(e, 'reason', None) and 'timed out' in str(e.reason):
            return "Timeout"
        return "I/O error: %r %s" % (e, e)
    except socket.timeout:
        return "Attempted connect timed out."
    except ssl.SSLError as err:
        return "SSL error: " + str(err)
    except InvalidURL:
        return "Invalid URL"
    except Exception as e:
        return "Link checker internal error: " + str(e)
