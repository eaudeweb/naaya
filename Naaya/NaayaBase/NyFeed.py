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
# Dragos Chirila, Finsiel Romania

#Python imports
import feedparser
from copy import deepcopy

#Zope imports

#Product imports

class NyFeed:
    """ """

    def __init__(self):
        """ """
        self.__feed_gone = 0
        self.__feed_feed = None
        self.__feed_status = None
        self.__feed_version = None
        self.__feed_bozo_exception = None
        self.__feed_encoding = None
        self.__feed_etag = None
        self.__feed_modified = None
        self.__feed_entries = []

    def __set_feed(self, gone=0, feed=None, status=None, version=None, bozo_exception=None, encoding=None, etag=None,
        modified=None, entries=None):
        #set feed info
        self.__feed_gone = gone
        if feed is not None: self.__feed_feed = deepcopy(feed)
        else: self.__feed_feed = None
        self.__feed_status = status
        self.__feed_version = version
        self.__feed_bozo_exception = bozo_exception
        self.__feed_encoding = encoding
        self.__feed_etag = etag
        self.__feed_modified = modified
        if entries is not None: self.__feed_entries = deepcopy(entries)
        else: self.__feed_entries = []
        self._p_changed = 1

    #api
    def get_feed_gone(self): return self.__feed_gone
    def get_feed_status(self): return self.__feed_status
    def get_feed_version(self): return self.__feed_version
    def get_feed_bozo_exception(self): return self.__feed_bozo_exception
    def get_feed_encoding(self): return self.__feed_encoding
    def get_feed_etag(self): return self.__feed_etag
    def get_feed_modified(self): return self.__feed_modified

    def get_feed_title(self):
        try: return self.__feed_feed.title
        except: return ''

    def get_feed_url(self):
        #abstract method; this should be implemented by the class who extends NyFeed
        #return the value of the feed url (this can be stored in whatever.. variable)
        raise NotImplementedError, 'get_feed_url'

    def set_new_feed_url(self):
        #abstract method; this should be implemented by the class who extends NyFeed
        #after receiving a 301 status code, the feed url must be changed
        raise NotImplementedError, 'set_new_feed_url'

    def get_feed_items(self):return self.__feed_entries
    def count_feed_items(self): return len(self.__feed_entries)

    def get_feed_item_title(self, item): return item['title']
    def get_feed_item_link(self, item): return item['link']
    def get_feed_item_keys(self, item):
        #returns all item keys without 'title' and 'link'
        l_keys = item.keys()
        if 'title' in l_keys: l_keys.remove('title')
        if 'link' in l_keys: l_keys.remove('link')
        return l_keys
    def get_feed_item_value(self, item, key):
        value = item.get(key, None)
        if type(value) == type(u''): value = value
        return value

    def harvest_feed(self):
        p = feedparser.parse(self.get_feed_url(), etag=self.__feed_etag, modified=self.__feed_modified)
        if p.get('bozo', 0) == 1:
            #some error occurred
            if p.has_key('status'):
                if p.status == 304:
                    #the feed was not modified; do nothing
                    self.__feed_status = p.status
                    self._p_changed = 1
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
                elif p.status == 200:
                    #the feed was harvested but with a warning
                    #store feed stuff
                    if p.etag != '': etag = p.etag
                    else: etag = None
                    if p.has_key('modified'): modified = p.modified
                    else: modified = None
                    self.__set_feed(feed=p.feed, status=p.status, version=p.version, encoding=p.encoding, etag=etag,
                        modified=modified, entries=p.entries)
                else:
                    #don't know how to handle this; set it as error
                    error = str(p.bozo_exception)
                    self.__set_feed(bozo_exception=error)
            else:
                error = str(p.bozo_exception)
                self.__set_feed(bozo_exception=error)
        else:
            #no error; check for status
            if p.has_key('status'):
                if p.status == 301:
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
                    self.__feed_status = p.status
                    self._p_changed = 1
                elif p.status == 200:
                    #everything is OK
                    #store feed stuff
                    if p.etag != '': etag = p.etag
                    else: etag = None
                    if p.has_key('modified'): modified = p.modified
                    else: modified = None
                    self.__set_feed(feed=p.feed, status=p.status, version=p.version, encoding=p.encoding, etag=etag,
                        modified=modified, entries=p.entries)
                elif p.status == 410:
                    #the feed is gone; DO NOT HARVEST ANYMORE!!!
                    self.set_new_feed_url('')
                    error = 'The feed is gone. Do not harvest it anymore!'
                    self.__set_feed(gone=1, bozo_exception=error)
                else:
                    #don't know how to handle this; set it as error
                    error = 'Don\'t know how to handle this status %s' % p.status
                    self.__set_feed(bozo_exception=error, status=p.status)
            else:
                #don't know how to handle this; set it as error
                error = 'Don\'t know how to handle this, missing status'
                self.__set_feed(bozo_exception=error)
        p = None
