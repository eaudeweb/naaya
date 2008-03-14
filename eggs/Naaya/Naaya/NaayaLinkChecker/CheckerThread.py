#The contents of this file are subject to the Mozilla Public
#License Version 1.1 (the "License"); you may not use this file
#except in compliance with the License. You may obtain a copy of
#the License at http://www.mozilla.org/MPL/
#
#Software distributed under the License is distributed on an "AS
#IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
#implied. See the License for the specific language governing
#rights and limitations under the License.
#
#The Initial Owner of the Original Code is European Environment
#Agency (EEA).  Portions created by Finsiel Romania are
#Copyright (C) 2006 by European Environment Agency.  All
#Rights Reserved.
#
#Contributor(s):
#  Original Code: Cornel Nitu (Finsiel Romania)

from httplib import InvalidURL
from Queue import Empty
import socket
from threading import Thread
import time
from types import *

from MyURLopener import MyURLopener

class CheckerThread(Thread):

    def __init__(self, urls, logresults, proxy):
        """
            @param urls: a queue of URLs to check
            @type urls: Queue of strings
            @param proxy: proxy
        """
        Thread.__init__(self)
        self.urls = urls
        self.logresults = logresults
        self.proxy = proxy

    def run(self):
        while True:
            try:
                url = self.urls.get_nowait()
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
            msg = self.sanitize(msg)
            return msg
        except socket.timeout:
            return "Attempted connect timed out."
        except socket.sslerror, err:
            return "SSL error: " + err
        except InvalidURL:
            return "Invalid URL."

    def sanitize(self, msg):
        if isinstance(IOError, ClassType) and isinstance(msg, IOError):
            # Do the other branch recursively
            msg.args = self.sanitize(msg.args)
        elif isinstance(msg, TupleType):
            if len(msg) >= 4 and msg[0] == 'http error' and isinstance(msg[3], InstanceType):
                # Remove the Message instance -- it may contain
                # a file object which prevents pickling.
                msg = str(msg[1]) + ': ' + str(msg[2])
        return msg
