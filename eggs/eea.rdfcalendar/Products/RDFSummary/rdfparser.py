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
# The Original Code is RDFSummary version 1.0.
#
# The Initial Developer of the Original Code is European Environment
# Agency (EEA).  Portions created by CMG and Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Contributor(s):
# Soren Roug, EEA
# Dominique Dutoit, European Commission
# Tomas Hjelmberg, CMG
# URAGO Keisuke, <bravo@resourcez.org> - for slash code
# David Chandek-Stark for RSS 2.0 additions in known_items.
# Histoshi Igarashi for fail-tolerance in end_image and unknown_endtag
# Keisuke Urago for content module
#
#
#
# $Id: RDFSummary.py 3319 2005-04-07 08:50:31Z roug $

import urllib2
import feedparser
from copy import deepcopy

class RDFParser:
    """ Parse an RSS/RDF file using feedparser module """

    def __init__(self, proxy, fetchimage):
        self.channel = {}
        self.textinput = {}
        self.items = []
        self.image = {}
        self.encoding = None
        if proxy:
            self._proxies = {'http': proxy}
        else:
            self._proxies = {}
        self.fetchimage = fetchimage
        #other stuff
        self.feed_gone = 0
        self.feed_status = None
        self.feed_version = None
        self.feed_bozo_exception = None
        self.feed_encoding = None
        self.feed_etag = None
        self.feed_modified = None
        self.feed_redirect = None

    def set_new_feed_url(self, feed_url):
        """ after receiving a 301 status code, the feed url must be changed """
        self.feed_redirect = feed_url

    def __set_feed(self, gone=0, feed=None, status=None, version=None, bozo_exception=None, encoding=None, etag=None,
        modified=None, entries=None):
        #set feed info
        if feed is not None:
            for k,v in feed.items():
                self.channel[k] = v
            #additional keys
            try: self.channel['description'] = feed.description
            except: pass
            self.channel['encoding'] = encoding
            try: del(self.channel['links'])
            except: pass
            if self.channel.has_key('image'):
                for k,v in self.channel['image'].items():
                    self.image[k] = v
                try: self.get_image(self.channel['image']['url'])
                except: pass
            if self.channel.has_key('textinput'):
                for k,v in self.channel['textinput'].items():
                    self.textinput[k] = v
            #remove keys
            for k,v in self.channel.items():
                if type(v) != type(u'') and type(v) != type(''):
                    del(self.channel[k])
        else: self.channel = {}

        self.feed_gone = gone
        self.feed_status = status
        self.feed_version = version
        self.feed_bozo_exception = bozo_exception
        self.feed_encoding = encoding
        self.feed_etag = etag
        self.feed_modified = modified

        if entries is not None:
            self.items = deepcopy(entries)
            for item in self.items:
                #additional keys
                try: item['creator'] = item['author']
                except: pass
                try: item['description'] = item.summary
                except: pass
                try: item['rdfsubject'] = item['id']
                except: pass
                #rename keys for RDFCalendar
                try:
                    item['startdate'] = item['ev_startdate']
                    del item['ev_startdate']
                except: pass
                try:
                    item['organizer'] = item['ev_organizer']
                    del item['ev_organizer']
                except: pass
                try:
                    item['location'] = item['ev_location']
                    del item['ev_location']
                except: pass
                try:
                    item['enddate'] = item['ev_enddate']
                    del item['ev_enddate']
                except: pass
                try:
                    item['type'] = item['ev_type']
                    del item['ev_type']
                except: pass
                #remove keys
                for k,v in item.items():
                    if type(v) != type(u'') and type(v) != type(''):
                        del(item[k])
        else: self.items = []

    def open_url(self, url, proxy_support):
        import base64, urllib
        auth = None
        urltype, rest = urllib.splittype(url)
        realhost, rest = urllib.splithost(rest)
        if realhost:
            user_passwd, realhost = urllib.splituser(realhost)
            if user_passwd:
                url = "%s://%s%s" % (urltype, realhost, rest)
                auth = base64.encodestring(user_passwd).strip()

        # try to open with urllib2 (to use optional headers)
        request = urllib2.Request(url)
        request.add_header("User-Agent", 'RDFSummary (helpdesk@eionet.eu.int)')
        request.add_header("Accept-encoding", "")
        if auth:
            request.add_header("Authorization", "Basic %s" % auth)
        opener = urllib2.build_opener(proxy_support, auth, urllib2.HTTPHandler)
        opener.addheaders = []
        try:
            return opener.open(request)
        finally:
            opener.close() # JohnD

    def parse_url(self, url, etag, modified, REQUEST):
        """ Grab the file from the webserver and feed it to the parser """
        self.baseurl = url
        proxy_support = urllib2.ProxyHandler(self._proxies)
        f = self.open_url(url, proxy_support)

        if not f:
            raise IOError, "Failure in open"
        self.rdfsource = f.read()

        if self.rdfsource:
            proxy_support = urllib2.ProxyHandler(self._proxies)
            p = feedparser.parse(url, etag=etag, modified=modified, handlers=[proxy_support])
            if p.get('bozo', 0) == 1:
                #some error occurred
                if p.has_key('status'):
                    if p.status == 200:
                        #the feed was harvested but with a warning
                        #store feed stuff
                        if p.etag != '': etag = p.etag
                        else: etag = None
                        if p.has_key('modified'): modified = p.modified
                        else: modified = None
                        self.__set_feed(feed=p.feed, status=p.status, version=p.version, encoding=p.encoding, etag=etag,
                            modified=modified, entries=p.entries)
                    elif p.status == 301:
                        #the feed was permanently moved to a new location
                        #update the new location and also store feed stuff
                        self.set_new_feed_url(p.url)
                    elif p.status == 304:
                        #the feed was not modified; do nothing
                        self.feed_status = p.status
                    else:
                        #don't know how to handle this; set it as error
                        raise RuntimeError, str(p.bozo_exception)
                else:
                    raise RuntimeError, str(p.bozo_exception)
            else:
                #no error; check for status
                if p.has_key('status'):
                    if p.status == 200:
                        #everything is OK
                        #store feed stuff
                        if p.etag != '': etag = p.etag
                        else: etag = None
                        if p.has_key('modified'): modified = p.modified
                        else: modified = None
                        self.__set_feed(feed=p.feed, status=p.status, version=p.version, encoding=p.encoding, etag=etag,
                            modified=modified, entries=p.entries)
                    elif p.status == 301:
                        #the feed was permanently moved to a new location
                        #update the new location and also store feed stuff
                        self.set_new_feed_url(p.url)
                        if p.etag != '': etag = p.etag
                        else: etag = None
                        if p.has_key('modified'): modified = p.modified
                        else: modified = None
                        self.__set_feed(feed=p.feed, status=p.status, version=p.version, encoding=p.encoding, etag=etag,
                            modified=modified, entries=p.entries)
                    elif p.status == 302:
                        #the feed was temporarily moved to a new location
                        #store feed stuff
                        if p.etag != '': etag = p.etag
                        else: etag = None
                        if p.has_key('modified'): modified = p.modified
                        else: modified = None
                        self.__set_feed(feed=p.feed, status=p.status, version=p.version, encoding=p.encoding, etag=etag,
                            modified=modified, entries=p.entries)
                    elif p.status == 304:
                        #the feed was not modified; do nothing
                        self.feed_status = p.status
                    elif p.status == 410:
                        #the feed is gone; DO NOT HARVEST ANYMORE!!!
                        raise RuntimeError, 'The feed is gone. Do not harvest it anymore!'
                    else:
                        #don't know how to handle this; set it as error
                        raise RuntimeError, 'Don\'t know how to handle this status %s' % p.status
                else:
                    #don't know how to handle this; set it as error
                    raise RuntimeError, 'Don\'t know how to handle this, missing status'
            p = None
        else:
            raise RuntimeError, "Unable to GET content"

    def get_image(self, img_url):
        if self.fetchimage != "yes":
            return
        try:
            proxy_support = urllib2.ProxyHandler(self._proxies)
            opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)

            urllib2.install_opener(opener)
            f = urllib2.urlopen(img_url)

            if not f:
                raise IOError, "Failure in open"
            data = f.read()
            headers = f.info()
            f.close()
            if headers.has_key('content-type'):
                ctype=headers['content-type']
            else:
                ctype='image/gif'

            # now to import the image data
            self.image['data'] = data
            self.image['content_type'] = ctype
            self.image['size'] = len(data)
        except:
            return
