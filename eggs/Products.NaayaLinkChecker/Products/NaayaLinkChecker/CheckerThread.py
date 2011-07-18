from httplib import InvalidURL
from Queue import Empty
import socket
from threading import Thread
import time
from types import *

from MyURLopener import MyURLopener

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
            result = self.readhtml(url)
            self.logresults[url] = str(result)

    def readhtml(self, url):
        file = MyURLopener()
        if self.proxy != '':
            file.proxies['http'] = self.proxy
        socket.setdefaulttimeout(5)
        try:
            file.open(url)
            file.close()
            return 'OK'
        except IOError, msg:
            return "I/O error: %r %s" % (msg, msg)
        except socket.timeout:
            return "Attempted connect timed out."
        except socket.sslerror, err:
            return "SSL error: " + err
        except InvalidURL:
            return "Invalid URL."
        except Exception, e:
            return "Link checker error: " + err
