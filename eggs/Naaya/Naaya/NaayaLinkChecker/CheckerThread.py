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
# Portions created by EEA are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Contributor:
# Cornel Nitu, Finsiel Romania
#
# $Id: CheckerThread.py 864 2003-12-08 17:14:01Z finrocvs $
#

from types import *
import socket
import threading
import time

from MyURLopener import MyURLopener
import LinkChecker
logresults = {}

class CheckerThread(threading.Thread):

    def __init__(self, URLList, URLListLock, proxy):
        threading.Thread.__init__(self)
        self.URLList = URLList
        self.URLListLock = URLListLock
        self.proxy = proxy

    def grabNextURL(self):
        self.URLListLock.acquire(1)
        if (len(self.URLList) < 1):
            NextURL = None
        else:
            NextURL = self.URLList[0]
            del self.URLList[0]
        self.URLListLock.release()
        return NextURL

    def run(self):
        while 1:
            NextURL = self.grabNextURL()
            if (NextURL == None):
                break;
            result = self.readhtml(NextURL)
            logresults[NextURL] = str(result)

    def readhtml(self, url):
        file = MyURLopener()
        if self.proxy != '':
            file.proxies['http'] = self.proxy
        try:
            socket.setdefaulttimeout(5)
            file.open(url)
            file.close()
            return 'OK'
        except IOError, msg:
            msg = self.sanitize(msg)
            return msg
        except socket.timeout:
            return "Attempted connect timed out."

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